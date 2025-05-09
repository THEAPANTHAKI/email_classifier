from flask import Flask, request, render_template
import sqlite3
from langdetect import detect
from openai import AzureOpenAI

# Azure OpenAI Setup
client = AzureOpenAI(
    api_key="YOUR_API_KEY",  # or use env vars
    azure_endpoint="YOUR_AZURE_ENDPOINT",
    api_version="2024-12-01-preview"
)
deployment = "YOUR_DEPLOYMENT_NAME"

app = Flask(__name__)

# Classifier function
def classify_intent(content):
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": (
                "You are an AI assistant that reads customer emails and classifies them into:\n"
                "- New Loan Inquiry\n- Loan Closure\n- General Query\n- Repayment Issue\n"
                "- Document Submission\n- Interest Rate Query\nOutput ONLY the category name."
            )},
            {"role": "user", "content": content[:300]}
        ],
        temperature=0.0,
        max_tokens=50,
        top_p=1.0,
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form["email"]
        subject = request.form["subject"]
        content = request.form["content"]

        category = classify_intent(content)

        conn = sqlite3.connect("emails.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO emails (email, subject, content, category) VALUES (?, ?, ?, ?)",
                    (email.strip(), subject.strip(), content.strip(), category))
        conn.commit()
        conn.close()

        return f"<h2>Category: {category}</h2><a href='/'>Classify Another</a>"

    return render_template("form.html")

@app.route("/logs")
def logs():
    conn = sqlite3.connect("emails.db")
    cur = conn.cursor()
    cur.execute("SELECT email, subject, content, category FROM emails")
    rows = cur.fetchall()
    conn.close()
    return render_template("logs.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
