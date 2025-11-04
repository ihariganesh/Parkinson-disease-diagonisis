#!/usr/bin/env python3
"""
Advanced Parkinson's Disease Detector with Transfer Learning Models
Integrates trained ResNet50 and EfficientNet models with Grad-CAM visualization
"""

import os
import sys
import numpy as np
import cv2
import json
from pathlib import Path
from datetime import datetime
import logging

try:
    import tensorflow as tf  # type: ignore
    from tensorflow import keras  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
    import matplotlib.cm as cm  # type: ignore
    TF_AVAILABLE = True
    print("✅ TensorFlow available for advanced detection")
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow not available, using fallback detection")

class AdvancedParkinsonDetector:
    def __init__(self, models_dir="/home/hari/Downloads/parkinson/parkinson-app/backend/models"):
        self.models_dir = models_dir
        self.models = {}
        self.input_shape = (224, 224, 3)
        
        if TF_AVAILABLE:
            self.load_models()
        else:
            print("⚠️ TensorFlow not available, advanced detection disabled")
    
    def load_models(self):
        """Load all trained models"""
        print("🔄 Loading trained models...")
        
        model_files = {
            'resnet50_spiral': 'resnet50_spiral_final.h5',
            'resnet50_wave': 'resnet50_wave_final.h5',
            'efficientnet_spiral': 'efficientnet_spiral_final.h5',
            'efficientnet_wave': 'efficientnet_wave_final.h5'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            
            if os.path.exists(model_path):
                try:
                    model = keras.models.load_model(model_path)
                    self.models[model_name] = model
                    print(f"✅ Loaded {model_name}")
                except Exception as e:
                    print(f"❌ Failed to load {model_name}: {e}")
            else:
                print(f"⚠️ Model file not found: {model_path}")
        
        if not self.models:
            print("❌ No models loaded successfully")
        else:
            print(f"✅ Loaded {len(self.models)} models successfully")
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            image = cv2.resize(image, self.input_shape[:2])
            
            # Normalize pixel values to [0,1]
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            return None
    
    def predict_ensemble(self, image_path, drawing_type):
        """Make ensemble prediction using multiple models"""
        if not TF_AVAILABLE or not self.models:
            return self.fallback_prediction(image_path, drawing_type)
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return self.fallback_prediction(image_path, drawing_type)
            
            # Get relevant models for the drawing type
            relevant_models = {
                name: model for name, model in self.models.items()
                if drawing_type.lower() in name.lower()
            }
            
            if not relevant_models:
                print(f"❌ No models available for {drawing_type}")
                return self.fallback_prediction(image_path, drawing_type)
            
            predictions = {}
            confidences = []
            
            # Make predictions with each relevant model
            for model_name, model in relevant_models.items():
                try:
                    pred = model.predict(processed_image, verbose=0)[0][0]
                    
                    # Calculate confidence as distance from decision boundary
                    confidence = abs(pred - 0.5) * 2
                    confidences.append(confidence)
                    
                    predictions[model_name] = {
                        'probability': float(pred),
                        'confidence': float(confidence),
                        'prediction': 'Parkinson' if pred > 0.5 else 'Healthy'
                    }
                    
                except Exception as e:
                    print(f"❌ Error with model {model_name}: {e}")
                    continue
            
            if not predictions:
                return self.fallback_prediction(image_path, drawing_type)
            
            # Ensemble decision (weighted average)
            ensemble_prob = np.mean([p['probability'] for p in predictions.values()])
            ensemble_confidence = np.max(confidences) if confidences else 0.5
            
            final_prediction = 'Parkinson' if ensemble_prob > 0.5 else 'Healthy'
            
            # Detailed analysis
            analysis_details = self.analyze_image_features(image_path, drawing_type)
            
            result = {
                'prediction': final_prediction,
                'confidence_score': float(ensemble_confidence),
                'probability': float(ensemble_prob),
                'individual_models': predictions,
                'analysis_details': analysis_details,
                'model_type': 'ensemble',
                'drawing_type': drawing_type,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Ensemble prediction: {final_prediction} (confidence: {ensemble_confidence:.2f})")
            return result
            
        except Exception as e:
            print(f"❌ Error in ensemble prediction: {e}")
            return self.fallback_prediction(image_path, drawing_type)
    
    def analyze_image_features(self, image_path, drawing_type):
        """Analyze specific features relevant to Parkinson's detection"""
        try:
            # Load original image for analysis
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return {"error": "Could not load image for feature analysis"}
            
            # Basic image analysis
            height, width = image.shape
            total_pixels = height * width
            
            # Edge detection for tremor analysis
            edges = cv2.Canny(image, 50, 150)
            edge_pixels = np.sum(edges > 0)
            edge_ratio = edge_pixels / total_pixels
            
            # Contour analysis
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_count = len(contours)
            
            # Calculate image moments for shape analysis
            moments = cv2.moments(image)
            
            # Brightness and contrast analysis
            mean_intensity = np.mean(image)
            std_intensity = np.std(image)
            
            features = {
                'image_dimensions': [int(width), int(height)],
                'edge_ratio': float(edge_ratio),
                'contour_count': int(contour_count),
                'mean_intensity': float(mean_intensity),
                'std_intensity': float(std_intensity),
                'drawing_type': drawing_type
            }
            
            # Drawing-specific analysis
            if drawing_type.lower() == 'spiral':
                features.update(self.analyze_spiral_features(image))
            elif drawing_type.lower() == 'wave':
                features.update(self.analyze_wave_features(image))
            
            return features
            
        except Exception as e:
            return {"error": f"Feature analysis failed: {str(e)}"}
    
    def analyze_spiral_features(self, image):
        """Analyze spiral-specific features"""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {"spiral_analysis": "No contours found"}
            
            # Get the largest contour (assuming it's the spiral)
            main_contour = max(contours, key=cv2.contourArea)
            
            # Calculate spiral properties
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            
            # Compactness (measure of how circular/smooth the spiral is)
            compactness = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # Convex hull analysis (tremor indicator)
            hull = cv2.convexHull(main_contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            return {
                'spiral_area': float(area),
                'spiral_perimeter': float(perimeter),
                'spiral_compactness': float(compactness),
                'spiral_solidity': float(solidity),
                'tremor_indicator': float(1 - solidity)  # Lower solidity = more tremor
            }
            
        except Exception as e:
            return {"spiral_analysis_error": str(e)}
    
    def analyze_wave_features(self, image):
        """Analyze wave-specific features"""
        try:
            # Find the main horizontal line of the wave
            height, width = image.shape
            
            # Get horizontal profile (sum along y-axis)
            horizontal_profile = np.sum(image, axis=0)
            
            # Find peaks in the horizontal profile
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(horizontal_profile, height=np.max(horizontal_profile) * 0.3)
            
            # Calculate wave properties
            if len(peaks) > 1:
                # Wave frequency (peaks per unit length)
                wave_frequency = len(peaks) / width
                
                # Peak distances (regularity measure)
                peak_distances = np.diff(peaks)
                distance_variance = np.var(peak_distances) if len(peak_distances) > 1 else 0
                
                # Amplitude analysis
                peak_heights = horizontal_profile[peaks]
                amplitude_variance = np.var(peak_heights) if len(peak_heights) > 1 else 0
                
                return {
                    'wave_frequency': float(wave_frequency),
                    'peak_count': int(len(peaks)),
                    'distance_variance': float(distance_variance),
                    'amplitude_variance': float(amplitude_variance),
                    'regularity_score': float(1 / (1 + distance_variance))  # Higher = more regular
                }
            else:
                return {
                    'wave_analysis': 'Insufficient peaks detected',
                    'peak_count': int(len(peaks))
                }
                
        except Exception as e:
            return {"wave_analysis_error": str(e)}
    
    def generate_gradcam(self, image_path, drawing_type, layer_name=None):
        """Generate Grad-CAM visualization"""
        if not TF_AVAILABLE or not self.models:
            return None
        
        try:
            # Get the best model for this drawing type
            model_name = f"resnet50_{drawing_type.lower()}"
            if model_name not in self.models:
                return None
            
            model = self.models[model_name]
            
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return None
            
            # If no layer specified, use the last convolutional layer
            if layer_name is None:
                for layer in reversed(model.layers):
                    if len(layer.output_shape) == 4:  # Convolutional layer
                        layer_name = layer.name
                        break
            
            # Create Grad-CAM model
            grad_model = keras.models.Model(
                inputs=model.input,
                outputs=[model.get_layer(layer_name).output, model.output]
            )
            
            # Generate Grad-CAM
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(processed_image)
                class_channel = predictions[:, 0]
            
            # Compute gradients
            grads = tape.gradient(class_channel, conv_outputs)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            
            # Generate heatmap
            conv_outputs = conv_outputs[0]
            heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            
            # Convert to numpy
            heatmap = heatmap.numpy()
            
            # Resize heatmap to match original image size
            original_image = cv2.imread(image_path)
            heatmap = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
            
            # Create overlay
            heatmap = np.uint8(255 * heatmap)
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            # Combine with original image
            overlay = cv2.addWeighted(original_image, 0.6, heatmap, 0.4, 0)
            
            # Save Grad-CAM result
            gradcam_path = image_path.replace('.png', '_gradcam.png').replace('.jpg', '_gradcam.jpg')
            cv2.imwrite(gradcam_path, overlay)
            
            return {
                'gradcam_path': gradcam_path,
                'layer_name': layer_name,
                'explanation': 'Red areas indicate regions the model focused on for prediction'
            }
            
        except Exception as e:
            print(f"❌ Error generating Grad-CAM: {e}")
            return None
    
    def fallback_prediction(self, image_path, drawing_type):
        """Fallback prediction when TensorFlow models aren't available"""
        try:
            # Basic file and image analysis
            file_size = os.path.getsize(image_path)
            
            # Load image for basic analysis
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                mean_intensity = np.mean(image)
                std_intensity = np.std(image)
                
                # Simple heuristic based on image properties and file size
                complexity_score = (std_intensity / mean_intensity) * (file_size / 10000)
                
                if drawing_type.lower() == 'spiral':
                    # Spiral analysis heuristic
                    confidence = min(0.9, 0.5 + (complexity_score * 0.1))
                    prediction = "Parkinson" if complexity_score > 3.0 else "Healthy"
                else:
                    # Wave analysis heuristic
                    confidence = min(0.85, 0.5 + (complexity_score * 0.08))
                    prediction = "Parkinson" if complexity_score > 3.5 else "Healthy"
            else:
                # If image can't be loaded, random prediction
                confidence = 0.5
                prediction = "Healthy"
            
            return {
                'prediction': prediction,
                'confidence_score': confidence,
                'probability': 0.7 if prediction == "Parkinson" else 0.3,
                'analysis_details': {
                    'method': 'fallback_heuristic',
                    'file_size': file_size,
                    'complexity_score': float(complexity_score) if 'complexity_score' in locals() else 0
                },
                'model_type': 'fallback',
                'drawing_type': drawing_type,
                'timestamp': datetime.now().isoformat(),
                'note': 'Advanced ML models not available, using basic heuristics'
            }
            
        except Exception as e:
            return {
                'prediction': 'Error',
                'confidence_score': 0.0,
                'probability': 0.0,
                'analysis_details': {'error': str(e)},
                'model_type': 'error',
                'drawing_type': drawing_type,
                'timestamp': datetime.now().isoformat()
            }

# Global detector instance
detector = None

def get_detector():
    """Get or create detector instance"""
    global detector
    if detector is None:
        detector = AdvancedParkinsonDetector()
    return detector

def analyze_handwriting(image_path, drawing_type):
    """Main interface for handwriting analysis"""
    detector = get_detector()
    
    # Make prediction
    result = detector.predict_ensemble(image_path, drawing_type)
    
    # Generate Grad-CAM if possible
    if TF_AVAILABLE and detector.models:
        gradcam_result = detector.generate_gradcam(image_path, drawing_type)
        if gradcam_result:
            result['gradcam'] = gradcam_result
    
    return result

if __name__ == "__main__":
    # Test the detector
    print("🧠 Testing Advanced Parkinson Detector")
    
    # Test with a sample image (you can add your test image path here)
    test_image = "/home/hari/Downloads/parkinson/handwritings/drawings/spiral/testing/healthy/V01HE01.png"
    
    if os.path.exists(test_image):
        result = analyze_handwriting(test_image, "spiral")
        print(json.dumps(result, indent=2))
    else:
        print("No test image found. Please check the path.")
        
        # Show available test images
        test_dir = "/home/hari/Downloads/parkinson/handwritings/drawings/spiral/testing/healthy"
        if os.path.exists(test_dir):
            test_files = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg'))]
            if test_files:
                print(f"Available test images: {test_files[:3]}")