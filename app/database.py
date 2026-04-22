import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = "mysql+pymysql://root:Lesoutils%401907@localhost:3306/taxe_app_db"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
