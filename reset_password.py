from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import os

DATABASE_URL = "mysql+pymysql://root:Lesoutils%401907@localhost:3306/taxe_app_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from sqlalchemy import text
hashed_password = pwd_context.hash("password123")
db.execute(text(f"UPDATE users SET hashed_password = '{hashed_password}' WHERE email = 'master@gmail.com'"))
db.commit()
print("Password for master@gmail.com reset to 'password123'")
db.close()
