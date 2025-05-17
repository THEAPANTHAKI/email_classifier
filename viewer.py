from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

def fetch_logs():
    conn = sqlite3.connect('email_classification.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT email, subject, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag
        FROM emails ORDER BY timestamp DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    return render_template('logs.html')
@app.route('/logs')
def logs():
    data = fetch_logs()
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)

