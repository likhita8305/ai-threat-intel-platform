# File: app/models.py
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base

class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)
    severity = Column(String)
    source = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # --- NEW AND UPDATED COLUMNS FOR AI ANALYSIS ---
    priority_score = Column(Float, default=0.0)
    ai_summary = Column(String, nullable=True)
    ai_mitigation = Column(String, nullable=True)
    ai_entities = Column(String, nullable=True)
