from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/")
async def get_patients(db: Session = Depends(get_db)):
    """Get all patients - placeholder endpoint"""
    return {"message": "Patients endpoint - implementation needed"}

@router.get("/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get specific patient - placeholder endpoint"""
    return {"message": f"Patient {patient_id} endpoint - implementation needed"}