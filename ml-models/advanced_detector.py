"""
Advanced Parkinson's Detection System using Transfer Learning Models
Integrates ResNet, EfficientNet, MobileNetV2, Vision Transformer, and Ensemble models
"""

import os
import numpy as np  # type: ignore
import cv2  # type: ignore
import tensorflow as tf  # type: ignore
from tensorflow import keras  # type: ignore
import joblib  # type: ignore
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AdvancedParkinsonsDetector:
    def __init__(self, model_dir="trained_models"):
        """
        Initialize the advanced detector with all trained models
        
        Args:
            model_dir: Directory containing the trained models
        """
        self.model_dir = Path(model_dir)
        self.models = {}
        self.img_size = (224, 224)
        
        # Load all available models
        self.load_models()
        
        # Model confidence thresholds (optimized)
        self.thresholds = {
            'resnet50': 0.5,
            'efficientnet': 0.5,
            'mobilenetv2': 0.5,
            'vision_transformer': 0.5,
            'ensemble': 0.5
        }
        
        # Model weights for ensemble prediction
        self.model_weights = {
            'resnet50': 0.25,
            'efficientnet': 0.25,
            'mobilenetv2': 0.20,
            'vision_transformer': 0.15,
            'ensemble': 0.15
        }
    
    def load_models(self):
        """Load all trained models"""
        print("Loading trained models...")
        
        model_files = {
            'resnet50': 'resnet50_best.h5',
            'efficientnet': 'efficientnet_best.h5',
            'mobilenetv2': 'mobilenetv2_best.h5',
            'vision_transformer': 'vision_transformer_best.h5',
            'ensemble': 'ensemble_best.h5'
        }
        
        for model_name, filename in model_files.items():
            model_path = self.model_dir / filename
            if model_path.exists():
                try:
                    self.models[model_name] = keras.models.load_model(str(model_path))
                    print(f"✓ Loaded {model_name}")
                except Exception as e:
                    print(f"✗ Failed to load {model_name}: {str(e)}")
            else:
                print(f"✗ Model file not found: {filename}")
        
        if not self.models:
            print("Warning: No models loaded. Using fallback prediction.")
        else:
            print(f"Successfully loaded {len(self.models)} models")
    
    def preprocess_image(self, image_path_or_array):
        """
        Preprocess image for model prediction
        
        Args:
            image_path_or_array: Path to image file or numpy array
        
        Returns:
            preprocessed_image: Normalized image array ready for prediction
        """
        try:
            # Load image
            if isinstance(image_path_or_array, (str, Path)):
                image = cv2.imread(str(image_path_or_array))
                if image is None:
                    raise ValueError(f"Could not load image from {image_path_or_array}")
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image = image_path_or_array.copy()
            
            # Resize to model input size
            image = cv2.resize(image, self.img_size)
            
            # Normalize
            image = image.astype('float32') / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None
    
    def predict_single_model(self, image, model_name):
        """
        Make prediction using a single model
        
        Args:
            image: Preprocessed image array
            model_name: Name of the model to use
        
        Returns:
            dict: Prediction results
        """
        if model_name not in self.models:
            return None
        
        try:
            model = self.models[model_name]
            prediction = model.predict(image, verbose=0)[0][0]
            
            # Apply threshold
            threshold = self.thresholds.get(model_name, 0.5)
            predicted_class = int(prediction > threshold)
            confidence = float(prediction if predicted_class == 1 else 1 - prediction)
            
            return {
                'model': model_name,
                'raw_prediction': float(prediction),
                'predicted_class': predicted_class,
                'predicted_label': 'Parkinson' if predicted_class == 1 else 'Healthy',
                'confidence': confidence,
                'threshold_used': threshold
            }
            
        except Exception as e:
            print(f"Error in {model_name} prediction: {str(e)}")
            return None
    
    def predict_ensemble_voting(self, image):
        """
        Make ensemble prediction using voting
        
        Args:
            image: Preprocessed image array
        
        Returns:
            dict: Ensemble prediction results
        """
        predictions = []
        model_results = {}
        
        # Get predictions from all models
        for model_name in self.models.keys():
            result = self.predict_single_model(image, model_name)
            if result:
                predictions.append(result)
                model_results[model_name] = result
        
        if not predictions:
            return self.fallback_prediction(image)
        
        # Weighted voting
        weighted_score = 0
        total_weight = 0
        
        for result in predictions:
            model_name = result['model']
            weight = self.model_weights.get(model_name, 0.2)
            weighted_score += result['raw_prediction'] * weight
            total_weight += weight
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = np.mean([r['raw_prediction'] for r in predictions])
        
        # Final prediction
        final_class = int(final_score > 0.5)
        final_confidence = float(final_score if final_class == 1 else 1 - final_score)
        
        # Calculate agreement metrics
        class_predictions = [r['predicted_class'] for r in predictions]
        agreement = np.mean(np.array(class_predictions) == final_class)
        
        return {
            'ensemble_prediction': {
                'raw_prediction': float(final_score),
                'predicted_class': final_class,
                'predicted_label': 'Parkinson' if final_class == 1 else 'Healthy',
                'confidence': final_confidence,
                'model_agreement': float(agreement),
                'models_used': len(predictions)
            },
            'individual_models': model_results,
            'prediction_summary': self.generate_prediction_summary(model_results, final_class, final_confidence)
        }
    
    def generate_prediction_summary(self, model_results, final_class, final_confidence):
        """Generate a comprehensive prediction summary"""
        if not model_results:
            return "No valid predictions available."
        
        parkinson_votes = sum(1 for r in model_results.values() if r['predicted_class'] == 1)
        healthy_votes = len(model_results) - parkinson_votes
        
        summary = {
            'final_diagnosis': 'Parkinson' if final_class == 1 else 'Healthy',
            'confidence_level': self.get_confidence_level(final_confidence),
            'confidence_score': f"{final_confidence:.1%}",
            'model_consensus': f"{parkinson_votes} models predict Parkinson, {healthy_votes} predict Healthy",
            'individual_confidences': {
                name: f"{result['confidence']:.1%}" 
                for name, result in model_results.items()
            },
            'recommendation': self.generate_recommendation(final_class, final_confidence, parkinson_votes, len(model_results))
        }
        
        return summary
    
    def get_confidence_level(self, confidence):
        """Convert confidence score to level"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Moderate"
        elif confidence >= 0.6:
            return "Low"
        else:
            return "Very Low"
    
    def generate_recommendation(self, predicted_class, confidence, parkinson_votes, total_models):
        """Generate clinical recommendation"""
        if predicted_class == 1:  # Parkinson predicted
            if confidence >= 0.8 and parkinson_votes >= total_models * 0.7:
                return "Strong indicators suggest consulting a neurologist for comprehensive evaluation."
            elif confidence >= 0.6:
                return "Some indicators present. Consider consulting a healthcare professional for further assessment."
            else:
                return "Weak indicators detected. Continue monitoring and consider professional consultation if symptoms persist."
        else:  # Healthy predicted
            if confidence >= 0.8:
                return "Drawing patterns appear normal. Continue regular health monitoring."
            else:
                return "Patterns appear mostly normal, but continue monitoring for any changes."
    
    def fallback_prediction(self, image):
        """Fallback prediction when no models are available"""
        print("Using fallback prediction method...")
        
        # Simple image analysis fallback
        try:
            img_array = image[0] if len(image.shape) == 4 else image
            
            # Calculate some basic features as fallback
            gray = cv2.cvtColor((img_array * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            
            # Simple tremor detection based on line smoothness
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Analyze the largest contour (presumably the main drawing)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate contour properties
                perimeter = cv2.arcLength(largest_contour, True)
                area = cv2.contourArea(largest_contour)
                
                if perimeter > 0:
                    compactness = (perimeter ** 2) / (4 * np.pi * area) if area > 0 else float('inf')
                    
                    # Simple heuristic: higher compactness might indicate tremor
                    tremor_score = min(compactness / 10.0, 1.0)  # Normalize
                    
                    predicted_class = int(tremor_score > 0.5)
                    confidence = tremor_score if predicted_class == 1 else 1 - tremor_score
                    
                    return {
                        'ensemble_prediction': {
                            'raw_prediction': float(tremor_score),
                            'predicted_class': predicted_class,
                            'predicted_label': 'Parkinson' if predicted_class == 1 else 'Healthy',
                            'confidence': float(confidence),
                            'model_agreement': 1.0,
                            'models_used': 1
                        },
                        'individual_models': {
                            'fallback': {
                                'model': 'fallback',
                                'predicted_class': predicted_class,
                                'predicted_label': 'Parkinson' if predicted_class == 1 else 'Healthy',
                                'confidence': float(confidence)
                            }
                        },
                        'prediction_summary': {
                            'final_diagnosis': 'Parkinson' if predicted_class == 1 else 'Healthy',
                            'confidence_level': self.get_confidence_level(confidence),
                            'confidence_score': f"{confidence:.1%}",
                            'recommendation': "This is a basic analysis. Please consult a medical professional for accurate diagnosis."
                        }
                    }
        
        except Exception as e:
            print(f"Fallback prediction error: {str(e)}")
        
        # Ultimate fallback
        return {
            'ensemble_prediction': {
                'raw_prediction': 0.5,
                'predicted_class': 0,
                'predicted_label': 'Uncertain',
                'confidence': 0.0,
                'model_agreement': 0.0,
                'models_used': 0
            },
            'individual_models': {},
            'prediction_summary': {
                'final_diagnosis': 'Uncertain',
                'confidence_level': 'Very Low',
                'confidence_score': '0.0%',
                'recommendation': "Unable to analyze. Please consult a medical professional."
            }
        }
    
    def analyze_handwriting(self, image_path_or_array, drawing_type="spiral"):
        """
        Main function to analyze handwriting sample
        
        Args:
            image_path_or_array: Path to image or image array
            drawing_type: Type of drawing (spiral or wave)
        
        Returns:
            dict: Complete analysis results
        """
        print(f"Analyzing {drawing_type} drawing...")
        
        # Preprocess image
        processed_image = self.preprocess_image(image_path_or_array)
        if processed_image is None:
            return {'error': 'Failed to preprocess image'}
        
        # Get ensemble prediction
        results = self.predict_ensemble_voting(processed_image)
        
        # Add metadata
        results['metadata'] = {
            'drawing_type': drawing_type,
            'analysis_timestamp': datetime.now().isoformat(),
            'models_available': list(self.models.keys()),
            'image_size': self.img_size,
            'preprocessing_successful': True
        }
        
        return results
    
    def batch_analyze(self, image_paths, drawing_types=None):
        """
        Analyze multiple images
        
        Args:
            image_paths: List of image paths
            drawing_types: List of drawing types (optional)
        
        Returns:
            list: List of analysis results
        """
        results = []
        
        if drawing_types is None:
            drawing_types = ["spiral"] * len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            drawing_type = drawing_types[i] if i < len(drawing_types) else "spiral"
            result = self.analyze_handwriting(image_path, drawing_type)
            result['image_path'] = str(image_path)
            results.append(result)
        
        return results
    
    def get_model_info(self):
        """Get information about loaded models"""
        info = {
            'total_models': len(self.models),
            'available_models': list(self.models.keys()),
            'model_weights': self.model_weights,
            'thresholds': self.thresholds,
            'input_size': self.img_size
        }
        
        return info

# Convenience functions for easy integration
def create_detector():
    """Create and return a detector instance"""
    return AdvancedParkinsonsDetector()

def analyze_image(image_path, drawing_type="spiral"):
    """Quick analysis of a single image"""
    detector = create_detector()
    return detector.analyze_handwriting(image_path, drawing_type)

def analyze_uploaded_file(file_content, drawing_type="spiral"):
    """Analyze uploaded file content"""
    import io
    from PIL import Image
    
    try:
        # Convert file content to image array
        image = Image.open(io.BytesIO(file_content))
        image_array = np.array(image.convert('RGB'))
        
        detector = create_detector()
        return detector.analyze_handwriting(image_array, drawing_type)
        
    except Exception as e:
        return {'error': f'Failed to process uploaded file: {str(e)}'}

if __name__ == "__main__":
    # Test the detector
    detector = create_detector()
    print("Advanced Parkinson's Detector initialized")
    print(f"Models loaded: {list(detector.models.keys())}")
    
    # Test with a sample image if available
    test_image_path = "/home/hari/Downloads/parkinson/parkinson-app/archive/drawings/spiral/testing/healthy"
    if Path(test_image_path).exists():
        test_files = list(Path(test_image_path).glob("*.png"))
        if test_files:
            print(f"\nTesting with: {test_files[0]}")
            result = detector.analyze_handwriting(test_files[0])
            print("\nTest Results:")
            print(json.dumps(result['prediction_summary'], indent=2))