import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import google.generativeai as genai

from . import models, schemas
from .database import SessionLocal

# Re-initialize model configuration for this file
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        model = None
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    model = None

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assessments/{threat_id}/generate/", response_model=list[dict])
def generate_assessment(threat_id: int, db: Session = Depends(get_db)):
    """
    Generates a practical assessment quiz for a specific threat using AI.
    """
    db_threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if db_threat is None:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    if not model:
        raise HTTPException(status_code=503, detail="AI Model not configured")

    prompt = f"""
    You are a cybersecurity training instructor. Based on the following threat, create a 3-question multiple-choice quiz.
    The quiz should test a security analyst's practical understanding of the threat's impact and mitigation.
    Provide a structured JSON response which is a list of objects. Do not include ```json markdown.
    Each object in the list should have the following keys: "question", "options" (a list of 4 strings), "answer" (the correct option string), and "explanation".

    Threat Title: "{db_threat.title}"
    Description: "{db_threat.ai_summary}"
    Mitigation Steps: "{db_threat.ai_mitigation}"
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        quiz = json.loads(cleaned_response_text)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI assessment: {e}")
