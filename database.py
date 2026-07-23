import sqlite3
import logging

logger = logging.getLogger(__name__)


def create_database():
    connection = sqlite3.connect("resume.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            ats_score REAL,
            resume_match REAL,
            candidate_rank TEXT,
            status TEXT
        )
        """
    )
    connection.commit()
    connection.close()


def save_candidate(
    name,
    email,
    phone,
    skills,
    ats_score,
    resume_match,
    candidate_rank,
    status,
):
    """
    Upserts a candidate record. If a candidate with the same email
    already exists (and the email was actually detected), their row
    is updated with the latest analysis instead of creating a
    duplicate entry. If the email couldn't be detected ("Not Found"),
    a new row is inserted since there's no reliable way to match it
    to an existing candidate.
    """
    connection = sqlite3.connect("resume.db")
    cursor = connection.cursor()

    existing_id = None
    if email and email != "Not Found":
        cursor.execute(
            "SELECT id FROM candidates WHERE LOWER(email) = LOWER(?)",
            (email,),
        )
        row = cursor.fetchone()
        if row:
            existing_id = row[0]
            logger.debug("Found existing candidate id=%s for email=%s", existing_id, email)

    if existing_id is not None:
        logger.info("Updating candidate %s (%s)", name, email)
        cursor.execute(
            """
            UPDATE candidates
            SET name = ?,
                phone = ?,
                skills = ?,
                ats_score = ?,
                resume_match = ?,
                candidate_rank = ?,
                status = ?
            WHERE id = ?
            """,
            (
                name,
                phone,
                skills,
                ats_score,
                resume_match,
                candidate_rank,
                status,
                existing_id,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO candidates (
                name,
                email,
                phone,
                skills,
                ats_score,
                resume_match,
                candidate_rank,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                phone,
                skills,
                ats_score,
                resume_match,
                candidate_rank,
                status,
            ),
        )

    connection.commit()
    connection.close()


def save_canditate(*args, **kwargs):
    return save_candidate(*args, **kwargs)


def fetch_candidate():
    connection = sqlite3.connect("resume.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM candidates")

    data = cursor.fetchall()
    connection.close()
    return data


def fetch_candidates():
    return fetch_candidate()