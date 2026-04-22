import sys
import os
from sqlalchemy import text

# Resolve the Backend root (two levels up from app/migrations/)
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_path)

from app.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            # Check for created_at column in paiements
            query = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'paiements' 
                AND column_name = 'created_at' 
                AND table_schema = (SELECT DATABASE())
            """)
            exists = conn.execute(query).scalar()
            
            if not exists:
                print("Adding created_at column to paiements table...")
                conn.execute(text("ALTER TABLE paiements ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
                print("Successfully added created_at column.")
            else:
                print("created_at column already exists.")

            # Ensure date_paiement exists (it should, but let's be safe)
            query_dp = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'paiements' 
                AND column_name = 'date_paiement' 
                AND table_schema = (SELECT DATABASE())
            """)
            exists_dp = conn.execute(query_dp).scalar()
            
            if not exists_dp:
                print("Adding date_paiement column to paiements table...")
                conn.execute(text("ALTER TABLE paiements ADD COLUMN date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
                print("Successfully added date_paiement column.")
            else:
                print("date_paiement column already exists.")

        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
