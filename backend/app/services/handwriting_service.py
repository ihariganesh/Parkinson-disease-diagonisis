"""
Handwriting Analysis Service
Wrapper for handwriting analyzer to integrate with multi-modal system
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
    print("⚠️  TensorFlow not available - handwriting ML model disabled. Falling back to SVM + HOG models.")

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
    """Handwriting analysis service for Parkinson's disease detection"""
    
    def __init__(self):
        """Initialize handwriting analyzer"""
        self.spiral_model = None
        self.wave_model = None
        
        self.spiral_svm = None
        self.spiral_scaler = None
        self.wave_svm = None
        self.wave_scaler = None
        
        self.image_size_cnn = (224, 224)  # ResNet50 input size
        self.image_size_svm = (128, 128)  # SVM+HOG input size
        
        self._load_models()
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int]) -> np.ndarray:
        """Preprocess image for analysis"""
        try:
            # Read image
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize image
            image = cv2.resize(image, target_size)
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Apply Gaussian blur to reduce noise
            image = cv2.GaussianBlur(image, (3, 3), 0)
            
            # Enhance contrast
            image = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(
                (image * 255).astype(np.uint8)
            ).astype(np.float32) / 255.0
            
            return image
            
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
        """Load trained models for spiral and wave drawings"""
        base_dir = Path(__file__).parent.parent.parent.parent  # Go to parkinson-app/
        models_dir = base_dir / "backend"/ "models" if (base_dir / "backend" / "models").exists() else base_dir / "models"
        
        if TF_AVAILABLE:
            # Load CNN models
            spiral_model_path = models_dir / "resnet50_spiral_best.h5"
            if spiral_model_path.exists():
                try:
                    self.spiral_model = tf.keras.models.load_model(str(spiral_model_path))
                    print(f"✅ Loaded spiral ResNet50 model")
                except Exception as e:
                    print(f"⚠️  Could not load spiral model: {e}")
            
            wave_model_path = models_dir / "resnet50_wave_best.h5"
            if wave_model_path.exists():
                try:
                    self.wave_model = tf.keras.models.load_model(str(wave_model_path))
                    print(f"✅ Loaded wave ResNet50 model")
                except Exception as e:
                    print(f"⚠️  Could not load wave model: {e}")
                    
        if not TF_AVAILABLE or (not self.spiral_model and not self.wave_model):
            # Load SVM fallback models
            if SVM_AVAILABLE:
                try:
                    # Look globally in standard places, often models are just at root/models
                    spiral_svm_path = base_dir / "models" / "spiral_svm_model_svm.pkl"
                    spiral_scaler_path = base_dir / "models" / "spiral_svm_model_scaler.pkl"
                    if spiral_svm_path.exists() and spiral_scaler_path.exists():
                        self.spiral_svm = joblib.load(spiral_svm_path)
                        self.spiral_scaler = joblib.load(spiral_scaler_path)
                        print(f"✅ Loaded spiral SVM fallback model")
                    else:
                        print(f"⚠️  Spiral SVM model not found at {spiral_svm_path}")
                        
                    wave_svm_path = base_dir / "models" / "wave_svm_model_svm.pkl"
                    wave_scaler_path = base_dir / "models" / "wave_svm_model_scaler.pkl"
                    if wave_svm_path.exists() and wave_scaler_path.exists():
                        self.wave_svm = joblib.load(wave_svm_path)
                        self.wave_scaler = joblib.load(wave_scaler_path)
                        print(f"✅ Loaded wave SVM fallback model")
                    else:
                        print(f"⚠️  Wave SVM model not found at {wave_svm_path}")
                except Exception as e:
                    print(f"⚠️  Could not load SVM fallback models: {e}")

    def analyze_spiral(self, image_path: str) -> Dict:
        """Analyze spiral drawing"""
        try:
            if self.spiral_model and TF_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_cnn)
                image = np.expand_dims(image, axis=-1)
                image = np.expand_dims(image, axis=0)
                prediction = self.spiral_model.predict(image, verbose=0)[0][0]
                probability = float(prediction)
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                confidence = abs(probability - 0.5) * 2
                
            elif self.spiral_svm and SVM_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_svm)
                features = self._extract_hog_features(image)
                features_scaled = self.spiral_scaler.transform(features)
                prediction_prob = self.spiral_svm.predict_proba(features_scaled)[0]
                
                # Class 1 is Parkinson's in standard SKLearn setup (assumed based on HOG tests)
                probability = float(prediction_prob[1])
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                confidence = abs(probability - 0.5) * 2
                
            else:
                return {
                    "success": False,
                    "error": "No model available for spiral analysis (TensorFlow and SVM models failed to load)",
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
            if self.wave_model and TF_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_cnn)
                image = np.expand_dims(image, axis=-1)
                image = np.expand_dims(image, axis=0)
                prediction = self.wave_model.predict(image, verbose=0)[0][0]
                probability = float(prediction)
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                confidence = abs(probability - 0.5) * 2
                
            elif self.wave_svm and SVM_AVAILABLE:
                image = self.preprocess_image(image_path, self.image_size_svm)
                features = self._extract_hog_features(image)
                features_scaled = self.wave_scaler.transform(features)
                prediction_prob = self.wave_svm.predict_proba(features_scaled)[0]
                
                probability = float(prediction_prob[1])
                diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
                confidence = abs(probability - 0.5) * 2
                
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
