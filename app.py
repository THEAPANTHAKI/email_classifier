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

# Create DB table if it doesn't exist
def ensure_table():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call Azure OpenAI to classify the email
def classify_intent(content):
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a loan support AI assistant. Your job is to classify the customer's email into exactly one of the following predefined categories:\n\n"
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
                    "Read the email carefully and output ONLY the exact category name from the list above. "
                    "Do NOT explain your choice or add any extra text. "
                    "If the email content is unclear or doesn't match any category, return 'General Query'."
                )
            },
            {"role": "user", "content": content[:300]}
        ],
        temperature=0.0,
        max_tokens=50,
        top_p=1.0
    )
    return response.choices[0].message.content.strip()

# Home route (form + result)
@app.route("/", methods=["GET", "POST"])
def home():
    ensure_table()
    category = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        content = request.form.get("content", "").strip()

        if not email or not subject or not content:
            return "<h3 style='color:red;'>All fields are required.</h3>"

        try:
            category = classify_intent(content)
        except Exception as e:
            return f"<h2>Classification Failed</h2><p>{str(e)}</p>"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("email_classification.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO emails (email, subject, content, category, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (email, subject, content, category, timestamp))
        conn.commit()
        conn.close()

    return render_template("index.html", category=category)

# Logs page
@app.route("/logs")
def logs():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT email, subject, content, category, timestamp
        FROM emails
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template("logs.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
