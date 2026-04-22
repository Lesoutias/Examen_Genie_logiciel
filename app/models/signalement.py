from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Signalement(Base):
    __tablename__ = "signalements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # User who reported
    sujet = Column(String(255), index=True)
    description = Column(Text)
    date_signalement = Column(DateTime, default=datetime.utcnow)
    statut = Column(String(255), default="en attente") # en attente, confirme, rejete
    
    auteur = relationship("User")
