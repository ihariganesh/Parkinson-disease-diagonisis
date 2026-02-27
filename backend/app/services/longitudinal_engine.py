"""
Longitudinal Neuro-Motor Modeling – Trend Engine

Core computation layer that transforms raw biomarker time-series into:
  1. Rate of Change  (neuro-motor velocity)
  2. Cross-Modality Consistency  (directional agreement)
  3. Trend Acceleration  (change in slope)
  4. Risk Evolution Assessment  (progression classification)

Mathematical foundation:
  - Linear regression for slope estimation
  - Exponential smoothing for noise reduction
  - Change-point heuristics for acceleration
  - Weighted fusion for cross-modality agreement
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, func as sa_func

from app.db.longitudinal_models import (
    BiomarkerObservation,
    BiomarkerTrend,
    CrossModalitySnapshot,
    RiskEvolutionAssessment,
    BiomarkerModality,
    ProgressionCategory,
    TrendDirection,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Helper: simple OLS regression
# ═══════════════════════════════════════════════════════════════════════════

def _linear_regression(
    x: np.ndarray, y: np.ndarray
) -> Tuple[float, float, float, float]:
    """
    Ordinary Least Squares on 1-D arrays.

    Returns:
        slope, intercept, r_squared, p_value (approximation)
    """
    n = len(x)
    if n < 2:
        return 0.0, float(y[0]) if n == 1 else 0.0, 0.0, 1.0

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_yy = np.sum((y - y_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))

    if ss_xx == 0:
        return 0.0, y_mean, 0.0, 1.0

    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean

    # R²
    ss_res = np.sum((y - (slope * x + intercept)) ** 2)
    r_squared = 1.0 - (ss_res / ss_yy) if ss_yy != 0 else 0.0
    r_squared = max(0.0, min(1.0, r_squared))

    # Approximate p-value via t-statistic
    if n > 2 and ss_res > 0:
        se_slope = np.sqrt(ss_res / (n - 2) / ss_xx)
        t_stat = slope / se_slope if se_slope != 0 else 0.0
        # Simplified: use |t| > 2 ≈ p < 0.05 heuristic
        p_value = max(0.001, 1.0 / (1.0 + abs(t_stat)))
    else:
        p_value = 1.0

    return float(slope), float(intercept), float(r_squared), float(p_value)


def _exponential_smooth(values: np.ndarray, alpha: float = 0.3) -> np.ndarray:
    """Simple exponential smoothing to reduce noise."""
    result = np.zeros_like(values, dtype=float)
    result[0] = values[0]
    for i in range(1, len(values)):
        result[i] = alpha * values[i] + (1 - alpha) * result[i - 1]
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Main Engine
# ═══════════════════════════════════════════════════════════════════════════

class LongitudinalTrendEngine:
    """
    Progression Engine – models disease *evolution*, not just *presence*.

    Usage:
        engine = LongitudinalTrendEngine(db)
        assessment = engine.run_full_assessment(patient_id)
    """

    # Biomarkers where *higher* value means *worse* PD (default).
    # Biomarkers not listed here are assumed "higher = worse".
    HIGHER_IS_BETTER = {
        "smoothness_index",
        "hnr",               # harmonics-to-noise ratio
        "dopamine_density",
        "sbr_left",
        "sbr_right",
        "stroke_speed",
    }

    # Default window in months for trend calculation
    DEFAULT_WINDOW_MONTHS = 6

    def __init__(self, db: Session):
        self.db = db

    # ───────────────────────────────────────────────────────────────────
    # 1. Ingest biomarker from an analysis result
    # ───────────────────────────────────────────────────────────────────

    def record_biomarkers(
        self,
        patient_id: str,
        modality: str,
        biomarkers: Dict[str, float],
        source_report_id: Optional[str] = None,
        source_analysis_id: Optional[str] = None,
        recorded_at: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> List[BiomarkerObservation]:
        """
        Persist a batch of biomarker readings from one analysis session.

        Args:
            patient_id:  User ID of the patient
            modality:    "handwriting" | "voice" | "dat_scan" | "composite"
            biomarkers:  {"tremor_amplitude": 0.34, "smoothness_index": 0.78, …}
        """
        mod = BiomarkerModality(modality)
        ts = recorded_at or datetime.now(timezone.utc)
        observations: List[BiomarkerObservation] = []

        for name, value in biomarkers.items():
            obs = BiomarkerObservation(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                modality=mod,
                biomarker_name=name,
                value=float(value),
                source_report_id=source_report_id,
                source_analysis_id=source_analysis_id,
                recorded_at=ts,
                observation_metadata=metadata,
            )
            self.db.add(obs)
            observations.append(obs)

        self.db.commit()
        logger.info(
            "Recorded %d biomarkers for patient %s [%s]",
            len(observations), patient_id, modality,
        )
        return observations

    # ───────────────────────────────────────────────────────────────────
    # 2. Compute trends (slope + acceleration) for each biomarker
    # ───────────────────────────────────────────────────────────────────

    def compute_trends(
        self,
        patient_id: str,
        window_months: int = DEFAULT_WINDOW_MONTHS,
    ) -> List[BiomarkerTrend]:
        """
        For every biomarker that has ≥2 observations within the window,
        compute slope and acceleration and persist a BiomarkerTrend row.
        """
        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(days=window_months * 30)

        # Fetch observations in window
        obs_rows = (
            self.db.query(BiomarkerObservation)
            .filter(
                BiomarkerObservation.patient_id == patient_id,
                BiomarkerObservation.recorded_at >= window_start,
                BiomarkerObservation.recorded_at <= window_end,
            )
            .order_by(BiomarkerObservation.recorded_at)
            .all()
        )

        # Group by (modality, biomarker_name)
        groups: Dict[Tuple[str, str], List[BiomarkerObservation]] = defaultdict(list)
        for obs in obs_rows:
            groups[(obs.modality.value, obs.biomarker_name)].append(obs)

        trends: List[BiomarkerTrend] = []

        # Look up the previous trend for acceleration calculation
        for (mod_str, marker_name), obs_list in groups.items():
            if len(obs_list) < 2:
                continue

            timestamps = np.array([
                (o.recorded_at - obs_list[0].recorded_at).total_seconds() / (30 * 86400)  # months
                for o in obs_list
            ])
            values = np.array([o.value for o in obs_list])

            # Smooth then regress
            smoothed = _exponential_smooth(values) if len(values) > 3 else values
            slope, intercept, r_sq, p_val = _linear_regression(timestamps, smoothed)

            # Determine direction (account for "higher is better" markers)
            higher_is_better = marker_name in self.HIGHER_IS_BETTER
            if abs(slope) < 1e-6:
                direction = TrendDirection.STABLE
            elif (slope > 0) == higher_is_better:
                direction = TrendDirection.IMPROVING
            else:
                direction = TrendDirection.WORSENING

            # Acceleration: compare slope to previous trend's slope
            prev_trend = (
                self.db.query(BiomarkerTrend)
                .filter(
                    BiomarkerTrend.patient_id == patient_id,
                    BiomarkerTrend.biomarker_name == marker_name,
                )
                .order_by(BiomarkerTrend.computed_at.desc())
                .first()
            )
            acceleration = (slope - prev_trend.slope) if prev_trend else None

            # Normalised slope (% change relative to baseline)
            baseline = float(obs_list[0].value) if obs_list[0].value != 0 else 1.0
            slope_norm = slope / abs(baseline)

            trend = BiomarkerTrend(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                modality=BiomarkerModality(mod_str),
                biomarker_name=marker_name,
                slope=slope,
                slope_normalised=slope_norm,
                acceleration=acceleration,
                r_squared=r_sq,
                p_value=p_val,
                direction=direction,
                window_start=window_start,
                window_end=window_end,
                observation_count=len(obs_list),
                baseline_value=float(obs_list[0].value),
                latest_value=float(obs_list[-1].value),
            )
            self.db.add(trend)
            trends.append(trend)

        self.db.commit()
        logger.info(
            "Computed %d trends for patient %s (window=%d months)",
            len(trends), patient_id, window_months,
        )
        return trends

    # ───────────────────────────────────────────────────────────────────
    # 3. Cross-Modality Consistency
    # ───────────────────────────────────────────────────────────────────

    def compute_cross_modality(
        self, patient_id: str, trends: Optional[List[BiomarkerTrend]] = None
    ) -> Optional[CrossModalitySnapshot]:
        """
        Measures whether handwriting, voice, and DaT trends all point
        in the same direction.  High consistency = stronger evidence.
        """
        if trends is None:
            # Use latest trends
            trends = (
                self.db.query(BiomarkerTrend)
                .filter(BiomarkerTrend.patient_id == patient_id)
                .order_by(BiomarkerTrend.computed_at.desc())
                .all()
            )

        if not trends:
            return None

        # Group trends by modality and pick representative direction
        modality_data: Dict[str, Dict] = {}
        for t in trends:
            mod = t.modality.value
            if mod not in modality_data:
                modality_data[mod] = {
                    "directions": [],
                    "slopes": [],
                    "weights": [],
                }
            modality_data[mod]["directions"].append(t.direction.value)
            modality_data[mod]["slopes"].append(t.slope_normalised or t.slope)
            modality_data[mod]["weights"].append(t.r_squared or 0.5)

        if len(modality_data) < 2:
            return None  # need ≥2 modalities for cross-modal analysis

        # Determine dominant direction per modality
        modality_dirs: Dict[str, str] = {}
        modality_slopes_agg: Dict[str, float] = {}
        for mod, data in modality_data.items():
            # Weighted vote
            dir_scores = {"worsening": 0.0, "stable": 0.0, "improving": 0.0}
            for d, w in zip(data["directions"], data["weights"]):
                dir_scores[d] += w
            modality_dirs[mod] = max(dir_scores, key=dir_scores.get)
            modality_slopes_agg[mod] = float(np.mean(data["slopes"]))

        # Directional consistency = fraction of modalities sharing the majority direction
        all_dirs = list(modality_dirs.values())
        from collections import Counter
        dir_counts = Counter(all_dirs)
        most_common_dir, most_common_count = dir_counts.most_common(1)[0]
        directional_consistency = most_common_count / len(all_dirs)

        # Pairwise correlation of slopes
        modalities_list = list(modality_slopes_agg.keys())
        pairwise: Dict[str, float] = {}
        for i in range(len(modalities_list)):
            for j in range(i + 1, len(modalities_list)):
                m1, m2 = modalities_list[i], modalities_list[j]
                # Both moving in same direction → positive correlation proxy
                s1, s2 = modality_slopes_agg[m1], modality_slopes_agg[m2]
                # Sign agreement → 1, disagreement → -1, one zero → 0
                if s1 * s2 > 0:
                    corr = 1.0
                elif s1 * s2 < 0:
                    corr = -1.0
                else:
                    corr = 0.0
                pairwise[f"{m1}_{m2}"] = corr

        # Agreement score: weighted blend of directional consistency and correlations
        avg_corr = float(np.mean(list(pairwise.values()))) if pairwise else 0.0
        agreement_score = 0.6 * directional_consistency + 0.4 * ((avg_corr + 1) / 2)
        agreement_score = max(0.0, min(1.0, agreement_score))

        # Determine window from trends
        window_start = min(t.window_start for t in trends)
        window_end = max(t.window_end for t in trends)

        snapshot = CrossModalitySnapshot(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            agreement_score=agreement_score,
            directional_consistency=directional_consistency,
            pairwise_correlations=pairwise,
            modalities_included=list(modality_data.keys()),
            modality_directions=modality_dirs,
            modality_slopes=modality_slopes_agg,
            window_start=window_start,
            window_end=window_end,
        )
        self.db.add(snapshot)
        self.db.commit()
        logger.info(
            "Cross-modality snapshot for patient %s: agreement=%.2f, consistency=%.2f",
            patient_id, agreement_score, directional_consistency,
        )
        return snapshot

    # ───────────────────────────────────────────────────────────────────
    # 4. Risk Evolution Assessment (the Progression Engine)
    # ───────────────────────────────────────────────────────────────────

    def compute_risk_evolution(
        self,
        patient_id: str,
        trends: Optional[List[BiomarkerTrend]] = None,
        cross_modality: Optional[CrossModalitySnapshot] = None,
        current_probability: Optional[float] = None,
    ) -> RiskEvolutionAssessment:
        """
        Final composite assessment: Stable / Emerging / Progressive / Rapid.

        Combines:
          - Current static probability (from latest diagnosis report)
          - Mean normalised slope (velocity)
          - Mean acceleration
          - Cross-modality agreement
        """
        if trends is None:
            trends = (
                self.db.query(BiomarkerTrend)
                .filter(BiomarkerTrend.patient_id == patient_id)
                .order_by(BiomarkerTrend.computed_at.desc())
                .all()
            )

        # Gather slope & acceleration arrays
        slopes = [t.slope_normalised or t.slope for t in trends if t.direction != TrendDirection.STABLE]
        accelerations = [t.acceleration for t in trends if t.acceleration is not None]

        avg_slope = float(np.mean(slopes)) if slopes else 0.0
        avg_accel = float(np.mean(accelerations)) if accelerations else 0.0

        # Cross-modality
        cm_agreement = cross_modality.agreement_score if cross_modality else 0.5

        # Observation span
        if trends:
            earliest = min(t.window_start for t in trends)
            # Ensure both datetimes are timezone-aware for comparison
            now = datetime.now(timezone.utc)
            if earliest.tzinfo is None:
                from datetime import timezone as _tz
                earliest = earliest.replace(tzinfo=_tz.utc)
            months_of_data = (now - earliest).days / 30.0
        else:
            months_of_data = 0.0

        # ── Weighted risk scoring ──
        # Components (all normalised 0-1)
        prob_component = current_probability if current_probability is not None else 0.5
        slope_component = min(1.0, max(0.0, (avg_slope + 0.5)))  # shift to 0-1
        accel_component = min(1.0, max(0.0, (avg_accel + 0.3) / 0.6))
        agreement_component = cm_agreement

        # Confidence is higher with more data and more modalities
        data_factor = min(1.0, months_of_data / 6.0)
        modality_factor = min(1.0, len(set(t.modality.value for t in trends)) / 3.0) if trends else 0.0
        confidence = 0.5 * data_factor + 0.5 * modality_factor

        # Composite risk (weighted sum)
        risk_score = (
            0.30 * prob_component
            + 0.30 * slope_component
            + 0.20 * accel_component
            + 0.20 * agreement_component
        )
        risk_score = max(0.0, min(1.0, risk_score))

        # ── Classification ──
        worsening_count = sum(
            1 for t in trends if t.direction == TrendDirection.WORSENING
        )
        worsening_frac = worsening_count / len(trends) if trends else 0.0

        has_accel = avg_accel > 0.05
        high_agreement = cm_agreement > 0.7

        if risk_score < 0.3 and worsening_frac < 0.3:
            category = ProgressionCategory.STABLE
        elif risk_score < 0.5 or (worsening_frac < 0.5 and not has_accel):
            category = ProgressionCategory.EMERGING_RISK
        elif has_accel and high_agreement:
            category = ProgressionCategory.RAPID_PROGRESSION
        else:
            category = ProgressionCategory.PROGRESSIVE_RISK

        # ── Previous assessment for delta ──
        prev = (
            self.db.query(RiskEvolutionAssessment)
            .filter(RiskEvolutionAssessment.patient_id == patient_id)
            .order_by(RiskEvolutionAssessment.computed_at.desc())
            .first()
        )
        risk_delta = (risk_score - prev.risk_score) if prev else None

        # ── Clinical narrative ──
        findings = self._generate_key_findings(trends, cross_modality, avg_slope, avg_accel)
        summary = self._generate_clinical_summary(
            category, risk_score, avg_slope, avg_accel, cm_agreement, months_of_data,
        )
        recommendations = self._generate_recommendations(category, findings)

        # ── Trend details for storage ──
        trend_details = [
            {
                "biomarker": t.biomarker_name,
                "modality": t.modality.value,
                "slope": t.slope,
                "slope_normalised": t.slope_normalised,
                "acceleration": t.acceleration,
                "direction": t.direction.value,
                "r_squared": t.r_squared,
                "observations": t.observation_count,
                "baseline": t.baseline_value,
                "latest": t.latest_value,
            }
            for t in trends
        ]

        assessment = RiskEvolutionAssessment(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            progression_category=category,
            risk_score=risk_score,
            risk_delta=risk_delta,
            confidence=confidence,
            current_probability=current_probability,
            avg_slope=avg_slope,
            avg_acceleration=avg_accel,
            cross_modality_agreement=cm_agreement,
            months_of_data=months_of_data,
            clinical_summary=summary,
            key_findings=findings,
            recommendations=recommendations,
            trend_details=trend_details,
        )
        self.db.add(assessment)
        self.db.commit()

        logger.info(
            "Risk evolution for patient %s: %s (score=%.2f, Δ=%s)",
            patient_id,
            category.value,
            risk_score,
            f"{risk_delta:+.3f}" if risk_delta is not None else "n/a",
        )
        return assessment

    # ───────────────────────────────────────────────────────────────────
    # 5. Full pipeline
    # ───────────────────────────────────────────────────────────────────

    def run_full_assessment(
        self,
        patient_id: str,
        window_months: int = DEFAULT_WINDOW_MONTHS,
        current_probability: Optional[float] = None,
    ) -> Dict:
        """
        Execute the complete longitudinal pipeline:
            observations → trends → cross-modality → risk evolution
        """
        trends = self.compute_trends(patient_id, window_months)
        cross_modality = self.compute_cross_modality(patient_id, trends)
        assessment = self.compute_risk_evolution(
            patient_id, trends, cross_modality, current_probability,
        )
        return {
            "trends": trends,
            "cross_modality": cross_modality,
            "assessment": assessment,
        }

    # ───────────────────────────────────────────────────────────────────
    # 6. Query helpers
    # ───────────────────────────────────────────────────────────────────

    def get_patient_timeline(
        self, patient_id: str, biomarker_name: Optional[str] = None
    ) -> List[Dict]:
        """Return raw time-series for charting."""
        q = (
            self.db.query(BiomarkerObservation)
            .filter(BiomarkerObservation.patient_id == patient_id)
        )
        if biomarker_name:
            q = q.filter(BiomarkerObservation.biomarker_name == biomarker_name)
        rows = q.order_by(BiomarkerObservation.recorded_at).all()
        return [
            {
                "id": r.id,
                "modality": r.modality.value,
                "biomarker": r.biomarker_name,
                "value": r.value,
                "recorded_at": r.recorded_at.isoformat(),
            }
            for r in rows
        ]

    def get_latest_assessment(self, patient_id: str) -> Optional[RiskEvolutionAssessment]:
        """Get the most recent risk evolution assessment."""
        return (
            self.db.query(RiskEvolutionAssessment)
            .filter(RiskEvolutionAssessment.patient_id == patient_id)
            .order_by(RiskEvolutionAssessment.computed_at.desc())
            .first()
        )

    def get_assessment_history(self, patient_id: str, limit: int = 20) -> List[RiskEvolutionAssessment]:
        """Get history of risk evolution assessments."""
        return (
            self.db.query(RiskEvolutionAssessment)
            .filter(RiskEvolutionAssessment.patient_id == patient_id)
            .order_by(RiskEvolutionAssessment.computed_at.desc())
            .limit(limit)
            .all()
        )

    # ───────────────────────────────────────────────────────────────────
    # Private: narrative generators
    # ───────────────────────────────────────────────────────────────────

    @staticmethod
    def _generate_key_findings(
        trends: List[BiomarkerTrend],
        cross_modality: Optional[CrossModalitySnapshot],
        avg_slope: float,
        avg_accel: float,
    ) -> List[str]:
        findings: List[str] = []

        worsening = [t for t in trends if t.direction == TrendDirection.WORSENING]
        improving = [t for t in trends if t.direction == TrendDirection.IMPROVING]
        stable = [t for t in trends if t.direction == TrendDirection.STABLE]

        if worsening:
            names = ", ".join(set(t.biomarker_name for t in worsening))
            findings.append(f"Worsening trend detected in: {names}")

        if improving:
            names = ", ".join(set(t.biomarker_name for t in improving))
            findings.append(f"Improvement observed in: {names}")

        if stable:
            findings.append(f"{len(stable)} biomarker(s) remain stable")

        if avg_accel > 0.05:
            findings.append(
                f"Trend acceleration detected (avg Δslope = {avg_accel:+.4f}/month²) — "
                "rate of deterioration is increasing"
            )
        elif avg_accel < -0.05:
            findings.append(
                "Deceleration observed — rate of change is slowing (positive sign)"
            )

        if cross_modality:
            if cross_modality.agreement_score > 0.8:
                findings.append(
                    f"Strong cross-modality agreement ({cross_modality.agreement_score:.0%}) — "
                    "multiple systems show consistent trends"
                )
            elif cross_modality.agreement_score < 0.4:
                findings.append(
                    "Low cross-modality agreement — trends are inconsistent across "
                    "modalities, suggesting isolated changes"
                )

        return findings

    @staticmethod
    def _generate_clinical_summary(
        category: ProgressionCategory,
        risk_score: float,
        avg_slope: float,
        avg_accel: float,
        agreement: float,
        months: float,
    ) -> str:
        cat_labels = {
            ProgressionCategory.STABLE: "Neurological indicators are stable",
            ProgressionCategory.EMERGING_RISK: "Early signs of emerging neurological change detected",
            ProgressionCategory.PROGRESSIVE_RISK: "Progressive neurological deterioration observed",
            ProgressionCategory.RAPID_PROGRESSION: "Rapid neurological progression detected — accelerated monitoring recommended",
        }
        base = cat_labels.get(category, "Assessment complete")

        parts = [
            base + ".",
            f"Composite risk score: {risk_score:.0%}.",
            f"Average biomarker velocity: {avg_slope:+.4f}/month.",
        ]

        if avg_accel != 0:
            parts.append(f"Trend acceleration: {avg_accel:+.4f}/month².")

        parts.append(f"Cross-modality agreement: {agreement:.0%}.")
        parts.append(f"Assessment based on {months:.1f} months of longitudinal data.")

        return " ".join(parts)

    @staticmethod
    def _generate_recommendations(
        category: ProgressionCategory,
        findings: List[str],
    ) -> List[str]:
        recs: List[str] = []

        if category == ProgressionCategory.STABLE:
            recs.append("Continue routine monitoring schedule")
            recs.append("Maintain current treatment plan")
            recs.append("Next comprehensive assessment recommended in 3-6 months")

        elif category == ProgressionCategory.EMERGING_RISK:
            recs.append("Increase monitoring frequency to monthly assessments")
            recs.append("Consider additional DaT scan to confirm dopaminergic changes")
            recs.append("Discuss symptom awareness with patient")
            recs.append("Next assessment recommended in 1-2 months")

        elif category == ProgressionCategory.PROGRESSIVE_RISK:
            recs.append("Schedule neurologist consultation within 2 weeks")
            recs.append("Increase assessment frequency to bi-weekly")
            recs.append("Evaluate current treatment efficacy")
            recs.append("Consider medication adjustment or initiation")
            recs.append("Begin structured physical therapy programme")

        elif category == ProgressionCategory.RAPID_PROGRESSION:
            recs.append("URGENT: Schedule neurologist consultation within 1 week")
            recs.append("Weekly monitoring recommended")
            recs.append("Review and adjust treatment plan immediately")
            recs.append("Full multimodal re-assessment recommended")
            recs.append("Consider advanced imaging and specialist referral")

        return recs
