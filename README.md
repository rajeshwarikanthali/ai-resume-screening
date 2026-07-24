# AI Resume Screening System

An intelligent, AI-powered resume screening application built with **Streamlit**, **scikit-learn**, **Plotly**, and **SQLite**. It evaluates candidate resumes against job descriptions using NLP, skill matching, and multi-factor scoring — all wrapped in a modern dark-themed UI.

---

## Features

###  Candidate Analysis
- **PDF Resume Parsing** — Extracts text from PDF resumes (supports OCR fallback for scanned documents)
- **Candidate Information Extraction** — Automatically extracts name, email, phone, and skills from resumes
- **ATS Score Calculation** — Multi-factor scoring system:
  - Resume Match (TF-IDF cosine similarity)
  - Skill Score (matched skills against job description)
  - Project Experience Score
  - Certification Score
  - Experience Years Score
- **Skill Matching** — Compares candidate skills against job description requirements using a comprehensive skills dictionary (250+ skills across 12 categories)
- **Missing Skills Detection** — Identifies skills required by the job but missing from the resume
- **Recruiter Recommendations** — Generates actionable recommendations and resume improvement suggestions
- **Radar Chart Visualization** — Visual breakdown of candidate performance across all scoring dimensions

###  Recruiter Dashboard
- **Live Statistics** — Total candidates, shortlisted/not-shortlisted counts, average ATS score
- **Data Visualization** — Bar charts for ATS scores by candidate, pie charts for shortlisted vs not-shortlisted
- **Candidate Table** — Sortable, filterable table with status and name search
- **CSV Export** — Download full candidate reports
- **Top Candidates** — Configurable leaderboard of top-scoring candidates

###  UI/UX
- Dark theme with gradient backgrounds and card-based layout
- Animated ATS score gauge (SVG-based circular progress)
- Color-coded skill badges (matched vs missing)
- Status badges with emoji indicators
- Animated loading status for analysis progress
- Responsive design with custom scrollbar
- Interactive Plotly charts

---

##  Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web application framework |
| **scikit-learn** | TF-IDF vectorization & cosine similarity for resume matching |
| **Plotly** | Interactive data visualizations (bar, pie, radar charts) |
| **Pandas** | Data manipulation and analysis |
| **pdfplumber** | PDF text extraction |
| **pytesseract + pdf2image** | OCR fallback for scanned PDFs |
| **SQLite** | Local database for candidate storage |
| **NumPy** | Numerical operations |

---

##  Project Structure

```
AI Resume Screening/
├── app.py                  # Main Streamlit application
├── resume_utils.py         # Resume parsing, scoring, and analysis utilities
├── database.py             # SQLite database operations
├── skills.json             # Comprehensive skills dictionary (250+ skills)
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme & server configuration
├── .gitignore              # Git ignore rules
├── TODO.md                 # Implementation progress tracker
└── README.md               # Project documentation
```



##  Usage

1. **Upload a Resume** — Click "Browse files" in the sidebar to upload a PDF resume
2. **Enter Job Description** — Paste the full job description in the text area
3. **Analyze** — Click the "🚀 Analyze Resume" button
4. **View Results** — The analysis tab shows:
   - ATS Score gauge
   - Candidate details (name, email, phone)
   - Skills found with match/missing badges
   - Score breakdown with radar chart
   - Skill match percentage against job description
   - Recruiter recommendation with detailed reasons
   - Resume improvement suggestions
5. **Dashboard** — Switch to the Recruiter Dashboard tab to view all analyzed candidates with filtering, sorting, and CSV export

---

##  Scoring Methodology

| Component | Max Score | Description |
|-----------|-----------|-------------|
| Skill Score | 40 | Matched skills × 4 (capped at 40) |
| Resume Match | 30 | TF-IDF cosine similarity × 0.30 |
| Projects | 10 | 2 points per project mention (capped at 10) |
| Certifications | 5 | 1 point per certification mention (capped at 5) |
| Experience | 5 | Years of experience (capped at 5) |
| **Total ATS** | **100** | Sum of all components |

### Shortlisting Threshold
- **≥ 80**: SHORTLISTED
- **< 80**: NOT SHORTLISTED

---

##  Skills Dictionary

The application uses a comprehensive `skills.json` file with **250+ skills** across **12 categories**:

- Programming Languages
- AI & Machine Learning
- ML/DL Frameworks
- Data Manipulation & Visualization
- Databases
- Web & Mobile Development
- Cloud & DevOps
- Version Control & Tools
- Computer Science Fundamentals
- Testing Frameworks
- UI/UX & Design
- Other (Authentication, Web3, Cybersecurity, etc.)

---

## 👩‍💻 Developed By

**Rajeshwari Kanthali**

---
.

