from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class Vendeur(Base):
    __tablename__ = "vendeurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), index=True)
    prenom = Column(String(255))
    identifiant_national = Column(String(255), unique=True, index=True)
    telephone = Column(String(255))
    emplacement = Column(String(255)) # stall or shop location
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
