import sys, os
_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend not in sys.path: sys.path.insert(0, _backend)
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Email: {u.email}, Hash: {u.hashed_password}")
db.close()

