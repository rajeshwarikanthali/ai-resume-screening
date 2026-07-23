import pdfplumber
import re
import json
import os
import logging
from typing import Optional, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# ---------------------------------------------------------------------------
# Skills dictionary loading
# ---------------------------------------------------------------------------
def load_skills_from_json(path: Optional[str] = None) -> dict:
    """Load skills from external JSON file; falls back to built-in dict."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "skills.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            flat = {}
            for category, skills in raw.items():
                for skill_name, aliases in skills.items():
                    flat[skill_name] = aliases
            logger.info("Loaded %d skills from %s", len(flat), path)
            return flat
        except Exception as exc:
            logger.error("Failed to load skills from %s: %s", path, exc)
    logger.warning("skills.json not found; using built-in fallback")
    return _builtin_skills()


def _builtin_skills():
    """Minimal fallback when skills.json is unavailable."""
    return {
        "Python": ["python"], "Java": ["java"], "C++": ["c++", "cpp"],
        "JavaScript": ["javascript", "js"], "SQL": ["sql"],
        "Machine Learning": ["machine learning", "ml"],
        "Data Science": ["data science", "ds"],
        "AWS": ["aws"], "Docker": ["docker"], "Git": ["git"],
        "HTML": ["html"], "CSS": ["css"], "React": ["react"],
        "Node.js": ["nodejs", "node js"], "Pandas": ["pandas"],
        "NumPy": ["numpy"], "TensorFlow": ["tensorflow"],
        "PyTorch": ["pytorch"], "Flask": ["flask"], "Django": ["django"],
    }


SKILLS = load_skills_from_json()


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF file using pdfplumber.
    If pdfplumber returns very little text (likely a scanned PDF),
    attempt OCR via pytesseract as a fallback.
    Returns the extracted text string (may be empty on failure).
    """
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if len(text.strip()) < 50:
            logger.info(
                "pdfplumber extracted only %d chars; attempting OCR fallback",
                len(text.strip()),
            )
            ocr_text = _ocr_fallback(uploaded_file)
            if ocr_text:
                logger.info("OCR fallback succeeded (%d chars)", len(ocr_text))
                return ocr_text
            logger.warning("OCR fallback also returned no text.")
        return text
    except Exception as e:
        logger.error("PDF extraction failed: %s", e, exc_info=True)
        return ""


def _ocr_fallback(uploaded_file):
    """Attempt OCR on the PDF using pdf2image + pytesseract."""
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
    except ImportError:
        logger.warning(
            "pdf2image or pytesseract not installed. "
            "pip install pdf2image pytesseract pillow"
        )
        return ""
    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes)
        full_text = []
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            full_text.append(page_text)
        return "\n".join(full_text)
    except Exception as ocr_err:
        logger.error("OCR fallback failed: %s", ocr_err, exc_info=True)
        return ""


# Headers that should never be treated as a candidate name
_KNOWN_HEADERS = {
    "curriculum vitae", "cv", "resume", "resume", "profile",
    "objective", "career objective", "professional summary",
    "summary", "work experience", "experience", "education",
    "skills", "technical skills", "certifications", "projects",
    "publications", "languages", "interests", "contact",
    "references", "personal details", "personal information",
    "about me", "qualifications", "employment history",
    "achievements", "accomplishments", "volunteer experience",
    "internship", "internships", "trainings", "training",
    "declaration", "hobbies", "strengths",
}


def extract_name(text):
    """
    Extract candidate name from resume text using smarter heuristics:
    1. Look at the first 10 non-empty lines
    2. Match 2-4 capitalized words (e.g., "First Last")
    3. Skip known section headers
    4. Fall back to first alphabetical line
    """
    lines = text.split("\n")
    name_candidates = []
    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue
        if line.lower().strip(":") in _KNOWN_HEADERS:
            continue
        if len(line) < 3 or len(line) > 50:
            continue
        if re.search(r'[0-9@#$%^&*()_+=<>?/\\|~`]', line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(w[0].isupper() for w in words if w):
                name_candidates.append(line)
        elif len(words) == 1 and words[0].isalpha() and words[0][0].isupper():
            name_candidates.append(line)
    if name_candidates:
        for candidate in name_candidates:
            if len(candidate.split()) >= 2:
                return candidate
        return name_candidates[0]
    for line in lines:
        line = line.strip()
        if 3 < len(line) < 50:
            if line.replace(" ", "").isalpha():
                return line
    return "Not Found"


def extract_email(text):
    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    emails = re.findall(pattern, text)
    if emails:
        return emails[0]
    return "Not Found"

def extract_phone_number(text):
    pattern = r'(?:\+91[- ]?)?[6-9]\d{9}'
    phones = re.findall(pattern, text)
    if phones:
        return phones[0]
    return "Not Found"


def extract_skills(text):
    """
    Extract skills from text using the module-level SKILLS dictionary
    (loaded from skills.json at import time).
    """
    text = text.lower()
    found_skills = []
    for main_skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, text):
                if main_skill not in found_skills:
                    found_skills.append(main_skill)
                break
    return found_skills


