from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaxDistributionPoint(BaseModel):
    label: str
    amount: float

class DashboardSummary(BaseModel):
    total_today: float
    growth_rate: float
    active_vendeurs: int
    active_agents: int
    unpaid_vendeurs_count: int
    pending_signals_count: int

class WeeklyRevenuePoint(BaseModel):
    label: str
    amount: float

class RecentCollection(BaseModel):
    id: int
    vendeur_name: str
    location: str
    time_ago: str
    amount: float
    status: str

class RecentSignal(BaseModel):
    id: int
    sujet: str
    auteur_name: str
    time_ago: str
    statut: str

class UnpaidByTax(BaseModel):
    taxe_name: str
    count: int

class DashboardData(BaseModel):
    summary: DashboardSummary
    weekly_revenue: List[WeeklyRevenuePoint]
    recent_activity: List[RecentCollection]
    tax_distribution: List[TaxDistributionPoint]
    unpaid_by_tax: List[UnpaidByTax]
    recent_signals: List[RecentSignal]

class TaxMonthlyPoint(BaseModel):
    month: str
    amount: float

class TaxGlobalStats(BaseModel):
    total_amount: float
    monthly_average: float
    growth_rate: float
    monthly_data: List[TaxMonthlyPoint]
    tax_breakdown: List[TaxDistributionPoint]

class ReportPoint(BaseModel):
    label: str
    value: float
    percentage: Optional[float] = None

class GlobalReports(BaseModel):
    market_distribution: List[ReportPoint]
    compliance_stats: List[ReportPoint]
    agent_performance: List[ReportPoint]
    revenue_by_category: List[ReportPoint]
