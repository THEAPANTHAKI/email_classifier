import sqlite3

def fetch_logs():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute('SELECT email, subject, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag FROM emails ORDER BY timestamp DESC')
    rows = cur.fetchall()
    conn.close()
    return rows
