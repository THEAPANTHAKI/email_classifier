import tkinter as tk
from tkinter import scrolledtext
import sqlite3
import importlib.util

# Load classification module dynamically
spec = importlib.util.spec_from_file_location("email_classifier", "email_classifier.py")
email_classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(email_classifier)

# Updated classifier
def classify_all(subject, content):
    try:
        full_input = f"{subject.strip()} {content.strip()}"
        intent = email_classifier.classify_intent(full_input)
        loan_type = email_classifier.classify_loan_type(full_input)
        sub_process = email_classifier.classify_subprocess(full_input)
        message_type = email_classifier.classify_message_type(full_input)
        return intent, loan_type, sub_process, message_type
    except Exception as e:
        print(f"Error during classification: {e}")
        return "Error", "Error", "Error", "Error"

# Init database
def init_db():
    conn = sqlite3.connect('email_classification.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            subject TEXT,
            content TEXT,
            intent TEXT,
            loan_type TEXT,
            sub_process TEXT,
            message_type TEXT
        )
    ''')
    conn.close()

# Classify + store
def classify_and_store():
    email_id = email_entry.get().strip()
    subject = subject_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    if not email_id or not subject or not content:
        result_label.config(text="Please fill all fields.", fg="red")
        return

    intent, loan_type, sub_process, message_type = classify_all(subject, content)

    if "Error" in (intent, loan_type, sub_process, message_type):
        result_label.config(text="Classification failed. Check console.", fg="red")
    else:
        result_text = (
            f"Intent: {intent}\n"
            f"Loan Type: {loan_type}\n"
            f"Sub-Process: {sub_process}\n"
            f"Message Type: {message_type}"
        )
        result_label.config(text=result_text, fg="green")

        conn = sqlite3.connect('email_classification.db')
        conn.execute('''
            INSERT INTO emails (email_id, subject, content, intent, loan_type, sub_process, message_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email_id, subject, content, intent, loan_type, sub_process, message_type))
        conn.commit()
        conn.close()

# Show previous logs
def show_logs_window():
    conn = sqlite3.connect('email_classification.db')
    cursor = conn.execute('''
        SELECT email_id, subject, intent, loan_type, sub_process, message_type
        FROM emails ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    log_window = tk.Toplevel(root)
    log_window.title("Previous Classifications")
    log_window.geometry("950x400")

    text_area = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, width=120, height=20)
    text_area.pack(padx=10, pady=10)

    headers = f"{'Email ID':<25}{'Subject':<30}{'Intent':<25}{'Loan Type':<25}{'Sub-Process':<25}{'Message Type'}\n"
    text_area.insert(tk.END, headers)
    text_area.insert(tk.END, "-" * 140 + "\n")

    for row in rows:
        text_area.insert(tk.END, f"{row[0]:<25}{row[1]:<30}{row[2]:<25}{row[3]:<25}{row[4]:<25}{row[5]}\n")

    text_area.configure(state='disabled')

# GUI Setup
root = tk.Tk()
root.title("Email Classifier")

tk.Label(root, text="Email ID:").pack()
email_entry = tk.Entry(root, width=50)
email_entry.pack()

tk.Label(root, text="Subject:").pack()
subject_entry = tk.Entry(root, width=50)
subject_entry.pack()

tk.Label(root, text="Email Content:").pack()
content_text = tk.Text(root, height=10, width=50)
content_text.pack()

tk.Button(root, text="Classify Email", command=classify_and_store).pack(pady=10)

result_label = tk.Label(root, text="", fg="blue", justify="left")
result_label.pack()

tk.Button(root, text="View All Logs", command=show_logs_window).pack(pady=5)

init_db()
root.mainloop()
