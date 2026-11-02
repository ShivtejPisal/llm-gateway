import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

# .env lives at the repo root, one level above this folder.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://gateway:gateway@localhost:5433/semantic_cache",
)


def connect():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def insert_entry(conn, prompt, response, model, embedding):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cache_entries (prompt, response, model, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            (prompt, response, model, embedding),
        )
    conn.commit()


def find_nearest(conn, embedding, limit=1):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT prompt, response, model,
                   1 - (embedding <=> %s) AS similarity
            FROM cache_entries
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (embedding, embedding, limit),
        )
        return cur.fetchall()
