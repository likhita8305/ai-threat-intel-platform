import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import schemas, models
from .database import SessionLocal

import google.generativeai as genai

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("🔴 ERROR: GEMINI_API_KEY environment variable not found.")
        model = None
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🟢 Gemini AI Model configured successfully.")
except Exception as e:
    print(f"🔴 An error occurred during AI model configuration: {e}")
    model = None

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def analyze_threat_with_ai(threat_title: str, threat_description: str):
    if not model:
        print("AI model not available. Skipping analysis.")
        return {
            "ai_summary": "AI model is not configured.",
            "ai_mitigation": "Not available.",
            "ai_entities": "Not available.",
            "priority_score": 0.0,
        }
    
    print(f"--- Analyzing threat: {threat_title} ---")

    prompt = f"""
    Analyze the following cybersecurity threat and provide a structured JSON response.
    Do not include ```json markdown.

    Threat Title: "{threat_title}"
    Description: "{threat_description}"

    Provide the following fields in your JSON response:
    1.  "summary": A concise, one-sentence summary of the threat for a non-technical executive.
    2.  "mitigation": Three actionable, bullet-pointed mitigation steps. Use '*' for bullet points.
    3.  "entities": A comma-separated string of key entities (e.g., malware names, vulnerability IDs, targeted groups).
    4.  "priority_score": An integer score from 1 to 10, where 10 is the most critical. Base this on the potential impact and urgency.
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        analysis = json.loads(cleaned_response_text)
        return {
            "ai_summary": analysis.get("summary", "N/A"),
            "ai_mitigation": analysis.get("mitigation", "N/A"),
            "ai_entities": analysis.get("entities", "N/A"),
            "priority_score": float(analysis.get("priority_score", 0.0)),
        }
    except Exception as e:
        print(f"🔴🔴🔴 AI ANALYSIS FAILED. THE HIDDEN ERROR IS: {e} 🔴🔴🔴")
        return {
            "ai_summary": "Error during AI analysis.",
            "ai_mitigation": "Could not be generated.",
            "ai_entities": "Could not be extracted.",
            "priority_score": 0.0,
        }

@router.post("/threats/", response_model=schemas.Threat)
def create_threat(threat: schemas.ThreatCreate, db: Session = Depends(get_db)):
    ai_analysis = analyze_threat_with_ai(threat.title, threat.description)
    db_threat = models.Threat(
        **threat.dict(),
        priority_score=ai_analysis["priority_score"],
        ai_summary=ai_analysis["ai_summary"],
        ai_mitigation=ai_analysis["ai_mitigation"],
        ai_entities=ai_analysis["ai_entities"]
    )
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat

@router.get("/threats/", response_model=list[schemas.Threat])
def read_threats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    threats = db.query(models.Threat).offset(skip).limit(limit).all()
    return threats

@router.get("/threats/prioritized/", response_model=list[schemas.Threat])
def read_prioritized_threats(db: Session = Depends(get_db)):
    threats = db.query(models.Threat).order_by(desc(models.Threat.priority_score)).limit(20).all()
    return threats

# --- THIS IS THE NEW ENDPOINT FOR THE CISO BRIEFING ---
@router.post("/threats/{threat_id}/ciso_briefing/")
def generate_ciso_briefing(threat_id: int, db: Session = Depends(get_db)):
    """
    Generates a high-level, non-technical briefing for a specific threat.
    """
    db_threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if db_threat is None:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    if not model:
        raise HTTPException(status_code=503, detail="AI Model not configured")

    prompt = f"""
    You are a cybersecurity advisor briefing a non-technical executive (CISO).
    Analyze the following threat and provide a concise, two-paragraph summary.
    Focus on the potential business impact, risk, and recommended strategic posture.
    Avoid technical jargon.

    Threat Title: "{db_threat.title}"
    Description: "{db_threat.description}"
    """
    try:
        response = model.generate_content(prompt)
        return {"briefing": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI briefing: {e}")

