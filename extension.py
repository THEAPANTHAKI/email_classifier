import os
import base64
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# api scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# loading prompt
def load_sql_if_empty():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()

    # Check if table exists and has data
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='keyword_mapping';")
    if cur.fetchone()[0] == 0:
        print("'keyword_mapping' table does not exist. Creating from prompt.sql...")
        with open("prompt.sql", "r") as f:
            cur.executescript(f.read())
            conn.commit()
            print("Table created and populated.")
    else:
        cur.execute("SELECT count(*) FROM keyword_mapping;")
        if cur.fetchone()[0] == 0:
            print("Table exists but is empty. Populating from prompt.sql...")
            with open("prompt.sql", "r") as f:
                cur.executescript(f.read())
                conn.commit()
                print("Table populated.")
        else:
            print(" 'keyword_mapping' table already populated.")
    conn.close()

# classifying
def classify_email_from_db(content):
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()

    words = content.lower().split()

    #defaults
    intent = "General Query"
    loan_type = "General Loan"
    message_type = "General Communication"
    subprocess = "General Sub-process"

    for word in words:
        cur.execute("SELECT intent, loan_type, message_type, subprocess FROM keyword_mapping WHERE keyword = ?", (word,))
        result = cur.fetchone()
        if result:
            if result[0]: intent = result[0]
            if result[1]: loan_type = result[1]
            if result[2]: message_type = result[2]
            if result[3]: subprocess = result[3]

    conn.close()
    return intent, loan_type, message_type, subprocess

# init db
def init_db():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            subject TEXT,
            content TEXT,
            intent TEXT,
            message_type TEXT,
            loan_type TEXT,
            subprocess TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS keyword_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            intent TEXT,
            loan_type TEXT,
            message_type TEXT,
            subprocess TEXT
        )
    ''')

    conn.commit()
    conn.close()

#save
def save_to_db(sender, subject, content, intent, message_type, loan_type, subprocess):
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO emails (email, subject, content, intent, message_type, loan_type, subprocess)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (sender, subject, content, intent, message_type, loan_type, subprocess))
    conn.commit()
    conn.close()

# auto reply
def send_reply(service, to):
    message = MIMEText("Thank you for contacting us. We've received your email and will get back to you shortly.")
    message['to'] = to
    message['subject'] = "Auto-response from Loan Support"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

# main
def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')

        payload = msg_data['payload']
        parts = payload.get('parts')
        if parts and parts[0]['body'].get('data'):
            data = parts[0]['body']['data']
        else:
            data = payload['body'].get('data', '')
        content = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8', errors='ignore')

        intent, loan_type, message_type, subprocess = classify_email_from_db(content)

        save_to_db(sender, subject, content, intent, message_type, loan_type, subprocess)
        send_reply(service, sender)
        service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()

# entry point
if __name__ == '__main__':
    init_db()
    load_sql_if_empty()
    main()
