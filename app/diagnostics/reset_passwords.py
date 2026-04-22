import sys, os
_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend not in sys.path: sys.path.insert(0, _backend)
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import pwd_context

def reset():
    db = SessionLocal()
    users = db.query(User).all()
    count = 0
    # Create the correct hash for "1234"
    valid_hash = pwd_context.hash("1234")
    
    for u in users:
        print(f"Updating user {u.email} to password '1234'")
        u.hashed_password = valid_hash
        count += 1
    
    db.commit()
    print(f"Done updated {count} users")
    db.close()

if __name__ == '__main__':
    reset()

