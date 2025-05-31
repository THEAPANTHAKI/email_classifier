import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Azure GPT client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# === HTML route ===
@app.route("/")
def home():
    return render_template("chat.html")

# === Chatbot logic ===
@app.route("/api/messages", methods=["POST"])
def messages():
    data = request.get_json()
    user_message = data.get("text", "")

    # Step 1: Ask GPT to generate an SQL query for the request
    try:
        prompt = [
            {"role": "system", "content": (
                "You are an AI assistant for a chatbot that queries an SQLite database named 'email_classification.db'. "
                "The table is called 'emails' and has the columns: id, email, subject, message_type, loan_type, intent, subprocess, timestamp. "
                "Given a user query, respond with ONLY a valid SQL SELECT statement (without explanations). Limit results to 5 rows."
            )},
            {"role": "user", "content": f"Generate an SQL query for this request: {user_message}"}
        ]

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=prompt
        )

        generated_sql = response.choices[0].message.content.strip()

        # Step 2: Run the SQL query on your SQLite database
        conn = sqlite3.connect("email_classification.db")
        cursor = conn.cursor()
        cursor.execute(generated_sql)
        rows = cursor.fetchall()
        conn.close()

        # Format the results
        if not rows:
            reply = "No results found for that query."
        else:
            reply = "\n".join([str(row) for row in rows])

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"text": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
