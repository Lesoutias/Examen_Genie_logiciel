import sys, os
_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend not in sys.path: sys.path.insert(0, _backend)
import sys
import os
from sqlalchemy import text

# Add the Backend directory to sys.path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from app.database import engine

def check():
    with engine.connect() as conn:
        print("--- Paiements ---")
        res = conn.execute(text("SELECT * FROM paiements LIMIT 10")).fetchall()
        for row in res:
            print(row)
        
        print("\n--- Taxes ---")
        res = conn.execute(text("SELECT * FROM taxes LIMIT 10")).fetchall()
        for row in res:
            print(row)
            
        print("\n--- Vendeurs ---")
        res = conn.execute(text("SELECT id, nom, prenom FROM vendeurs LIMIT 10")).fetchall()
        for row in res:
            print(row)

if __name__ == "__main__":
    check()

