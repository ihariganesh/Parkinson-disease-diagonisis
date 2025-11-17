"""
Handwriting Analysis Service
Wrapper for handwriting analyzer to integrate with multi-modal system
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, Tuple
import tensorflow as tf
import cv2


class HandwritingService:
    """Handwriting analysis service for Parkinson's disease detection"""
    
    def __init__(self):
        """Initialize handwriting analyzer"""
        self.spiral_model = None
        self.wave_model = None
        self.image_size = (224, 224)  # ResNet50 input size
        self._load_models()
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for ResNet50 model"""
        try:
            # Read image
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize image
            image = cv2.resize(image, self.image_size)
            
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
    
    def _load_models(self):
        """Load trained models for spiral and wave drawings"""
        base_dir = Path(__file__).parent.parent.parent.parent  # Go to parkinson-app/
        models_dir = base_dir / "backend" / "models"
        
        # Load spiral model
        spiral_model_path = models_dir / "resnet50_spiral_best.h5"
        if spiral_model_path.exists():
            try:
                self.spiral_model = tf.keras.models.load_model(str(spiral_model_path))
                print(f"✅ Loaded spiral ResNet50 model")
            except Exception as e:
                print(f"⚠️  Could not load spiral model: {e}")
                self.spiral_model = None
        else:
            print(f"⚠️  Spiral model not found at {spiral_model_path}")
            self.spiral_model = None
        
        # Load wave model
        wave_model_path = models_dir / "resnet50_wave_best.h5"
        if wave_model_path.exists():
            try:
                self.wave_model = tf.keras.models.load_model(str(wave_model_path))
                print(f"✅ Loaded wave ResNet50 model")
            except Exception as e:
                print(f"⚠️  Could not load wave model: {e}")
                self.wave_model = None
        else:
            print(f"⚠️  Wave model not found at {wave_model_path}")
            self.wave_model = None
    
    def analyze_spiral(self, image_path: str) -> Dict:
        """Analyze spiral drawing"""
        if not self.spiral_model:
            return {
                "success": False,
                "error": "Spiral model not available",
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_path)
            image = np.expand_dims(image, axis=-1)  # Add channel dimension
            image = np.expand_dims(image, axis=0)   # Add batch dimension
            
            # Make prediction
            prediction = self.spiral_model.predict(image, verbose=0)[0][0]
            
            # Convert to probability and diagnosis
            probability = float(prediction)
            diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
            confidence = abs(probability - 0.5) * 2  # 0-1 scale
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "probability": probability,
                "pd_probability": probability,  # Add for multimodal compatibility
                "confidence": confidence,
                "modality": "spiral"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
    
    
    def analyze_wave(self, image_path: str) -> Dict:
        """Analyze wave drawing"""
        if not self.wave_model:
            return {
                "success": False,
                "error": "Wave model not available",
                "diagnosis": "Unknown",
                "probability": 0.5,
                "confidence": 0.0
            }
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_path)
            image = np.expand_dims(image, axis=-1)  # Add channel dimension
            image = np.expand_dims(image, axis=0)   # Add batch dimension
            
            # Make prediction
            prediction = self.wave_model.predict(image, verbose=0)[0][0]
            
            # Convert to probability and diagnosis
            probability = float(prediction)
            diagnosis = "Parkinson's Disease" if probability > 0.5 else "Healthy"
            confidence = abs(probability - 0.5) * 2  # 0-1 scale
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "probability": probability,
                "pd_probability": probability,  # Add for multimodal compatibility
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
        # For now, assume it could be either and try to analyze as spiral
        # In production, you might want to detect the type or require separate uploads
        try:
            # Try analyzing as spiral first
            result = self.analyze_spiral(image_path)
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
