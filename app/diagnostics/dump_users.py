import sqlite3

conn = sqlite3.connect('taxe_app.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email, hashed_password FROM users")
for row in cursor.fetchall():
    print(row)
conn.close()
