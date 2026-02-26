"""
Multi-Modal Parkinson's Disease Analysis Service
Combines DaT scan, handwriting, and voice analysis for comprehensive diagnosis.

Weights:
  DaT Scan  = 50 %
  Handwriting/Wave Image = 25 %
  Voice     = 25 %

Each modality is optional; the fusion engine re-normalises weights across
whichever modalities are actually provided.
"""

import logging
import os
import sys
import tempfile
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

# ─── Service imports ─────────────────────────────────────────────────────────

from app.services.dat_service_direct import DaTScanAnalysisServiceDirect
from app.services.handwriting_service import HandwritingService

# Speech service: prefer the enhanced v2 pipeline used by analysis.py
_ml_models_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../ml-models")
)

def _load_speech_service():
    """Load the best available speech analysis service."""
    v2_path = os.path.join(_ml_models_path, "speech_analysis_service_v2.py")
    v1_path = os.path.join(_ml_models_path, "speech_analysis_service.py")

    for service_path, attr_name, init_kwarg in [
        (v2_path, "SpeechAnalysisServiceV2", "models_dir"),
        (v1_path, "SpeechAnalysisService",   "models_dir"),
    ]:
        if os.path.exists(service_path):
            try:
                spec = importlib.util.spec_from_file_location("_svc", service_path)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls  = getattr(mod, attr_name, None)
                if cls:
                    svc = cls(**{init_kwarg: os.path.join(_ml_models_path, "models/speech")})
                    logger.info("✓ Multimodal: loaded speech service from %s", service_path)
                    return svc
            except Exception as e:
                logger.warning("Could not load speech service %s: %s", service_path, e)

    # Fallback: use SpeechService wrapper
    try:
        from app.services.speech_service import SpeechService
        svc = SpeechService()
        logger.info("✓ Multimodal: using fallback SpeechService")
        return svc
    except Exception as e:
        logger.warning("SpeechService fallback also failed: %s", e)
        return None


# ─── Main service class ───────────────────────────────────────────────────────

