from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy import text

DATABASE_URL = "mysql+pymysql://root:Lesoutils%401907@localhost:3306/taxe_app_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("12345")

emails = ["agentlocal@gmail.com", "metreyves@gmail.com"]
for email in emails:
    db.execute(text(f"UPDATE users SET hashed_password = '{hashed_password}' WHERE email = '{email}'"))
db.commit()
print("Passwords for agent and vendeur reset to '12345'")
db.close()
