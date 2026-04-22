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
            # Check if column exists first (MySQL specific check might vary, but IF NOT EXISTS is not standard for ADD COLUMN in all MySQL versions)
            # Standard way is to try and catch or check information_schema
            query = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'vendeur_id' 
                AND table_schema = DATABASE()
            """)
            exists = conn.execute(query).scalar()
            
            if not exists:
                print("Adding vendeur_id column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN vendeur_id INTEGER REFERENCES vendeurs(id)"))
                conn.commit()
                print("Successfully added vendeur_id column.")
            else:
                print("vendeur_id column already exists.")
        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
