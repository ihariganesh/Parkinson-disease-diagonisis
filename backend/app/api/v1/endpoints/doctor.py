"""
Doctor Dashboard API Endpoints
Comprehensive doctor features for patient management, report review, and communication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from ....db.database import get_db
from ....db.models import (
    User, UserRole, DiagnosisReport, DiagnosisStage,
    DoctorPatientAssignment, DoctorReportReview, DoctorCustomRecommendation,
    PatientProgressTracking, DoctorPatientMessage, HighRiskCaseFlag, CaseFlagEnum
)
from .auth import get_current_user

router = APIRouter(prefix="/doctor", tags=["doctor"])


# ==================== PYDANTIC MODELS ====================

class PatientSummary(BaseModel):
    patient_id: str
    patient_name: str
    medical_record_number: Optional[str]
    last_analysis_date: Optional[datetime]
    pd_prediction: str  # "Yes" or "No"
    estimated_stage: str  # "Early", "Moderate", "Advanced", "Healthy"
    confidence_score: float
    risk_level: str  # "Low", "Medium", "High"
    has_flags: bool
    
    class Config:
        from_attributes = True


class ReportDetailResponse(BaseModel):
    report_id: str
    patient_id: str
    patient_name: str
    analysis_date: datetime
    
    # Multimodal breakdown
    dat_scan: Optional[Dict[str, Any]]
    handwriting: Optional[Dict[str, Any]]
    speech: Optional[Dict[str, Any]]
    
    # Final prediction
    final_diagnosis: str
    confidence: float
    stage: int
    
    # Doctor review
    doctor_review: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class StageValidationRequest(BaseModel):
    report_id: str
    confirmed_stage: int
    clinical_notes: Optional[str]
    symptoms_description: Optional[str]


class CustomRecommendationRequest(BaseModel):
    report_id: str
    patient_id: str
    category: str
    recommendation_text: str
    priority: str
    follow_up_required: bool = False
    follow_up_date: Optional[datetime]


class MessageRequest(BaseModel):
    recipient_id: str
    report_id: Optional[str]
    subject: Optional[str]
    message_text: str
    message_type: str = "general"
    attachment_url: Optional[str]
    attachment_name: Optional[str]


class CaseFlagRequest(BaseModel):
    patient_id: str
    report_id: Optional[str]
    flag_type: str
    severity: str
    reason: str


# ==================== HELPER FUNCTIONS ====================

def verify_doctor_role(current_user: User):
    """Verify user is a doctor"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )


def get_risk_level(confidence: float, stage: int) -> str:
    """Calculate risk level based on confidence and stage"""
    if stage == 0:
        return "Low"
    elif stage == 1:
        return "Low" if confidence < 0.7 else "Medium"
    elif stage == 2:
        return "Medium" if confidence < 0.8 else "High"
    else:
        return "High"


# ==================== API ENDPOINTS ====================

