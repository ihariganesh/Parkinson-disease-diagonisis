"""
Lifestyle Recommendations API Endpoints
Provides AI-powered personalized lifestyle recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from ...db.database import get_db
from ...db.models import User
from ...services.gemini_service import get_gemini_service
from ...api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/lifestyle", tags=["lifestyle"])


@router.post("/recommendations/{report_id}")
async def generate_lifestyle_recommendations(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized lifestyle recommendations based on diagnosis report
    
    Args:
        report_id: ID of the diagnosis report
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Lifestyle recommendations with multiple categories
    """
    try:
        # Import here to avoid circular imports
        from ...models.medical import DiagnosisReport
        
        # Get diagnosis report
        report = db.query(DiagnosisReport).filter(
            DiagnosisReport.id == report_id,
            DiagnosisReport.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnosis report not found"
            )
        
        # Calculate age from date of birth
        age = current_user.age if hasattr(current_user, 'age') else 50  # Default if not available
        
        # Prepare symptoms data
        symptoms = {
            'dat_scan': report.datScanResult if hasattr(report, 'datScanResult') else None,
            'handwriting': report.handwritingResult if hasattr(report, 'handwritingResult') else None,
            'voice': report.voiceResult if hasattr(report, 'voiceResult') else None
        }
        
        # Get Gemini service
        gemini_service = get_gemini_service()
        
        # Generate recommendations
        recommendations = await gemini_service.generate_recommendations(
            diagnosis=report.finalDiagnosis,
            pd_probability=float(report.confidence * 100),
            confidence=float(report.confidence * 100),
            age=age,
            symptoms=symptoms,
            medical_history=report.additionalNotes if hasattr(report, 'additionalNotes') else None
        )
        
        return {
            'success': True,
            'report_id': report_id,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating lifestyle recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/recommendations/quick")
async def generate_quick_recommendations(
    diagnosis: str,
    pd_probability: float,
    age: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Generate quick lifestyle recommendations without requiring a saved report
    
    Args:
        diagnosis: Diagnosis result
        pd_probability: Parkinson's disease probability (0-100)
        age: Patient age (optional, will use current_user.age if available)
        current_user: Authenticated user
        
    Returns:
        Lifestyle recommendations
    """
    try:
        # Use provided age or calculate from user's DOB
        patient_age = age if age is not None else (
            current_user.age if hasattr(current_user, 'age') else 50
        )
        
        # Get Gemini service
        gemini_service = get_gemini_service()
        
        # Generate recommendations
        recommendations = await gemini_service.generate_recommendations(
            diagnosis=diagnosis,
            pd_probability=pd_probability,
            confidence=pd_probability,  # Use same as probability for quick generation
            age=patient_age,
            symptoms=None,
            medical_history=None
        )
        
        return {
            'success': True,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating quick recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/recommendations/history")
async def get_recommendations_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get history of lifestyle recommendations for the current user
    
    Args:
        limit: Maximum number of recommendations to return
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of previous recommendations
    """
    try:
        # Import here to avoid circular imports
        from ...models.medical import DiagnosisReport
        
        # Get user's diagnosis reports
        reports = db.query(DiagnosisReport).filter(
            DiagnosisReport.user_id == current_user.id
        ).order_by(
            DiagnosisReport.createdAt.desc()
        ).limit(limit).all()
        
        return {
            'success': True,
            'reports': [
                {
                    'id': report.id,
                    'diagnosis': report.finalDiagnosis,
                    'confidence': float(report.confidence),
                    'created_at': report.createdAt.isoformat(),
                    'doctor_verified': report.doctorVerified
                }
                for report in reports
            ]
        }
        
    except Exception as e:
        print(f"Error fetching recommendations history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )
