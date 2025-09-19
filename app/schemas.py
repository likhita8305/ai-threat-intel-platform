# File: app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class ThreatBase(BaseModel):
    title: str
    type: str
    severity: str
    source: str
    description: str | None = None

class ThreatCreate(ThreatBase):
    pass

class Threat(ThreatBase):
    id: int
    created_at: datetime
    priority_score: float
    
    # --- ADD THESE NEW FIELDS FOR THE API RESPONSE ---
    ai_summary: str | None = None
    ai_mitigation: str | None = None
    ai_entities: str | None = None

    class Config:
        from_attributes = True # Replaces orm_mode = True in Pydantic v2

