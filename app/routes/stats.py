from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List

from app.utils.dependencies import get_db, get_current_user
from app.models.paiement import Paiement
from app.models.vendeur import Vendeur
from app.models.user import User
from app.models.signalement import Signalement
from app.models.taxe import Taxe
from app.schemas.stats import (
    DashboardData, DashboardSummary, WeeklyRevenuePoint, 
    RecentCollection, TaxDistributionPoint, RecentSignal, 
    UnpaidByTax, TaxGlobalStats, TaxMonthlyPoint, GlobalReports, ReportPoint
)

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/dashboard", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    today = now.date()
    yesterday = today - timedelta(days=1)

    # 1. Total Today
    total_today = db.query(func.sum(Paiement.montant)).filter(
        func.date(Paiement.date_paiement) == today
    ).scalar() or 0.0

    # 2. Total Yesterday (for growth)
    total_yesterday = db.query(func.sum(Paiement.montant)).filter(
        func.date(Paiement.date_paiement) == yesterday
    ).scalar() or 0.0

    growth_rate = 0.0
    if total_yesterday > 0:
        growth_rate = ((total_today - total_yesterday) / total_yesterday) * 100

    # 3. Active counts
    active_vendeurs = db.query(func.count(Vendeur.id)).scalar() or 0
    active_agents = db.query(func.count(User.id)).filter(User.role == "Agent de Collecte").scalar() or 0

    # 4. Alerts counts
    paid_recently_subquery = db.query(Paiement.vendeur_id).filter(
        Paiement.date_paiement >= (now - timedelta(days=2))
    ).subquery()
    unpaid_vendeurs_count = db.query(func.count(Vendeur.id)).filter(
        ~Vendeur.id.in_(paid_recently_subquery)
    ).scalar() or 0

    pending_signals_count = db.query(func.count(Signalement.id)).scalar() or 0

    summary = DashboardSummary(
        total_today=total_today,
        growth_rate=growth_rate,
        active_vendeurs=active_vendeurs,
        active_agents=active_agents,
        unpaid_vendeurs_count=unpaid_vendeurs_count,
        pending_signals_count=pending_signals_count
    )

    # 5. Weekly Revenue (Last 7 days)
    weekly_revenue = []
    day_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        label = day_names[target_date.weekday()]
        
        amount = db.query(func.sum(Paiement.montant)).filter(
            func.date(Paiement.date_paiement) == target_date
        ).scalar() or 0.0
        
        weekly_revenue.append(WeeklyRevenuePoint(label=label, amount=amount))

    # 6. Recent Activity
    recent_query = db.query(
        Paiement.id,
        Vendeur.nom.label("v_nom"),
        Vendeur.prenom.label("v_prenom"),
        Vendeur.emplacement.label("v_loc"),
        Paiement.date_paiement,
        Paiement.montant
    ).join(Vendeur, Paiement.vendeur_id == Vendeur.id).order_by(desc(Paiement.date_paiement)).limit(5).all()

    recent_activity = []
    for row in recent_query:
        diff = now - row.date_paiement
        if diff.seconds < 3600:
            time_ago = f"Il y a {diff.seconds // 60} min"
        elif diff.days == 0:
            time_ago = f"Il y a {diff.seconds // 3600} h"
        else:
            time_ago = f"Il y a {diff.days} j"

        recent_activity.append(RecentCollection(
            id=row.id,
            vendeur_name=f"{row.v_nom} {row.v_prenom}",
            location=row.v_loc or "Inconnu",
            time_ago=time_ago,
            amount=row.montant,
            status="PAYÉ"
        ))

    # 7. Tax Distribution
    tax_dist_query = db.query(
        Taxe.nom.label("taxe_nom"),
        func.sum(Paiement.montant).label("total")
    ).join(Taxe, Paiement.taxe_id == Taxe.id).group_by(Taxe.nom).all()

    tax_distribution = [
        TaxDistributionPoint(label=row.taxe_nom, amount=row.total or 0.0)
        for row in tax_dist_query
    ]

    # 8. Unpaid By Tax
    taxes = db.query(Taxe).all()
    unpaid_by_tax = []
    for t in taxes:
        if t.prix_libre: continue
        paid_today_subquery = db.query(Paiement.vendeur_id).filter(
            Paiement.taxe_id == t.id,
            func.date(Paiement.date_paiement) == today
        ).subquery()
        count = db.query(func.count(Vendeur.id)).filter(~Vendeur.id.in_(paid_today_subquery)).scalar() or 0
        if count > 0:
            unpaid_by_tax.append(UnpaidByTax(taxe_name=t.nom, count=count))

    # 9. Recent Signals
    signals_query = db.query(
        Signalement.id, Signalement.sujet, Signalement.date_signalement,
        Signalement.statut, User.full_name.label("auteur_nom")
    ).join(User, Signalement.user_id == User.id).order_by(desc(Signalement.date_signalement)).limit(3).all()

    recent_signals = []
    for s in signals_query:
        diff = now - s.date_signalement
        if diff.seconds < 3600:
            time_ago = f"Il y a {diff.seconds // 60} min"
        elif diff.days == 0:
            time_ago = f"Il y a {diff.seconds // 3600} h"
        else:
            time_ago = f"Il y a {diff.days} j"

        recent_signals.append(RecentSignal(
            id=s.id, sujet=s.sujet, auteur_name=s.auteur_nom,
            time_ago=time_ago, statut=s.statut
        ))

    return DashboardData(
        summary=summary, weekly_revenue=weekly_revenue,
        recent_activity=recent_activity, tax_distribution=tax_distribution,
        unpaid_by_tax=unpaid_by_tax, recent_signals=recent_signals
    )

