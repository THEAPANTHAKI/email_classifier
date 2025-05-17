import sqlite3
from datetime import datetime

conn = sqlite3.connect("email_classification.db")
cur = conn.cursor()

cur.execute('''
    INSERT INTO emails (email, subject, content, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    "test@example.com",
    "Test Subject",
    "This is a test email content",
    "New Loan Inquiry",
    "Query",
    "Personal Loan",
    "Account Opening",
    datetime.now(),
    "No"
))

conn.commit()
conn.close()

print("✅ Test email inserted.")
