import sys
import os

# Resolve the Backend root (two levels up from app/migrations/)
_backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

import logging
from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO)

def migrate():
    logging.info("Connecting to MySQL Database...")
    try:
        with engine.connect() as conn:
            # Trying to add column role
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50);"))
                logging.info("Column 'role' added successfully.")
            except Exception as e:
                logging.info(f"Skipping 'role', maybe it exists? Error: {e}")

            # Trying to add column phone_number
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(50);"))
                logging.info("Column 'phone_number' added successfully.")
            except Exception as e:
                logging.info(f"Skipping 'phone_number', maybe it exists? Error: {e}")
                
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to connect or migrate: {e}")

if __name__ == "__main__":
    migrate()