@router.get("/taxes", response_model=TaxGlobalStats)
def get_tax_global_stats(year: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if year is None:
        year = datetime.utcnow().year
    
    months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
    monthly_data = []
    total_this_year = 0.0
    
    for i in range(1, 13):
        amount = db.query(func.sum(Paiement.montant)).filter(
            func.extract('year', Paiement.date_paiement) == year,
            func.extract('month', Paiement.date_paiement) == i
        ).scalar() or 0.0
        monthly_data.append(TaxMonthlyPoint(month=months[i-1], amount=amount))
        total_this_year += amount

    monthly_average = total_this_year / 12
    total_last_year = db.query(func.sum(Paiement.montant)).filter(
        func.extract('year', Paiement.date_paiement) == year - 1
    ).scalar() or 0.0
    
    growth_rate = 0.0
    if total_last_year > 0:
        growth_rate = ((total_this_year - total_last_year) / total_last_year) * 100

    tax_breakdown_query = db.query(
        Taxe.nom.label("taxe_nom"), func.sum(Paiement.montant).label("total")
    ).join(Taxe, Paiement.taxe_id == Taxe.id).filter(
        func.extract('year', Paiement.date_paiement) == year
    ).group_by(Taxe.nom).all()
    
    tax_breakdown = [
        TaxDistributionPoint(label=row.taxe_nom, amount=row.total or 0.0)
        for row in tax_breakdown_query
    ]

    return TaxGlobalStats(
        total_amount=total_this_year, monthly_average=monthly_average,
        growth_rate=growth_rate, monthly_data=monthly_data, tax_breakdown=tax_breakdown
    )

@router.get("/reports", response_model=GlobalReports)
def get_global_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Market Distribution
    market_query = db.query(
        Vendeur.emplacement.label("marche"),
        func.sum(Paiement.montant).label("total")
    ).join(Paiement, Vendeur.id == Paiement.vendeur_id).group_by(Vendeur.emplacement).all()
    
    total_revenue = sum(row.total for row in market_query) or 1.0
    market_distribution = [
        ReportPoint(label=row.marche or "Inconnu", value=row.total, percentage=(row.total / total_revenue) * 100)
        for row in market_query
    ]

    # 2. Compliance Stats
    today = datetime.utcnow().date()
    daily_taxes = db.query(Taxe).filter(Taxe.frequence == "Journalière").all()
    total_vendeurs = db.query(func.count(Vendeur.id)).scalar() or 1
    
    if not daily_taxes:
        compliance_stats = [ReportPoint(label="À Jour", value=total_vendeurs, percentage=100.0)]
    else:
        paid_today_count = db.query(func.count(func.distinct(Paiement.vendeur_id))).filter(
            Paiement.taxe_id.in_([t.id for t in daily_taxes]),
            func.date(Paiement.date_paiement) == today
        ).scalar() or 0
        compliance_stats = [
            ReportPoint(label="À Jour", value=paid_today_count, percentage=(paid_today_count / total_vendeurs) * 100),
            ReportPoint(label="En Retard", value=total_vendeurs - paid_today_count, percentage=((total_vendeurs - paid_today_count) / total_vendeurs) * 100)
        ]

    # 3. Agent Performance (Last 30 days)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    agent_query = db.query(
        User.full_name.label("name"),
        func.sum(Paiement.montant).label("total")
    ).join(Paiement, User.id == Paiement.collection_user_id).filter(
        Paiement.date_paiement >= last_30_days
    ).group_by(User.full_name).order_by(desc("total")).all()
    
    agent_performance = [ReportPoint(label=row.name, value=row.total) for row in agent_query]

    # 4. Revenue by Category
    category_query = db.query(
        Taxe.frequence.label("cat"),
        func.sum(Paiement.montant).label("total")
    ).join(Paiement, Taxe.id == Paiement.taxe_id).group_by(Taxe.frequence).all()
    
    revenue_by_category = [ReportPoint(label=row.cat, value=row.total) for row in category_query]

    return GlobalReports(
        market_distribution=market_distribution,
        compliance_stats=compliance_stats,
        agent_performance=agent_performance,
        revenue_by_category=revenue_by_category
    )
