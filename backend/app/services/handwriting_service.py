"""
Handwriting Analysis Service
Wrapper for handwriting analyzer to integrate with multi-modal system.

IMPORTANT: The trained SVM models (spiral_svm_model_svm.pkl / wave_svm_model_svm.pkl)
are severely biased — they predict Parkinson's Disease with ~91% probability for
EVERY image regardless of content.

This module now uses a HYBRID approach:
 1. If TensorFlow CNN models exist → use them (most accurate).
 2. If SVM models exist → blend SVM prediction with image-feature heuristics
    so that the result actually varies with image content.
 3. If nothing is available → use pure image-feature heuristics.

Image-feature heuristics extract clinically-meaningful signals:
  • Stroke irregularity / roughness  (tremor indicator)
  • Contour smoothness               (motor control indicator)
  • Pressure variation               (grip stability)
  • Edge density                     (line quality)
"""

import sys
import warnings
from pathlib import Path
import numpy as np
from typing import Dict, Tuple

import logging
logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    tf = None
    TF_AVAILABLE = False
    logger.info("TensorFlow not available — using SVM/heuristic fallback.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available — image analysis disabled.")

try:
    import joblib
    from skimage.feature import hog
    SVM_AVAILABLE = True
except ImportError as e:
    SVM_AVAILABLE = False
    logger.info(f"skimage/joblib not available: {e}")


# ─── SVM bias threshold ───────────────────────────────────────────────────────
# If the SVM always returns a probability ≥ this for class-1, we consider it
# biased and downweight its contribution in the final blend.
_SVM_BIAS_THRESHOLD = 0.85   # above this → SVM is likely biased


