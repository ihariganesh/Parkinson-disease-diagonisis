"""
Enhanced Speech Analysis Service for Parkinson's Disease Detection
Version 2.0 - Addresses feature mismatch and validation issues
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
import os
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import tempfile
import shutil
import warnings

from speech_feature_extractor import SpeechFeatureExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechAnalysisServiceV2:
    def __init__(self, models_dir="models/speech"):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.expected_features = None
        self.feature_extractor = SpeechFeatureExtractor()
        self.is_loaded = False
        self.feature_stats = None
        
        # Get feature statistics
        self._initialize_feature_stats()
        
    def _initialize_feature_stats(self):
        """Initialize feature extraction statistics"""
        try:
            self.feature_stats = self.feature_extractor.get_feature_statistics()
            if self.feature_stats:
                logger.info(f"✓ Feature extractor initialized: {self.feature_stats['total_features']} features available")
                logger.info(f"✓ Parselmouth available: {self.feature_stats['parselmouth_available']}")
            else:
                logger.warning("⚠️  Could not initialize feature statistics")
        except Exception as e:
            logger.error(f"❌ Error initializing feature stats: {e}")
            self.feature_stats = None
    
    def validate_feature_compatibility(self) -> Dict:
        """Validate compatibility between model and feature extractor"""
        if not self.is_loaded:
            return {
                'compatible': False,
                'error': 'Model not loaded'
            }
            
        if not self.feature_stats:
            return {
                'compatible': False,
                'error': 'Feature statistics not available'
            }
            
        extractable_features = self.feature_stats['total_features']
        expected_features = len(self.feature_names) if self.feature_names else 0
        
        if expected_features == 0:
            return {
                'compatible': False,
                'error': 'Model feature names not available'
            }
            
        # Calculate compatibility metrics
        if extractable_features == expected_features:
            compatibility_score = 1.0
            status = 'perfect'
        else:
            # Check how many features match
            available_feature_names = set(self.feature_stats['feature_names'])
            expected_feature_names = set(self.feature_names)
            matching_features = len(available_feature_names.intersection(expected_feature_names))
            
            compatibility_score = matching_features / expected_features
            if compatibility_score >= 0.8:
                status = 'good'
            elif compatibility_score >= 0.5:
                status = 'moderate'
            else:
                status = 'poor'
        
        return {
            'compatible': compatibility_score >= 0.5,
            'compatibility_score': compatibility_score,
            'status': status,
            'extractable_features': extractable_features,
            'expected_features': expected_features,
            'matching_features': matching_features if 'matching_features' in locals() else extractable_features,
            'missing_features': expected_features - extractable_features if expected_features > extractable_features else 0,
            'parselmouth_available': self.feature_stats['parselmouth_available'],
            'feature_breakdown': self.feature_stats['feature_categories']
        }
        
    def load_models(self):
        """Load the trained model and preprocessors with validation"""
        try:
            # Find the latest model files
            if not os.path.exists(self.models_dir):
                logger.error(f"❌ Models directory not found: {self.models_dir}")
                return False
                
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.h5')]
            scaler_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_scaler') and f.endswith('.pkl')]
            encoder_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_label_encoder') and f.endswith('.pkl')]
            feature_files = [f for f in os.listdir(self.models_dir) if f.startswith('speech_feature_names') and f.endswith('.pkl')]
            
            if not (model_files and scaler_files and encoder_files and feature_files):
                logger.error("❌ Required model files not found. Please train the model first.")
                logger.info("Missing files:")
                if not model_files: logger.info("  - Model file (.h5)")
                if not scaler_files: logger.info("  - Scaler file (.pkl)")
                if not encoder_files: logger.info("  - Label encoder file (.pkl)")
                if not feature_files: logger.info("  - Feature names file (.pkl)")
                return False
                
            # Use the latest files (assuming timestamp in filename)
            latest_model = sorted(model_files)[-1]
            latest_scaler = sorted(scaler_files)[-1]
            latest_encoder = sorted(encoder_files)[-1]
            latest_features = sorted(feature_files)[-1]
            
            # Load model
            model_path = os.path.join(self.models_dir, latest_model)
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"✓ Loaded model from: {model_path}")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, latest_scaler)
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"✓ Loaded scaler from: {scaler_path}")
            
            # Load label encoder
            encoder_path = os.path.join(self.models_dir, latest_encoder)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info(f"✓ Loaded label encoder from: {encoder_path}")
            
            # Load feature names
            features_path = os.path.join(self.models_dir, latest_features)
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info(f"✓ Loaded feature names from: {features_path}")
            
            self.is_loaded = True
            
            # Validate feature compatibility
            compatibility = self.validate_feature_compatibility()
            logger.info(f"🔍 Feature Compatibility Check:")
            logger.info(f"   Status: {compatibility['status'].upper()}")
            logger.info(f"   Score: {compatibility['compatibility_score']:.2%}")
            logger.info(f"   Expected features: {compatibility['expected_features']}")
            logger.info(f"   Extractable features: {compatibility['extractable_features']}")
            logger.info(f"   Matching features: {compatibility['matching_features']}")
            
            if compatibility['missing_features'] > 0:
                logger.warning(f"⚠️  {compatibility['missing_features']} features will be zero-padded")
                
            if not compatibility['compatible']:
                logger.error("❌ Model and feature extractor are not compatible!")
                logger.error("   Recommendation: Retrain model with current feature extractor")
                return False
            elif compatibility['status'] == 'poor':
                logger.warning("⚠️  Poor compatibility detected. Model may perform poorly.")
                
            logger.info("✓ All models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            self.is_loaded = False
            return False
            
    def preprocess_features(self, features_dict: Dict) -> Optional[np.ndarray]:
        """Preprocess extracted features for model prediction with validation"""
        try:
            # Convert to DataFrame
            features_df = pd.DataFrame([features_dict])
            
            # Log feature extraction results
            extracted_count = len(features_df.columns)
            expected_count = len(self.feature_names)
            
            logger.debug(f"Extracted {extracted_count} features, expected {expected_count}")
            
            # Align features with training data
            missing_features = set(self.feature_names) - set(features_df.columns)
            extra_features = set(features_df.columns) - set(self.feature_names)
            
            if missing_features:
                logger.debug(f"Adding {len(missing_features)} missing features with default values")
                for feature in missing_features:
                    features_df[feature] = 0.0
                    
            if extra_features:
                logger.debug(f"Removing {len(extra_features)} extra features")
                
            # Remove extra features and reorder to match training data
            features_df = features_df[self.feature_names]
            
            # Handle any missing values
            features_df = features_df.fillna(0.0)
            
            # Scale features
            features_scaled = self.scaler.transform(features_df.values)
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing features: {e}")
            return None
            
    def predict(self, audio_file_path: str) -> Optional[Dict]:
        """Analyze audio file and predict Parkinson's disease probability with validation"""
        if not self.is_loaded:
            if not self.load_models():
                return None
                
        try:
            # Extract features from audio
            logger.info(f"🎵 Extracting features from: {audio_file_path}")
            features = self.feature_extractor.extract_all_features(audio_file_path)
            
            if features is None:
                logger.error("❌ Feature extraction failed")
                return None
                
            # Log feature extraction summary
            logger.info(f"✓ Extracted {len(features)} features")
            
            # Preprocess features
            features_processed = self.preprocess_features(features)
            
            if features_processed is None:
                logger.error("❌ Feature preprocessing failed")
                return None
                
            # Make prediction
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                prediction_proba = self.model.predict(features_processed, verbose=0)[0][0]
                
            prediction_class = int(prediction_proba > 0.5)
            
            # Get class label
            class_label = self.label_encoder.inverse_transform([prediction_class])[0]
            
            # Get compatibility info for result
            compatibility = self.validate_feature_compatibility()
            
            # Interpret results
            result = {
                "prediction_probability": float(prediction_proba),
                "predicted_class": int(prediction_class),
                "class_label": str(class_label),
                "confidence": float(abs(prediction_proba - 0.5) * 2),  # Distance from decision boundary
                "risk_level": self._get_risk_level(prediction_proba),
                "interpretation": self._interpret_prediction(prediction_proba),
                "extracted_features": self._convert_numpy_types(features),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_info": {
                    "feature_compatibility": compatibility['status'],
                    "compatibility_score": compatibility['compatibility_score'],
                    "extractable_features": compatibility['extractable_features'],
                    "expected_features": compatibility['expected_features'],
                    "parselmouth_available": compatibility['parselmouth_available']
                }
            }
            
            logger.info(f"✓ Prediction completed: {class_label} (probability: {prediction_proba:.4f})")
            
            # Add warning if compatibility is poor
            if compatibility['status'] == 'poor':
                result["warning"] = "Low feature compatibility detected. Results may be unreliable. Consider retraining the model."
            elif compatibility['status'] == 'moderate':
                result["warning"] = "Moderate feature compatibility. Results should be interpreted cautiously."
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during prediction: {e}")
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
                
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        compatibility = self.validate_feature_compatibility() if self.is_loaded else None
        
        return {
            "service_version": "2.0",
            "model_loaded": self.is_loaded,
            "feature_extractor": {
                "available": self.feature_stats is not None,
                "features_count": self.feature_stats['total_features'] if self.feature_stats else 0,
                "total_features": self.feature_stats['total_features'] if self.feature_stats else 0,
                "parselmouth_available": self.feature_stats['parselmouth_available'] if self.feature_stats else False,
                "feature_categories": self.feature_stats['feature_categories'] if self.feature_stats else {},
                "dependencies_available": self.feature_stats['dependencies'] if self.feature_stats else {}
            },
            "compatibility": compatibility,
            "recommendations": self._get_recommendations()
        }
        
    def _get_recommendations(self) -> List[str]:
        """Get system recommendations based on current state"""
        recommendations = []
        
        if not self.is_loaded:
            recommendations.append("Load the trained model to enable predictions")
            
        if self.feature_stats and not self.feature_stats['parselmouth_available']:
            recommendations.append("Install parselmouth for better feature extraction: pip install praat-parselmouth")
            
        if self.is_loaded:
            compatibility = self.validate_feature_compatibility()
            if compatibility['status'] == 'poor':
                recommendations.append("Retrain the model with current feature extractor for better accuracy")
            elif compatibility['status'] == 'moderate':
                recommendations.append("Consider retraining the model for optimal performance")
                
        return recommendations
    
    def analyze_audio(self, audio_file_path: str) -> Optional[Dict]:
        """Convenience method to analyze audio file by path (for compatibility)"""
        return self.analyze_audio_file(audio_file_path)
    
    def analyze_audio_file(self, audio_file_path: str) -> Optional[Dict]:
        """Analyze audio file and return prediction results"""
        try:
            # Load the audio file
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            
            return self.analyze_audio_from_bytes(audio_bytes, os.path.basename(audio_file_path))
            
        except Exception as e:
            logger.error(f"Error analyzing audio file: {e}")
            return None

