import os
import psycopg


DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def save_job_if_new(job):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO jobs (job_id, company, title)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_id) DO NOTHING
                RETURNING job_id
                """,
                (
                    job["id"],
                    job["company"],
                    job["title"],
                )
            )

            result = cur.fetchone()

            if result:
                return True

            return False
