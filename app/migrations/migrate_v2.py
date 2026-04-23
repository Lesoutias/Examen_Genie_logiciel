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
            print("Creating stored procedure sp_update_taxe...")
            conn.execute(text("DROP PROCEDURE IF EXISTS sp_update_taxe"))

            create_taxe_procedure_sql = """
            CREATE PROCEDURE sp_update_taxe(
                IN p_id INT,
                IN p_nom VARCHAR(255),
                IN p_montant_base FLOAT,
                IN p_frequence VARCHAR(255),
                IN p_description TEXT,
                IN p_prix_libre BOOLEAN
            )
            BEGIN
                UPDATE taxes
                SET 
                    nom = p_nom,
                    montant_base = p_montant_base,
                    frequence = p_frequence,
                    description = p_description,
                    prix_libre = p_prix_libre
                WHERE id = p_id;
            END
            """
            conn.execute(text(create_taxe_procedure_sql))
            conn.commit()
            print("Successfully created stored procedures.")

            status = conn.execute(text("SHOW PROCEDURE STATUS WHERE Db = DATABASE()"))
            procedures = [row[1] for row in status.fetchall()]
            print(f"Stored procedures in current schema: {procedures}")

        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
