"""
DaT Scan Inference Service
Handles real-time predictions for uploaded DaT scans
"""

import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tensorflow as tf
from tensorflow import keras
import json
from datetime import datetime


class DaTScanInferenceService:
    """
    Inference service for DaT scan classification
    Loads trained model and makes predictions on new scans
    """
    
    def __init__(
        self,
        model_path: str,
        target_size: Tuple[int, int] = (128, 128),
        max_slices: int = 16,
        threshold: float = 0.5
    ):
        """
        Initialize inference service
        
        Args:
            model_path: Path to trained model (.keras file)
            target_size: Image preprocessing size
            max_slices: Maximum number of slices expected
            threshold: Classification threshold
        """
        self.model_path = Path(model_path)
        self.target_size = target_size
        self.max_slices = max_slices
        self.threshold = threshold
        
        self.model = None
        self.class_names = ['Healthy', 'Parkinson']
        
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        print(f"Loading model from: {self.model_path}")
        
        # Import custom layer
        from dat_cnn_lstm_model import GrayscaleToRGBLayer
        
        # Load model with custom objects
        self.model = keras.models.load_model(
            str(self.model_path),
            custom_objects={'GrayscaleToRGBLayer': GrayscaleToRGBLayer}
        )
        print("✅ Model loaded successfully!")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess a single DaT scan slice
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image array (H, W, 1)
        """
        # Read image in grayscale
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Resize to target size
        img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)
        
        # Normalize pixel values to [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # Add channel dimension
        img = np.expand_dims(img, axis=-1)
        
        return img
    
    def load_scan_sequence(self, scan_dir: str) -> np.ndarray:
        """
        Load and preprocess a complete scan sequence from directory
        
        Args:
            scan_dir: Directory containing scan slices
            
        Returns:
            Preprocessed scan sequence (max_slices, H, W, 1)
        """
        scan_path = Path(scan_dir)
        
        if not scan_path.exists():
            raise ValueError(f"Scan directory not found: {scan_dir}")
        
        # Get all image files (sorted)
        image_files = sorted(scan_path.glob("*.png")) + \
                     sorted(scan_path.glob("*.jpg")) + \
                     sorted(scan_path.glob("*.jpeg"))
        
        if len(image_files) == 0:
            raise ValueError(f"No image files found in: {scan_dir}")
        
        # Load and preprocess all slices
        slices = []
        for img_file in image_files:
            try:
                img = self.preprocess_image(str(img_file))
                slices.append(img)
            except Exception as e:
                print(f"Warning: Failed to load {img_file}: {e}")
                continue
        
        if len(slices) == 0:
            raise ValueError(f"No valid slices loaded from: {scan_dir}")
        
        slices = np.array(slices)
        
        # Pad or sample to max_slices
        if len(slices) < self.max_slices:
            # Pad with zeros
            padding = np.zeros(
                (self.max_slices - len(slices), *self.target_size, 1),
                dtype=np.float32
            )
            slices = np.concatenate([slices, padding], axis=0)
        elif len(slices) > self.max_slices:
            # Take evenly spaced slices
            indices = np.linspace(0, len(slices) - 1, self.max_slices, dtype=int)
            slices = slices[indices]
        
        return slices
    
    def load_scan_from_files(self, file_paths: List[str]) -> np.ndarray:
        """
        Load and preprocess scan from list of file paths
        
        Args:
            file_paths: List of paths to scan slice images
            
        Returns:
            Preprocessed scan sequence (max_slices, H, W, 1)
        """
        if not file_paths:
            raise ValueError("No file paths provided")
        
        # Sort files by name
        file_paths = sorted(file_paths)
        
        # Load and preprocess all slices
        slices = []
        for img_file in file_paths:
            try:
                img = self.preprocess_image(img_file)
                slices.append(img)
            except Exception as e:
                print(f"Warning: Failed to load {img_file}: {e}")
                continue
        
        if len(slices) == 0:
            raise ValueError("No valid slices loaded")
        
        slices = np.array(slices)
        
        # Pad or sample to max_slices
        if len(slices) < self.max_slices:
            padding = np.zeros(
                (self.max_slices - len(slices), *self.target_size, 1),
                dtype=np.float32
            )
            slices = np.concatenate([slices, padding], axis=0)
        elif len(slices) > self.max_slices:
            indices = np.linspace(0, len(slices) - 1, self.max_slices, dtype=int)
            slices = slices[indices]
        
        return slices
    
    def predict(
        self,
        scan_input: str | List[str],
        return_confidence: bool = True
    ) -> Dict:
        """
        Make prediction on DaT scan
        
        Args:
            scan_input: Directory path containing slices OR list of file paths
            return_confidence: Whether to return confidence scores
            
        Returns:
            Dictionary with prediction results
        """
        # Load scan sequence
        if isinstance(scan_input, str):
            scan_sequence = self.load_scan_sequence(scan_input)
        else:
            scan_sequence = self.load_scan_from_files(scan_input)
        
        # Add batch dimension
        scan_batch = np.expand_dims(scan_sequence, axis=0)
        
        # Make prediction
        probability = self.model.predict(scan_batch, verbose=0)[0][0]
        
        # Convert to class prediction
        predicted_class = int(probability > self.threshold)
        predicted_label = self.class_names[predicted_class]
        
        # Calculate confidence
        if predicted_class == 1:
            confidence = float(probability)
        else:
            confidence = float(1 - probability)
        
        # Prepare result
        result = {
            'prediction': predicted_label,
            'class': predicted_class,
            'timestamp': datetime.now().isoformat()
        }
        
        if return_confidence:
            result['confidence'] = confidence
            result['probability_parkinson'] = float(probability)
            result['probability_healthy'] = float(1 - probability)
        
        # Add risk assessment
        result['risk_level'] = self._assess_risk(probability)
        result['interpretation'] = self._get_interpretation(predicted_class, confidence)
        
        return result
    
    def predict_batch(
        self,
        scan_inputs: List[str | List[str]]
    ) -> List[Dict]:
        """
        Make predictions on multiple scans
        
        Args:
            scan_inputs: List of scan directories or file path lists
            
        Returns:
            List of prediction results
        """
        results = []
        for scan_input in scan_inputs:
            try:
                result = self.predict(scan_input)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'prediction': None
                })
        
        return results
    
    def _assess_risk(self, probability: float) -> str:
        """Assess risk level based on probability"""
        if probability < 0.3:
            return "Low"
        elif probability < 0.5:
            return "Mild"
        elif probability < 0.7:
            return "Moderate"
        elif probability < 0.85:
            return "High"
        else:
            return "Very High"
    
    def _get_interpretation(self, predicted_class: int, confidence: float) -> str:
        """Get human-readable interpretation"""
        if predicted_class == 0:  # Healthy
            if confidence > 0.9:
                return "Scan shows normal dopamine transporter levels with high confidence. No signs of Parkinson's disease detected."
            elif confidence > 0.7:
                return "Scan suggests normal dopamine transporter levels. Low probability of Parkinson's disease."
            else:
                return "Scan appears normal but confidence is moderate. Consider follow-up examination."
        else:  # Parkinson
            if confidence > 0.9:
                return "Scan shows significant dopamine transporter deficit with high confidence. Strong indication of Parkinson's disease."
            elif confidence > 0.7:
                return "Scan indicates reduced dopamine transporter levels. Moderate to high probability of Parkinson's disease."
            else:
                return "Scan suggests possible dopamine transporter deficit. Further clinical evaluation recommended."
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_path': str(self.model_path),
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'target_size': self.target_size,
            'max_slices': self.max_slices,
            'threshold': self.threshold,
            'class_names': self.class_names
        }


# Global inference service instance (singleton)
_inference_service: Optional[DaTScanInferenceService] = None


def get_inference_service(
    model_path: Optional[str] = None,
    force_reload: bool = False
) -> DaTScanInferenceService:
    """
    Get or create global inference service instance
    
    Args:
        model_path: Path to model (required on first call)
        force_reload: Force reload of model
        
    Returns:
        DaTScanInferenceService instance
    """
    global _inference_service
    
    if _inference_service is None or force_reload:
        if model_path is None:
            # Try to find latest model
            model_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/models/dat_scan")
            if model_dir.exists():
                model_files = list(model_dir.glob("dat_model_*.keras"))
                if model_files:
                    model_path = str(sorted(model_files)[-1])  # Get latest
        
        if model_path is None:
            raise ValueError("Model path must be provided for first initialization")
        
        _inference_service = DaTScanInferenceService(model_path)
    
    return _inference_service


def main():
    """Test inference service"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python dat_inference_service.py <model_path> <scan_directory>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    scan_dir = sys.argv[2]
    
    # Initialize service
    print("Initializing inference service...")
    service = DaTScanInferenceService(model_path)
    
    # Print model info
    print("\n" + "="*80)
    print("MODEL INFO")
    print("="*80)
    info = service.get_model_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Make prediction
    print("\n" + "="*80)
    print("MAKING PREDICTION")
    print("="*80)
    print(f"Scan directory: {scan_dir}")
    
    result = service.predict(scan_dir)
    
    print("\n" + "="*80)
    print("PREDICTION RESULT")
    print("="*80)
    for key, value in result.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    print("\n✅ Inference complete!")


if __name__ == "__main__":
    main()
