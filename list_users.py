from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "mysql+pymysql://root:Lesoutils%401907@localhost:3306/taxe_app_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

from sqlalchemy import text
result = db.execute(text("SELECT email, full_name, role FROM users")).fetchall()
for row in result:
    print(f"Email: {row[0]}, Name: {row[1]}, Role: {row[2]}")
db.close()
