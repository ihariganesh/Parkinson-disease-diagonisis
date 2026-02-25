"""
Longitudinal Auto-Ingestion Hook

Automatically extracts and records biomarker observations
whenever an analysis completes (handwriting, voice, DaT scan).

Import and call `auto_record_from_analysis()` at the end of
each analysis endpoint to feed the longitudinal pipeline.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.services.longitudinal_engine import LongitudinalTrendEngine

logger = logging.getLogger(__name__)


def auto_record_from_analysis(
    db: Session,
    patient_id: str,
    modality: str,
    analysis_result: dict,
    source_report_id: Optional[str] = None,
    source_analysis_id: Optional[str] = None,
) -> int:
    """
    Extract numeric biomarkers from an analysis result dict
    and persist them via the longitudinal engine.

    Args:
        db:               Database session
        patient_id:       User ID of the patient
        modality:         "handwriting" | "voice" | "dat_scan"
        analysis_result:  The raw dict returned by the ML service
        source_report_id: Optional link to DiagnosisReport
        source_analysis_id: Optional link to AnalysisResult

    Returns:
        Number of biomarker observations recorded.
    """
    biomarkers = _extract_biomarkers(modality, analysis_result)

    if not biomarkers:
        logger.debug(
            "No numeric biomarkers extracted from %s analysis for patient %s",
            modality, patient_id,
        )
        return 0

    try:
        engine = LongitudinalTrendEngine(db)
        observations = engine.record_biomarkers(
            patient_id=patient_id,
            modality=modality,
            biomarkers=biomarkers,
            source_report_id=source_report_id,
            source_analysis_id=source_analysis_id,
        )
        logger.info(
            "Auto-recorded %d biomarkers from %s for patient %s",
            len(observations), modality, patient_id,
        )
        return len(observations)
    except Exception as exc:
        logger.error(
            "Failed to auto-record biomarkers: %s", exc, exc_info=True,
        )
        return 0


def _extract_biomarkers(modality: str, result: dict) -> Dict[str, float]:
    """
    Extract numeric biomarker values from a raw analysis result.
    Each modality has its own known keys.
    """
    biomarkers: Dict[str, float] = {}

    if modality == "handwriting":
        _pick(biomarkers, result, [
            "tremor_amplitude",
            "smoothness_index",
            "stroke_speed",
            "pressure_variance",
            "confidence_score",
            "prediction_score",
        ])
        # Also check nested 'analysis_details' or 'features'
        _pick_nested(biomarkers, result, "analysis_details")
        _pick_nested(biomarkers, result, "features")

    elif modality == "voice":
        _pick(biomarkers, result, [
            "jitter",
            "shimmer",
            "hnr",
            "mfcc_mean",
            "f0_mean",
            "f0_std",
            "confidence",
            "prediction_score",
        ])
        _pick_nested(biomarkers, result, "features")
        _pick_nested(biomarkers, result, "analysis_details")

    elif modality == "dat_scan":
        _pick(biomarkers, result, [
            "dopamine_density",
            "sbr_left",
            "sbr_right",
            "asymmetry_index",
            "confidence",
            "prediction_score",
            "classification_confidence",
        ])
        _pick_nested(biomarkers, result, "features")
        _pick_nested(biomarkers, result, "analysis_details")

    else:
        # Generic: grab any numeric top-level keys
        for k, v in result.items():
            if isinstance(v, (int, float)) and not k.startswith("_"):
                biomarkers[k] = float(v)

    return biomarkers


def _pick(target: dict, source: dict, keys: list) -> None:
    """Copy numeric values from source to target for known keys."""
    for k in keys:
        v = source.get(k)
        if isinstance(v, (int, float)):
            target[k] = float(v)


def _pick_nested(target: dict, source: dict, nested_key: str) -> None:
    """If source[nested_key] is a dict, pick numeric values from it."""
    nested = source.get(nested_key)
    if isinstance(nested, dict):
        for k, v in nested.items():
            if isinstance(v, (int, float)) and k not in target:
                target[k] = float(v)
