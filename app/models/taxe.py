from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class Taxe(Base):
    __tablename__ = "taxes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), index=True) # e.g. "Taxe de place", "Taxe d'hygiène"
    montant_base = Column(Float, default=0.0)
    frequence = Column(String(255)) # e.g. "Journalier", "Mensuel", "Annuel", "Occasionnel"
    description = Column(String(255), nullable=True)
    prix_libre = Column(Boolean, default=False)  # If True, agent sets price at collection time

