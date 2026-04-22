from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import text, func
from app.utils.dependencies import get_db, get_current_user
from app.models.vendeur import Vendeur
from app.models.user import User
from app.models.paiement import Paiement
from app.models.taxe import Taxe
from app.schemas.vendeur import VendeurCreate, VendeurOut, VendeurViewOut, VendeurMe, PaymentHistoryItem, VendeurStatusOut
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/vendeurs", tags=["vendeurs"])

logger = logging.getLogger(__name__)

@router.get("/view", response_model=List[VendeurViewOut])
def read_vendeurs_view(q: str = "", tax_id: Optional[int] = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Query the view with search and pagination, joining with paiements for last date of specific tax
    params = {"skip": skip, "limit": limit}
    
    # Base SQL
    sql = """
        SELECT 
            lv.id, 
            lv.noms, 
            lv.telephone, 
            lv.id_nat, 
            lv.marche, 
            MAX(p.date_paiement) as derniere_collecte
        FROM list_vendeurs lv
    """
    
    # Conditional LEFT JOIN
    if tax_id:
        sql += " LEFT JOIN paiements p ON lv.id = p.vendeur_id AND p.taxe_id = :tax_id "
        params["tax_id"] = tax_id
    else:
        sql += " LEFT JOIN paiements p ON lv.id = p.vendeur_id "
        
    # Search filter
    if q:
        sql += " WHERE (lv.noms LIKE :q OR lv.id_nat LIKE :q) "
        params["q"] = f"%{q}%"
        
    # Grouping and Pagination
    sql += """
        GROUP BY lv.id, lv.noms, lv.telephone, lv.id_nat, lv.marche
        ORDER BY lv.noms ASC
        LIMIT :limit OFFSET :skip
    """
    
    # Debug logging
    logger.error(f"DEBUG: Running query for tax_id={tax_id}, q='{q}'")
    
    result = db.execute(text(sql), params).fetchall()
    
    # Debug logging
    if result:
        logger.error(f"DEBUG: Found {len(result)} vendors. First vendor last date: {result[0][5]}")
    else:
        logger.error("DEBUG: No vendors found.")
    
    return [
        VendeurViewOut(
            id=row[0], 
            noms=row[1], 
            telephone=row[2], 
            id_nat=row[3], 
            marche=row[4],
            derniere_collecte=row[5]
        ) for row in result
    ]

@router.post("/", response_model=VendeurOut)
def create_vendeur(vendeur: VendeurCreate, db: Session = Depends(get_db)):
    db_vendeur = db.query(Vendeur).filter(Vendeur.identifiant_national == vendeur.identifiant_national).first()
    if db_vendeur:
        raise HTTPException(status_code=400, detail="Vendeur already registered")
    
    new_vendeur = Vendeur(**vendeur.dict())
    db.add(new_vendeur)
    db.commit()
    db.refresh(new_vendeur)
    return new_vendeur

@router.get("/me", response_model=VendeurMe)
def read_vendeur_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "Vendeur":
        raise HTTPException(status_code=403, detail="Not authorized as a Vendeur")
    
    vendeur = None
    if current_user.vendeur_id:
        vendeur = db.query(Vendeur).filter(Vendeur.id == current_user.vendeur_id).first()
    
    # If not found via vendeur_id, try matching by phone or name (Auto-link)
    if not vendeur:
        # Try matching by phone number
        if current_user.phone_number:
            vendeur = db.query(Vendeur).filter(Vendeur.telephone == current_user.phone_number).first()
        
        # If still not found, try matching by full name
        if not vendeur and current_user.full_name:
            name_parts = current_user.full_name.split(" ", 1)
            nom = name_parts[0]
            prenom = name_parts[1] if len(name_parts) > 1 else ""
            vendeur = db.query(Vendeur).filter(Vendeur.nom == nom, Vendeur.prenom == prenom).first()
        
        # If we found a match, link it permanently
        if vendeur:
            current_user.vendeur_id = vendeur.id
            db.add(current_user)
            db.commit()

    if not vendeur:
        raise HTTPException(status_code=404, detail="Vendeur profile not found for this user")
    
    # Calculate stats
    payments = db.query(Paiement).filter(Paiement.vendeur_id == vendeur.id).all()
    total_paye = sum(p.montant for p in payments)
    
    last_payment = db.query(Paiement).filter(Paiement.vendeur_id == vendeur.id).order_by(Paiement.date_paiement.desc()).first()
    
    derniere_collecte = "Aucune"
    status = "EN RETARD"
    
    if last_payment:
        dt = last_payment.date_paiement
        now = datetime.utcnow()
        if dt.date() == now.date():
            derniere_collecte = "Aujourd'hui"
            status = "À JOUR"
        elif dt.date() == (now - timedelta(days=1)).date():
            derniere_collecte = "Hier"
            status = "À JOUR" # Simple rule: if paid yesterday/today, considered up to date
        else:
            derniere_collecte = dt.strftime("%d %b %Y")
    
    # Fetch history with Taxe names
    history_query = db.query(
        Paiement.id,
        Taxe.nom.label("taxe_nom"),
        Paiement.montant,
        Paiement.date_paiement,
        Paiement.reference
    ).join(Taxe, Paiement.taxe_id == Taxe.id).filter(Paiement.vendeur_id == vendeur.id).order_by(Paiement.date_paiement.desc()).limit(20).all()
    
    history = [
        PaymentHistoryItem(
            id=row.id,
            taxe_nom=row.taxe_nom,
            montant=row.montant,
            date_paiement=row.date_paiement,
            reference=row.reference
        ) for row in history_query
    ]
    
    return VendeurMe(
        id=vendeur.id,
        nom=vendeur.nom,
        prenom=vendeur.prenom,
        identifiant_national=vendeur.identifiant_national,
        telephone=vendeur.telephone,
        emplacement=vendeur.emplacement,
        status=status,
        total_paye=total_paye,
        derniere_collecte=derniere_collecte,
        history=history
    )

@router.get("/", response_model=List[VendeurStatusOut])
def read_vendeurs(
    skip: int = 0, 
    limit: int = 100, 
    period: str = "daily", # daily, weekly, monthly
    db: Session = Depends(get_db)
):
    # Fetch all vendors
    vendeurs = db.query(Vendeur).offset(skip).limit(limit).all()
    
    # Get all active taxes grouped by frequency
    taxes_by_freq = {
        "Journalière": db.query(Taxe).filter(Taxe.frequence == "Journalière").all(),
        "Mensuelle": db.query(Taxe).filter(Taxe.frequence == "Mensuelle").all(),
        "Annuelle": db.query(Taxe).filter(Taxe.frequence == "Annuelle").all()
    }
    
    results = []
    now = datetime.utcnow()
    
    for v in vendeurs:
        # Get total amount
        total_stmt = db.query(func.sum(Paiement.montant)).filter(Paiement.vendeur_id == v.id).scalar() or 0.0
        
        # Get last payment overall
        last_pay = db.query(Paiement).filter(Paiement.vendeur_id == v.id).order_by(Paiement.date_paiement.desc()).first()
        
        statuses = {}
        for period_key, freq_name in [("daily", "Journalière"), ("monthly", "Mensuelle"), ("yearly", "Annuelle")]:
            taxes = taxes_by_freq[freq_name]
            status = "À JOUR"
            
            if not taxes:
                status = "À JOUR"
            else:
                for t in taxes:
                    if period_key == "daily":
                        # Logic: En retard if any day since account creation is missing a payment
                        # Calculate total days since creation
                        start_date = v.created_at.date()
                        end_date = now.date()
                        total_expected_days = (end_date - start_date).days + 1
                        
                        # Count unique days with payments for this tax
                        days_paid = db.query(func.count(func.distinct(func.date(Paiement.date_paiement)))).filter(
                            Paiement.vendeur_id == v.id,
                            Paiement.taxe_id == t.id,
                            func.date(Paiement.date_paiement) >= start_date,
                            func.date(Paiement.date_paiement) <= end_date
                        ).scalar() or 0
                        
                        if days_paid < total_expected_days:
                            status = "EN RETARD"
                            break
                    else:
                        # For monthly/yearly, we keep current period check for now or similar cumulative logic?
                        # User only specified daily for now.
                        paid_query = db.query(Paiement).filter(Paiement.vendeur_id == v.id, Paiement.taxe_id == t.id)
                        
                        if period_key == "monthly":
                            paid_query = paid_query.filter(
                                func.extract('year', Paiement.date_paiement) == now.year,
                                func.extract('month', Paiement.date_paiement) == now.month
                            )
                        elif period_key == "yearly":
                            paid_query = paid_query.filter(func.extract('year', Paiement.date_paiement) == now.year)
                        
                        has_paid = paid_query.first() is not None
                        if not has_paid:
                            status = "EN RETARD"
                            break
            statuses[f"status_{period_key}"] = status

        results.append(VendeurStatusOut(
            id=v.id,
            noms=f"{v.nom} {v.prenom}",
            telephone=v.telephone,
            id_nat=v.identifiant_national,
            marche=v.emplacement,
            status_daily=statuses["status_daily"],
            status_monthly=statuses["status_monthly"],
            status_yearly=statuses["status_yearly"],
            derniere_collecte=last_pay.date_paiement if last_pay else None,
            montant_total=total_stmt
        ))
        
    return results

@router.get("/{vendeur_id}", response_model=VendeurOut)
def read_vendeur(vendeur_id: int, db: Session = Depends(get_db)):
    vendeur = db.query(Vendeur).filter(Vendeur.id == vendeur_id).first()
    if vendeur is None:
        raise HTTPException(status_code=404, detail="Vendeur not found")
    return vendeur