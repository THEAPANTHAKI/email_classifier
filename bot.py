import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env or Azure settings
load_dotenv()

app = Flask(__name__)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# === Database Query Logic ===
def query_database(user_message):
    conn = sqlite3.connect("email_classification.db")
    cursor = conn.cursor()
    msg = user_message.lower()

    try:
        if "latest repayment" in msg:
            cursor.execute("""
                SELECT subject FROM emails 
                WHERE intent = 'Repayment Issue'
                ORDER BY timestamp DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return row[0] if row else "No repayment issues found."

        elif "loan type stats" in msg:
            cursor.execute("""
                SELECT loan_type, COUNT(*) 
                FROM emails GROUP BY loan_type
            """)
            rows = cursor.fetchall()
            return "\n".join([f"{lt}: {count}" for lt, count in rows]) or "No data found."

        elif "list all complaints" in msg:
            cursor.execute("""
                SELECT subject FROM emails 
                WHERE message_type = 'Complaint' 
                ORDER BY timestamp DESC LIMIT 5
            """)
            rows = cursor.fetchall()
            return "\n".join([row[0] for row in rows]) or "No complaints found."

        return None

    except Exception as e:
        return f"Error accessing database: {str(e)}"
    finally:
        conn.close()

# === Routes ===
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/api/messages", methods=["POST"])
def messages():
    data = request.get_json()
    user_message = data.get("text", "")

    # Try database first
    db_response = query_database(user_message)
    if db_response:
        return jsonify({"text": db_response})

    # Fallback to GPT
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        return jsonify({"text": reply})
    except Exception as e:
        return jsonify({"text": f"Error from OpenAI: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
