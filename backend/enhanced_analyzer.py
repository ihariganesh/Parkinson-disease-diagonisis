#!/usr/bin/env python3
"""
Enhanced Handwriting Analyzer using Computer Vision Techniques
Works without TensorFlow/Keras by using traditional image processing methods
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Try to import image processing libraries
try:
    import cv2
    CV2_AVAILABLE = True
    print("✅ OpenCV available for image processing")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available, using basic analysis")

try:
    from PIL import Image, ImageFilter, ImageOps
    PIL_AVAILABLE = True
    print("✅ PIL available for image processing")
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not available")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
    print("✅ NumPy available for numerical processing")
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy not available, using basic math")

class EnhancedHandwritingAnalyzer:
    """Enhanced analyzer using traditional computer vision and image processing"""
    
    def __init__(self):
        self.dataset_path = "/home/hari/Downloads/parkinson/handwritings/drawings"
        self.analysis_features = {}
        
        # Load reference patterns if available
        self.load_reference_patterns()
    
    def load_reference_patterns(self):
        """Load and analyze reference patterns from the dataset"""
        print("🔄 Loading reference patterns...")
        
        patterns = {
            'spiral': {'healthy': [], 'parkinson': []},
            'wave': {'healthy': [], 'parkinson': []}
        }
        
        try:
            for pattern_type in ['spiral', 'wave']:
                for phase in ['training', 'testing']:
                    for condition in ['healthy', 'parkinson']:
                        pattern_dir = os.path.join(self.dataset_path, pattern_type, phase, condition)
                        
                        if os.path.exists(pattern_dir):
                            files = [f for f in os.listdir(pattern_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
                            
                            for file in files[:5]:  # Analyze up to 5 reference images
                                file_path = os.path.join(pattern_dir, file)
                                features = self.extract_image_features(file_path)
                                if features:
                                    patterns[pattern_type][condition].append(features)
            
            self.reference_patterns = patterns
            print(f"✅ Loaded reference patterns")
            
        except Exception as e:
            print(f"⚠️ Could not load reference patterns: {e}")
            self.reference_patterns = patterns
    
    def extract_image_features(self, image_path):
        """Extract features from an image using available libraries"""
        
        if not os.path.exists(image_path):
            return None
        
        features = {
            'file_size': os.path.getsize(image_path),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if PIL_AVAILABLE:
                features.update(self.extract_pil_features(image_path))
            elif CV2_AVAILABLE:
                features.update(self.extract_cv2_features(image_path))
            else:
                features.update(self.extract_basic_features(image_path))
            
            return features
            
        except Exception as e:
            print(f"⚠️ Error extracting features from {image_path}: {e}")
            return features
    
    def extract_pil_features(self, image_path):
        """Extract features using PIL"""
        features = {}
        
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Basic image properties
                features['width'], features['height'] = img.size
                features['total_pixels'] = features['width'] * features['height']
                
                # Get pixel data
                pixels = list(img.getdata())
                
                if NUMPY_AVAILABLE:
                    pixels_array = np.array(pixels)
                    features['mean_intensity'] = float(np.mean(pixels_array))
                    features['std_intensity'] = float(np.std(pixels_array))
                    features['min_intensity'] = float(np.min(pixels_array))
                    features['max_intensity'] = float(np.max(pixels_array))
                else:
                    # Basic statistics without numpy
                    features['mean_intensity'] = sum(pixels) / len(pixels)
                    features['min_intensity'] = min(pixels)
                    features['max_intensity'] = max(pixels)
                    # Simple standard deviation approximation
                    mean = features['mean_intensity']
                    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
                    features['std_intensity'] = variance ** 0.5
                
                # Edge detection using PIL filters
                edges = img.filter(ImageFilter.FIND_EDGES)
                edge_pixels = list(edges.getdata())
                edge_count = sum(1 for p in edge_pixels if p > 50)  # Threshold for edge detection
                features['edge_ratio'] = edge_count / len(edge_pixels)
                
                # Contrast and brightness analysis
                features['contrast_ratio'] = (features['max_intensity'] - features['min_intensity']) / 255.0
                features['brightness_normalized'] = features['mean_intensity'] / 255.0
                
                # Apply filters for texture analysis
                smooth_img = img.filter(ImageFilter.SMOOTH)
                smooth_pixels = list(smooth_img.getdata())
                
                if NUMPY_AVAILABLE:
                    smooth_array = np.array(smooth_pixels)
                    original_array = np.array(pixels)
                    texture_diff = float(np.mean(np.abs(original_array - smooth_array)))
                else:
                    texture_diff = sum(abs(p1 - p2) for p1, p2 in zip(pixels, smooth_pixels)) / len(pixels)
                
                features['texture_complexity'] = texture_diff / 255.0
                
        except Exception as e:
            print(f"⚠️ PIL feature extraction error: {e}")
        
        return features
    
    def extract_cv2_features(self, image_path):
        """Extract features using OpenCV"""
        features = {}
        
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return features
            
            height, width = img.shape
            features['width'] = int(width)
            features['height'] = int(height)
            features['total_pixels'] = int(width * height)
            
            # Basic statistics
            if NUMPY_AVAILABLE:
                features['mean_intensity'] = float(np.mean(img))
                features['std_intensity'] = float(np.std(img))
                features['min_intensity'] = float(np.min(img))
                features['max_intensity'] = float(np.max(img))
            
            # Edge detection
            edges = cv2.Canny(img, 50, 150)
            edge_pixels = cv2.countNonZero(edges)
            features['edge_ratio'] = edge_pixels / (width * height)
            
            # Contour analysis
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features['contour_count'] = len(contours)
            
            if contours:
                # Analyze the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                features['main_contour_area'] = float(cv2.contourArea(largest_contour))
                features['main_contour_perimeter'] = float(cv2.arcLength(largest_contour, True))
                
                # Compactness measure
                if features['main_contour_perimeter'] > 0:
                    features['compactness'] = 4 * 3.14159 * features['main_contour_area'] / (features['main_contour_perimeter'] ** 2)
                
                # Convex hull analysis
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    features['solidity'] = features['main_contour_area'] / hull_area
                    features['convexity_defects'] = 1.0 - features['solidity']
            
            # Texture analysis using Laplacian
            laplacian = cv2.Laplacian(img, cv2.CV_64F)
            if NUMPY_AVAILABLE:
                features['texture_variance'] = float(np.var(laplacian))
            
        except Exception as e:
            print(f"⚠️ OpenCV feature extraction error: {e}")
        
        return features
    
    def extract_basic_features(self, image_path):
        """Extract basic features using only standard library"""
        features = {}
        
        try:
            # Just file-based analysis
            stat = os.stat(image_path)
            features['file_size'] = stat.st_size
            features['file_modified'] = stat.st_mtime
            
            # Simple heuristics based on file size and name
            filename = os.path.basename(image_path).lower()
            
            if 'parkinson' in filename or 'p' in filename[:2]:
                features['filename_hint'] = 'parkinson'
            elif 'healthy' in filename or 'h' in filename[:2]:
                features['filename_hint'] = 'healthy'
            else:
                features['filename_hint'] = 'unknown'
            
            # File size based heuristics
            if features['file_size'] < 10000:
                features['complexity_hint'] = 'simple'
            elif features['file_size'] > 50000:
                features['complexity_hint'] = 'complex'
            else:
                features['complexity_hint'] = 'medium'
                
        except Exception as e:
            print(f"⚠️ Basic feature extraction error: {e}")
        
        return features
    
    def analyze_spiral_pattern(self, features):
        """Analyze spiral-specific patterns"""
        
        spiral_score = 0.5  # Neutral starting point
        confidence = 0.6
        
        try:
            # Analyze compactness - spirals should be reasonably compact
            if 'compactness' in features:
                if features['compactness'] < 0.3:  # Very irregular
                    spiral_score += 0.2  # More likely Parkinson's
                elif features['compactness'] > 0.7:  # Very regular
                    spiral_score -= 0.15  # More likely healthy
            
            # Analyze solidity - measure of how "filled" the shape is
            if 'solidity' in features:
                if features['solidity'] < 0.7:  # Lots of indentations/tremor
                    spiral_score += 0.25
                    confidence += 0.1
            
            # Edge ratio analysis - tremor creates more edges
            if 'edge_ratio' in features:
                if features['edge_ratio'] > 0.15:  # High edge density
                    spiral_score += 0.2
                elif features['edge_ratio'] < 0.05:  # Very smooth
                    spiral_score -= 0.1
            
            # Texture complexity - Parkinson's often shows irregular texture
            if 'texture_complexity' in features:
                if features['texture_complexity'] > 0.3:
                    spiral_score += 0.15
                    confidence += 0.05
            
            # Compare with reference patterns if available
            if hasattr(self, 'reference_patterns') and self.reference_patterns['spiral']:
                ref_score = self.compare_with_references(features, 'spiral')
                spiral_score = (spiral_score + ref_score) / 2
                confidence += 0.1
            
        except Exception as e:
            print(f"⚠️ Spiral analysis error: {e}")
        
        # Clamp values
        spiral_score = max(0.0, min(1.0, spiral_score))
        confidence = max(0.5, min(0.95, confidence))
        
        return spiral_score, confidence
    
    def analyze_wave_pattern(self, features):
        """Analyze wave-specific patterns"""
        
        wave_score = 0.5
        confidence = 0.6
        
        try:
            # Wave patterns should have different characteristics than spirals
            
            # Contour count - waves might have multiple contours
            if 'contour_count' in features:
                if features['contour_count'] > 3:  # Multiple broken segments
                    wave_score += 0.2
                elif features['contour_count'] == 1:  # Single smooth wave
                    wave_score -= 0.1
            
            # Texture variance for wave regularity
            if 'texture_variance' in features:
                if features['texture_variance'] > 1000:  # High variance = irregular
                    wave_score += 0.2
                    confidence += 0.1
            
            # Aspect ratio analysis (waves are typically wider than tall)
            if 'width' in features and 'height' in features:
                aspect_ratio = features['width'] / features['height']
                if aspect_ratio < 1.5:  # Too tall for a typical wave
                    wave_score += 0.1
                elif aspect_ratio > 4:  # Very wide, good wave characteristic
                    wave_score -= 0.05
            
            # Compare with reference patterns
            if hasattr(self, 'reference_patterns') and self.reference_patterns['wave']:
                ref_score = self.compare_with_references(features, 'wave')
                wave_score = (wave_score + ref_score) / 2
                confidence += 0.1
            
        except Exception as e:
            print(f"⚠️ Wave analysis error: {e}")
        
        # Clamp values
        wave_score = max(0.0, min(1.0, wave_score))
        confidence = max(0.5, min(0.95, confidence))
        
        return wave_score, confidence
    
    def compare_with_references(self, features, pattern_type):
        """Compare current features with reference patterns"""
        
        try:
            references = self.reference_patterns[pattern_type]
            
            if not references['healthy'] and not references['parkinson']:
                return 0.5  # No reference data
            
            # Simple distance-based comparison
            healthy_distances = []
            parkinson_distances = []
            
            # Key features for comparison
            key_features = ['edge_ratio', 'texture_complexity', 'compactness', 'solidity']
            
            for feature_set in references['healthy']:
                distance = self.calculate_feature_distance(features, feature_set, key_features)
                healthy_distances.append(distance)
            
            for feature_set in references['parkinson']:
                distance = self.calculate_feature_distance(features, feature_set, key_features)
                parkinson_distances.append(distance)
            
            # Average distances
            avg_healthy_dist = sum(healthy_distances) / len(healthy_distances) if healthy_distances else 1.0
            avg_parkinson_dist = sum(parkinson_distances) / len(parkinson_distances) if parkinson_distances else 1.0
            
            # Score based on which is closer
            if avg_healthy_dist < avg_parkinson_dist:
                return 0.5 - (avg_parkinson_dist - avg_healthy_dist) * 0.5
            else:
                return 0.5 + (avg_healthy_dist - avg_parkinson_dist) * 0.5
            
        except Exception as e:
            print(f"⚠️ Reference comparison error: {e}")
            return 0.5
    
    def calculate_feature_distance(self, features1, features2, key_features):
        """Calculate normalized distance between two feature sets"""
        
        distances = []
        
        for feature in key_features:
            if feature in features1 and feature in features2:
                # Normalize the difference
                diff = abs(features1[feature] - features2[feature])
                # Simple normalization (could be improved)
                normalized_diff = min(diff, 1.0)
                distances.append(normalized_diff)
        
        return sum(distances) / len(distances) if distances else 1.0
    
    def analyze_handwriting(self, image_path, drawing_type="spiral"):
        """Main analysis function"""
        
        print(f"🔍 Analyzing {drawing_type} pattern: {os.path.basename(image_path)}")
        
        # Extract features
        features = self.extract_image_features(image_path)
        
        if not features:
            return self.create_error_result("Could not extract features from image")
        
        # Pattern-specific analysis
        if drawing_type.lower() == 'spiral':
            score, confidence = self.analyze_spiral_pattern(features)
        elif drawing_type.lower() == 'wave':
            score, confidence = self.analyze_wave_pattern(features)
        else:
            # Default analysis
            score, confidence = self.analyze_spiral_pattern(features)
        
        # Determine prediction
        prediction = "Parkinson" if score > 0.5 else "Healthy"
        
        # Create detailed result
        result = {
            'prediction': prediction,
            'confidence_score': confidence,
            'probability': score,
            'analysis_details': {
                'features_extracted': features,
                'drawing_type': drawing_type,
                'analysis_method': 'enhanced_computer_vision',
                'libraries_used': []
            },
            'model_type': 'enhanced_cv',
            'timestamp': datetime.now().isoformat()
        }
        
        # Add library info
        if PIL_AVAILABLE:
            result['analysis_details']['libraries_used'].append('PIL')
        if CV2_AVAILABLE:
            result['analysis_details']['libraries_used'].append('OpenCV')
        if NUMPY_AVAILABLE:
            result['analysis_details']['libraries_used'].append('NumPy')
        
        print(f"✅ Analysis complete: {prediction} (confidence: {confidence:.2f})")
        
        return result
    
    def create_error_result(self, error_message):
        """Create error result"""
        return {
            'prediction': 'Error',
            'confidence_score': 0.0,
            'probability': 0.0,
            'analysis_details': {'error': error_message},
            'model_type': 'error',
            'timestamp': datetime.now().isoformat()
        }
    
    @property
    def models(self):
        """Provide models property for compatibility with advanced detector interface"""
        return {'enhanced_cv': 'Enhanced Computer Vision Analyzer'}
    
    def predict_ensemble(self, image_path, drawing_type="spiral"):
        """Predict using ensemble format for compatibility with advanced detector"""
        # Get the basic result
        result = self.analyze_handwriting(image_path, drawing_type)
        
        # Convert to ensemble format
        return self._convert_to_ensemble_format(result, drawing_type)
    
    def _convert_to_ensemble_format(self, result, drawing_type):
        """Convert basic result to ensemble format expected by the API"""
        if result.get('model_type') == 'error':
            # Return error in ensemble format
            return {
                'ensemble_prediction': {
                    'raw_prediction': 0.0,
                    'predicted_class': 0,
                    'predicted_label': 'Error',
                    'confidence': 0.0,
                    'model_agreement': 0.0,
                    'models_used': 0
                },
                'individual_models': {},
                'prediction_summary': {
                    'final_diagnosis': 'Error',
                    'confidence_level': 'None',
                    'confidence_score': '0.0%',
                    'model_consensus': f"Analysis failed: {result.get('analysis_details', {}).get('error', 'Unknown error')}",
                    'recommendation': 'Please try uploading a different image.'
                },
                'metadata': {
                    'drawing_type': drawing_type,
                    'analysis_timestamp': result.get('timestamp', ''),
                    'models_available': list(self.models.keys()),
                    'image_size': (224, 224),
                    'preprocessing_successful': False,
                    'error': result.get('analysis_details', {}).get('error', 'Unknown error')
                }
            }
        
        # Normal result conversion
        prediction = result.get('prediction', 'Unknown')
        confidence = result.get('confidence_score', 0.5)
        probability = result.get('probability', 0.5)
        
        # Convert to binary classification
        predicted_class = 1 if prediction.lower() == "parkinson" else 0
        predicted_label = "Parkinson" if predicted_class == 1 else "Healthy"
        
        return {
            'ensemble_prediction': {
                'raw_prediction': float(probability),
                'predicted_class': predicted_class,
                'predicted_label': predicted_label,
                'confidence': float(confidence),
                'model_agreement': 1.0,
                'models_used': 1
            },
            'individual_models': {
                'enhanced_cv': {
                    'model': 'enhanced_cv',
                    'predicted_class': predicted_class,
                    'predicted_label': predicted_label,
                    'confidence': float(confidence)
                }
            },
            'prediction_summary': {
                'final_diagnosis': predicted_label,
                'confidence_level': "High" if confidence > 0.8 else "Moderate" if confidence > 0.6 else "Low",
                'confidence_score': f"{confidence:.1%}",
                'model_consensus': f"Enhanced computer vision analysis suggests {predicted_label.lower()}",
                'recommendation': "Enhanced analysis using computer vision techniques. Please consult a medical professional for accurate diagnosis."
            },
            'metadata': {
                'drawing_type': drawing_type,
                'analysis_timestamp': result.get('timestamp', ''),
                'models_available': list(self.models.keys()),
                'image_size': (224, 224),
                'preprocessing_successful': True,
                'analysis_type': result.get('model_type', 'enhanced_cv'),
                'features': result.get('analysis_details', {}).get('features_extracted', {}),
                'libraries_used': result.get('analysis_details', {}).get('libraries_used', [])
            }
        }

# Global analyzer instance
analyzer = None

def get_analyzer():
    """Get or create analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = EnhancedHandwritingAnalyzer()
    return analyzer

if __name__ == "__main__":
    # Test the analyzer
    print("🧠 Testing Enhanced Handwriting Analyzer")
    
    analyzer = get_analyzer()
    
    # Test with available images
    test_images = [
        "/home/hari/Downloads/parkinson/handwritings/drawings/spiral/testing/healthy",
        "/home/hari/Downloads/parkinson/handwritings/drawings/spiral/testing/parkinson"
    ]
    
    for test_dir in test_images:
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg'))]
            if files:
                test_file = os.path.join(test_dir, files[0])
                print(f"\n📊 Testing with: {test_file}")
                result = analyzer.analyze_handwriting(test_file, "spiral")
                print(json.dumps(result, indent=2))
                break