import sys, os
_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend not in sys.path: sys.path.insert(0, _backend)
import sqlite3
import bcrypt

# Generate a proper bcrypt hash for 'password'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(b'password', salt).decode('utf-8')

conn = sqlite3.connect('taxe_app.db')
cursor = conn.cursor()

# Find all users that don't have a valid bcrypt hash
cursor.execute("SELECT id, email FROM users WHERE hashed_password NOT LIKE '$2b$%' OR hashed_password IS NULL")
users = cursor.fetchall()

if users:
    for user in users:
        print(f"Fixing db password for user: {user[1]}")
    
    # Update them directly via SQL
    cursor.execute("UPDATE users SET hashed_password = ? WHERE hashed_password NOT LIKE '$2b$%' OR hashed_password IS NULL", (hashed,))
    conn.commit()
    print(f"Updated {cursor.rowcount} passwords.")
else:
    print("All passwords are valid.")
    
conn.close()

