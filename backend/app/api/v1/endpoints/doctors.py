from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.db.database import get_db
from app.db.models import User, UserRole, DiagnosisReport, MedicalData
from app.core.security import get_current_user

router = APIRouter()

@router.get("/patients")
async def get_doctor_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to the current doctor"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # For now, return all patients - in a real system, you'd have doctor-patient relationships
    patients = db.query(User).filter(User.role == UserRole.PATIENT).all()
    
    return [
        {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "phone_number": patient.phone_number,
            "created_at": patient.created_at,
            "is_active": patient.is_active
        }
        for patient in patients
    ]

@router.get("/reports")
async def get_diagnosis_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all diagnosis reports for the current doctor"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # Get reports created by this doctor or assigned to them
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.doctor_id == current_user.id
    ).all()
    
    return [
        {
            "id": report.id,
            "patient_id": report.patient_id,
            "diagnosis": report.diagnosis,
            "confidence_score": report.confidence_score,
            "status": report.status,
            "created_at": report.created_at,
            "notes": report.notes
        }
        for report in reports
    ]

@router.get("/analytics")
async def get_doctor_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data for the doctor dashboard"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # Count total patients
    total_patients = db.query(User).filter(User.role == UserRole.PATIENT).count()
    
    # Count reports by this doctor
    total_reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.doctor_id == current_user.id
    ).count()
    
    # Count pending reports
    pending_reports = db.query(DiagnosisReport).filter(
        and_(
            DiagnosisReport.doctor_id == current_user.id,
            DiagnosisReport.status == "pending"
        )
    ).count()
    
    # Count medical data uploads today (simple metric)
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    recent_uploads = db.query(MedicalData).filter(
        MedicalData.created_at >= today
    ).count()
    
    return {
        "total_patients": total_patients,
        "total_reports": total_reports,
        "pending_reports": pending_reports,
        "recent_uploads": recent_uploads
    }

@router.get("/patient/{patient_id}")
async def get_patient_details(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific patient"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    patient = db.query(User).filter(
        and_(User.id == patient_id, User.role == UserRole.PATIENT)
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get patient's medical data
    medical_data = db.query(MedicalData).filter(
        MedicalData.patient_id == patient_id
    ).all()
    
    # Get patient's diagnosis reports
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.patient_id == patient_id
    ).all()
    
    return {
        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "phone_number": patient.phone_number,
            "created_at": patient.created_at,
            "is_active": patient.is_active
        },
        "medical_data": [
            {
                "id": data.id,
                "data_type": data.data_type,
                "file_path": data.file_path,
                "created_at": data.created_at,
                "metadata": data.metadata
            }
            for data in medical_data
        ],
        "reports": [
            {
                "id": report.id,
                "diagnosis": report.diagnosis,
                "confidence_score": report.confidence_score,
                "status": report.status,
                "created_at": report.created_at,
                "notes": report.notes
            }
            for report in reports
        ]
    }