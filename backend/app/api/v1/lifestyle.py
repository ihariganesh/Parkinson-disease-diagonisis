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


@router.get("/recommendations/{report_id}")
@router.post("/recommendations/{report_id}")
async def generate_lifestyle_recommendations(
    report_id: str,
    force_regenerate: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized lifestyle recommendations based on diagnosis report
    
    Args:
        report_id: ID of the diagnosis report
        force_regenerate: Force regeneration of recommendations (ignore cache)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Lifestyle recommendations with multiple categories
    """
    try:
        # Import here to avoid circular imports
        from ...db.models import DiagnosisReport, CachedRecommendations
        
        # Get diagnosis report
        report = db.query(DiagnosisReport).filter(
            DiagnosisReport.id == report_id,
            DiagnosisReport.patient_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnosis report not found"
            )
        
        # Check if cached recommendations exist (unless force_regenerate)
        if not force_regenerate:
            cached = db.query(CachedRecommendations).filter(
                CachedRecommendations.report_id == report_id
            ).first()
            
            if cached:
                # Check if cache is still valid (24 hours)
                if cached.expires_at is None or cached.expires_at > datetime.now():
                    print(f"✅ Returning cached recommendations for report {report_id}")
                    return {
                        'success': True,
                        'report_id': report_id,
                        'recommendations': cached.recommendations,
                        'generated_at': cached.created_at.isoformat(),
                        'cached': True
                    }
        
        # Get user demographics
        age = current_user.age if hasattr(current_user, 'age') else 50  # Default if not available
        gender = getattr(current_user, 'gender', 'not_specified')
        location = {
            'city': getattr(current_user, 'address_city', None),
            'state': getattr(current_user, 'address_state', None),
            'country': getattr(current_user, 'address_country', None)
        }
        
        # Determine disease severity
        stage = getattr(report, 'stage', 0)
        confidence = float(report.confidence)
        if stage == 0 and confidence < 0.3:
            severity = "Healthy - Low Risk"
        elif stage == 0:
            severity = "Healthy - Monitor Regularly"
        elif stage == 1:
            severity = "Early Stage - Mild Symptoms"
        elif stage == 2:
            severity = "Moderate Stage - Active Management"
        else:
            severity = "Advanced Stage - Comprehensive Care"
        
        # Prepare symptoms data from multimodal_analysis
        multimodal = report.multimodal_analysis if report.multimodal_analysis else {}
        symptoms = {
            'dat_scan': multimodal.get('dat_scan'),
            'handwriting': multimodal.get('handwriting'),
            'voice': multimodal.get('voice')
        }
        
        # Get Gemini service
        gemini_service = get_gemini_service()
        
        # Generate recommendations with full demographics
        recommendations = await gemini_service.generate_recommendations(
            diagnosis=report.final_diagnosis.value if hasattr(report.final_diagnosis, 'value') else str(report.final_diagnosis),
            pd_probability=float(report.confidence * 100),
            confidence=float(report.confidence * 100),
            age=age,
            gender=gender,
            location=location,
            severity=severity,
            stage=stage,
            symptoms=symptoms,
            medical_history=report.doctor_notes
        )
        
        # Cache the recommendations for 24 hours
        from datetime import timedelta
        import uuid
        
        # Remove old cache if exists
        db.query(CachedRecommendations).filter(
            CachedRecommendations.report_id == report_id
        ).delete()
        
        # Create new cache entry
        cached_rec = CachedRecommendations(
            id=str(uuid.uuid4()),
            report_id=report_id,
            recommendations=recommendations,
            generation_metadata={
                'age': age,
                'gender': gender,
                'location': location,
                'severity': severity,
                'stage': stage
            },
            expires_at=datetime.now() + timedelta(hours=24)
        )
        db.add(cached_rec)
        db.commit()
        print(f"✅ Cached recommendations for report {report_id}")
        
        return {
            'success': True,
            'report_id': report_id,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat(),
            'cached': False
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