@router.get("/patients", response_model=List[PatientSummary])
async def get_assigned_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """
    Get list of patients assigned to this doctor
    
    Returns patient cards with:
    - Name/ID
    - Last analysis date
    - PD prediction (Yes/No)
    - Estimated stage
    - Risk level
    - Confidence score
    """
    verify_doctor_role(current_user)
    
    # Get assigned patients
    query = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == current_user.id
    )
    
    if not include_inactive:
        query = query.filter(DoctorPatientAssignment.is_active == True)
    
    assignments = query.all()
    
    patient_summaries = []
    
    for assignment in assignments:
        patient = db.query(User).filter(User.id == assignment.patient_id).first()
        if not patient:
            continue
        
        # Get latest report
        latest_report = db.query(DiagnosisReport).filter(
            DiagnosisReport.patient_id == patient.id
        ).order_by(desc(DiagnosisReport.created_at)).first()
        
        if latest_report:
            # Determine PD prediction
            pd_prediction = "No" if latest_report.final_diagnosis == DiagnosisStage.HEALTHY else "Yes"
            
            # Map stage to readable format
            stage_map = {
                0: "Healthy",
                1: "Early Stage",
                2: "Moderate Stage",
                3: "Advanced Stage",
                4: "Severe Stage"
            }
            estimated_stage = stage_map.get(latest_report.stage, "Unknown")
            
            # Calculate risk level
            risk_level = get_risk_level(latest_report.confidence, latest_report.stage)
            
            # Check for flags
            has_flags = db.query(HighRiskCaseFlag).filter(
                HighRiskCaseFlag.patient_id == patient.id,
                HighRiskCaseFlag.is_resolved == False
            ).count() > 0
            
        else:
            pd_prediction = "N/A"
            estimated_stage = "No Analysis"
            risk_level = "Unknown"
            has_flags = False
        
        # Get medical record number (if exists)
        from ....db.models import Patient
        patient_record = db.query(Patient).filter(Patient.user_id == patient.id).first()
        mrn = patient_record.medical_record_number if patient_record else None
        
        patient_summaries.append(PatientSummary(
            patient_id=patient.id,
            patient_name=f"{patient.first_name} {patient.last_name}",
            medical_record_number=mrn,
            last_analysis_date=latest_report.created_at if latest_report else None,
            pd_prediction=pd_prediction,
            estimated_stage=estimated_stage,
            confidence_score=float(latest_report.confidence) if latest_report else 0.0,
            risk_level=risk_level,
            has_flags=has_flags
        ))
    
    return patient_summaries