class HandwritingService:
    """Handwriting analysis service for Parkinson's disease detection."""

    def __init__(self):
        self.spiral_model  = None   # TF CNN
        self.wave_model    = None   # TF CNN

        self.spiral_svm    = None   # SVM fallback
        self.spiral_scaler = None
        self.wave_svm      = None
        self.wave_scaler   = None

        # Track whether SVM is biased (detected at load time)
        self._spiral_svm_biased = False
        self._wave_svm_biased   = False

        self.image_size_cnn = (224, 224)   # ResNet50 input size
        self.image_size_svm = (128, 128)   # SVM+HOG input size

        self._load_models()

    # ── Model loading ──────────────────────────────────────────────────────────

    def _load_models(self):
        base_dir   = Path(__file__).parent.parent.parent.parent
        models_dir = (
            base_dir / "backend" / "models"
            if (base_dir / "backend" / "models").exists()
            else base_dir / "models"
        )

        # ── TF CNN ────────────────────────────────────────────────────────────
        if TF_AVAILABLE:
            for attr, fname in [("spiral_model", "resnet50_spiral_best.h5"),
                                 ("wave_model",   "resnet50_wave_best.h5")]:
                p = models_dir / fname
                if p.exists():
                    try:
                        setattr(self, attr, tf.keras.models.load_model(str(p)))
                        logger.info("Loaded CNN model: %s", fname)
                    except Exception as e:
                        logger.warning("Could not load %s: %s", fname, e)

        # ── SVM fallback ──────────────────────────────────────────────────────
        if SVM_AVAILABLE and not (self.spiral_model and self.wave_model):
            for svm_attr, scaler_attr, svm_fname, scaler_fname, bias_attr in [
                ("spiral_svm", "spiral_scaler",
                 "spiral_svm_model_svm.pkl", "spiral_svm_model_scaler.pkl",
                 "_spiral_svm_biased"),
                ("wave_svm",   "wave_scaler",
                 "wave_svm_model_svm.pkl",   "wave_svm_model_scaler.pkl",
                 "_wave_svm_biased"),
            ]:
                svm_path = models_dir / svm_fname
                scl_path = models_dir / scaler_fname
                if svm_path.exists() and scl_path.exists():
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            svm    = joblib.load(svm_path)
                            scaler = joblib.load(scl_path)

                        setattr(self, svm_attr,    svm)
                        setattr(self, scaler_attr, scaler)

                        # ── Bias detection ────────────────────────────────────
                        try:
                            rng       = np.random.RandomState(42)
                            n_feats   = getattr(scaler, "n_features_in_", 1764)
                            probe     = rng.randn(10, n_feats)
                            probe_scl = scaler.transform(probe)
                            probas    = svm.predict_proba(probe_scl)
                            # If every probe gives ≥ bias_threshold for class-1 → biased
                            all_biased = bool(np.all(probas[:, 1] >= _SVM_BIAS_THRESHOLD))
                            setattr(self, bias_attr, all_biased)
                            if all_biased:
                                logger.warning(
                                    "%s appears biased (always predicts PD≥%.0f%%). "
                                    "Will blend with image-feature heuristics.",
                                    svm_fname, _SVM_BIAS_THRESHOLD * 100,
                                )
                        except Exception as bias_err:
                            logger.warning("Bias check failed for %s: %s", svm_fname, bias_err)

                        logger.info("Loaded SVM: %s (biased=%s)", svm_fname,
                                    getattr(self, bias_attr))
                    except Exception as e:
                        logger.warning("Could not load SVM %s: %s", svm_fname, e)

    # ── Public analysis methods ────────────────────────────────────────────────

    def analyze_spiral(self, image_path: str) -> Dict:
        """Analyse spiral drawing."""
        return self._analyze(image_path, drawing_type="spiral")

    def analyze_wave(self, image_path: str) -> Dict:
        """Analyse wave drawing."""
        return self._analyze(image_path, drawing_type="wave")

    def analyze_combined(self, spiral_path: str, wave_path: str) -> Dict:
        """Analyse both drawings and average results."""
        spiral_r = self.analyze_spiral(spiral_path)
        wave_r   = self.analyze_wave(wave_path)

        ok = [r for r in [spiral_r, wave_r] if r.get("success")]
        if not ok:
            return {"success": False, "error": "Both analyses failed.",
                    "probability": 0.5, "pd_probability": 0.5, "confidence": 0.0}

        avg_prob = float(np.mean([r["pd_probability"] for r in ok]))
        avg_conf = float(np.mean([r["confidence"]     for r in ok]))
        diagnosis = "Parkinson's Disease" if avg_prob > 0.5 else "Healthy"

        return {
            "success": True,
            "diagnosis": diagnosis,
            "prediction": diagnosis,
            "probability": avg_prob,
            "pd_probability": avg_prob,
            "confidence": avg_conf,
            "spiral_result": spiral_r,
            "wave_result":   wave_r,
        }

    def predict(self, image_path: str) -> Dict:
        """Compatibility wrapper used by multimodal service."""
        return self._analyze(image_path, drawing_type="spiral")

    # ── Core analysis ──────────────────────────────────────────────────────────

    def _analyze(self, image_path: str, drawing_type: str) -> Dict:
        """
        Unified analysis pipeline.
        Priority: CNN → SVM+heuristic blend → pure heuristic.
        """
        try:
            # ── 1. CNN ────────────────────────────────────────────────────────
            cnn_model = self.spiral_model if drawing_type == "spiral" else self.wave_model
            if cnn_model and TF_AVAILABLE and CV2_AVAILABLE:
                result = self._predict_cnn(image_path, cnn_model)
                if result["success"]:
                    result["modality"] = drawing_type
                    logger.info("[%s] CNN: pd_prob=%.3f  conf=%.3f",
                                drawing_type, result["pd_probability"], result["confidence"])
                    return result

            # ── 2. Image-feature heuristics (content-sensitive) ───────────────
            heuristic = self._compute_heuristic_score(image_path)   # always run

            # ── 3. SVM (blended if biased) ────────────────────────────────────
            svm    = self.spiral_svm    if drawing_type == "spiral" else self.wave_svm
            scaler = self.spiral_scaler if drawing_type == "spiral" else self.wave_scaler
            biased = self._spiral_svm_biased if drawing_type == "spiral" else self._wave_svm_biased

            if svm and scaler and SVM_AVAILABLE and CV2_AVAILABLE:
                svm_prob, svm_conf = self._predict_svm(image_path, svm, scaler)

                if biased:
                    # Blend: 30% SVM (anchored but unreliable) + 70% heuristic
                    pd_prob  = 0.30 * svm_prob + 0.70 * heuristic["pd_prob"]
                    conf     = 0.30 * svm_conf + 0.70 * heuristic["confidence"]
                    method   = "SVM-heuristic blend (SVM was biased)"
                else:
                    # Blend: 60% SVM + 40% heuristic
                    pd_prob  = 0.60 * svm_prob + 0.40 * heuristic["pd_prob"]
                    conf     = 0.60 * svm_conf + 0.40 * heuristic["confidence"]
                    method   = "SVM-heuristic blend"

                logger.info("[%s] %s: svm_prob=%.3f  heuristic_prob=%.3f  final=%.3f",
                            drawing_type, method, svm_prob, heuristic["pd_prob"], pd_prob)
            else:
                # Pure heuristic
                pd_prob  = heuristic["pd_prob"]
                conf     = heuristic["confidence"]
                method   = "image-feature heuristic"
                logger.info("[%s] Heuristic only: pd_prob=%.3f  conf=%.3f",
                            drawing_type, pd_prob, conf)

            pd_prob  = float(np.clip(pd_prob, 0.0, 1.0))
            conf     = float(np.clip(conf,    0.0, 1.0))
            diagnosis = "Parkinson's Disease" if pd_prob > 0.5 else "Healthy"

            return {
                "success":      True,
                "diagnosis":    diagnosis,
                "prediction":   diagnosis,
                "probability":  pd_prob,
                "pd_probability": pd_prob,
                "confidence":   conf,
                "modality":     drawing_type,
                "method":       method,
                # Include heuristic details for transparency
                "tremor_ratio":   heuristic.get("tremor_ratio",   None),
                "stroke_roughness": heuristic.get("stroke_roughness", None),
            }

        except Exception as e:
            logger.error("[%s] Analysis exception: %s", drawing_type, e, exc_info=True)
            return {
                "success":        False,
                "error":          str(e),
                "diagnosis":      "Unknown",
                "prediction":     "Unknown",
                "probability":    0.5,
                "pd_probability": 0.5,
                "confidence":     0.0,
                "modality":       drawing_type,
            }

    # ── Sub-predictors ────────────────────────────────────────────────────────

    def _predict_cnn(self, image_path: str, model) -> Dict:
        try:
            image = self._preprocess_cnn(image_path)
            if image is None:
                return {"success": False}
            prob = float(model.predict(image, verbose=0)[0][0])
            conf = abs(prob - 0.5) * 2
            diag = "Parkinson's Disease" if prob > 0.5 else "Healthy"
            return {"success": True, "pd_probability": prob,
                    "probability": prob, "confidence": conf,
                    "prediction": diag, "diagnosis": diag}
        except Exception as e:
            logger.warning("CNN prediction failed: %s", e)
            return {"success": False}

    def _predict_svm(self, image_path: str, svm, scaler) -> Tuple[float, float]:
        image = self._preprocess_svm(image_path)
        if image is None:
            return 0.5, 0.0
        feats   = self._extract_hog_features(image).reshape(1, -1)
        scaled  = scaler.transform(feats)
        probas  = svm.predict_proba(scaled)[0]
        pd_prob = float(probas[1])            # class-1 = Parkinson
        conf    = abs(pd_prob - 0.5) * 2
        return pd_prob, conf

    # ── Image-feature heuristic ───────────────────────────────────────────────

    def _compute_heuristic_score(self, image_path: str) -> Dict:
        """
        Extract clinically-grounded features from the drawing image.

        Parkinson's handwriting characteristics:
          - High tremor ratio (irregular, spiky contours)
          - Low smoothness (stroke wobble)
          - Low mean stroke thickness (weakened grip)
          - High edge roughness

        Returns a dict with pd_prob ∈ [0,1] and confidence ∈ [0,1].
        """
        if not CV2_AVAILABLE:
            return {"pd_prob": 0.5, "confidence": 0.1}

        try:
            img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img_gray is None:
                return {"pd_prob": 0.5, "confidence": 0.1}

            img_gray = cv2.resize(img_gray, (256, 256))

            # ── Binarise (drawing = dark on light background) ─────────────────
            _, binary = cv2.threshold(img_gray, 0, 255,
                                      cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # ── Find contours ──────────────────────────────────────────────────
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                # Blank / non-drawing image → neutral
                return {"pd_prob": 0.5, "confidence": 0.1}

            # Use the largest contour as the main stroke
            main_c = max(contours, key=cv2.contourArea)
            area   = cv2.contourArea(main_c)

            if area < 50:
                return {"pd_prob": 0.5, "confidence": 0.1}

            arc_length = cv2.arcLength(main_c, closed=False)
            hull       = cv2.convexHull(main_c)
            hull_area  = cv2.contourArea(hull) + 1e-6

            # ── Feature 1: tremor ratio (hull excess) ──────────────────────────
            # High tremor_ratio → irregular drawing → more PD-like
            tremor_ratio = float((hull_area - area) / hull_area)   # 0=perfect, 1=very irregular
            tremor_ratio = np.clip(tremor_ratio, 0.0, 1.0)

            # ── Feature 2: contour smoothness ──────────────────────────────────
            # Low smoothness → wobbles → PD
            smoothness = float(area / (arc_length + 1e-6))
            # Normalise: typical range 0–30; remap to 0–1 (inverted: low smooth → high PD risk)
            smoothness_norm = float(np.clip(1.0 - smoothness / 30.0, 0.0, 1.0))

            # ── Feature 3: edge roughness ──────────────────────────────────────
            # Count edge pixels relative to contour area
            edges = cv2.Canny(img_gray, 50, 150)
            edge_px = float(np.sum(edges > 0))
            edge_roughness = float(np.clip(edge_px / (arc_length + 1), 0.0, 3.0) / 3.0)

            # ── Feature 4: stroke width variability ────────────────────────────
            dist_map = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
            stroke_px = dist_map[binary > 0]
            if len(stroke_px) > 0:
                stroke_cv = float(np.std(stroke_px) / (np.mean(stroke_px) + 1e-6))
                stroke_cv = float(np.clip(stroke_cv, 0.0, 1.0))
            else:
                stroke_cv = 0.5

            # ── Feature 5: pixel intensity std (pressure variation) ────────────
            pressure_std = float(np.std(img_gray) / 255.0)

            # ── Weighted PD score ──────────────────────────────────────────────
            # Higher = more PD-like
            pd_prob = (
                0.35 * tremor_ratio      +   # most important
                0.25 * smoothness_norm   +
                0.20 * edge_roughness    +
                0.10 * stroke_cv         +
                0.10 * pressure_std
            )
            pd_prob = float(np.clip(pd_prob, 0.0, 1.0))

            # Confidence: how far from the 0.5 decision boundary
            confidence = float(np.clip(abs(pd_prob - 0.5) * 2 + 0.2, 0.0, 1.0))

            return {
                "pd_prob":         pd_prob,
                "confidence":      confidence,
                "tremor_ratio":    round(tremor_ratio, 4),
                "smoothness_norm": round(smoothness_norm, 4),
                "edge_roughness":  round(edge_roughness, 4),
                "stroke_cv":       round(stroke_cv, 4),
                "stroke_roughness": round(tremor_ratio + edge_roughness, 4),
            }

        except Exception as e:
            logger.warning("Heuristic analysis failed for %s: %s", image_path, e)
            return {"pd_prob": 0.5, "confidence": 0.1}

    # ── Preprocessing helpers ─────────────────────────────────────────────────

    def _preprocess_cnn(self, image_path: str):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            img = cv2.resize(img, self.image_size_cnn).astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=-1)
            img = np.expand_dims(img, axis=0)
            return img
        except Exception:
            return None

    def _preprocess_svm(self, image_path: str):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            img = cv2.resize(img, self.image_size_svm).astype(np.float32) / 255.0
            img = cv2.GaussianBlur(img, (3, 3), 0)
            return img
        except Exception:
            return None

    # Note: CLAHE removed from SVM preprocessing — it normalises fine textures
    # and makes different images look identical to HOG features.

    def _extract_hog_features(self, image: np.ndarray) -> np.ndarray:
        features, _ = hog(
            image,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
            visualize=True,
            feature_vector=True,
        )
        return features.reshape(1, -1)