# Global service instance
speech_service_v2 = SpeechAnalysisServiceV2()

def get_speech_service_v2():
    """Get the enhanced speech analysis service instance"""
    return speech_service_v2

def analyze_speech_file_v2(audio_file_path: str) -> Optional[Dict]:
    """Convenience function to analyze a speech file with v2 service"""
    service = get_speech_service_v2()
    return service.predict(audio_file_path)

def analyze_speech_bytes_v2(audio_bytes: bytes, filename: str) -> Optional[Dict]:
    """Convenience function to analyze speech from bytes with v2 service"""
    service = get_speech_service_v2()
    return service.analyze_audio_from_bytes(audio_bytes, filename)

if __name__ == "__main__":
    # Test the enhanced service
    service = SpeechAnalysisServiceV2()
    
    # Get system info
    info = service.get_system_info()
    print("=== Speech Analysis Service V2 ===")
    print(f"Service Version: {info['service_version']}")
    print(f"Feature Extractor Available: {info['feature_extractor']['available']}")
    print(f"Total Features: {info['feature_extractor']['total_features']}")
    print(f"Parselmouth Available: {info['feature_extractor']['parselmouth_available']}")
    
    if info['recommendations']:
        print("\nRecommendations:")
        for rec in info['recommendations']:
            print(f"  - {rec}")
    
    # Try to load models
    if service.load_models():
        print("\n✓ Service ready for predictions")
        
        # Test with available audio files
        test_files = ["test_audio.wav", "test_audio.mp3"]
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\n=== Testing with {test_file} ===")
                result = service.predict(test_file)
                if result:
                    print(f"✓ Prediction: {result['class_label']} (probability: {result['prediction_probability']:.4f})")
                    print(f"✓ Confidence: {result['confidence']:.4f}")
                    print(f"✓ Feature compatibility: {result['model_info']['feature_compatibility']}")
                else:
                    print(f"❌ Failed to analyze {test_file}")
                break
    else:
        print("\n❌ Failed to load models")
        print("Please ensure the model is trained first")