def extract_candidate_info(resume_text):
    """
    Extracts structured candidate info from resume text using the
    regex-based extractors below.
    """
    return {
        "name": extract_name(resume_text),
        "email": extract_email(resume_text),
        "phone": extract_phone_number(resume_text),
        "skills": extract_skills(resume_text),
        "experience_years": calculate_experience_score(resume_text),
        "summary": "",
    }


def calculate_resume_match(resume_text,job_description):

    documents = [resume_text,job_description]

    vectorizer = TfidfVectorizer()

    matrix = vectorizer.fit_transform(documents)

    similarity_score = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )
    score = round(similarity_score[0][0] * 100,2)
    return score


def calculate_skill_score(skills, job_description):
    jd = job_description.lower()
    matched = sum(1 for skill in skills if skill.lower() in jd)
    return min(matched * 4, 40)


def calculate_resume_score(resume_match):
    return round(resume_match * 0.30, 2)


def calculate_project_score(text):
    count = len(re.findall(r'\bproject\b', text.lower()))
    return min(count * 2, 10)


def calculate_certification_score(text):
    count = len(re.findall(r'\bcertif\w+', text.lower()))
    return min(count, 5)


def calculate_experience_score(text):
    match = re.search(r'(\d+)\s*(?:\+\s*)?year', text.lower())
    if match:
        return min(int(match.group(1)), 5)
    return 0


def calculate_ats_score(skill_score, resume_score, project_score, certification_score, experience_score):
    score = skill_score + resume_score + project_score + certification_score + experience_score
    return round(min(score, 100), 2)


def get_candidate_status(ats_score):
    if ats_score >= 80:
        return "SHORTLISTED"
    return "NOT SHORTLISTED"


def get_candidate_rank(ats_score):
    if ats_score >=80:
        return "Rank - 1"
    elif ats_score >= 70:
        return "Rank - 2"
    elif ats_score >= 60:
        return "Rank - 3"
    else:
        return "Rank - 4"


def calculate_skill_match_percentage(candidate_skills, jd_skills):
    """
    Percentage of the job description's required skills that the
    candidate actually has, based on the shared skills dictionary.
    """
    if not jd_skills:
        return 0.0
    candidate_set = {s.lower() for s in candidate_skills}
    matched = sum(1 for skill in jd_skills if skill.lower() in candidate_set)
    return round((matched / len(jd_skills)) * 100, 2)


def detect_missing_skills(candidate_skills, jd_skills):
    """
    Skills required by the job description (per the shared skills
    dictionary) that were not found in the candidate's resume.
    """
    candidate_set = {s.lower() for s in candidate_skills}
    return [skill for skill in jd_skills if skill.lower() not in candidate_set]


def get_recruiter_recommendation(ats_score):
    if ats_score >= 90:
        return "success", "Highly Recommended for Interview."
    elif ats_score >= 80:
        return "success", "Recommended for Interview."
    elif ats_score >= 70:
        return "success", "Candidate can be considered."
    elif ats_score >= 60:
        return "warning", "Candidate partially matches the requirements."
    else:
        return "error", "Candidate does not sufficiently match the requirements."


def get_recommendation_reasons(skill_match_percentage, resume_match, project_score,
                                certification_score, experience_score, missing_skills):
    """
    Explains WHY the candidate did or didn't meet the requirements,
    referencing the actual sub-scores and missing skills so the
    recommendation isn't just a bare verdict.
    """
    reasons = []

    if skill_match_percentage < 50:
        reasons.append(f"Only {skill_match_percentage}% of the required skills were found on the resume.")
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        reasons.append(f"Missing key skills from the job description: {top_missing}.")
    if resume_match < 40:
        reasons.append(f"Overall resume-to-JD text match is low ({resume_match}%).")
    if project_score < 4:
        reasons.append("Resume shows limited or no relevant project experience.")
    if certification_score < 1:
        reasons.append("No relevant certifications were detected.")
    if experience_score < 1:
        reasons.append("No clear years of experience were detected on the resume.")

    if not reasons:
        reasons.append("Candidate meets the core requirements found in the job description.")

    return reasons


def generate_resume_suggestions(project_score, certification_score, experience_score, missing_skills):
    """
    Rule-based, actionable suggestions for improving the resume,
    derived from the same sub-scores already being calculated.
    """
    suggestions = []

    if project_score < 6:
        suggestions.append(
            "Add more project entries with clear outcomes — mention the tools used and measurable results."
        )
    if certification_score < 2:
        suggestions.append(
            "Consider adding relevant certifications to strengthen credibility for this role."
        )
    if experience_score < 2:
        suggestions.append(
            "Clarify years of experience explicitly (e.g. '3+ years') so it's easy to detect."
        )
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(
            f"The job description mentions skills not found on the resume: {top_missing}. "
            "Add them if applicable, or consider upskilling in these areas."
        )
    if not suggestions:
        suggestions.append("Resume looks strong against this job description — no major gaps detected.")

    return suggestions