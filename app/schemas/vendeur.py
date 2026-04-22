from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class VendeurBase(BaseModel):
    nom: str
    prenom: str
    identifiant_national: str
    telephone: str
    emplacement: str
    is_active: Optional[bool] = True

class VendeurCreate(VendeurBase):
    pass

class VendeurOut(VendeurBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VendeurViewOut(BaseModel):
    id: int
    noms: str
    telephone: str
    id_nat: str
    marche: str
    derniere_collecte: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentHistoryItem(BaseModel):
    id: int
    taxe_nom: str
    montant: float
    date_paiement: datetime
    reference: str

class VendeurMe(BaseModel):
    id: int
    nom: str
    prenom: str
    identifiant_national: str
    telephone: str
    emplacement: str
    status: str # "À JOUR" or "EN RETARD"
    total_paye: float
    derniere_collecte: Optional[str] # "Hier", "Aujourd'hui", or date
    history: List[PaymentHistoryItem]

class VendeurStatusOut(VendeurViewOut):
    status_daily: str
    status_monthly: str
    status_yearly: str
    derniere_collecte: Optional[datetime]
    montant_total: float
