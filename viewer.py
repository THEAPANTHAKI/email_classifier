from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def fetch_logs():
    with sqlite3.connect('email_classification.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT email, subject, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag
            FROM emails ORDER BY timestamp DESC
        ''')
        return cur.fetchall()

@app.route('/')
def index():
    logs = fetch_logs()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
