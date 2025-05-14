import sqlite3

# Connect to the same DB used in your extension
conn = sqlite3.connect("email_classification.db")
cur = conn.cursor()

# Check if table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keyword_mapping';")
if cur.fetchone() is None:
    print("❌ Table 'keyword_mapping' does not exist.")
    conn.close()
    exit()

# Fetch and display all rows
cur.execute("SELECT * FROM keyword_mapping;")
rows = cur.fetchall()

print(f"\n📄 Total records found: {len(rows)}")
print("🧾 Showing all records:\n")

for row in rows:
    print(row)

conn.close()
