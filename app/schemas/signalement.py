from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SignalementBase(BaseModel):
    sujet: str
    description: str

class SignalementCreate(SignalementBase):
    pass

class SignalementUpdate(BaseModel):
    statut: str

class SignalementOut(SignalementBase):
    id: int
    user_id: int
    date_signalement: datetime
    statut: str

    class Config:
        from_attributes = True
