import tkinter as tk
from tkinter import scrolledtext
import sqlite3
import importlib.util


# Loading
spec = importlib.util.spec_from_file_location("email_classifier", "email_classifier.py")
email_classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(email_classifier)

def classify(subject, content):
    try:
        full_input = f"{subject.strip()} {content.strip()}"
        category = email_classifier.classify_intent(full_input)
        return category if category else "Unable to classify"
    except Exception as e:
        print(f"Error during classification: {e}")
        return "Error"

def init_db():
    conn = sqlite3.connect('email_classification.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            subject TEXT,
            content TEXT,
            category TEXT
        )
    ''')
    conn.close()

def classify_and_store():
    email_id = email_entry.get().strip()
    subject = subject_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    if not email_id or not subject or not content:
        result_label.config(text="Please fill all fields.", fg="red")
        return

    category = classify(subject, content)
    result_label.config(text=f"Predicted Category: {category}", fg="green")

    if category.lower() not in ["error", "unable to classify"]:
        conn = sqlite3.connect('email_classification.db')
        conn.execute("INSERT INTO emails (email_id, subject, content, category) VALUES (?, ?, ?, ?)",
                     (email_id, subject, content, category))
        conn.commit()
        conn.close()

def show_logs_window():
    conn = sqlite3.connect('email_classification.db')
    cursor = conn.execute("SELECT email_id, subject, category FROM emails ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()


    #popup window
    log_window = tk.Toplevel(root)
    log_window.title("Previous Classifications")
    log_window.geometry("700x400")

    text_area = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, width=90, height=20)
    text_area.pack(padx=10, pady=10)

    text_area.insert(tk.END, f"{'Email ID':<25}{'Subject':<40}{'Category'}\n")
    text_area.insert(tk.END, "-" * 90 + "\n")
    for row in rows:
        text_area.insert(tk.END, f"{row[0]:<25}{row[1]:<40}{row[2]}\n")
    text_area.configure(state='disabled')



#GUI setup
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

result_label = tk.Label(root, text="", fg="blue")
result_label.pack()

tk.Button(root, text="View All Logs", command=show_logs_window).pack(pady=5)

init_db()
root.mainloop()
