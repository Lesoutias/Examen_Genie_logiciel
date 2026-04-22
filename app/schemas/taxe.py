from pydantic import BaseModel
from typing import Optional

class TaxeBase(BaseModel):
    nom: str
    montant_base: float = 0.0
    frequence: str
    description: Optional[str] = None
    prix_libre: bool = False

class TaxeCreate(TaxeBase):
    pass

class TaxeUpdate(TaxeBase):
    pass

class TaxeOut(TaxeBase):
    id: int

    class Config:
        from_attributes = True
