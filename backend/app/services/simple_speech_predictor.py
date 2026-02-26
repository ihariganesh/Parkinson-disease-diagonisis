"""
Simplified Speech Prediction Service
Fallback to scikit-learn ensemble model as TensorFlow is not available in production env.
"""

import numpy as np
import pickle
import joblib
from pathlib import Path
from typing import Dict, Optional
import os

class SimpleSpeechPredictor:
    """
    Lightweight speech prediction service
    Assumes features are pre-extracted and provided
    """
    
    def __init__(self, models_dir: str = "models/speech"):
        """
        Initialize the predictor
        
        Args:
            models_dir: Directory containing model files
        """
        self.models_dir = Path(models_dir)
        self.model = None
        self.scaler = None
        self.is_loaded = False
        
        # Try to load the latest model
        self._load_latest_model()
    
    def _load_latest_model(self):
        """Load the trained scikit-learn model and scaler"""
        try:
            model_path = self.models_dir / "speech_rf_model.pkl"
            scaler_path = self.models_dir / "speech_rf_scaler.pkl"
            
            if not model_path.exists() or not scaler_path.exists():
                print("  Speech RF model files not found")
                return
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            self.is_loaded = True
            print(f" Speech RF model loaded successfully!")
            
        except Exception as e:
            print(f"  Error loading speech RF model: {e}")
            self.is_loaded = False
    
    def predict_from_features(self, features: np.ndarray) -> Dict:
        """
        Make prediction from pre-extracted features
        
        Args:
            features: Numpy array of shape (n_features,) or (1, n_features)
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            return {
                "success": False,
                "error": "Model not loaded",
                "pd_probability": 0.5,
                "prediction": "Healthy",
                "confidence": 0.0
            }
        
        try:
            # Ensure features is 2D
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # The RF model was trained on 753 features, audio_feature_extractor returns 754.
            # Usually the first feature from extractor is 'id' or dummy based on standard dataset.
            expected_features = self.model.n_features_in_
            
            if features.shape[1] > expected_features:
                # Keep the last `expected_features` (drop the 'id' at index 0)
                features = features[:, -expected_features:]
            elif features.shape[1] < expected_features:
                 return {
                    "success": False,
                    "error": f"Feature count mismatch: expected {expected_features}, got {features.shape[1]}",
                    "pd_probability": 0.5,
                    "prediction": "Healthy",
                    "confidence": 0.0
                }
            
            # Handle any NaN or inf values
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            
            # Class 1 is PD 
            pd_prob = float(prediction_proba[1])
            diagnosis = "Parkinson's Disease" if pd_prob > 0.5 else "Healthy"
            confidence = abs(pd_prob - 0.5) * 2
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "pd_probability": pd_prob,
                "probability": pd_prob,
                "confidence": confidence,
                "modality": "voice"
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  Prediction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "pd_probability": 0.5,
                "prediction": "Healthy",
                "confidence": 0.0
            }
    
    def predict_baseline(self) -> Dict:
        """Return baseline prediction when model unavailable"""
        return {
            "success": True,
            "diagnosis": "Healthy",
            "prediction": "Healthy",
            "pd_probability": 0.50,
            "probability": 0.50,
            "confidence": 0.30,
            "modality": "voice",
            "note": "Using baseline estimate - model not available"
        }
    
    def is_available(self) -> bool:
        """Check if model is loaded and ready"""
        return self.is_loaded


# Global instance for easy import
_predictor_instance = None

def get_predictor(models_dir: str = None) -> SimpleSpeechPredictor:
    """Get or create the global predictor instance"""
    global _predictor_instance
    
    if _predictor_instance is None:
        if models_dir is None:
            # Try to find models directory relative to this file
            current_dir = Path(__file__).parent
            models_dir = current_dir.parent / "models" / "speech"
            
            # Fallback for standard app structure
            if not models_dir.exists():
                models_dir = current_dir.parent.parent.parent / "models" / "speech"
        
        _predictor_instance = SimpleSpeechPredictor(models_dir)
    
    return _predictor_instance
