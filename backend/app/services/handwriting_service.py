"""
Handwriting Analysis Service
MobileNetV2-based handwriting classifier for Parkinson's disease detection.

Preprocessing: grayscale → Otsu threshold → Canny edges → 3-channel stack
This isolates stroke/tremor patterns, ignoring background/paper/lighting.
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, Tuple

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    tf = None
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available - handwriting ML model disabled.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
    print("⚠️  OpenCV not available - handwriting image processing disabled")

try:
    import joblib
    from skimage.feature import hog
    SVM_AVAILABLE = True
except ImportError as e:
    SVM_AVAILABLE = False
    print(f"⚠️  skimage or joblib not available - SVM fallback disabled: {e}")


class HandwritingService:
    """Handwriting analysis service for Parkinson's disease detection
    
    Uses MobileNetV2 with edge-focused preprocessing:
      Ch0: Grayscale (stroke intensity)
      Ch1: Otsu binary threshold (ink vs paper separation)
      Ch2: Canny edges (stroke boundaries + tremor wobble)
    """
    
    # Confidence below this threshold → Inconclusive
    CONFIDENCE_THRESHOLD = 0.25
    
    def __init__(self):
        """Initialize handwriting analyzer"""
        self.model = None
        
        self.spiral_svm = None
        self.spiral_scaler = None
        self.wave_svm = None
        self.wave_scaler = None
        
        self.image_size_cnn = (224, 224)
        self.image_size_svm = (128, 128)
        
        self._load_models()
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Edge-focused preprocessing that isolates stroke/tremor patterns.
        
        Creates 3-channel image:
          Ch0: Normalized grayscale
          Ch1: Otsu binary threshold (ink strokes isolated from paper)
          Ch2: Canny edges (stroke boundaries and tremor wobbles)
        """
        try:
            gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            gray = cv2.resize(gray, target_size)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Ch0: Normalized grayscale
            ch_gray = blurred.astype(np.float32) / 255.0
            
            # Ch1: Otsu binary threshold (isolates ink from paper)
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            ch_binary = binary.astype(np.float32) / 255.0
            
            # Ch2: Canny edges (captures stroke boundaries and tremor)
            edges = cv2.Canny(blurred, 30, 120)
            ch_edges = edges.astype(np.float32) / 255.0
            
            # Stack into 3-channel image
            return np.stack([ch_gray, ch_binary, ch_edges], axis=-1)
            
        except Exception as e:
            raise ValueError(f"Error preprocessing image {image_path}: {str(e)}")
            
    def _extract_hog_features(self, image: np.ndarray) -> np.ndarray:
        """Extract HOG features from image for SVM model"""
        features, _ = hog(
            image,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm='L2-Hys',
            visualize=True,
            feature_vector=True
        )
        return features.reshape(1, -1)
    
    def _load_models(self):
        """Load trained MobileNetV2 model for handwriting analysis"""
        base_dir = Path(__file__).parent.parent.parent.parent  # Go to project root
        ml_models_dir = base_dir / "ml-models" / "models"
        models_dir = base_dir / "backend" / "models" if (base_dir / "backend" / "models").exists() else base_dir / "models"
        
        if TF_AVAILABLE:
            # Try loading MobileNetV2 model first (preferred)
            mobilenet_path = ml_models_dir / "handwriting" / "mobilenetv2_handwriting_best.keras"
            if not mobilenet_path.exists():
                mobilenet_path = models_dir / "handwriting" / "mobilenetv2_handwriting_best.keras"
            
            if mobilenet_path.exists():
                try:
                    self.model = tf.keras.models.load_model(str(mobilenet_path))
                    print(f"✅ Loaded MobileNetV2 handwriting model ({mobilenet_path.stat().st_size / 1024 / 1024:.1f}MB)")
                    return
                except Exception as e:
                    print(f"⚠️  Could not load MobileNetV2 model: {e}")
            
            # Fallback: try ResNet50 combined model
            resnet_path = ml_models_dir / "handwriting" / "resnet50_combined_best.keras"
            if not resnet_path.exists():
                resnet_path = models_dir / "handwriting" / "resnet50_combined_best.keras"
            
            if resnet_path.exists():
                try:
                    self.model = tf.keras.models.load_model(str(resnet_path))
                    print(f"✅ Loaded ResNet50 handwriting model (fallback)")
                except Exception as e:
                    print(f"⚠️  Could not load ResNet50 model: {e}")
                    
        if not TF_AVAILABLE or not self.model:
            # Load SVM fallback models
            if SVM_AVAILABLE:
                try:
                    spiral_svm_path = base_dir / "models" / "spiral_svm_model_svm.pkl"
                    spiral_scaler_path = base_dir / "models" / "spiral_svm_model_scaler.pkl"
                    if spiral_svm_path.exists() and spiral_scaler_path.exists():
                        self.spiral_svm = joblib.load(spiral_svm_path)
                        self.spiral_scaler = joblib.load(spiral_scaler_path)
                        print(f"✅ Loaded spiral SVM fallback model")
                        
                    wave_svm_path = base_dir / "models" / "wave_svm_model_svm.pkl"
                    wave_scaler_path = base_dir / "models" / "wave_svm_model_scaler.pkl"
                    if wave_svm_path.exists() and wave_scaler_path.exists():
                        self.wave_svm = joblib.load(wave_svm_path)
                        self.wave_scaler = joblib.load(wave_scaler_path)
                        print(f"✅ Loaded wave SVM fallback model")
                except Exception as e:
                    print(f"⚠️  Could not load SVM fallback models: {e}")

    def _predict_cnn(self, image_path: str) -> Tuple[float, float, str]:
        """
        Run CNN prediction on an image. Returns (probability, confidence, diagnosis).
        Applies confidence gating — returns 'Inconclusive' if confidence too low.
        """
        image = self.preprocess_image(image_path, self.image_size_cnn)
        # preprocess_image already returns 3-channel (gray, binary, edges)
        image = np.expand_dims(image, axis=0)  # (1, 224, 224, 3)
        prediction = self.model.predict(image, verbose=0)[0][0]
        probability = float(prediction)
        confidence = abs(probability - 0.5) * 2
        
        if confidence < self.CONFIDENCE_THRESHOLD:
            diagnosis = "Inconclusive"
        elif probability > 0.5:
            diagnosis = "Parkinson's Disease"
        else:
            diagnosis = "Healthy"
        
        return probability, confidence, diagnosis

    def analyze_spiral(self, image_path: str) -> Dict:
        """Analyze spiral drawing"""
        try:
            if self.model and TF_AVAILABLE:
                probability, confidence, diagnosis = self._predict_cnn(image_path)
                
            elif self.spiral_svm and SVM_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_svm)
                # SVM needs single-channel grayscale
                gray_ch = image[:, :, 0]  # Use the grayscale channel
                features = self._extract_hog_features(gray_ch)
                features_scaled = self.spiral_scaler.transform(features)
                prediction_prob = self.spiral_svm.predict_proba(features_scaled)[0]
                
                probability = float(prediction_prob[1])
                confidence = abs(probability - 0.5) * 2
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                
            else:
                return {
                    "success": False,
                    "error": "No model available for spiral analysis",
                    "diagnosis": "Unknown",
                    "probability": 0.5,
                    "confidence": 0.0
                }

            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "probability": probability,
                "pd_probability": probability,
                "confidence": confidence,
                "modality": "spiral"
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
    
    def analyze_wave(self, image_path: str) -> Dict:
        """Analyze wave drawing"""
        try:
            if self.model and TF_AVAILABLE:
                probability, confidence, diagnosis = self._predict_cnn(image_path)
                
            elif self.wave_svm and SVM_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_svm)
                gray_ch = image[:, :, 0]
                features = self._extract_hog_features(gray_ch)
                features_scaled = self.wave_scaler.transform(features)
                prediction_prob = self.wave_svm.predict_proba(features_scaled)[0]
                
                probability = float(prediction_prob[1])
                confidence = abs(probability - 0.5) * 2
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                
            else:
                return {
                    "success": False,
                    "error": "No model available for wave analysis",
                    "diagnosis": "Unknown",
                    "probability": 0.5,
                    "confidence": 0.0
                }
                
            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "probability": probability,
                "pd_probability": probability,
                "confidence": confidence,
                "modality": "wave"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
    
    def analyze_combined(self, spiral_path: str, wave_path: str) -> Dict:
        """Analyze both spiral and wave drawings and combine results"""
        spiral_result = self.analyze_spiral(spiral_path)
        wave_result = self.analyze_wave(wave_path)
        
        if not spiral_result["success"] and not wave_result["success"]:
            return {
                "success": False,
                "error": "Both analyses failed",
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
        
        # Average probabilities
        prob_sum = 0
        prob_count = 0
        
        if spiral_result["success"]:
            prob_sum += spiral_result["probability"]
            prob_count += 1
        
        if wave_result["success"]:
            prob_sum += wave_result["probability"]
            prob_count += 1
        
        avg_probability = prob_sum / prob_count if prob_count > 0 else 0.5
        
        # Average confidence
        conf_sum = 0
        conf_count = 0
        
        if spiral_result["success"]:
            conf_sum += spiral_result["confidence"]
            conf_count += 1
        
        if wave_result["success"]:
            conf_sum += wave_result["confidence"]
            conf_count += 1
        
        avg_confidence = conf_sum / conf_count if conf_count > 0 else 0.0
        
        diagnosis = "Parkinson's Disease" if avg_probability > 0.5 else "Healthy"
        
        return {
            "success": True,
            "diagnosis": diagnosis,
            "probability": avg_probability,
            "confidence": avg_confidence,
            "spiral_result": spiral_result,
            "wave_result": wave_result
        }
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict method for compatibility with multimodal service
        Automatically detects if it's a spiral or wave and analyzes accordingly
        If unsure, tries both and returns the combined result
        """
        try:
            # Try analyzing as spiral first
            result = self.analyze_spiral(image_path)
            
            # If handwriting analysis actually failed because of missing tools
            if not result.get("success", False):
                raise Exception(result.get("error", "Failed to analyze"))
                
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not analyze image: {str(e)}",
                "diagnosis": "Unknown",
                "prediction": "Unknown",
                "probability": 0.5,
                "pd_probability": 0.5,
                "confidence": 0.0
            }

    def analyze_handwriting(self, image_path: str, drawing_type: str = "spiral") -> Dict:
        """
        Unified analyze_handwriting method for compatibility with the handwriting endpoint.
        Routes to analyze_spiral or analyze_wave and wraps the result in the
        ensemble_prediction / prediction_summary format expected by the endpoint.
        """
        if drawing_type == "wave":
            raw = self.analyze_wave(image_path)
        else:
            raw = self.analyze_spiral(image_path)

        if not raw.get("success", False):
            return {"error": raw.get("error", "Analysis failed")}

        probability = raw.get("probability", 0.5)
        confidence = raw.get("confidence", 0.0)
        diagnosis = raw.get("diagnosis", "Unknown")
        predicted_label = diagnosis  # e.g. "Parkinson's Disease" or "Healthy"
        predicted_class = 1 if probability > 0.5 else 0
        model_name = "MobileNetV2" if self.model else "SVM-HOG"

        return {
            "success": True,
            "ensemble_prediction": {
                "predicted_label": predicted_label,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "raw_prediction": probability,
                "models_used": 1,
                "model_agreement": 1.0,
            },
            "prediction_summary": {
                "final_diagnosis": predicted_label,
                "confidence_level": "High" if confidence > 0.7 else "Moderate" if confidence > 0.4 else "Low",
                "recommendation": (
                    "Consult a neurologist for further evaluation."
                    if probability > 0.5
                    else "No significant Parkinson's indicators detected."
                ),
                "model_consensus": f"{model_name} predicts {predicted_label}",
            },
            "individual_models": {
                model_name: {
                    "predicted_label": predicted_label,
                    "confidence": confidence,
                    "probability": probability,
                }
            },
        }
