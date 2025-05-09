from flask import Flask, request, render_template
import sqlite3
from langdetect import detect
from openai import AzureOpenAI

#Hardcoded Azure OpenAI credentials
client = AzureOpenAI(
    api_key="5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd",  
    azure_endpoint="https://theap-madml99h-eastus2.cognitiveservices.azure.com/", 
    api_version="2024-12-01-preview"
)
deployment = "gpt-4.1" 

app = Flask(__name__)

# the SQLite DB and table exist
def ensure_table():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            subject TEXT,
            content TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

# classify the intent of the email using Azure OpenAI
# classify the intent of the email using Azure OpenAI
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
            {
                "role": "user",
                "content": content[:300]
            }
        ],
        temperature=0.0,
        max_tokens=50,
        top_p=1.0
    )
    return response.choices[0].message.content.strip()

# Home page with form
@app.route("/", methods=["GET", "POST"])
def home():
    ensure_table()
    if request.method == "POST":
        email = request.form["email"]
        subject = request.form["subject"]
        content = request.form["content"]

        try:
            category = classify_intent(content)
        except Exception as e:
            return f"<h2>Classification Failed</h2><p>{str(e)}</p>"

        conn = sqlite3.connect("email_classification.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO emails (email, subject, content, category) VALUES (?, ?, ?, ?)",
                    (email.strip(), subject.strip(), content.strip(), category))
        conn.commit()
        conn.close()

        return f"<h2>Category: {category}</h2><a href='/'>Classify Another</a>"

    return render_template("form.html")

# View past logs
@app.route("/logs")
def logs():
    conn = sqlite3.connect("email_classification.db")
    cur = conn.cursor()
    cur.execute("SELECT email, subject, content, category FROM emails")
    rows = cur.fetchall()
    conn.close()
    return render_template("logs.html", rows=rows)

# Only used locally (ignored by gunicorn on Render)
if __name__ == "__main__":
    app.run(debug=True)
