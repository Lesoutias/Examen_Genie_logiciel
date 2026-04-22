from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaiementBase(BaseModel):
    vendeur_id: int
    taxe_id: int
    montant: float
    reference: str

class PaiementCreate(PaiementBase):
    date_paiement: Optional[datetime] = None

class PaiementOut(PaiementBase):
    id: int
    collection_user_id: int
    date_paiement: datetime
    created_at: datetime

    class Config:
        from_attributes = True
