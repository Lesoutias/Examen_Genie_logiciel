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
            # 1. Add status column
            query = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'status' 
                AND table_schema = DATABASE()
            """)
            exists = conn.execute(query).scalar()
            
            if not exists:
                print("Adding status column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'en attente'"))
                # Set existing users to 'valide'
                conn.execute(text("UPDATE users SET status = 'valide'"))
                conn.commit()
                print("Successfully added status column.")
            else:
                print("status column already exists.")

            # 2. Create Stored Procedure
            print("Creating stored procedure sp_UpdateUser...")
            # MySQL stored procedures with DELIMITER can be tricky via SQLAlchemy text()
            # We can run it as separate statements or just the CREATE statement if it's simple
            
            # Read the SQL file
            sql_file_path = os.path.join(backend_path, 'app', 'sql', 'update_user_procedure.sql')
            with open(sql_file_path, 'r') as f:
                sql_content = f.read()
            
            # SQLAlchemy doesn't support DELIMITER. We need to split or use a raw connection
            # For simplicity, we'll execute the DROP and CREATE separately without DELIMITER
            
            conn.execute(text("DROP PROCEDURE IF EXISTS sp_UpdateUser"))
            
            create_procedure_sql = """
            CREATE PROCEDURE sp_UpdateUser(
                IN p_user_id INT,
                IN p_full_name VARCHAR(255),
                IN p_phone_number VARCHAR(50),
                IN p_role VARCHAR(50)
            )
            BEGIN
                UPDATE users 
                SET full_name = p_full_name,
                    phone_number = p_phone_number,
                    role = p_role
                WHERE id = p_user_id;
            END
            """
            conn.execute(text(create_procedure_sql))
            conn.commit()
            print("Successfully created stored procedure.")

        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
