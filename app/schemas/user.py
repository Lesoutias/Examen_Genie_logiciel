from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.schemas.vendeur import VendeurOut

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    status: Optional[str] = "en attente"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str
    full_name: str
    phone_number: str
    identifiant_national: Optional[str] = None
    emplacement: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    vendeur: Optional[VendeurOut] = None

    class Config:
        from_attributes = True
