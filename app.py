import streamlit as st
import logging
import time
from resume_utils import *
from database import create_database, fetch_candidate, save_canditate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_database()


st.markdown("""
<style>
    /* ── Global ── */
    .stApp {
        background: linear-gradient(135deg, #0A0E1A 0%, #111827 100%);
    }

    /* ── Hide default Streamlit footer / hamburger ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Main container ── */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ── Cards ── */
    .card {
        background: linear-gradient(145deg, #1a1f2e, #111827);
        border: 1px solid #2d3548;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.25s ease;
    }
    .card:hover {
        border-color: #6C5CE7;
        box-shadow: 0 6px 30px rgba(108,92,231,0.15);
        transform: translateY(-2px);
    }
    .card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8892b0;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: #E2E8F0;
        line-height: 1.2;
    }
    .card-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* ── Status Badges ── */
    .badge-shortlisted {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34,197,94,0.15);
        border: 1px solid #22C55E;
        color: #22C55E;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-not-shortlisted {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(239,68,68,0.15);
        border: 1px solid #EF4444;
        color: #EF4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ── Skill Badges ── */
    .skill-badge {
        display: inline-block;
        background: rgba(108,92,231,0.12);
        border: 1px solid rgba(108,92,231,0.3);
        color: #b8b5ff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px 4px;
        transition: all 0.2s;
    }
    .skill-badge:hover {
        background: rgba(108,92,231,0.25);
        border-color: #6C5CE7;
    }
    .skill-badge-missing {
        display: inline-block;
        background: rgba(239,68,68,0.1);
        border: 1px dashed rgba(239,68,68,0.4);
        color: #f87171;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px 4px;
    }

    /* ── ATS Score Gauge Container ── */
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    .gauge-svg {
        width: 180px;
        height: 100px;
    }
    .gauge-label {
        font-size: 0.85rem;
        color: #8892b0;
        margin-top: 0.25rem;
        letter-spacing: 1px;
    }

    /* ── Progress Bar inside cards ── */
    .progress-track {
        width: 100%;
        height: 6px;
        background: #1e293b;
        border-radius: 10px;
        margin-top: 8px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.8s ease;
    }

    /* ── Score bar mini ── */
    .score-bar-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 4px 0;
    }
    .score-bar-track {
        flex: 1;
        height: 8px;
        background: #1e293b;
        border-radius: 10px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.6s ease;
    }
    .score-bar-label {
        min-width: 60px;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .score-bar-value {
        min-width: 40px;
        text-align: right;
        font-size: 0.8rem;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* ── Section dividers ── */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2d3548, transparent);
        margin: 1.5rem 0;
    }

    /* ── Sidebar branding ── */
    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sidebar-brand h2 {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C5CE7, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }
    .sidebar-brand p {
        font-size: 0.75rem;
        color: #64748b;
        margin: 0;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #111827;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #2d3548;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.85rem;
        color: #64748b;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6C5CE7, #8b5cf6) !important;
        color: white !important;
    }

    /* ── Custom scrollbar ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0E1A;
    }
    ::-webkit-scrollbar-thumb {
        background: #2d3548;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6C5CE7;
    }

    /* ── Expander styling ── */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #E2E8F0;
        background: #1a1f2e;
        border-radius: 8px;
        border: 1px solid #2d3548;
    }
    .streamlit-expanderContent {
        border: 1px solid #2d3548;
        border-top: none;
        border-radius: 0 0 8px 8px;
        background: #111827;
        padding: 0.5rem;
    }

    /* ── Footer ── */
    .app-footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid #2d3548;
        margin-top: 2rem;
    }
    .app-footer p {
        font-size: 0.75rem;
        color: #475569;
        margin: 0;
    }
    .app-footer .version {
        color: #6C5CE7;
        font-weight: 600;
    }

    /* ── Animated loading dots ── */
    @keyframes blink {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    .loading-dots span {
        animation: blink 1.4s infinite both;
        font-size: 1.5rem;
        color: #6C5CE7;
    }
    .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
    .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)




def render_ats_gauge(score: float):
    """Render a circular gauge as inline SVG for ATS score."""
    normalized = min(score / 100, 1.0)
    dash_array = 251.2  # circumference for r=40
    dash_offset = dash_array * (1 - normalized)

    # Color based on score
    if score >= 80:
        color = "#22C55E"
        label = "Excellent"
    elif score >= 70:
        color = "#EAB308"
        label = "Good"
    elif score >= 50:
        color = "#F97316"
        label = "Average"
    else:
        color = "#EF4444"
        label = "Poor"

    svg = f"""
    <div class="gauge-container">
        <svg class="gauge-svg" viewBox="0 0 100 55">
            <path d="M 10 45 A 40 40 0 1 1 90 45"
                  fill="none" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>
            <path d="M 10 45 A 40 40 0 1 1 90 45"
                  fill="none" stroke="{color}" stroke-width="8" stroke-linecap="round"
                  stroke-dasharray="{dash_array}"
                  stroke-dashoffset="{dash_offset}"
                  style="transition: stroke-dashoffset 1s ease;"/>
            <text x="50" y="30" text-anchor="middle"
                  fill="#E2E8F0" font-size="22" font-weight="700">{int(score)}</text>
            <text x="50" y="42" text-anchor="middle"
                  fill="#64748b" font-size="9">/ 100</text>
        </svg>
        <div class="gauge-label">{label}</div>
    </div>
    """
    return svg



def status_badge_html(status: str) -> str:
    if status == "SHORTLISTED":
        return '<span class="badge-shortlisted">✅ SHORTLISTED</span>'
    return '<span class="badge-not-shortlisted">❌ NOT SHORTLISTED</span>'



def score_bar_html(label: str, value: float, max_val: float, color: str = "#6C5CE7"):
    pct = min((value / max_val) * 100, 100)
    return f"""
    <div class="score-bar-container">
        <span class="score-bar-label">{label}</span>
        <div class="score-bar-track">
            <div class="score-bar-fill" style="width: {pct}%; background: {color};"></div>
        </div>
        <span class="score-bar-value">{value}/{max_val}</span>
    </div>
    """



def skill_badges_html(skills: list, missing: list = None):
    html = '<div style="display: flex; flex-wrap: wrap; gap: 4px;">'
    if missing is None:
        missing = []
    missing_set = set(s.lower() for s in missing)
    for s in skills:
        if s.lower() in missing_set:
            html += f'<span class="skill-badge-missing">{s} ✗</span>'
        else:
            html += f'<span class="skill-badge">{s}</span>'
    html += '</div>'
    return html



def analysis_progress(step: int, total: int = 6):
    messages = [
        " Extracting text from PDF...",
        " Parsing candidate information...",
        " Analyzing skills & experience...",
        " Calculating scores & match...",
        " Evaluating against job description...",
        " Generating recommendations..."
    ]
    progress_val = step / total
    bar = st.progress(0.0)
    msg = st.empty()
    for i in range(step):
        bar.progress((i + 1) / total)
        msg.info(messages[i])
        time.sleep(0.25)
    bar.progress(1.0)
    msg.empty()



with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>📄 AI Resume Screener</h2>
        <p>Intelligent Candidate Evaluation</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    st.markdown("##### 🔎 Analyze a Candidate")
    st.caption("Upload a resume and paste a job description to get an instant AI-powered evaluation.")

    st.markdown("##### 📤 Upload Resume")
    uploaded_resume = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        label_visibility="collapsed"
    )

    st.markdown("##### 📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here...",
        height=200,
        label_visibility="collapsed",
        placeholder="Paste the full job description here..."
    )

    analyze_clicked = st.button(
        "🚀 Analyze Resume",
        type="primary",
        use_container_width=True
    )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.caption("Supports PDF resumes with text & scanned (OCR) content.")



tab1, tab2 = st.tabs(["📋 Candidate Analysis", "📊 Recruiter Dashboard"])


with tab1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h1 style="margin:0; font-size: 1.8rem;">Candidate Analysis</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top: -0.5rem;'>Comprehensive resume evaluation against job requirements.</p>", unsafe_allow_html=True)

    if analyze_clicked:
        if uploaded_resume is None:
            st.warning("⚠️ Please upload a Resume PDF.")
            st.stop()
        elif job_description == "" or job_description.strip() == "":
            st.warning("⚠️ Please enter a Job Description.")
            st.stop()
        else:
            # ---- Analysis with progress ----
            results_placeholder = st.container()

            with st.status("🔄 **Analyzing candidate...**", expanded=True) as status:
                st.write("📄 Extracting text from PDF...")
                resume_text = extract_text_from_pdf(uploaded_resume)

                if not resume_text:
                    st.error("❌ Could not extract text from the PDF. The file may be empty, corrupted, or a scanned image without OCR support.")
                    st.stop()

                st.write("🔍 Parsing candidate information...")
                candidate_info = extract_candidate_info(resume_text)
                name = candidate_info["name"]
                email = candidate_info["email"]
                phone = candidate_info["phone"]
                skills = candidate_info["skills"]
                ai_summary = candidate_info.get("summary", "")
                logger.info("Analyzing candidate: %s (%s) - %d skills found", name, email, len(skills))

                st.write("📊 Calculating scores & match...")
                resume_match = calculate_resume_match(resume_text, job_description)
                skill_score = calculate_skill_score(skills, job_description)
                resume_score = calculate_resume_score(resume_match)
                project_score = calculate_project_score(resume_text)
                certification_score = calculate_certification_score(resume_text)
                experience_score = calculate_experience_score(resume_text)
                ats_score = calculate_ats_score(
                    skill_score, resume_score, project_score,
                    certification_score, experience_score
                )

                st.write("⚖️ Evaluating against job description...")
                jd_skills = extract_skills(job_description)
                skill_match_percentage = calculate_skill_match_percentage(skills, jd_skills)
                missing_skills = detect_missing_skills(skills, jd_skills)

                st.write("📋 Generating recommendations...")
                recommendation_type, recommendation_text = get_recruiter_recommendation(ats_score)
                recommendation_reasons = get_recommendation_reasons(
                    skill_match_percentage, resume_match, project_score,
                    certification_score, experience_score, missing_skills
                )
                resume_suggestions = generate_resume_suggestions(
                    project_score, certification_score, experience_score, missing_skills
                )

                status.update(label="✅ **Analysis complete!**", state="complete", expanded=False)

            # ---- Save to DB ----
            status_val = get_candidate_status(ats_score)
            rank = get_candidate_rank(ats_score)
            save_canditate(
                name, email, phone, ", ".join(skills),
                ats_score, resume_match, rank, status_val
            )
            logger.info("ATS Score: %s, Status: %s, Rank: %s", ats_score, status_val, rank)

            # ---- Status Banner ----
            if status_val == "SHORTLISTED":
                #st.balloons()
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.05));
                            border: 1px solid #22C55E; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 1.2rem; font-weight: 700; color: #22C55E;">
                    ✅ SHORTLISTED — This candidate meets the threshold requirements.
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05));
                            border: 1px solid #EF4444; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 1.2rem; font-weight: 700; color: #EF4444;">
                    ❌ NOT SHORTLISTED — Score is below the shortlisting threshold (80).
                    </span>
                </div>
                """, unsafe_allow_html=True)


            
            col_gauge, col_info = st.columns([1, 2])
            with col_gauge:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(render_ats_gauge(ats_score), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_info:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Candidate Details</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="color: #8892b0; padding: 4px 8px 4px 0; font-size: 0.85rem; width: 120px;">👤 Name</td>
                        <td style="color: #E2E8F0; font-weight: 600;">{name}</td></tr>
                    <tr><td style="color: #8892b0; padding: 4px 8px 4px 0; font-size: 0.85rem;">📧 Email</td>
                        <td style="color: #E2E8F0;">{email}</td></tr>
                    <tr><td style="color: #8892b0; padding: 4px 8px 4px 0; font-size: 0.85rem;">📞 Phone</td>
                        <td style="color: #E2E8F0;">{phone}</td></tr>
                    <tr><td style="color: #8892b0; padding: 4px 8px 4px 0; font-size: 0.85rem;">🏆 Status</td>
                        <td>{status_badge_html(status_val)}</td></tr>
                    <tr><td style="color: #8892b0; padding: 4px 8px 4px 0; font-size: 0.85rem;">🎯 Rank</td>
                        <td style="color: #E2E8F0; font-weight: 600;">{rank}</td></tr>
                </table>
                """, unsafe_allow_html=True)
                if ai_summary:
                    st.markdown(f"<p style='color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;'><strong>💡 AI Summary:</strong> {ai_summary}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🧠 Skills Found</div>', unsafe_allow_html=True)
            if skills:
                st.markdown(skill_badges_html(skills, missing_skills), unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #64748b;'>No skills detected on the resume.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📈 Score Breakdown</div>', unsafe_allow_html=True)

            col_scores, col_radar = st.columns([1, 1])

            with col_scores:
                st.markdown(score_bar_html("Resume Match", round(resume_match, 1), 100, "#6C5CE7"), unsafe_allow_html=True)
                st.markdown(score_bar_html("Skill Score", skill_score, 40, "#8b5cf6"), unsafe_allow_html=True)
                st.markdown(score_bar_html("Projects", project_score, 10, "#22C55E"), unsafe_allow_html=True)
                st.markdown(score_bar_html("Certifications", certification_score, 5, "#EAB308"), unsafe_allow_html=True)
                st.markdown(score_bar_html("Experience", experience_score, 5, "#F97316"), unsafe_allow_html=True)

            with col_radar:
                radar_categories = ["Resume Match", "Skill Score", "Projects", "Certifications", "Experience"]
                radar_values = [
                    round(resume_match, 1),
                    round((skill_score / 40) * 100, 1),
                    round((project_score / 10) * 100, 1),
                    round((certification_score / 5) * 100, 1),
                    round((experience_score / 5) * 100, 1),
                ]
                radar_fig = go.Figure()
                radar_fig.add_trace(go.Scatterpolar(
                    r=radar_values + [radar_values[0]],
                    theta=radar_categories + [radar_categories[0]],
                    fill="toself",
                    name="Candidate",
                    line_color="#6C5CE7",
                    fillcolor="rgba(108,92,231,0.15)",
                ))
                radar_fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color="#64748b"),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                    showlegend=False,
                    margin=dict(l=30, r=30, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#E2E8F0",
                    height=280,
                )
                st.plotly_chart(radar_fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)


            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🎯 Skill Match Against Job Description</div>', unsafe_allow_html=True)
            col_sm1, col_sm2 = st.columns([1, 1])
            with col_sm1:
                st.metric("Skill Match", f"{skill_match_percentage}%",
                          delta=f"{skill_match_percentage - 50:+.1f}% vs baseline",
                          delta_color="normal")
            with col_sm2:
                if missing_skills:
                    st.markdown(f"<p style='color: #f87171; font-size: 0.85rem;'><strong>Missing Skills ({len(missing_skills)}):</strong></p>", unsafe_allow_html=True)
                    st.markdown(skill_badges_html(missing_skills, missing_skills), unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #22C55E; font-size: 0.9rem;'>✅ Candidate covers all JD-listed skills.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---- Row 5: Recommendation & Suggestions ----
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📋 Recruiter Recommendation</div>', unsafe_allow_html=True)

            # Recommendation type mapping to emoji/color
            rec_emoji = {"success": "✅", "warning": "⚠️", "error": "❌"}
            rec_color = {"success": "#22C55E", "warning": "#EAB308", "error": "#EF4444"}
            st.markdown(
                f"<p style='color: {rec_color.get(recommendation_type, '#E2E8F0')}; "
                f"font-size: 1.05rem; font-weight: 600;'>"
                f"{rec_emoji.get(recommendation_type, '')} {recommendation_text}</p>",
                unsafe_allow_html=True
            )

            with st.expander("🔍 Why this recommendation?"):
                for reason in recommendation_reasons:
                    st.markdown(f"- {reason}")

            with st.expander("💡 Resume Improvement Suggestions"):
                for suggestion in resume_suggestions:
                    st.markdown(f"- {suggestion}")

            st.markdown('</div>', unsafe_allow_html=True)


            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">⭐ Candidate Performance</div>', unsafe_allow_html=True)
            stars = ""
            star_color = "#64748b"
            if ats_score >= 90:
                stars = "★★★★★"
                star_color = "#22C55E"
                label = "Excellent Candidate"
            elif ats_score >= 80:
                stars = "★★★★"
                star_color = "#22C55E"
                label = "Very Good Candidate"
            elif ats_score >= 70:
                stars = "★★★"
                star_color = "#EAB308"
                label = "Good Candidate"
            elif ats_score >= 50:
                stars = "★★"
                star_color = "#F97316"
                label = "Average Candidate"
            else:
                stars = "★"
                star_color = "#EF4444"
                label = "Poor Candidate"
            st.markdown(
                f"<p style='font-size: 1.8rem; color: {star_color}; letter-spacing: 4px; margin: 0;'>{stars}</p>"
                f"<p style='color: #94a3b8; font-size: 0.9rem;'>{label}</p>",
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    padding: 4rem 1rem; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📄</div>
            <h3 style="color: #E2E8F0; margin-bottom: 0.5rem;">Ready to Analyze a Candidate?</h3>
            <p style="color: #64748b; max-width: 460px;">
                Upload a PDF resume and paste a job description in the sidebar,
                then click <strong>"Analyze Resume"</strong> to get instant AI-powered results.
            </p>
        </div>
        """, unsafe_allow_html=True)


