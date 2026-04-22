from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), nullable=True)
    status = Column(String(50), default="en attente")
    phone_number = Column(String(50), nullable=True)
    vendeur_id = Column(Integer, ForeignKey("vendeurs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendeur = relationship("Vendeur")
