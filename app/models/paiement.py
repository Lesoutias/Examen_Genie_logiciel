from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Paiement(Base):
    __tablename__ = "paiements"

    id = Column(Integer, primary_key=True, index=True)
    vendeur_id = Column(Integer, ForeignKey("vendeurs.id"))
    taxe_id = Column(Integer, ForeignKey("taxes.id"))
    collection_user_id = Column(Integer, ForeignKey("users.id")) # Who collected it
    
    montant = Column(Float)
    date_paiement = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(255), unique=True, index=True)
    
    # Optional relationships
    vendeur = relationship("Vendeur")
    taxe = relationship("Taxe")
    collecteur = relationship("User")
