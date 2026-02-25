"""
Longitudinal Neuro-Motor Modeling - Database Models

Time-series storage for biomarker observations, enabling:
- Rate of change (neuro-motor velocity)
- Cross-modality consistency
- Trend acceleration detection
- Disease progression tracking
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Float,
    Boolean, JSON, ForeignKey, Enum, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.models import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BiomarkerModality(enum.Enum):
    """Source modality for a biomarker reading."""
    HANDWRITING = "handwriting"
    VOICE = "voice"
    DAT_SCAN = "dat_scan"
    COMPOSITE = "composite"


class ProgressionCategory(enum.Enum):
    """Overall risk-evolution classification."""
    STABLE = "stable"
    EMERGING_RISK = "emerging_risk"
    PROGRESSIVE_RISK = "progressive_risk"
    RAPID_PROGRESSION = "rapid_progression"


class TrendDirection(enum.Enum):
    """Direction of a biomarker trend."""
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"


# ---------------------------------------------------------------------------
# Core time-series table – one row per biomarker per observation
# ---------------------------------------------------------------------------

class BiomarkerObservation(Base):
    """
    Individual biomarker measurement at a point in time.

    Schema:
        patient_id | modality | biomarker_name | value | recorded_at

    Examples of biomarker_name per modality:
        handwriting  → tremor_amplitude, smoothness_index, stroke_speed, pressure_variance
        voice        → jitter, shimmer, hnr, mfcc_mean, f0_std
        dat_scan     → dopamine_density, sbr_left, sbr_right, asymmetry_index
        composite    → fusion_score, overall_confidence
    """
    __tablename__ = "biomarker_observations"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    modality = Column(Enum(BiomarkerModality), nullable=False)
    biomarker_name = Column(String(128), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=True)           # e.g. "Hz", "dB", "%"
    
    # Link back to the analysis that produced this reading
    source_report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=True)
    source_analysis_id = Column(String, ForeignKey("analysis_results.id"), nullable=True)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    observation_metadata = Column(JSON, nullable=True)  # extra context (device, session info…)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    source_report = relationship("DiagnosisReport", foreign_keys=[source_report_id])

    __table_args__ = (
        Index("ix_bio_patient_marker_time", "patient_id", "biomarker_name", "recorded_at"),
        Index("ix_bio_patient_modality", "patient_id", "modality"),
    )


# ---------------------------------------------------------------------------
# Computed trend snapshots – stored after each trend analysis run
# ---------------------------------------------------------------------------

class BiomarkerTrend(Base):
    """
    Computed trend for a single biomarker over a time window.
    Stores slope (rate of change), acceleration, and statistical quality metrics.
    """
    __tablename__ = "biomarker_trends"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    modality = Column(Enum(BiomarkerModality), nullable=False)
    biomarker_name = Column(String(128), nullable=False)

    # --- Trend mathematics ---
    slope = Column(Float, nullable=False)                # rate of change per month
    slope_normalised = Column(Float, nullable=True)      # slope / baseline value
    acceleration = Column(Float, nullable=True)          # change in slope between windows
    r_squared = Column(Float, nullable=True)             # goodness-of-fit of linear model
    p_value = Column(Float, nullable=True)               # statistical significance

    direction = Column(Enum(TrendDirection), nullable=False)
    
    # --- Window metadata ---
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    observation_count = Column(Integer, nullable=False)  # data-points in window
    baseline_value = Column(Float, nullable=True)        # earliest value in window
    latest_value = Column(Float, nullable=True)          # most recent value in window

    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])

    __table_args__ = (
        Index("ix_trend_patient_marker", "patient_id", "biomarker_name"),
    )


# ---------------------------------------------------------------------------
# Cross-modality consistency snapshot
# ---------------------------------------------------------------------------

class CrossModalitySnapshot(Base):
    """
    Measures how well multiple modalities agree at a point in time.
    Agreement across handwriting, voice, and DaT reinforces confidence.
    """
    __tablename__ = "cross_modality_snapshots"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # --- Agreement metrics ---
    agreement_score = Column(Float, nullable=False)            # 0-1, 1 = perfect agreement
    directional_consistency = Column(Float, nullable=False)    # fraction of modalities trending same way
    pairwise_correlations = Column(JSON, nullable=True)        # e.g. {"voice_handwriting": 0.85, …}

    modalities_included = Column(JSON, nullable=False)         # ["handwriting", "voice", "dat_scan"]
    modality_directions = Column(JSON, nullable=False)         # {"handwriting": "worsening", …}
    modality_slopes = Column(JSON, nullable=True)              # raw slope values per modality

    # --- Window ---
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)

    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])


# ---------------------------------------------------------------------------
# Risk evolution assessment – the "Progression Engine" output
# ---------------------------------------------------------------------------

class RiskEvolutionAssessment(Base):
    """
    Final longitudinal risk assessment combining:
    - current probability
    - rate of change
    - cross-modality consistency
    - acceleration
    """
    __tablename__ = "risk_evolution_assessments"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # --- Core output ---
    progression_category = Column(Enum(ProgressionCategory), nullable=False)
    risk_score = Column(Float, nullable=False)                  # 0-1 composite risk
    risk_delta = Column(Float, nullable=True)                   # change since last assessment
    confidence = Column(Float, nullable=False)                  # how much data supports this

    # --- Components that fed the assessment ---
    current_probability = Column(Float, nullable=True)          # latest static model output
    avg_slope = Column(Float, nullable=True)                    # mean biomarker slope
    avg_acceleration = Column(Float, nullable=True)             # mean biomarker acceleration
    cross_modality_agreement = Column(Float, nullable=True)     # from CrossModalitySnapshot
    months_of_data = Column(Float, nullable=True)               # observation span

    # --- Clinical narrative ---
    clinical_summary = Column(Text, nullable=True)              # human-readable paragraph
    key_findings = Column(JSON, nullable=True)                  # list of bullet findings
    recommendations = Column(JSON, nullable=True)               # suggested next steps

    # --- Trend details embedded ---
    trend_details = Column(JSON, nullable=True)                 # per-biomarker slopes & accelerations
    
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])

    __table_args__ = (
        Index("ix_risk_patient_time", "patient_id", "computed_at"),
    )
