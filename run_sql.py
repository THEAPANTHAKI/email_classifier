import sqlite3

# Connect to database
conn = sqlite3.connect("email_classification.db")
cur = conn.cursor()

# Read and execute the SQL file
with open("prompt.sql", "r") as f:
    sql_script = f.read()
    cur.executescript(sql_script)

conn.commit()
conn.close()

print("✅ keyword_mapping table created and populated.")
