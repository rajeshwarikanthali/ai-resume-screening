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




