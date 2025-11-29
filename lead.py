# leads.py
# Simple functions to create and fetch leads using SQLAlchemy session
from database import SessionLocal, Lead

def save_lead(payload: dict):
    db = SessionLocal()
    try:
        lead = Lead(
            name=payload.get("name"),
            email=payload.get("email"),
            phone=payload.get("phone"),
            message=payload.get("message"),
            source=payload.get("source"),
            utm=payload.get("utm")
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return {"status":"ok","lead_id": lead.id}
    finally:
        db.close()

def get_recent_leads(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.query(Lead).order_by(Lead.id.desc()).limit(limit).all()
        return rows
    finally:
        db.close()
