from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime

from app.database import engine, Base, SessionLocal
from app.routes import auth, users, vendeurs, taxes, paiements, signalements, stats
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


def create_list_vendeurs_view():
    """Crée ou remplace la vue SQL list_vendeurs au démarrage."""
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS list_vendeurs;"))
        conn.execute(text(
            """
            CREATE VIEW list_vendeurs AS
            SELECT
                v.id,
                CONCAT(TRIM(v.nom), ' ', TRIM(v.prenom)) AS noms,
                v.telephone,
                v.identifiant_national AS id_nat,
                v.emplacement AS marche
            FROM vendeurs v
            WHERE v.is_active = TRUE;
            """
        ))
        conn.commit()
        print("✅ Vue list_vendeurs créée ou remplacée.")


def create_vue_taxes():
    """Crée ou remplace la vue SQL vue_taxes au démarrage."""
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vue_taxes;"))
        conn.execute(text(
            """
            CREATE VIEW vue_taxes AS
            SELECT
                id,
                nom,
                COALESCE(montant_base, 0) AS montant_base,
                COALESCE(frequence, 'Non définie') AS frequence,
                COALESCE(description, 'Aucune description') AS description,
                COALESCE(prix_libre, 0) AS prix_libre
            FROM taxes
            -- WHERE status = 'actif';
            """
        ))
        conn.commit()
        print("✅ Vue vue_taxes créée ou remplacée.")


# Événement au démarrage de l'application
@app.on_event("startup")
async def startup_event():
    print("🚀 Démarrage de l'application...")
    create_default_admin()
    create_list_vendeurs_view()
    create_vue_taxes()
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