@router.get("/patient/{patient_id}/report/{report_id}", response_model=ReportDetailResponse)
async def get_patient_report_detail(
    patient_id: str,
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed report for a specific patient
    
    Includes:
    - Multimodal analysis breakdown (DaT scan, handwriting, speech)
    - Final PD probability with confidence
    - Doctor review/validation if exists
    """
    verify_doctor_role(current_user)
    
    # Verify doctor has access to this patient
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == current_user.id,
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this patient"
        )
    
    # Get report
    report = db.query(DiagnosisReport).filter(
        DiagnosisReport.id == report_id,
        DiagnosisReport.patient_id == patient_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get patient info
    patient = db.query(User).filter(User.id == patient_id).first()
    
    # Extract multimodal analysis
    multimodal = report.multimodal_analysis or {}
    
    # Get doctor review if exists
    doctor_review_record = db.query(DoctorReportReview).filter(
        DoctorReportReview.report_id == report_id,
        DoctorReportReview.doctor_id == current_user.id
    ).first()
    
    doctor_review = None
    if doctor_review_record:
        doctor_review = {
            "ai_stage_prediction": doctor_review_record.ai_stage_prediction,
            "doctor_confirmed_stage": doctor_review_record.doctor_confirmed_stage,
            "stage_override": doctor_review_record.stage_override,
            "clinical_notes": doctor_review_record.clinical_notes,
            "symptoms_description": doctor_review_record.symptoms_description,
            "reviewed": doctor_review_record.reviewed,
            "reviewed_at": doctor_review_record.reviewed_at
        }
    
    return ReportDetailResponse(
        report_id=report.id,
        patient_id=patient.id,
        patient_name=f"{patient.first_name} {patient.last_name}",
        analysis_date=report.created_at,
        dat_scan=multimodal.get('dat_scan'),
        handwriting=multimodal.get('handwriting'),
        speech=multimodal.get('voice'),
        final_diagnosis=report.final_diagnosis.value,
        confidence=float(report.confidence),
        stage=report.stage,
        doctor_review=doctor_review
    )


@router.post("/validate-stage")
async def validate_disease_stage(
    validation: StageValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Doctor validates/overrides AI-predicted disease stage
    
    Allows doctor to:
    - Confirm AI prediction
    - Override with different stage
    - Add clinical notes
    """
    verify_doctor_role(current_user)
    
    # Get report
    report = db.query(DiagnosisReport).filter(
        DiagnosisReport.id == validation.report_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if review already exists
    existing_review = db.query(DoctorReportReview).filter(
        DoctorReportReview.report_id == validation.report_id,
        DoctorReportReview.doctor_id == current_user.id
    ).first()
    
    if existing_review:
        # Update existing review
        existing_review.doctor_confirmed_stage = validation.confirmed_stage
        existing_review.stage_override = (validation.confirmed_stage != report.stage)
        existing_review.clinical_notes = validation.clinical_notes
        existing_review.symptoms_description = validation.symptoms_description
        existing_review.reviewed = True
        existing_review.reviewed_at = datetime.now()
        existing_review.updated_at = datetime.now()
    else:
        # Create new review
        review = DoctorReportReview(
            id=str(uuid.uuid4()),
            report_id=validation.report_id,
            doctor_id=current_user.id,
            ai_stage_prediction=report.stage,
            doctor_confirmed_stage=validation.confirmed_stage,
            stage_override=(validation.confirmed_stage != report.stage),
            clinical_notes=validation.clinical_notes,
            symptoms_description=validation.symptoms_description,
            reviewed=True,
            reviewed_at=datetime.now()
        )
        db.add(review)
    
    # Update report with doctor validation
    report.doctor_id = current_user.id
    report.doctor_verified = True
    report.doctor_notes = validation.clinical_notes
    
    db.commit()
    
    return {
        "success": True,
        "message": "Stage validation saved",
        "stage_override": validation.confirmed_stage != report.stage
    }


@router.post("/custom-recommendation")
async def add_custom_recommendation(
    recommendation: CustomRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Doctor adds custom or edited recommendations
    
    Can include:
    - Exercise plans
    - Speech therapy suggestions
    - Medication adjustments (text only)
    - Follow-up intervals
    """
    verify_doctor_role(current_user)
    
    # Verify report exists
    report = db.query(DiagnosisReport).filter(
        DiagnosisReport.id == recommendation.report_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Create custom recommendation
    custom_rec = DoctorCustomRecommendation(
        id=str(uuid.uuid4()),
        report_id=recommendation.report_id,
        doctor_id=current_user.id,
        patient_id=recommendation.patient_id,
        category=recommendation.category,
        recommendation_text=recommendation.recommendation_text,
        priority=recommendation.priority,
        follow_up_required=recommendation.follow_up_required,
        follow_up_date=recommendation.follow_up_date
    )
    
    db.add(custom_rec)
    db.commit()
    
    return {
        "success": True,
        "recommendation_id": custom_rec.id,
        "message": "Custom recommendation added"
    }


@router.get("/patient/{patient_id}/recommendations")
async def get_patient_recommendations(
    patient_id: str,
    report_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all recommendations for a patient (AI + doctor custom)
    """
    verify_doctor_role(current_user)
    
    query = db.query(DoctorCustomRecommendation).filter(
        DoctorCustomRecommendation.patient_id == patient_id
    )
    
    if report_id:
        query = query.filter(DoctorCustomRecommendation.report_id == report_id)
    
    recommendations = query.order_by(desc(DoctorCustomRecommendation.created_at)).all()
    
    return {
        "success": True,
        "count": len(recommendations),
        "recommendations": [
            {
                "id": rec.id,
                "category": rec.category,
                "recommendation_text": rec.recommendation_text,
                "priority": rec.priority,
                "follow_up_required": rec.follow_up_required,
                "follow_up_date": rec.follow_up_date,
                "created_at": rec.created_at
            }
            for rec in recommendations
        ]
    }


@router.get("/patient/{patient_id}/progression")
async def get_patient_progression(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    months: int = 6
):
    """
    Track patient progression over time
    
    Shows:
    - Timeline of uploads
    - Changes in scores over weeks/months
    - Improvement or deterioration trends
    """
    verify_doctor_role(current_user)
    
    # Get reports for the time period
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.patient_id == patient_id,
        DiagnosisReport.created_at >= cutoff_date
    ).order_by(DiagnosisReport.created_at).all()
    
    # Get progress tracking entries
    progress_entries = db.query(PatientProgressTracking).filter(
        PatientProgressTracking.patient_id == patient_id,
        PatientProgressTracking.tracked_at >= cutoff_date
    ).order_by(PatientProgressTracking.tracked_at).all()
    
    # Build timeline
    timeline = []
    for report in reports:
        multimodal = report.multimodal_analysis or {}
        
        timeline.append({
            "date": report.created_at.isoformat(),
            "type": "analysis",
            "stage": report.stage,
            "confidence": float(report.confidence),
            "scores": {
                "handwriting": multimodal.get('handwriting', {}).get('confidence', 0),
                "speech": multimodal.get('voice', {}).get('confidence', 0),
                "dat_scan": multimodal.get('dat_scan', {}).get('confidence', 0)
            }
        })
    
    # Calculate trends
    if len(reports) >= 2:
        first_stage = reports[0].stage
        latest_stage = reports[-1].stage
        
        if latest_stage > first_stage:
            trend = "deteriorating"
        elif latest_stage < first_stage:
            trend = "improving"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "success": True,
        "patient_id": patient_id,
        "timeline": timeline,
        "trend": trend,
        "total_analyses": len(reports),
        "period_months": months
    }


@router.post("/message/send")
async def send_message_to_patient(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send secure message to patient
    
    Can include:
    - Follow-up instructions
    - Test results
    - Uploaded PDFs or documents
    """
    verify_doctor_role(current_user)
    
    # Verify recipient is a patient assigned to this doctor
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == current_user.id,
        DoctorPatientAssignment.patient_id == message.recipient_id,
        DoctorPatientAssignment.is_active == True
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only message your assigned patients"
        )
    
    # Create message
    new_message = DoctorPatientMessage(
        id=str(uuid.uuid4()),
        sender_id=current_user.id,
        recipient_id=message.recipient_id,
        report_id=message.report_id,
        subject=message.subject,
        message_text=message.message_text,
        message_type=message.message_type,
        attachment_url=message.attachment_url,
        attachment_name=message.attachment_name
    )
    
    db.add(new_message)
    db.commit()
    
    return {
        "success": True,
        "message_id": new_message.id,
        "sent_at": new_message.sent_at
    }


@router.get("/messages")
async def get_doctor_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unread_only: bool = False
):
    """Get all messages (sent and received)"""
    verify_doctor_role(current_user)
    
    query = db.query(DoctorPatientMessage).filter(
        or_(
            DoctorPatientMessage.sender_id == current_user.id,
            DoctorPatientMessage.recipient_id == current_user.id
        )
    )
    
    if unread_only:
        query = query.filter(
            DoctorPatientMessage.recipient_id == current_user.id,
            DoctorPatientMessage.is_read == False
        )
    
    messages = query.order_by(desc(DoctorPatientMessage.sent_at)).all()
    
    return {
        "success": True,
        "count": len(messages),
        "messages": [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "recipient_id": msg.recipient_id,
                "subject": msg.subject,
                "message_text": msg.message_text,
                "message_type": msg.message_type,
                "is_read": msg.is_read,
                "sent_at": msg.sent_at,
                "has_attachment": bool(msg.attachment_url)
            }
            for msg in messages
        ]
    }


@router.post("/flag-case")
async def flag_high_risk_case(
    flag: CaseFlagRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Flag high-risk case requiring attention
    
    Types:
    - Needs urgent clinical visit
    - Possible misclassification
    - Needs further tests
    - Rapid progression
    """
    verify_doctor_role(current_user)
    
    # Validate flag type
    try:
        flag_enum = CaseFlagEnum[flag.flag_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid flag type. Must be one of: {[e.value for e in CaseFlagEnum]}"
        )
    
    # Create flag
    case_flag = HighRiskCaseFlag(
        id=str(uuid.uuid4()),
        patient_id=flag.patient_id,
        report_id=flag.report_id,
        doctor_id=current_user.id,
        flag_type=flag_enum,
        severity=flag.severity,
        reason=flag.reason
    )
    
    db.add(case_flag)
    db.commit()
    
    return {
        "success": True,
        "flag_id": case_flag.id,
        "message": f"Case flagged as {flag.flag_type}"
    }


@router.get("/flagged-cases")
async def get_flagged_cases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    resolved: bool = False
):
    """Get all flagged cases"""
    verify_doctor_role(current_user)
    
    query = db.query(HighRiskCaseFlag).filter(
        HighRiskCaseFlag.doctor_id == current_user.id,
        HighRiskCaseFlag.is_resolved == resolved
    )
    
    flags = query.order_by(desc(HighRiskCaseFlag.flagged_at)).all()
    
    flagged_cases = []
    for flag in flags:
        patient = db.query(User).filter(User.id == flag.patient_id).first()
        
        flagged_cases.append({
            "flag_id": flag.id,
            "patient_id": flag.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "flag_type": flag.flag_type.value,
            "severity": flag.severity,
            "reason": flag.reason,
            "flagged_at": flag.flagged_at,
            "is_resolved": flag.is_resolved,
            "resolved_at": flag.resolved_at,
            "resolution_notes": flag.resolution_notes
        })
    
    return {
        "success": True,
        "count": len(flagged_cases),
        "cases": flagged_cases
    }


@router.put("/flag/{flag_id}/resolve")
async def resolve_case_flag(
    flag_id: str,
    resolution_notes: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a case flag as resolved"""
    verify_doctor_role(current_user)
    
    flag = db.query(HighRiskCaseFlag).filter(
        HighRiskCaseFlag.id == flag_id,
        HighRiskCaseFlag.doctor_id == current_user.id
    ).first()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flag not found"
        )
    
    flag.is_resolved = True
    flag.resolved_at = datetime.now()
    flag.resolution_notes = resolution_notes
    
    db.commit()
    
    return {
        "success": True,
        "message": "Case flag resolved"
    }


@router.get("/dashboard/stats")
async def get_doctor_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for doctor
    
    Includes:
    - Total patients
    - New reports this week
    - Flagged cases
    - Unread messages
    """
    verify_doctor_role(current_user)
    
    # Total assigned patients
    total_patients = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == current_user.id,
        DoctorPatientAssignment.is_active == True
    ).count()
    
    # Get patient IDs
    patient_ids = [
        a.patient_id for a in db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.doctor_id == current_user.id,
            DoctorPatientAssignment.is_active == True
        ).all()
    ]
    
    # New reports this week
    week_ago = datetime.now() - timedelta(days=7)
    new_reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.patient_id.in_(patient_ids),
        DiagnosisReport.created_at >= week_ago
    ).count()
    
    # Flagged cases (unresolved)
    flagged_cases = db.query(HighRiskCaseFlag).filter(
        HighRiskCaseFlag.doctor_id == current_user.id,
        HighRiskCaseFlag.is_resolved == False
    ).count()
    
    # Unread messages
    unread_messages = db.query(DoctorPatientMessage).filter(
        DoctorPatientMessage.recipient_id == current_user.id,
        DoctorPatientMessage.is_read == False
    ).count()
    
    # Patients by stage
    stage_distribution = {}
    for patient_id in patient_ids:
        latest_report = db.query(DiagnosisReport).filter(
            DiagnosisReport.patient_id == patient_id
        ).order_by(desc(DiagnosisReport.created_at)).first()
        
        if latest_report:
            stage = latest_report.stage
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
    
    return {
        "success": True,
        "stats": {
            "total_patients": total_patients,
            "new_reports_this_week": new_reports,
            "flagged_cases": flagged_cases,
            "unread_messages": unread_messages,
            "stage_distribution": stage_distribution
        }
    }
