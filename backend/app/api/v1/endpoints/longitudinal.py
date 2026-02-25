"""
Longitudinal Neuro-Motor Modeling – API Endpoints

Provides REST endpoints for:
  - Recording biomarker observations
  - Computing trends, cross-modality consistency, risk evolution
  - Querying time-series data for front-end charting
  - Retrieving assessment history
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
from app.services.longitudinal_engine import LongitudinalTrendEngine

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════
# Request / Response schemas
# ═══════════════════════════════════════════════════════════════════════════

class RecordBiomarkersRequest(BaseModel):
    modality: str = Field(..., description="handwriting | voice | dat_scan | composite")
    biomarkers: Dict[str, float] = Field(
        ..., description="Map of biomarker_name → numeric value"
    )
    source_report_id: Optional[str] = None
    source_analysis_id: Optional[str] = None
    recorded_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class TrendResponse(BaseModel):
    biomarker: str
    modality: str
    slope: float
    slope_normalised: Optional[float]
    acceleration: Optional[float]
    r_squared: Optional[float]
    direction: str
    observation_count: int
    baseline_value: Optional[float]
    latest_value: Optional[float]
    window_start: str
    window_end: str


class CrossModalityResponse(BaseModel):
    agreement_score: float
    directional_consistency: float
    pairwise_correlations: Optional[dict]
    modalities_included: list
    modality_directions: dict
    modality_slopes: Optional[dict]
    window_start: str
    window_end: str


class RiskAssessmentResponse(BaseModel):
    id: str
    progression_category: str
    risk_score: float
    risk_delta: Optional[float]
    confidence: float
    current_probability: Optional[float]
    avg_slope: Optional[float]
    avg_acceleration: Optional[float]
    cross_modality_agreement: Optional[float]
    months_of_data: Optional[float]
    clinical_summary: Optional[str]
    key_findings: Optional[list]
    recommendations: Optional[list]
    trend_details: Optional[list]
    computed_at: str


class TimelinePoint(BaseModel):
    id: str
    modality: str
    biomarker: str
    value: float
    recorded_at: str


class FullAssessmentResponse(BaseModel):
    trends: List[TrendResponse]
    cross_modality: Optional[CrossModalityResponse]
    assessment: RiskAssessmentResponse


# ═══════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/biomarkers", status_code=status.HTTP_201_CREATED)
async def record_biomarkers(
    body: RecordBiomarkersRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record a batch of biomarker observations for the current patient.
    Called automatically after each analysis (handwriting, voice, DaT) completes.
    """
    engine = LongitudinalTrendEngine(db)
    observations = engine.record_biomarkers(
        patient_id=current_user.id,
        modality=body.modality,
        biomarkers=body.biomarkers,
        source_report_id=body.source_report_id,
        source_analysis_id=body.source_analysis_id,
        recorded_at=body.recorded_at,
        metadata=body.metadata,
    )
    return {
        "success": True,
        "message": f"Recorded {len(observations)} biomarker observations",
        "count": len(observations),
    }


