from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class AgentCollecteStats(Base):
    __tablename__ = "vw_agent_collecte_stats"
    __table_args__ = {'info': dict(is_view=True)}
    
    agent_id = Column(Integer, primary_key=True)
    agent_name = Column(String(255))
    total_collected = Column(Float)
    nb_collectes = Column(Integer)
