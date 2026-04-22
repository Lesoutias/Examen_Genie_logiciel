from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
from app.utils.dependencies import get_db, get_current_user
from app.models.taxe import Taxe
from app.models.paiement import Paiement
from app.schemas.taxe import TaxeCreate, TaxeOut, TaxeBase, TaxeUpdate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/taxes", tags=["taxes"])

@router.get("/view", response_model=List[TaxeOut])
def read_taxes_view(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM vue_taxes")).fetchall()
    # Map raw SQL results to the schema
    return [TaxeOut(id=row[0], nom=row[1], montant_base=row[2], frequence=row[3], description=row[4], prix_libre=bool(row[5])) for row in result]

@router.post("/", response_model=TaxeOut)
def create_taxe(taxe: TaxeCreate, db: Session = Depends(get_db)):
    # Protect this route in a real scenario to admins only
    new_taxe = Taxe(**taxe.dict())
    db.add(new_taxe)
    db.commit()
    db.refresh(new_taxe)
    return new_taxe

@router.get("/", response_model=List[TaxeOut])
def read_taxes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Taxe).offset(skip).limit(limit).all()

@router.get("/{taxe_id}", response_model=TaxeOut)
def read_taxe(taxe_id: int, db: Session = Depends(get_db)):
    taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if taxe is None:
        raise HTTPException(status_code=404, detail="Taxe not found")
    return taxe

@router.put("/{taxe_id}", response_model=TaxeOut)
def update_taxe(taxe_id: int, taxe: TaxeUpdate, db: Session = Depends(get_db)):
    db_taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if not db_taxe:
        raise HTTPException(status_code=404, detail="Taxe not found")
    
    try:
        # Using the stored procedure
        db.execute(
            text("CALL sp_update_taxe(:p_id, :p_nom, :p_montant_base, :p_frequence, :p_description, :p_prix_libre)"),
            {
                "p_id": taxe_id,
                "p_nom": taxe.nom,
                "p_montant_base": taxe.montant_base,
                "p_frequence": taxe.frequence,
                "p_description": taxe.description or "",
                "p_prix_libre": taxe.prix_libre
            }
        )
        db.commit()
        db.refresh(db_taxe)
        return db_taxe
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{taxe_id}")
def delete_taxe(taxe_id: int, db: Session = Depends(get_db)):
    db_taxe = db.query(Taxe).filter(Taxe.id == taxe_id).first()
    if not db_taxe:
        raise HTTPException(status_code=404, detail="Taxe non trouvée")
    
    # Check if there are any payments associated with this tax
    payments_count = db.query(Paiement).filter(Paiement.taxe_id == taxe_id).count()
    if payments_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de supprimer cette taxe car elle possède déjà des paiements enregistrés. Veuillez d'abord traiter ces données."
        )
    
    try:
        db.delete(db_taxe)
        db.commit()
        return {"ok": True, "message": "Taxe supprimée avec succès"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
