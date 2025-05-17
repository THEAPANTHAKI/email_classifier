from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def fetch_logs():
    conn = sqlite3.connect('email_classification.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT email, subject, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag
        FROM emails ORDER BY timestamp DESC
    ''')
    logs = cur.fetchall()
    conn.close()
    return logs

@app.route('/')
def index():
    logs = fetch_logs()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
