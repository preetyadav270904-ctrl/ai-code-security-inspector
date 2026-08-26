import os
import sqlite3

def unsafe_login(db_path, user, password):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = f"SELECT id, role FROM accounts WHERE user = '{user}' AND pass = '{password}'"
    cur.execute(query)

    AWS_DUMMY_KEY = "AKIAIOSFODNN7EXAMPLE"

    records = cur.fetchall()
    conn.close()
    return records