with tab2:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h1 style="margin:0; font-size: 1.8rem;">Recruiter Dashboard</h1>
        <span style="background: #22C55E; padding: 2px 12px; border-radius: 12px;
                     font-size: 0.7rem; color: white; font-weight: 600;">LIVE</span>
    </div>
    """, unsafe_allow_html=True)

    data = fetch_candidate()
    if data:
        df = pd.DataFrame(
            data,
            columns=[
                "ID", "Name", "Email", "Phone Number", "Skills",
                "ATS Score", "Resume Match", "Candidate Rank", "Status"
            ]
        )


        total_candidates = len(df)
        shortlisted_count = len(df[df["Status"] == "SHORTLISTED"])
        not_shortlisted_count = len(df[df["Status"] == "NOT SHORTLISTED"])

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <div class="card-title">Total Candidates</div>
                <div class="card-value">{total_candidates}</div>
            """, unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"""
            <div class="card" style="text-align: center; border-color: rgba(34,197,94,0.3);">
                <div class="card-title" style="color: #22C55E;">Shortlisted</div>
                <div class="card-value" style="color: #22C55E;">{shortlisted_count}</div>
                <div class="card-sub">{round(shortlisted_count/max(total_candidates,1)*100,1)}% of total</div>
            """, unsafe_allow_html=True)
        with col_s3:
            st.markdown(f"""
            <div class="card" style="text-align: center; border-color: rgba(239,68,68,0.3);">
                <div class="card-title" style="color: #EF4444;">Not Shortlisted</div>
                <div class="card-value" style="color: #EF4444;">{not_shortlisted_count}</div>
                <div class="card-sub">{round(not_shortlisted_count/max(total_candidates,1)*100,1)}% of total</div>
            """, unsafe_allow_html=True)
        with col_s4:
            avg_score = round(df["ATS Score"].mean(), 1)
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <div class="card-title">Avg. ATS Score</div>
                <div class="card-value">{avg_score}</div>
            """, unsafe_allow_html=True)

       
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">ATS Score by Candidate</div>', unsafe_allow_html=True)
            bar_fig = px.bar(
                df.sort_values("ATS Score", ascending=False),
                x="Name",
                y="ATS Score",
                color="Status",
                color_discrete_map={"SHORTLISTED": "#22C55E", "NOT SHORTLISTED": "#EF4444"},
                text_auto=".0f",
            )
            bar_fig.update_traces(textposition="outside", marker_line_width=0)
            bar_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E2E8F0",
                margin=dict(l=10, r=10, t=10, b=10),
                height=320,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e293b", range=[0, 100]),
            )
            st.plotly_chart(bar_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with chart_col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Shortlisted vs Not Shortlisted</div>', unsafe_allow_html=True)
            pie_fig = px.pie(
                names=["Shortlisted", "Not Shortlisted"],
                values=[shortlisted_count, not_shortlisted_count],
                color=["Shortlisted", "Not Shortlisted"],
                color_discrete_map={"Shortlisted": "#22C55E", "Not Shortlisted": "#EF4444"},
                hole=0.4,
            )
            pie_fig.update_traces(textposition="outside", textinfo="label+percent")
            pie_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#E2E8F0",
                margin=dict(l=10, r=10, t=10, b=10),
                height=320,
                showlegend=False,
            )
            st.plotly_chart(pie_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 All Candidates</div>', unsafe_allow_html=True)

        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "SHORTLISTED", "NOT SHORTLISTED"],
                label_visibility="collapsed"
            )
        with col_f2:
            search_query = st.text_input(
                "🔍 Search by name...",
                placeholder="Search name...",
                label_visibility="collapsed"
            )
        with col_f3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # spacer


       
        filtered_df = df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Name"].str.contains(search_query, case=False, na=False)
            ]

       
        display_df = filtered_df.copy()
        display_df["Status"] = display_df["Status"].apply(
            lambda x: "✅ SHORTLISTED" if x == "SHORTLISTED" else "❌ NOT SHORTLISTED"
        )

        st.dataframe(
            display_df.drop(columns=["ID", "Phone Number"]),
            use_container_width=True,
            column_config={
                "ATS Score": st.column_config.NumberColumn(format="%.1f"),
                "Resume Match": st.column_config.NumberColumn(format="%.1f"),
            },
            height=300,
        )

        col_dl1, col_dl2, _ = st.columns([1, 1, 2])
        with col_dl1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full Report (CSV)",
                data=csv,
                file_name="candidates_report.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_dl2:
            if total_candidates > 0:
                top_n = st.slider(
                    "Top candidates to show",
                    1,
                    min(10, total_candidates),
                    min(5, total_candidates),
                    label_visibility="collapsed",
                )
            else:
                top_n = 1

        st.markdown('</div>', unsafe_allow_html=True)

        
        if total_candidates > 0:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">🏆 Top {top_n} Candidates</div>', unsafe_allow_html=True)
            top_candidates = df.sort_values(by="ATS Score", ascending=False).head(top_n)
            top_display = top_candidates.copy()
            top_display["Rank"] = [f"#{i+1}" for i in range(len(top_candidates))]
            top_display["Status"] = top_display["Status"].apply(
                lambda x: "✅ SHORTLISTED" if x == "SHORTLISTED" else "❌ NOT SHORTLISTED"
            )
            st.dataframe(
                top_display[["Rank", "Name", "Email", "ATS Score", "Resume Match", "Status"]],
                use_container_width=True,
                column_config={
                    "ATS Score": st.column_config.NumberColumn(format="%.1f"),
                    "Resume Match": st.column_config.NumberColumn(format="%.1f"),
                },
                height=200,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    padding: 4rem 1rem; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #E2E8F0; margin-bottom: 0.5rem;">No Candidates Yet</h3>
            <p style="color: #64748b; max-width: 460px;">
                Analyze a resume in the <strong>Candidate Analysis</strong> tab to see candidates
                appear in the dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="app-footer">
    <p>Developed by <span class="version">Rajeshwari Kanthali</span></p>
</div>
""", unsafe_allow_html=True)





    