@router.post("/assess")
async def run_full_assessment(
    window_months: int = Query(6, ge=1, le=60),
    current_probability: Optional[float] = Query(None, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run the full longitudinal assessment pipeline:
      observations → trends → cross-modality → risk evolution
    """
    engine = LongitudinalTrendEngine(db)
    result = engine.run_full_assessment(
        patient_id=current_user.id,
        window_months=window_months,
        current_probability=current_probability,
    )

    return {
        "success": True,
        "data": _format_full_assessment(result),
    }


@router.get("/assessment/latest")
async def get_latest_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent risk evolution assessment."""
    engine = LongitudinalTrendEngine(db)
    assessment = engine.get_latest_assessment(current_user.id)
    if not assessment:
        return {"success": True, "data": None, "message": "No assessments yet"}
    return {
        "success": True,
        "data": _format_assessment(assessment),
    }


@router.get("/assessment/history")
async def get_assessment_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get history of risk evolution assessments for charting progression over time."""
    engine = LongitudinalTrendEngine(db)
    assessments = engine.get_assessment_history(current_user.id, limit=limit)
    return {
        "success": True,
        "data": [_format_assessment(a) for a in assessments],
    }


@router.get("/timeline")
async def get_patient_timeline(
    biomarker: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get raw biomarker time-series for front-end charting.
    Optionally filter by a specific biomarker name.
    """
    engine = LongitudinalTrendEngine(db)
    timeline = engine.get_patient_timeline(current_user.id, biomarker)
    return {
        "success": True,
        "data": timeline,
    }


@router.get("/biomarkers/available")
async def get_available_biomarkers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all distinct biomarker names recorded for this patient."""
    from app.db.longitudinal_models import BiomarkerObservation
    rows = (
        db.query(
            BiomarkerObservation.biomarker_name,
            BiomarkerObservation.modality,
        )
        .filter(BiomarkerObservation.patient_id == current_user.id)
        .distinct()
        .all()
    )
    biomarkers = [
        {"name": r.biomarker_name, "modality": r.modality.value}
        for r in rows
    ]
    return {"success": True, "data": biomarkers}


@router.get("/trends/latest")
async def get_latest_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent set of computed trends for all biomarkers."""
    from app.db.longitudinal_models import BiomarkerTrend
    trends = (
        db.query(BiomarkerTrend)
        .filter(BiomarkerTrend.patient_id == current_user.id)
        .order_by(BiomarkerTrend.computed_at.desc())
        .limit(50)
        .all()
    )
    return {
        "success": True,
        "data": [_format_trend(t) for t in trends],
    }


@router.get("/cross-modality/latest")
async def get_latest_cross_modality(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent cross-modality consistency snapshot."""
    from app.db.longitudinal_models import CrossModalitySnapshot
    snapshot = (
        db.query(CrossModalitySnapshot)
        .filter(CrossModalitySnapshot.patient_id == current_user.id)
        .order_by(CrossModalitySnapshot.computed_at.desc())
        .first()
    )
    if not snapshot:
        return {"success": True, "data": None}
    return {
        "success": True,
        "data": _format_cross_modality(snapshot),
    }


# Doctor endpoint: assess a specific patient
@router.post("/doctor/assess/{patient_id}")
async def doctor_assess_patient(
    patient_id: str,
    window_months: int = Query(6, ge=1, le=60),
    current_probability: Optional[float] = Query(None, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Doctor-initiated full assessment for a specific patient."""
    if current_user.role.value != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can assess other patients",
        )
    engine = LongitudinalTrendEngine(db)
    result = engine.run_full_assessment(
        patient_id=patient_id,
        window_months=window_months,
        current_probability=current_probability,
    )
    return {
        "success": True,
        "data": _format_full_assessment(result),
    }


@router.get("/doctor/timeline/{patient_id}")
async def doctor_get_timeline(
    patient_id: str,
    biomarker: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Doctor view of a patient's biomarker timeline."""
    if current_user.role.value != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view patient timelines",
        )
    engine = LongitudinalTrendEngine(db)
    timeline = engine.get_patient_timeline(patient_id, biomarker)
    return {"success": True, "data": timeline}


@router.get("/doctor/assessment/{patient_id}/latest")
async def doctor_get_latest_assessment(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Doctor view of a patient's latest assessment."""
    if current_user.role.value != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view patient assessments",
        )
    engine = LongitudinalTrendEngine(db)
    assessment = engine.get_latest_assessment(patient_id)
    if not assessment:
        return {"success": True, "data": None, "message": "No assessments yet"}
    return {"success": True, "data": _format_assessment(assessment)}


# ═══════════════════════════════════════════════════════════════════════════
# Formatters
# ═══════════════════════════════════════════════════════════════════════════

def _format_trend(t) -> dict:
    return {
        "biomarker": t.biomarker_name,
        "modality": t.modality.value,
        "slope": t.slope,
        "slope_normalised": t.slope_normalised,
        "acceleration": t.acceleration,
        "r_squared": t.r_squared,
        "p_value": t.p_value,
        "direction": t.direction.value,
        "observation_count": t.observation_count,
        "baseline_value": t.baseline_value,
        "latest_value": t.latest_value,
        "window_start": t.window_start.isoformat() if t.window_start else None,
        "window_end": t.window_end.isoformat() if t.window_end else None,
    }


def _format_cross_modality(s) -> dict:
    return {
        "agreement_score": s.agreement_score,
        "directional_consistency": s.directional_consistency,
        "pairwise_correlations": s.pairwise_correlations,
        "modalities_included": s.modalities_included,
        "modality_directions": s.modality_directions,
        "modality_slopes": s.modality_slopes,
        "window_start": s.window_start.isoformat() if s.window_start else None,
        "window_end": s.window_end.isoformat() if s.window_end else None,
    }


def _format_assessment(a) -> dict:
    return {
        "id": a.id,
        "progression_category": a.progression_category.value,
        "risk_score": a.risk_score,
        "risk_delta": a.risk_delta,
        "confidence": a.confidence,
        "current_probability": a.current_probability,
        "avg_slope": a.avg_slope,
        "avg_acceleration": a.avg_acceleration,
        "cross_modality_agreement": a.cross_modality_agreement,
        "months_of_data": a.months_of_data,
        "clinical_summary": a.clinical_summary,
        "key_findings": a.key_findings,
        "recommendations": a.recommendations,
        "trend_details": a.trend_details,
        "computed_at": a.computed_at.isoformat() if a.computed_at else None,
    }


def _format_full_assessment(result: dict) -> dict:
    trends = result.get("trends", [])
    cm = result.get("cross_modality")
    assessment = result.get("assessment")

    return {
        "trends": [_format_trend(t) for t in trends],
        "cross_modality": _format_cross_modality(cm) if cm else None,
        "assessment": _format_assessment(assessment) if assessment else None,
    }
