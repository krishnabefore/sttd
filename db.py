"""Database layer: one connection config + one helper every route uses."""
import os
import mysql.connector

DB = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'cognipath'),
    'password': os.getenv('DB_PASSWORD', 'cognipath'),
    'database': 'studypath',
}


def query(sql, params=(), one=False, commit=False):
    """Run one SQL statement.
    SELECT -> list of dict rows (or a single dict if one=True)
    INSERT/UPDATE (commit=True) -> the new row's id."""
    conn = mysql.connector.connect(**DB)
    try:
        cur = conn.cursor(dictionary=True, buffered=True)
        cur.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        return cur.fetchone() if one else cur.fetchall()
    finally:
        conn.close()
