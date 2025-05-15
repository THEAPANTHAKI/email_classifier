import os
import base64
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

#scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

#intent groups
INTENT_GROUPS = {
    "New Loan Inquiry": ["New Loan Inquiry", "General Query", "Document Submission"],
    "Repayment Issue": ["Repayment Issue", "Payment Handling"],
    "Loan Closure": ["Loan Closure", "Foreclosure"],
    "Interest Rate Query": ["Interest Rate Query", "General Query"],
    "Document Submission": ["Document Submission", "General Query"],
    "Loan Status Update": ["Loan Status Update", "Loan Status Check"],
    "Prepayment Request": ["Prepayment Request", "Part-Payment Request"],
    "General Query": ["General Query"],
    "Top-Up Loan Request": ["Top-Up Loan Request", "New Loan Inquiry"],
    "Balance Transfer Request": ["Balance Transfer Request"],
    "Loan Statement Request": ["Loan Statement Request", "Statement Request"],
    "Loan Eligibility Check": ["Loan Eligibility Check", "Eligibility Check"],
    "Co-Applicant or Guarantor Issue": ["Co-Applicant or Guarantor Issue"],
    "Loan Rejection Appeal": ["Loan Rejection Appeal"],
}

#db init
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duplicate_tag TEXT DEFAULT 'No'
        )
    ''')
    conn.commit()
    conn.close()

# classifier
def classify_email_from_db(content):
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()

    content = content.lower()
    words = content.split()

    intent = "General Inquiry"
    loan_type = "Other"
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

# duplicte 
def is_duplicate_email(sender, intent):
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    time_threshold = datetime.now() - timedelta(hours=24)

    similar_intents = INTENT_GROUPS.get(intent, [intent])
    placeholders = ','.join('?' for _ in similar_intents)

    query = f'''
        SELECT COUNT(*) FROM emails
        WHERE email = ? AND intent IN ({placeholders}) AND timestamp >= ?
    '''
    cur.execute(query, (sender, *similar_intents, time_threshold))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

#reply
def send_reply(service, to, reply_body):
    message = MIMEText(reply_body)
    message['to'] = to
    message['subject'] = "Auto-response from Loan Support"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

# main
def main():
    init_db()

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

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = ""
        sender = ""

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']

        # normalize 
        if '<' in sender:
            sender = sender.split('<')[-1].replace('>', '').strip()

        #get email
        if 'data' in msg_data['payload']['body']:
            body_data = msg_data['payload']['body']['data']
        else:
            body_data = msg_data['payload']['parts'][0]['body']['data']

        decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")

        # clasiisfy
        intent, loan_type, message_type, subprocess = classify_email_from_db(decoded_body)

        # check 
        duplicate = is_duplicate_email(sender, intent)
        duplicate_tag = "Yes" if duplicate else "No"

        # auto reply
        if duplicate:
            reply_text = "We’ve already received your request and are working on it. Thank you for your patience."
        else:
            reply_text = "Thank you for contacting us. We will get back to you shortly."

        # save to DB
        conn = sqlite3.connect("email_classification.db")
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO emails (email, subject, content, intent, message_type, loan_type, subprocess, timestamp, duplicate_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sender, subject, decoded_body, intent, message_type, loan_type, subprocess, datetime.now(), duplicate_tag))
        conn.commit()
        conn.close()

        #send reply
        send_reply(service, sender, reply_text)

        # read 
        service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == '__main__':
    main()
