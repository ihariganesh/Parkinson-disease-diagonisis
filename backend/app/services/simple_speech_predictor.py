"""
Simplified Speech Prediction Service
Uses pre-trained CNN+LSTM model with extracted features
Avoids real-time feature extraction to prevent hanging
"""

import numpy as np
import pickle
from pathlib import Path
from tensorflow import keras
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
        self.label_encoder = None
        self.feature_names = None
        self.is_loaded = False
        
        # Try to load the latest model
        self._load_latest_model()
    
    def _find_latest_model_files(self) -> Optional[Dict[str, Path]]:
        """Find the most recent model files"""
        try:
            # Find all model files
            model_files = sorted(self.models_dir.glob("speech_cnn_lstm_model_*.h5"))
            
            if not model_files:
                print("⚠️  No speech model files found")
                return None
            
            # Get the latest one
            latest_model = model_files[-1]
            timestamp = latest_model.stem.split('_')[-2] + '_' + latest_model.stem.split('_')[-1]
            
            files = {
                'model': latest_model,
                'scaler': self.models_dir / f"speech_scaler_{timestamp}.pkl",
                'encoder': self.models_dir / f"speech_label_encoder_{timestamp}.pkl",
                'features': self.models_dir / f"speech_feature_names_{timestamp}.pkl"
            }
            
            # Verify all files exist
            for file_type, file_path in files.items():
                if not file_path.exists():
                    print(f"⚠️  Missing {file_type} file: {file_path}")
                    return None
            
            return files
            
        except Exception as e:
            print(f"⚠️  Error finding model files: {e}")
            return None
    
    def _load_latest_model(self):
        """Load the most recent trained model"""
        try:
            files = self._find_latest_model_files()
            
            if not files:
                print("⚠️  Speech model not available - no model files found")
                return
            
            # Load model
            print(f"Loading speech model from: {files['model'].name}")
            self.model = keras.models.load_model(files['model'])
            
            # Load scaler
            with open(files['scaler'], 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load label encoder
            with open(files['encoder'], 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load feature names
            with open(files['features'], 'rb') as f:
                self.feature_names = pickle.load(f)
            
            self.is_loaded = True
            print(f"✅ Speech model loaded successfully!")
            print(f"   Model expects {len(self.feature_names)} features")
            
        except Exception as e:
            print(f"⚠️  Error loading speech model: {e}")
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
            
            # Validate feature count
            if features.shape[1] != len(self.feature_names):
                return {
                    "success": False,
                    "error": f"Feature count mismatch: expected {len(self.feature_names)}, got {features.shape[1]}",
                    "pd_probability": 0.5,
                    "prediction": "Healthy",
                    "confidence": 0.0
                }
            
            # Handle any NaN or inf values
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction_proba = self.model.predict(features_scaled, verbose=0)[0][0]
            
            # Convert to class
            predicted_class = 1 if prediction_proba > 0.5 else 0
            class_name = self.label_encoder.inverse_transform([predicted_class])[0]
            
            # Convert to string to avoid numpy type issues
            class_name_str = str(class_name)
            
            # Calculate confidence (distance from 0.5)
            confidence = abs(prediction_proba - 0.5) * 2
            
            # Map to expected format
            diagnosis = "Parkinson's Disease" if class_name_str.lower() == "parkinson's" else "Healthy"
            pd_prob = prediction_proba if class_name_str.lower() == "parkinson's" else (1.0 - prediction_proba)
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "prediction": diagnosis,
                "pd_probability": float(pd_prob),
                "probability": float(prediction_proba),
                "confidence": float(confidence),
                "modality": "voice"
            }
            
        except Exception as e:
            print(f"⚠️  Prediction error: {e}")
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
        
        _predictor_instance = SimpleSpeechPredictor(models_dir)
    
    return _predictor_instance
