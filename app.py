from flask import Flask, request, render_template
import sqlite3
from datetime import datetime
from openai import AzureOpenAI

# Azure OpenAI credentials
client = AzureOpenAI(
    api_key="5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd",
    azure_endpoint="https://theap-madml99h-eastus2.cognitiveservices.azure.com/",
    api_version="2024-12-01-preview"
)
deployment = "gpt-4.1"

app = Flask(__name__)

# Ensure database table exists
def ensure_table():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            intent TEXT NOT NULL,
            loan_type TEXT NOT NULL,
            sub_process TEXT NOT NULL,
            message_type TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Classifier Prompts
intent_prompt = (
    "You are a loan support AI assistant. Your job is to classify customer emails "
    "into one of the following categories:\n\n"
    "- New Loan Inquiry\n"
    "- Loan Closure\n"
    "- Repayment Issue\n"
    "- Interest Rate Query\n"
    "- Document Submission\n"
    "- Loan Status Update\n"
    "- Prepayment Request\n"
    "- Part-Payment Request\n"
    "- Balance Transfer Request\n"
    "- Top-Up Loan Request\n"
    "- Loan Statement Request\n"
    "- Loan Eligibility Check\n"
    "- Co-Applicant or Guarantor Issue\n"
    "- Loan Rejection Appeal\n"
    "- General Query\n\n"
    "Return ONLY the exact category name from the list above. If unsure, return 'General Query'."
)

loan_type_prompt = (
    "Based on the email content, classify the loan type. Choose ONLY one:\n"
    "- Home Loan\n"
    "- Vehicle Loan / Auto Loan\n"
    "- Loan Against Property\n"
    "- Gold Loan\n"
    "- Loan Against Securities\n"
    "- Loan Against Fixed Deposit\n"
    "- Commercial Property Loan\n"
    "- Construction Loan\n"
    "- Personal Loan\n"
    "- Education Loan\n"
    "- Travel Loan\n"
    "- Medical Loan\n"
    "- Wedding Loan\n"
    "- Consumer Durable Loan\n"
    "- Credit Card Loan\n"
    "- Business Loan\n"
    "- Working Capital Loan\n"
    "- Machinery Loan\n"
    "- Invoice Financing\n"
    "- MSME Loan\n"
    "- SME Loan\n"
    "- Startup Loan\n"
    "- Commercial Vehicle Loan\n"
    "- Agriculture Loan\n"
    "- Student Loan\n"
    "- NRI Loan\n"
    "- Debt Consolidation Loan\n"
    "- Overdraft Facility\n"
    "- Bridge Loan\n"
    "- Top-Up Loan\n"
    "- Emergency Loan\n\n"
    "If unclear, return 'General Loan'."
)

sub_process_prompt = (
    "Classify the customer's email into one sub-process:\n"
    "- Account Opening\n"
    "- Account Closure\n"
    "- Disbursement\n"
    "- Foreclosure\n"
    "- Collection Process\n"
    "- Payment Handling\n"
    "- Refund Request\n"
    "- Charges & Fees\n"
    "- Loan Restructuring\n"
    "- Feedback or Complaint\n"
    "- Legal Related\n"
    "- Settlement\n"
    "- Document Submission\n"
    "- Recovery\n"
    "- Loan Status Check\n"
    "- Co-applicant or Guarantor Issues\n"
    "- Eligibility Check\n"
    "- Statement Request\n"
    "- General Sub-process"
)

message_type_prompt = (
    "Classify the type of message based on tone and content:\n"
    "- Query\n"
    "- Request\n"
    "- Complaint\n"
    "- Feedback\n"
    "- Technical Issue\n"
    "- General Communication"
)

# Classifier Function
def classify(content, system_prompt):
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        temperature=0.0,
        max_tokens=50,
        top_p=1.0
    )
    return response.choices[0].message.content.strip()

# Homepage route
@app.route("/", methods=["GET", "POST"])
def home():
    ensure_table()
    results = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        content = request.form.get("content", "").strip()

        if not email or not subject or not content:
            return "<h3 style='color:red;'>All fields are required.</h3>"

        try:
            intent = classify(content, intent_prompt)
            loan_type = classify(content, loan_type_prompt)

            sub_process_raw = classify(content, sub_process_prompt)
            sub_process = (
                sub_process_raw
                .replace("Sub-process:", "")
                .replace("**", "")
                .strip()
            )

            message_type_raw = classify(content, message_type_prompt)
            message_type = (
                message_type_raw
                .split("Reason")[0]
                .replace("Type of message:", "")
                .replace("**", "")
                .strip()
            )
        except Exception as e:
            return f"<h2>Classification Failed</h2><p>{str(e)}</p>"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("email_classification.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO emails (email, subject, content, intent, loan_type, sub_process, message_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, subject, content, intent, loan_type, sub_process, message_type, timestamp))
        conn.commit()
        conn.close()

        results = {
            "intent": intent,
            "loan_type": loan_type,
            "sub_process": sub_process,
            "message_type": message_type
        }

    return render_template("index.html", results=results)

# Logs route
@app.route("/logs")
def logs():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT email, subject, content, intent, loan_type, sub_process, message_type, timestamp
        FROM emails
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template("logs.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
