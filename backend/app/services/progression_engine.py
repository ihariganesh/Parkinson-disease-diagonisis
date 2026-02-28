import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional

from app.db.longitudinal_models import (
    BiomarkerObservation,
    RiskEvolutionAssessment,
    BiomarkerTrend,
    CrossModalitySnapshot,
    BiomarkerModality,
    ProgressionCategory,
    TrendDirection
)

def compute_slope(time_series: List[dict]) -> float:
    """Computes the slope of the time series using linear regression.
    time_series should be list of dicts with 'timestamp' and 'value'.
    Returns slope in unit/month.
    """
    if len(time_series) < 2:
        return 0.0

    # Sort by timestamp
    sorted_ts = sorted(time_series, key=lambda x: x['timestamp'])
    
    # Calculate months from first observation
    first_time = sorted_ts[0]['timestamp']
    x = np.array([(pt['timestamp'] - first_time).total_seconds() / (30 * 86400) for pt in sorted_ts])
    y = np.array([pt['value'] for pt in sorted_ts])

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))

    if ss_xx == 0:
        return 0.0
    
    return float(ss_xy / ss_xx)

def compute_acceleration(slopes: List[float]) -> float:
    """Computes acceleration as the difference between the most recent slopes."""
    if len(slopes) < 2:
        return 0.0
    return float(slopes[-1] - slopes[-2])

def compute_cross_modality_agreement(time_series_by_modality: Dict[str, List[dict]]) -> float:
    """Computes how consistently different modalities are trending. Returns 0-1."""
    if not time_series_by_modality or len(time_series_by_modality) < 2:
        return 0.5 # Default middle confidence if not enough modalities

    slopes = []
    for mod, ts in time_series_by_modality.items():
        slopes.append(compute_slope(ts))
    
    # Simple agreement: what percentage of slopes share the same sign (direction)
    positives = sum(1 for s in slopes if s > 0)
    negatives = sum(1 for s in slopes if s < 0)
    
    max_agreement = max(positives, negatives)
    return float(max_agreement / len(slopes)) if slopes else 0.5

def compute_confidence(data_span_months: float, agreement: float, variance: float) -> float:
    """Computes confidence score 0-1 based on span, agreement, and inverse variance."""
    # Cap span at 12 months for confidence context
    span_score = min(1.0, data_span_months / 12.0)
    
    # We want variance to be low for high confidence
    var_score = max(0.0, 1.0 - variance) if variance else 1.0
    
    confidence = (0.4 * span_score) + (0.4 * agreement) + (0.2 * var_score)
    return float(max(0.0, min(1.0, confidence)))

def compute_risk_stage(current_risk: float, velocity: float, acceleration: float) -> str:
    """Computes the clinical risk stage."""
    if current_risk < 0.3 and velocity < 0.05:
        return "Stable"
    elif current_risk < 0.5 or (velocity < 0.1 and acceleration <= 0):
        return "Emerging Risk"
    elif acceleration > 0.05:
        return "Rapid Progression"
    else:
        return "Progressive Risk"

class ProgressionEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_progression_metrics(self, patient_id: str) -> dict:
        """
        Orchestrates calculation of progression metrics and retrieves time-series data.
        """
        # Fetch all observations
        observations = (
            self.db.query(BiomarkerObservation)
            .filter(BiomarkerObservation.patient_id == patient_id)
            .order_by(BiomarkerObservation.recorded_at.asc())
            .all()
        )

        time_series_data = []
        overall_ts = []
        by_modality = {"handwriting": [], "voice": [], "dat_scan": []}

        for obs in observations:
            # We map recorded_at to ISO string for JSON, but use datetime for compute
            ts = obs.recorded_at
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            
            pt = {
                "timestamp": ts,
                "value": obs.value,
                "modality": obs.modality.value,
                "biomarker": obs.biomarker_name
            }
            
            overall_ts.append(pt)
            if obs.modality.value in by_modality:
                by_modality[obs.modality.value].append(pt)

            # JSON serializable format
            time_series_data.append({
                "timestamp": ts.isoformat(),
                "modality": obs.modality.value,
                "biomarker": obs.biomarker_name,
                "value": obs.value
            })

        if not overall_ts:
            return {
                "risk_score": 0.0,
                "velocity": 0.0,
                "acceleration": 0.0,
                "agreement": 0.0,
                "confidence": 0.0,
                "risk_delta_since_last": 0.0,
                "data_span_months": 0.0,
                "time_series_data": [],
                "risk_stage": "Stable"
            }

        first_ts = overall_ts[0]["timestamp"]
        last_ts = overall_ts[-1]["timestamp"]
        data_span_months = (last_ts - first_ts).total_seconds() / (30 * 86400)

        # compute overall risk progression
        velocity = compute_slope(overall_ts)
        
        # Calculate multiple window slopes to find acceleration
        # e.g., first half vs second half
        half_idx = len(overall_ts) // 2
        if half_idx >= 2:
            slope1 = compute_slope(overall_ts[:half_idx])
            slope2 = compute_slope(overall_ts[half_idx:])
            acceleration = compute_acceleration([slope1, slope2])
        else:
            acceleration = 0.0

        agreement = compute_cross_modality_agreement(by_modality)

        values = [p["value"] for p in overall_ts]
        variance = float(np.var(values)) if values else 0.0
        
        confidence = compute_confidence(data_span_months, agreement, variance)
        
        # Use simple mean of latest values as current risk base proxy
        recent_values = values[-3:] if len(values) >=3 else values
        current_risk = float(np.mean(recent_values)) if recent_values else 0.0

        risk_stage = compute_risk_stage(current_risk, velocity, acceleration)

        # In a full system, you would grab risk_delta_since_last from previous calculations
        risk_delta_since_last = velocity * 1.0 # arbitrary approximation using velocity 

        return {
            "risk_score": current_risk,
            "velocity": velocity,
            "acceleration": acceleration,
            "agreement": agreement,
            "confidence": confidence,
            "risk_delta_since_last": risk_delta_since_last,
            "data_span_months": data_span_months,
            "time_series_data": time_series_data,
            "risk_stage": risk_stage
        }
