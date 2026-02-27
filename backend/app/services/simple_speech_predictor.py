"""
Speech Prediction Service — CNN+LSTM (Deep Learning)
=====================================================
Loads the trained CNN+LSTM Keras model and StandardScaler.
Accepts pre-extracted 753 speech features and returns PD probability.
Falls back to sklearn RF model if CNN+LSTM is unavailable.
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Optional
import os

# TensorFlow import
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    tf = None
    TF_AVAILABLE = False


class SimpleSpeechPredictor:
    """
    Speech prediction service using CNN+LSTM deep learning model.
    Falls back to scikit-learn RF if Keras model not available.
    """
    
    def __init__(self, models_dir: str = "models/speech"):
        self.models_dir = Path(models_dir)
        
        # CNN+LSTM model (preferred)
        self.keras_model = None
        self.keras_scaler = None
        
        # Fallback sklearn model
        self.sklearn_model = None
        self.sklearn_scaler = None
        self.sklearn_selector = None
        
        self.is_loaded = False
        self.model_type = None
        
        self._load_models()
    
    def _load_models(self):
        """Load CNN+LSTM model (preferred) or fall back to sklearn RF."""
        
        # ── 1. Try CNN+LSTM Keras model ────────────────────────
        if TF_AVAILABLE:
            base_dir = Path(__file__).parent.parent.parent.parent
            search_paths = [
                base_dir / "ml-models" / "models" / "speech",
                self.models_dir,
            ]
            
            for search_dir in search_paths:
                keras_path = search_dir / "cnn_lstm_speech_best.keras"
                scaler_path = search_dir / "cnn_lstm_scaler.pkl"
                
                if keras_path.exists() and scaler_path.exists():
                    try:
                        self.keras_model = tf.keras.models.load_model(str(keras_path))
                        self.keras_scaler = joblib.load(str(scaler_path))
                        self.is_loaded = True
                        self.model_type = "CNN+LSTM"
                        print(f"✅ Speech CNN+LSTM model loaded ({keras_path.stat().st_size / 1024:.0f}KB)")
                        return
                    except Exception as e:
                        print(f"⚠️  Could not load CNN+LSTM model: {e}")
                        self.keras_model = None
                        self.keras_scaler = None
        
        # ── 2. Fallback to sklearn RF ─────────────────────────
        try:
            model_path = self.models_dir / "speech_rf_model.pkl"
            scaler_path = self.models_dir / "speech_rf_scaler.pkl"
            selector_path = self.models_dir / "speech_feature_selector.pkl"
            
            if model_path.exists() and scaler_path.exists():
                self.sklearn_model = joblib.load(model_path)
                self.sklearn_scaler = joblib.load(scaler_path)
                if selector_path.exists():
                    self.sklearn_selector = joblib.load(selector_path)
                self.is_loaded = True
                self.model_type = "SVM-RBF"
                print(f"✅ Speech sklearn model loaded (fallback)")
                return
        except Exception as e:
            print(f"⚠️  Error loading sklearn model: {e}")
        
        print("⚠️  No speech models available")
    
    def predict_from_features(self, features: np.ndarray) -> Dict:
        """
        Make prediction from pre-extracted features.
        
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
            
            # Handle NaN / inf
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
            
            if self.keras_model is not None:
                return self._predict_cnn_lstm(features)
            else:
                return self._predict_sklearn(features)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "pd_probability": 0.5,
                "prediction": "Healthy",
                "confidence": 0.0
            }
    
    def _predict_cnn_lstm(self, features: np.ndarray) -> Dict:
        """Predict using CNN+LSTM Keras model."""
        expected = self.keras_scaler.n_features_in_
        
        # Trim or pad features to match scaler
        if features.shape[1] > expected:
            features = features[:, -expected:]
        elif features.shape[1] < expected:
            pad = np.zeros((features.shape[0], expected - features.shape[1]))
            features = np.hstack([features, pad])
        
        # Scale
        features_scaled = self.keras_scaler.transform(features)
        
        # Predict
        prediction = self.keras_model.predict(features_scaled, verbose=0)[0][0]
        pd_prob = float(prediction)
        confidence = abs(pd_prob - 0.5) * 2
        diagnosis = "Parkinson's Disease" if pd_prob > 0.5 else "Healthy"
        
        return {
            "success": True,
            "diagnosis": diagnosis,
            "prediction": diagnosis,
            "pd_probability": pd_prob,
            "probability": pd_prob,
            "confidence": confidence,
            "modality": "voice",
            "model_type": "CNN+LSTM"
        }
    
    def _predict_sklearn(self, features: np.ndarray) -> Dict:
        """Predict using sklearn RF model (fallback)."""
        expected = self.sklearn_scaler.n_features_in_ if hasattr(self.sklearn_scaler, 'n_features_in_') else 752
        
        if features.shape[1] > expected:
            features = features[:, -expected:]
        elif features.shape[1] < expected:
            return {
                "success": False,
                "error": f"Feature count mismatch: expected {expected}, got {features.shape[1]}",
                "pd_probability": 0.5,
                "prediction": "Healthy",
                "confidence": 0.0
            }
        
        features_scaled = self.sklearn_scaler.transform(features)
        
        if self.sklearn_selector is not None:
            features_scaled = self.sklearn_selector.transform(features_scaled)
        
        prediction_proba = self.sklearn_model.predict_proba(features_scaled)[0]
        pd_prob = float(prediction_proba[1])
        confidence = abs(pd_prob - 0.5) * 2
        diagnosis = "Parkinson's Disease" if pd_prob > 0.5 else "Healthy"
        
        return {
            "success": True,
            "diagnosis": diagnosis,
            "prediction": diagnosis,
            "pd_probability": pd_prob,
            "probability": pd_prob,
            "confidence": confidence,
            "modality": "voice",
            "model_type": "SVM-RBF"
        }
    
    def predict_baseline(self) -> Dict:
        """Return baseline prediction when model unavailable."""
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
        """Check if model is loaded and ready."""
        return self.is_loaded


# Global instance
_predictor_instance = None

def get_predictor(models_dir: str = None) -> SimpleSpeechPredictor:
    """Get or create the global predictor instance."""
    global _predictor_instance
    
    if _predictor_instance is None:
        if models_dir is None:
            current_dir = Path(__file__).parent
            models_dir = current_dir.parent / "models" / "speech"
            if not models_dir.exists():
                models_dir = current_dir.parent.parent.parent / "models" / "speech"
        
        _predictor_instance = SimpleSpeechPredictor(models_dir)
    
    return _predictor_instance
