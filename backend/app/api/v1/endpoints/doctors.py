from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.db.models import User, UserRole, DiagnosisReport, MedicalData, DoctorPatientLinkRequest, DoctorPatientAssignment, InvitationStatus
from app.core.security import get_current_user

router = APIRouter()

@router.post("/reports/{report_id}/verify")
async def verify_report(
    report_id: str,
    doctor_notes: Optional[str] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Doctor verifies a patient's diagnosis report"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can verify reports")
    
    report = db.query(DiagnosisReport).filter(DiagnosisReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.doctor_verified = True
    report.doctor_id = current_user.id
    if doctor_notes is not None:
        report.doctor_notes = doctor_notes
    report.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return {
        "success": True,
        "message": "Report verified successfully",
        "report": {
            "id": report.id,
            "doctor_verified": report.doctor_verified,
            "doctor_notes": report.doctor_notes,
            "doctor_id": report.doctor_id,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None
        }
    }

@router.post("/reports/{report_id}/unverify")
async def unverify_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Doctor removes verification from a report"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can manage reports")
    
    report = db.query(DiagnosisReport).filter(DiagnosisReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.doctor_verified = False
    report.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Verification removed"}

@router.get("/reports/pending")
async def get_pending_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all unverified reports across all patients"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.doctor_verified == False
    ).order_by(DiagnosisReport.created_at.desc()).all()
    
    result = []
    for report in reports:
        patient = db.query(User).filter(User.id == report.patient_id).first()
        result.append({
            "id": report.id,
            "patient_id": report.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "patient_pid": patient.patient_id if patient else None,
            "final_diagnosis": report.final_diagnosis.value if hasattr(report.final_diagnosis, 'value') else str(report.final_diagnosis),
            "confidence": report.confidence,
            "stage": report.stage,
            "multimodal_analysis": report.multimodal_analysis,
            "fusion_score": report.fusion_score,
            "doctor_verified": report.doctor_verified,
            "doctor_notes": report.doctor_notes,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        })
    
    return result

@router.get("/patients")
async def get_doctor_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to the current doctor"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # Get only assigned patients
    assignments = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == current_user.id,
        DoctorPatientAssignment.is_active == True
    ).all()
    patient_ids = [a.patient_id for a in assignments]
    
    patients = db.query(User).filter(
        User.id.in_(patient_ids),
        User.role == UserRole.PATIENT
    ).all()
    
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

@router.get("/requests")
async def get_patient_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending patient requests to connect"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    requests = db.query(DoctorPatientLinkRequest).filter(
        DoctorPatientLinkRequest.doctor_id == current_user.id,
        DoctorPatientLinkRequest.status == InvitationStatus.PENDING
    ).all()
    
    result = []
    for req in requests:
        patient = db.query(User).filter(User.id == req.patient_id).first()
        if patient:
            result.append({
                "id": req.id,
                "patient_id": patient.id,
                "patient_pid": patient.patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "message": req.patient_message,
                "requested_at": req.requested_at.isoformat() if req.requested_at else None
            })
    return result

@router.post("/requests/{req_id}/approve")
async def approve_request(
    req_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a patient connection request"""
    import uuid
    from datetime import datetime
    
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    req = db.query(DoctorPatientLinkRequest).filter(
        DoctorPatientLinkRequest.id == req_id,
        DoctorPatientLinkRequest.doctor_id == current_user.id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = InvitationStatus.APPROVED
    req.approved_at = datetime.utcnow()
    
    doc_patient_assignment = DoctorPatientAssignment(
        id=str(uuid.uuid4()),
        doctor_id=req.doctor_id,
        patient_id=req.patient_id,
        link_request_id=req.id,
        is_active=True
    )
    db.add(doc_patient_assignment)
    db.commit()
    return {"success": True, "message": "Patient linked successfully"}

@router.post("/requests/{req_id}/reject")
async def reject_request(
    req_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a patient connection request"""
    from datetime import datetime
    
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    req = db.query(DoctorPatientLinkRequest).filter(
        DoctorPatientLinkRequest.id == req_id,
        DoctorPatientLinkRequest.doctor_id == current_user.id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = InvitationStatus.REJECTED
    req.rejected_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Request rejected"}

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
    
    # Count pending reports (not verified by doctor)
    pending_reports = db.query(DiagnosisReport).filter(
        and_(
            # Can be adapted if reports are assigned to specific doctors, but right now let's just count unverified
            DiagnosisReport.doctor_verified == False
        )
    ).count()
    
    # Count medical data uploads today (simple metric)
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    recent_uploads = db.query(MedicalData).filter(
        MedicalData.uploaded_at >= today
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
                "final_diagnosis": report.final_diagnosis.value if hasattr(report.final_diagnosis, 'value') else str(report.final_diagnosis),
                "confidence": report.confidence,
                "stage": report.stage,
                "fusion_score": report.fusion_score,
                "doctor_verified": report.doctor_verified,
                "doctor_notes": report.doctor_notes,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ]
    }

@router.get("/search-patient/{patient_id}")
async def search_patient_by_id(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for a patient by their patient_id (PID-XXXXXX format) or their uuid"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # Search by patient_id field (PID-XXXXXX) or uuid
    patient = db.query(User).filter(
        and_(
            or_(User.patient_id == patient_id, User.id == patient_id), 
            User.role == UserRole.PATIENT
        )
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found. Please check the Patient ID.")
    
    # Get patient's diagnosis reports
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.patient_id == patient.id
    ).all()
    
    return {
        "patient": {
            "id": patient.id,
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "phone_number": patient.phone_number,
            "address_street": patient.address_street,
            "address_city": patient.address_city,
            "address_state": patient.address_state,
            "gender": patient.gender,
            "created_at": patient.created_at,
            "is_active": patient.is_active
        },
        "reports": [
            {
                "id": report.id,
                "final_diagnosis": report.final_diagnosis.value if hasattr(report.final_diagnosis, 'value') else str(report.final_diagnosis),
                "confidence": report.confidence,
                "stage": report.stage,
                "multimodal_analysis": report.multimodal_analysis,
                "fusion_score": report.fusion_score,
                "doctor_verified": report.doctor_verified,
                "doctor_notes": report.doctor_notes,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "updated_at": report.updated_at.isoformat() if report.updated_at else None
            }
            for report in reports
        ]
    }