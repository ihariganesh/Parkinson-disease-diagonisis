"""
Speech Analysis Service for Parkinson's Disease Detection
Integrates feature extraction, model prediction, and result interpretation
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
import os
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import tempfile
import shutil

from speech_feature_extractor import SpeechFeatureExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechAnalysisService:
    def __init__(self, models_dir="models/speech"):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.feature_extractor = SpeechFeatureExtractor()
        self.is_loaded = False
        
    def load_models(self):
        """Load the trained model and preprocessors"""
        try:
            # Find the latest model files
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.h5')]
            scaler_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_scaler') and f.endswith('.pkl')]
            encoder_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_label_encoder') and f.endswith('.pkl')]
            feature_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_feature_names') and f.endswith('.pkl')]
            
            if not (model_files and scaler_files and encoder_files and feature_files):
                logger.error("Required model files not found. Please train the model first.")
                return False
                
            # Use the latest files (assuming timestamp in filename)
            latest_model = sorted(model_files)[-1]
            latest_scaler = sorted(scaler_files)[-1]
            latest_encoder = sorted(encoder_files)[-1]
            latest_features = sorted(feature_files)[-1]
            
            # Load model
            model_path = os.path.join(self.models_dir, latest_model)
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Loaded model from: {model_path}")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, latest_scaler)
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Loaded scaler from: {scaler_path}")
            
            # Load label encoder
            encoder_path = os.path.join(self.models_dir, latest_encoder)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info(f"Loaded label encoder from: {encoder_path}")
            
            # Load feature names
            features_path = os.path.join(self.models_dir, latest_features)
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info(f"Loaded feature names from: {features_path}")
            
            self.is_loaded = True
            logger.info("All models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
            
    def preprocess_features(self, features_dict: Dict) -> Optional[np.ndarray]:
        """Preprocess extracted features for model prediction"""
        try:
            # Convert to DataFrame
            features_df = pd.DataFrame([features_dict])
            
            # Align features with training data
            # Add missing features with default values
            missing_features = set(self.feature_names) - set(features_df.columns)
            for feature in missing_features:
                features_df[feature] = 0.0
                
            # Remove extra features
            features_df = features_df[self.feature_names]
            
            # Handle any missing values
            features_df = features_df.fillna(0.0)
            
            # Scale features
            features_scaled = self.scaler.transform(features_df.values)
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            return None
            
    def predict(self, audio_file_path: str) -> Optional[Dict]:
        """Analyze audio file and predict Parkinson's disease probability"""
        if not self.is_loaded:
            if not self.load_models():
                return None
                
        try:
            # Extract features from audio
            logger.info(f"Extracting features from: {audio_file_path}")
            features = self.feature_extractor.extract_all_features(audio_file_path)
            
            if features is None:
                logger.error("Feature extraction failed")
                return None
                
            # Preprocess features
            features_processed = self.preprocess_features(features)
            
            if features_processed is None:
                logger.error("Feature preprocessing failed")
                return None
                
            # Make prediction
            prediction_proba = self.model.predict(features_processed, verbose=0)[0][0]
            prediction_class = int(prediction_proba > 0.5)
            
            # Get class label
            class_label = self.label_encoder.inverse_transform([prediction_class])[0]
            
            # Interpret results
            result = {
                "prediction_probability": float(prediction_proba),
                "predicted_class": int(prediction_class),
                "class_label": str(class_label),
                "confidence": float(abs(prediction_proba - 0.5) * 2),  # Distance from decision boundary
                "risk_level": self._get_risk_level(prediction_proba),
                "interpretation": self._interpret_prediction(prediction_proba),
                "extracted_features": self._convert_numpy_types(features),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Prediction completed: {class_label} (probability: {prediction_proba:.4f})")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None
            
    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level based on prediction probability"""
        if probability < 0.3:
            return "Low"
        elif probability < 0.7:
            return "Moderate"
        else:
            return "High"
            
    def _interpret_prediction(self, probability: float) -> str:
        """Provide human-readable interpretation of the prediction"""
        if probability < 0.3:
            return ("The speech analysis indicates a low likelihood of Parkinson's disease. "
                   "Speech patterns appear normal with minimal indicators of motor speech disorders.")
        elif probability < 0.5:
            return ("The speech analysis suggests a low-moderate likelihood of Parkinson's disease. "
                   "Some minor speech pattern variations detected, but within normal range.")
        elif probability < 0.7:
            return ("The speech analysis indicates a moderate likelihood of Parkinson's disease. "
                   "Several speech pattern indicators suggest possible motor speech changes. "
                   "Clinical evaluation recommended.")
        else:
            return ("The speech analysis suggests a high likelihood of Parkinson's disease. "
                   "Multiple speech pattern indicators consistent with motor speech disorders. "
                   "Clinical evaluation strongly recommended.")
    
    def _convert_numpy_types(self, data):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(data, dict):
            return {key: self._convert_numpy_types(value) for key, value in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._convert_numpy_types(item) for item in data]
        elif isinstance(data, np.integer):
            return int(data)
        elif isinstance(data, np.floating):
            return float(data)
        elif isinstance(data, np.ndarray):
            return data.tolist()
        else:
            return data
                   
    def analyze_audio_from_bytes(self, audio_bytes: bytes, filename: str) -> Optional[Dict]:
        """Analyze audio from bytes data (for uploaded files)"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
            
        try:
            # Analyze the temporary file
            result = self.predict(temp_path)
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    def batch_analyze(self, audio_files: list) -> Dict:
        """Analyze multiple audio files"""
        results = {}
        
        for audio_file in audio_files:
            try:
                result = self.predict(audio_file)
                results[audio_file] = result
            except Exception as e:
                logger.error(f"Error analyzing {audio_file}: {e}")
                results[audio_file] = None
                
        return results
        
    def get_feature_importance(self) -> Optional[Dict]:
        """Get feature importance from the model (if available)"""
        # This is a placeholder - actual implementation would depend on the model architecture
        # For CNN+LSTM, feature importance is not straightforward to extract
        # You might need to use techniques like LIME or SHAP for explainability
        
        if not self.feature_names:
            return None
            
        # Return placeholder feature importance
        return {
            "message": "Feature importance analysis not implemented for CNN+LSTM models",
            "total_features": len(self.feature_names),
            "feature_categories": {
                "praat_features": len([f for f in self.feature_names if any(key in f.lower() for key in ['jitter', 'shimmer', 'hnr', 'f0'])]),
                "mfcc_features": len([f for f in self.feature_names if 'mfcc' in f.lower()]),
                "spectral_features": len([f for f in self.feature_names if 'spectral' in f.lower()]),
                "other_features": len([f for f in self.feature_names if not any(key in f.lower() for key in ['jitter', 'shimmer', 'hnr', 'f0', 'mfcc', 'spectral'])])
            }
        }

# Global service instance
speech_service = SpeechAnalysisService()

def get_speech_service():
    """Get the global speech analysis service instance"""
    return speech_service

def analyze_speech_file(audio_file_path: str) -> Optional[Dict]:
    """Convenience function to analyze a speech file"""
    service = get_speech_service()
    return service.predict(audio_file_path)

def analyze_speech_bytes(audio_bytes: bytes, filename: str) -> Optional[Dict]:
    """Convenience function to analyze speech from bytes"""
    service = get_speech_service()
    return service.analyze_audio_from_bytes(audio_bytes, filename)

if __name__ == "__main__":
    # Test the service
    service = SpeechAnalysisService()
    
    if service.load_models():
        print("Speech analysis service loaded successfully")
        print("Service ready for predictions")
    else:
        print("Failed to load speech analysis service")
        print("Please ensure the model is trained first")