class MultiModalAnalysisService:
    """
    Multi-modal Parkinson's disease analysis service.
    Combines DaT scan, handwriting image, and voice analysis using
    configurable weights (50 / 25 / 25 by default).
    """

    WEIGHTS = {
        "dat":         0.50,   # 50 % — most reliable indicator
        "handwriting": 0.25,   # 25 % — motor / drawing symptoms
        "voice":       0.25,   # 25 % — speech characteristics
    }

    DIAGNOSIS_THRESHOLD        = 0.50
    HIGH_CONFIDENCE_THRESHOLD  = 0.80
    MOD_CONFIDENCE_THRESHOLD   = 0.60

    def __init__(self):
        logger.info("Initialising MultiModalAnalysisService …")
        self.dat_service         = DaTScanAnalysisServiceDirect()
        self.handwriting_service = HandwritingService()
        self.speech_service      = _load_speech_service()

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze_comprehensive(
        self,
        dat_scans:           Optional[List[Path]] = None,
        handwriting_spiral:  Optional[Path]       = None,
        handwriting_wave:    Optional[Path]       = None,
        voice_file:          Optional[Path]       = None,
        patient_id:          Optional[str]        = None,
    ) -> Dict:
        """
        Run per-modality analysis then fuse results with weighted averaging.

        Each modality is independent — a failure in one does NOT abort the others.
        Weights are re-normalised over the modalities that actually produced a score.
        """
        logger.info("=" * 70)
        logger.info("MULTI-MODAL PARKINSON'S ANALYSIS — patient=%s", patient_id)
        logger.info("Inputs  dat=%s  spiral=%s  wave=%s  voice=%s",
                    bool(dat_scans), bool(handwriting_spiral),
                    bool(handwriting_wave), bool(voice_file))

        results = {
            "timestamp":             datetime.now().isoformat(),
            "patient_id":            patient_id,
            "modalities_analyzed":   [],
            "modality_results":      {},
            "fusion_results":        {},
            "clinical_interpretation": "",
            "recommendations":       [],
        }

        modality_pd_probs  = {}   # {modality: pd_probability 0-1}
        modality_conf      = {}   # {modality: confidence 0-1}

        # ── 1. DaT Scan ───────────────────────────────────────────────────────
        dat_score = self._analyze_dat_scan(dat_scans, results)
        if dat_score is not None:
            modality_pd_probs["dat"] = dat_score["pd_prob"]
            modality_conf["dat"]     = dat_score["conf"]
            results["modalities_analyzed"].append("dat")
            logger.info("[DaT used] PD-prob=%.3f  conf=%.3f",
                        dat_score["pd_prob"], dat_score["conf"])

        # ── 2. Handwriting / Wave Image ───────────────────────────────────────
        img_score = self._analyze_wave_image(
            handwriting_spiral, handwriting_wave, results
        )
        if img_score is not None:
            modality_pd_probs["handwriting"] = img_score["pd_prob"]
            modality_conf["handwriting"]     = img_score["conf"]
            results["modalities_analyzed"].append("handwriting")
            logger.info("[Image used] PD-prob=%.3f  conf=%.3f",
                        img_score["pd_prob"], img_score["conf"])

        # ── 3. Voice ──────────────────────────────────────────────────────────
        voice_score = self._analyze_voice(voice_file, results)
        if voice_score is not None:
            modality_pd_probs["voice"] = voice_score["pd_prob"]
            modality_conf["voice"]     = voice_score["conf"]
            results["modalities_analyzed"].append("voice")
            logger.info("[Voice used] PD-prob=%.3f  conf=%.3f",
                        voice_score["pd_prob"], voice_score["conf"])

        # ── 4. Fusion ─────────────────────────────────────────────────────────
        if not modality_pd_probs:
            results["fusion_results"] = {
                "error": "No modality produced a usable result."
            }
            return results

        fusion = self._fuse(modality_pd_probs, modality_conf)
        results["fusion_results"] = fusion
        logger.info("FINAL weighted score=%.3f  diagnosis=%s",
                    fusion["final_probability"], fusion["final_diagnosis"])

        # ── 5. Clinical text ──────────────────────────────────────────────────
        results["clinical_interpretation"] = self._generate_interpretation(
            fusion["final_diagnosis"],
            fusion["final_probability"],
            fusion["confidence_level"],
            fusion["agreement_score"],
            results["modalities_analyzed"],
            modality_pd_probs,
        )
        results["recommendations"] = self._generate_recommendations(
            fusion["final_diagnosis"],
            fusion["confidence_level"],
            results["modalities_analyzed"],
        )

        logger.info("=" * 70)
        return results

    # ── Private: per-modality runners ─────────────────────────────────────────

    def _analyze_dat_scan(
        self,
        dat_scans: Optional[List[Path]],
        results:   Dict,
    ) -> Optional[Dict]:
        """
        Run DaT scan analysis.
        Returns {"pd_prob": float, "conf": float} on success, None on skip/error.
        """
        if not dat_scans:
            logger.info("[DaT] No DaT scan files provided — skipped.")
            return None

        logger.info("[DaT] Analysing %d scan slice(s) …", len(dat_scans))
        try:
            with tempfile.TemporaryDirectory() as tmp:
                import shutil
                tmp_dir = Path(tmp)
                for i, src in enumerate(dat_scans):
                    shutil.copy(src, tmp_dir / f"scan_{i:03d}.png")

                dat_result = self.dat_service.predict(str(tmp_dir))

            results["modality_results"]["dat"] = dat_result

            if not dat_result.get("success"):
                err = dat_result.get("error", "Unknown DaT error")
                logger.warning("[DaT] Analysis returned failure: %s", err)
                results["modality_results"]["dat"] = {"error": err}
                return None

            # Extract PD probability ─ handle both result shapes
            if "probabilities" in dat_result:
                pd_prob = float(dat_result["probabilities"].get("Parkinson", 0.5))
            elif "probability_parkinson" in dat_result:
                pd_prob = float(dat_result["probability_parkinson"])
            elif "probability" in dat_result:
                pd_prob = float(dat_result["probability"])
            else:
                pd_prob = 0.5

            conf = float(dat_result.get("confidence", 0.5))
            # Normalise the modality_results entry so the response schema is consistent
            results["modality_results"]["dat"].update({
                "pd_probability": pd_prob,
                "confidence": conf,
                "probability": pd_prob,
            })
            return {"pd_prob": pd_prob, "conf": conf}

        except Exception as e:
            logger.error("[DaT] Exception: %s", e, exc_info=True)
            results["modality_results"]["dat"] = {"error": str(e)}
            return None

    def _analyze_wave_image(
        self,
        spiral_path: Optional[Path],
        wave_path:   Optional[Path],
        results:     Dict,
    ) -> Optional[Dict]:
        """
        Run handwriting / wave-image analysis for spiral and/or wave files.
        Returns {"pd_prob": float, "conf": float} on success, None on skip/error.
        """
        if not spiral_path and not wave_path:
            logger.info("[Image] No handwriting/wave files provided — skipped.")
            return None

        logger.info("[Image] Analysing handwriting (spiral=%s  wave=%s) …",
                    bool(spiral_path), bool(wave_path))
        try:
            probs = []
            confs = []

            if spiral_path:
                r = self.handwriting_service.analyze_spiral(str(spiral_path))
                if r.get("success") or "pd_probability" in r or "probability" in r:
                    p = float(r.get("pd_probability", r.get("probability", 0.5)))
                    c = float(r.get("confidence", 0.5))
                    probs.append(p)
                    confs.append(c)
                    logger.info("  spiral → pd_prob=%.3f  conf=%.3f", p, c)
                else:
                    logger.warning("  spiral analysis failed: %s", r.get("error"))

            if wave_path:
                r = self.handwriting_service.analyze_wave(str(wave_path))
                if r.get("success") or "pd_probability" in r or "probability" in r:
                    p = float(r.get("pd_probability", r.get("probability", 0.5)))
                    c = float(r.get("confidence", 0.5))
                    probs.append(p)
                    confs.append(c)
                    logger.info("  wave   → pd_prob=%.3f  conf=%.3f", p, c)
                else:
                    logger.warning("  wave analysis failed: %s", r.get("error"))

            if not probs:
                results["modality_results"]["handwriting"] = {
                    "error": "Both spiral and wave analysis returned no result."
                }
                return None

            pd_prob = float(np.mean(probs))
            conf    = float(np.mean(confs))

            results["modality_results"]["handwriting"] = {
                "prediction":    "Parkinson's Disease" if pd_prob > 0.5 else "Healthy",
                "probability":   pd_prob,
                "pd_probability":pd_prob,
                "confidence":    conf,
                "files_analyzed":len(probs),
            }
            return {"pd_prob": pd_prob, "conf": conf}

        except Exception as e:
            logger.error("[Image] Exception: %s", e, exc_info=True)
            results["modality_results"]["handwriting"] = {"error": str(e)}
            return None

    def _analyze_voice(
        self,
        voice_file: Optional[Path],
        results:    Dict,
    ) -> Optional[Dict]:
        """
        Run voice / speech analysis.
        Returns {"pd_prob": float, "conf": float} on success, None on skip/error.
        """
        if not voice_file:
            logger.info("[Voice] No voice file provided — skipped.")
            return None

        logger.info("[Voice] Analysing voice recording: %s …", voice_file.name)

        if self.speech_service is None:
            logger.warning("[Voice] Speech service not available.")
            results["modality_results"]["voice"] = {
                "error": "Speech analysis service not available."
            }
            return None

        try:
            # ── Enhanced service (v2): has analyze_audio_from_bytes ──
            if hasattr(self.speech_service, "analyze_audio_from_bytes"):
                audio_bytes = voice_file.read_bytes()
                voice_result = self.speech_service.analyze_audio_from_bytes(
                    audio_bytes, voice_file.name
                )
            # ── Wrapper SpeechService ──
            elif hasattr(self.speech_service, "predict"):
                voice_result = self.speech_service.predict(str(voice_file))
            elif hasattr(self.speech_service, "analyze_voice"):
                voice_result = self.speech_service.analyze_voice(str(voice_file))
            else:
                raise RuntimeError("Speech service has no recognised analysis method.")

            if voice_result is None:
                raise RuntimeError("Speech service returned None.")

            # Normalise the result dict
            # Support: analysis_result nested dict (full service) or flat dict (SpeechService)
            inner = voice_result.get("analysis_result", voice_result)

            pd_prob = float(
                inner.get("probability_parkinson",
                inner.get("pd_probability",
                inner.get("probability", 0.5)))
            )
            conf = float(inner.get("confidence", 0.5))

            results["modality_results"]["voice"] = {
                "prediction":          inner.get("prediction", "Healthy" if pd_prob < 0.5 else "Parkinson's Disease"),
                "probability":         pd_prob,
                "pd_probability":      pd_prob,
                "probability_parkinson": pd_prob,
                "probability_healthy": float(1.0 - pd_prob),
                "confidence":          conf,
                "risk_level":          inner.get("risk_level", "Unknown"),
            }
            return {"pd_prob": pd_prob, "conf": conf}

        except Exception as e:
            logger.error("[Voice] Exception: %s", e, exc_info=True)
            results["modality_results"]["voice"] = {"error": str(e)}
            return None

    # ── Fusion engine ─────────────────────────────────────────────────────────

    def _fuse(
        self,
        pd_probs: Dict[str, float],
        confs:    Dict[str, float],
    ) -> Dict:
        """
        Weighted average of PD probabilities.
        Weights are taken from WEIGHTS and re-normalised to the available modalities.
        Log output uses the original configured weights for transparency.
        """
        available = list(pd_probs.keys())

        raw_weights   = {m: self.WEIGHTS.get(m, 0.0) for m in available}
        total_weight  = sum(raw_weights.values()) or 1.0
        norm_weights  = {m: w / total_weight for m, w in raw_weights.items()}

        weighted_sum = sum(pd_probs[m] * norm_weights[m] for m in available)
        final_probability = float(np.clip(weighted_sum, 0.0, 1.0))

        # Conservative confidence: minimum across active modalities
        final_confidence = float(min(confs.values()))

        final_diagnosis = (
            "Parkinson's Disease"
            if final_probability > self.DIAGNOSIS_THRESHOLD
            else "Healthy"
        )

        # Agreement score (1 = all agree, 0 = maximum disagreement)
        if len(available) > 1:
            std_dev = float(np.std(list(pd_probs.values())))
            agreement_score = float(np.clip(1.0 - std_dev / 0.5, 0.0, 1.0))
        else:
            agreement_score = 1.0

        if final_confidence > self.HIGH_CONFIDENCE_THRESHOLD and agreement_score > 0.85:
            confidence_level = "High"
        elif final_confidence > self.MOD_CONFIDENCE_THRESHOLD:
            confidence_level = "Moderate"
        else:
            confidence_level = "Low"

        logger.info("Fusion  modalities=%s  weights(norm)=%s",
                    available, {m: f"{norm_weights[m]:.2f}" for m in available})
        logger.info("        final_probability=%.4f  final_diagnosis=%s",
                    final_probability, final_diagnosis)

        return {
            "final_diagnosis":   final_diagnosis,
            "final_probability": final_probability,
            "confidence":        final_confidence,
            "confidence_level":  confidence_level,
            "agreement_score":   agreement_score,
            "modalities_used":   available,
            "weights_applied":   {m: round(norm_weights[m], 4) for m in available},
            "raw_weights":       {m: self.WEIGHTS.get(m, 0.0) for m in available},
        }

    # ── Clinical text generators ──────────────────────────────────────────────

    def _generate_interpretation(
        self,
        diagnosis:        str,
        probability:      float,
        confidence_level: str,
        agreement_score:  float,
        modalities:       List[str],
        predictions:      Dict[str, float],
    ) -> str:
        parts = [
            f"Multi-modal analysis using {len(modalities)} modality(ies) "
            f"({', '.join(modalities)}) "
        ]

        if diagnosis == "Parkinson's Disease":
            parts.append(
                f"indicates Parkinson's disease with {probability * 100:.1f}% probability. "
            )
        else:
            parts.append(
                f"suggests healthy status with {(1 - probability) * 100:.1f}% confidence. "
            )

        if len(modalities) > 1:
            if agreement_score > 0.85:
                parts.append("All modalities show strong agreement. ")
            elif agreement_score > 0.70:
                parts.append("Modalities show moderate agreement. ")
            else:
                parts.append(
                    "Modalities show some disagreement — additional evaluation is recommended. "
                )

        level_text = {
            "High":     "The analysis shows high confidence in the diagnosis. ",
            "Moderate": "The analysis shows moderate confidence. Additional clinical evaluation is recommended. ",
            "Low":      "The analysis shows low confidence. Clinical confirmation is strongly recommended. ",
        }
        parts.append(level_text.get(confidence_level, ""))

        if "dat" in modalities:
            p = predictions["dat"]
            if p > 0.7:
                parts.append(
                    "DaT scan shows reduced dopamine transporter binding consistent with PD. "
                )
            elif p < 0.3:
                parts.append("DaT scan shows normal dopamine transporter binding. ")

        if "handwriting" in modalities:
            p = predictions["handwriting"]
            if p > 0.7:
                parts.append(
                    "Handwriting analysis reveals motor control difficulties typical of PD. "
                )
            elif p < 0.3:
                parts.append("Handwriting analysis shows normal motor control. ")

        if "voice" in modalities:
            p = predictions["voice"]
            if p > 0.7:
                parts.append(
                    "Voice analysis detects speech characteristics associated with PD. "
                )
            elif p < 0.3:
                parts.append("Voice analysis shows normal speech characteristics. ")

        return "".join(parts)

    def _generate_recommendations(
        self,
        diagnosis:        str,
        confidence_level: str,
        modalities:       List[str],
    ) -> List[str]:
        recs = [
            "Consult with a qualified neurologist for clinical confirmation and diagnosis."
        ]

        if diagnosis == "Parkinson's Disease":
            recs.append(
                "Consider comprehensive neurological examination including motor function assessment."
            )
            if "dat" not in modalities:
                recs.append(
                    "Consider dopamine transporter (DaT) scan imaging for further confirmation."
                )
            recs.append("Monitor for progression of motor and non-motor symptoms.")
            recs.append(
                "Discuss treatment options including medication and lifestyle modifications."
            )
            if confidence_level != "High":
                recs.append(
                    "Consider repeat assessment in 6–12 months to monitor progression."
                )
        else:
            recs.append(
                "Continue regular health monitoring and maintain a healthy lifestyle."
            )
            if confidence_level == "Low":
                recs.append(
                    "Consider repeat screening if symptoms develop or worsen."
                )
            recs.append(
                "Be aware of early Parkinson's symptoms: tremor, rigidity, bradykinesia, postural instability."
            )

        missing = [m for m in ("dat", "handwriting", "voice") if m not in modalities]
        if missing:
            names = {"dat": "DaT scan imaging", "handwriting": "handwriting analysis",
                     "voice": "voice analysis"}
            recs.append(
                f"For a more comprehensive assessment, consider adding: "
                f"{', '.join(names[m] for m in missing)}."
            )

        return recs


# ─── Singleton ────────────────────────────────────────────────────────────────

_multimodal_service: Optional[MultiModalAnalysisService] = None


def get_multimodal_service() -> MultiModalAnalysisService:
    """Return the shared MultiModalAnalysisService singleton."""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultiModalAnalysisService()
    return _multimodal_service
