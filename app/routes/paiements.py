from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app.utils.dependencies import get_db, get_current_user
from app.models.paiement import Paiement
from app.models.vendeur import Vendeur
from app.models.taxe import Taxe
from app.models.user import User
from app.models.agent_stats import AgentCollecteStats
from app.schemas.paiement import PaiementCreate, PaiementOut
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/paiements", tags=["paiements"])

# ── Schemas (inline for simplicity) ───────────────────────────────────────────

class AgentCollecteSummary(BaseModel):
    agent_id: int
    agent_name: str
    total_collected: float
    nb_collectes: int

class CollecteListItem(BaseModel):
    id: int
    vendeur_name: str
    taxe_name: str
    montant: float
    date_paiement: datetime
    reference: str
    agent_name: str

class CollecteListResponse(BaseModel):
    items: List[CollecteListItem]
    total: int
    page: int
    pages: int

# ── Existing endpoints ─────────────────────────────────────────────────────────

@router.post("/", response_model=PaiementOut)
def create_paiement(
    paiement: PaiementCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_paiement = db.query(Paiement).filter(Paiement.reference == paiement.reference).first()
    if db_paiement:
        raise HTTPException(status_code=400, detail="Paiement reference already exists")
    
    paiement_data = paiement.dict()
    if not paiement_data.get('date_paiement'):
        paiement_data.pop('date_paiement', None) # Let the DB handle default if null
    
    new_paiement = Paiement(
        **paiement_data,
        collection_user_id=current_user.id
    )
    db.add(new_paiement)
    db.commit()
    db.refresh(new_paiement)
    return new_paiement

@router.get("/", response_model=List[PaiementOut])
def read_paiements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Paiement).offset(skip).limit(limit).all()

# ── New endpoints for Autorité Locale ─────────────────────────────────────────

@router.get("/by-agent", response_model=List[AgentCollecteSummary])
def get_collectes_by_agent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns agents ordered by total amount collected (leaderboard)."""
    rows = db.query(AgentCollecteStats).order_by(desc(AgentCollecteStats.total_collected)).all()

    return [
        AgentCollecteSummary(
            agent_id=row.agent_id,
            agent_name=row.agent_name or "Inconnu",
            total_collected=float(row.total_collected or 0),
            nb_collectes=row.nb_collectes
        )
        for row in rows
    ]

@router.get("/list", response_model=CollecteListResponse)
def get_collecte_list(
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of all collections with agent info,
    ordered by the agents who collected the most in total."""
    PAGE_SIZE = 10

    # Sub-query: rank agents by total amount collected
    agent_totals = db.query(
        Paiement.collection_user_id,
        func.sum(Paiement.montant).label("agent_total")
    ).group_by(Paiement.collection_user_id).subquery()

    # Base query joining collectes → vendor, tax, agent, agent_totals for ordering
    base_q = db.query(
        Paiement.id,
        Vendeur.nom.label("v_nom"),
        Vendeur.prenom.label("v_prenom"),
        Taxe.nom.label("t_nom"),
        Paiement.montant,
        Paiement.date_paiement,
        Paiement.reference,
        User.full_name.label("agent_name"),
        agent_totals.c.agent_total
    ).join(Vendeur, Paiement.vendeur_id == Vendeur.id)\
     .join(Taxe, Paiement.taxe_id == Taxe.id)\
     .join(User, Paiement.collection_user_id == User.id)\
     .join(agent_totals, agent_totals.c.collection_user_id == Paiement.collection_user_id)\
     .order_by(desc(agent_totals.c.agent_total), desc(Paiement.date_paiement))

    total = base_q.count()
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    rows = base_q.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    items = [
        CollecteListItem(
            id=row.id,
            vendeur_name=f"{row.v_nom} {row.v_prenom}",
            taxe_name=row.t_nom,
            montant=row.montant,
            date_paiement=row.date_paiement,
            reference=row.reference,
            agent_name=row.agent_name or "Inconnu"
        )
        for row in rows
    ]

    return CollecteListResponse(items=items, total=total, page=page, pages=pages)
