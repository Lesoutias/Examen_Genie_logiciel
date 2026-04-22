from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth, users, vendeurs, taxes, paiements, signalements, stats

from fastapi import FastAPI
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime
from app.database import SessionLocal, engine
from app.models.user import User

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Taxe App API",
    description="API for Market Tax Collection and Tracking System",
    version="1.0.0"
)

def create_default_admin():
    """Crée un administrateur par défaut s'il n'existe pas"""
    db = SessionLocal()
    try:
        # Vérifier si un admin existe déjà
        admin_email = "master@gmail.com"  # Changez selon vos besoins
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            # Hasher le mot de passe
            default_password = "password123"  # Changez ce mot de passe !
            salt = bcrypt.gensalt(rounds=12)
            hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt)
            
            # Créer l'admin
            default_admin = User(
                email=admin_email,
                hashed_password=hashed_password.decode('utf-8'),
                full_name="Master Mind",
                is_active=True,
                is_admin=False,
                role="Autorité Locale",
                status="valide",
                created_at=datetime.utcnow()
            )
            
            db.add(default_admin)
            db.commit()
            db.refresh(default_admin)
            print(f"✅ Administrateur par défaut créé: {admin_email} / {default_password}")
        else:
            print(f"ℹ️  Administrateur existe déjà: {admin_email}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        db.rollback()
    finally:
        db.close()

# Événement au démarrage de l'application
@app.on_event("startup")
async def startup_event():
    print("🚀 Démarrage de l'application...")
    create_default_admin()
    print("✅ Application prête !")
# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to the frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vendeurs.router)
app.include_router(taxes.router)
app.include_router(paiements.router)
app.include_router(signalements.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Taxe App API"}
