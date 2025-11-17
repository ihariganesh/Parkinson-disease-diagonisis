"""
DaT Scan Analysis Service for Backend
Integrates with FastAPI backend for DaT scan classification
"""

import sys
from pathlib import Path

# Add ml_models directory to path
ml_models_path = Path(__file__).parent.parent.parent / "ml_models"
sys.path.insert(0, str(ml_models_path))

from typing import List, Dict, Optional
import numpy as np
from datetime import datetime
import json

try:
    from dat_inference_service import DaTScanInferenceService, get_inference_service
except ImportError:
    print("Warning: Could not import dat_inference_service")
    DaTScanInferenceService = None
    get_inference_service = None


class DaTScanAnalysisService:
    """
    Service for DaT scan analysis in backend
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize DaT scan analysis service
        
        Args:
            model_path: Path to trained model (optional, will auto-detect)
        """
        self.model_path = model_path
        self.inference_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize inference service"""
        if get_inference_service is None:
            print("Warning: DaT scan inference service not available")
            return
        
        try:
            # Auto-detect model if not provided
            if self.model_path is None:
                model_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/models/dat_scan")
                if model_dir.exists():
                    model_files = list(model_dir.glob("dat_model_best_*.keras"))
                    if not model_files:
                        model_files = list(model_dir.glob("dat_model_*.keras"))
                    
                    if model_files:
                        # Get most recent model
                        self.model_path = str(sorted(model_files)[-1])
            
            if self.model_path:
                self.inference_service = get_inference_service(self.model_path)
                print(f"✅ DaT scan model loaded: {self.model_path}")
            else:
                print("⚠️  No DaT scan model found. Please train the model first.")
        
        except Exception as e:
            print(f"Error initializing DaT scan service: {e}")
            self.inference_service = None
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return self.inference_service is not None
    
    def analyze_scan_directory(
        self,
        scan_dir: str,
        patient_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze DaT scan from directory containing slices
        
        Args:
            scan_dir: Path to directory containing scan slices
            patient_id: Optional patient identifier
            
        Returns:
            Analysis results dictionary
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DaT scan analysis service not available. Model not loaded.',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Make prediction
            result = self.inference_service.predict(scan_dir, return_confidence=True)
            
            # Prepare response
            response = {
                'success': True,
                'analysis_type': 'dat_scan',
                'prediction': result['prediction'],
                'class': result['class'],
                'confidence': result['confidence'],
                'probability_healthy': result['probability_healthy'],
                'probability_parkinson': result['probability_parkinson'],
                'risk_level': result['risk_level'],
                'interpretation': result['interpretation'],
                'timestamp': result['timestamp']
            }
            
            # Add reliability warning for low confidence
            # Model has known bias (trained on small, imbalanced dataset)
            if result['confidence'] < 0.75:
                response['warning'] = (
                    "⚠️ Model confidence is below 75%. The current DaT scan model "
                    "was trained on a limited dataset and shows bias toward Parkinson's predictions. "
                    "Please verify results with clinical examination and additional diagnostic tests."
                )
                response['reliability'] = 'Low'
            elif result['confidence'] < 0.85:
                response['reliability'] = 'Moderate'
                response['note'] = "Moderate confidence. Consider additional diagnostic confirmation."
            else:
                response['reliability'] = 'High'
            
            if patient_id:
                response['patient_id'] = patient_id
            
            # Add recommendations
            response['recommendations'] = self._get_recommendations(result)
            
            return response
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_scan_files(
        self,
        file_paths: List[str],
        patient_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze DaT scan from list of uploaded files
        
        Args:
            file_paths: List of paths to scan slice images
            patient_id: Optional patient identifier
            
        Returns:
            Analysis results dictionary
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DaT scan analysis service not available. Model not loaded.',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Make prediction
            result = self.inference_service.predict(file_paths, return_confidence=True)
            
            # Prepare response
            response = {
                'success': True,
                'analysis_type': 'dat_scan',
                'num_slices': len(file_paths),
                'prediction': result['prediction'],
                'class': result['class'],
                'confidence': result['confidence'],
                'probability_healthy': result['probability_healthy'],
                'probability_parkinson': result['probability_parkinson'],
                'risk_level': result['risk_level'],
                'interpretation': result['interpretation'],
                'timestamp': result['timestamp']
            }
            
            # Add reliability warning for low confidence
            # Model has known bias (trained on small, imbalanced dataset)
            if result['confidence'] < 0.75:
                response['warning'] = (
                    "⚠️ Model confidence is below 75%. The current DaT scan model "
                    "was trained on a limited dataset and shows bias toward Parkinson's predictions. "
                    "Please verify results with clinical examination and additional diagnostic tests."
                )
                response['reliability'] = 'Low'
            elif result['confidence'] < 0.85:
                response['reliability'] = 'Moderate'
                response['note'] = "Moderate confidence. Consider additional diagnostic confirmation."
            else:
                response['reliability'] = 'High'
            
            if patient_id:
                response['patient_id'] = patient_id
            
            # Add recommendations
            response['recommendations'] = self._get_recommendations(result)
            
            return response
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_recommendations(self, result: Dict) -> List[str]:
        """
        Get clinical recommendations based on prediction
        
        Args:
            result: Prediction result
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        predicted_class = result['class']
        confidence = result['confidence']
        risk_level = result['risk_level']
        
        if predicted_class == 1:  # Parkinson's detected
            recommendations.append("⚠️ Consult a neurologist for comprehensive clinical evaluation")
            recommendations.append("📋 Complete neurological examination recommended")
            
            if confidence > 0.85:
                recommendations.append("🔬 Consider additional diagnostic tests (UPDRS, MDS-UPDRS)")
                recommendations.append("💊 Discuss treatment options with movement disorder specialist")
            
            if risk_level in ['High', 'Very High']:
                recommendations.append("🏥 Early intervention may improve long-term outcomes")
                recommendations.append("🧠 Consider cognitive assessment and monitoring")
        
        else:  # Healthy
            if confidence < 0.7:
                recommendations.append("🔄 Follow-up DaT scan in 12-24 months recommended")
                recommendations.append("📊 Monitor for any motor symptoms or changes")
            else:
                recommendations.append("✅ Normal dopamine transporter levels detected")
                recommendations.append("🔄 Routine monitoring as per clinical guidelines")
        
        # General recommendations
        recommendations.extend([
            "📝 Keep detailed records of symptoms and progression",
            "🏃 Maintain regular physical activity and healthy lifestyle",
            "🤝 Join support groups if diagnosis confirmed"
        ])
        
        return recommendations
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if not self.is_available():
            return {
                'available': False,
                'error': 'Service not initialized'
            }
        
        info = self.inference_service.get_model_info()
        info['available'] = True
        return info
    
    def get_service_status(self) -> Dict:
        """Get service status"""
        return {
            'service_name': 'DaT Scan Analysis',
            'version': '1.0.0',
            'available': self.is_available(),
            'model_loaded': self.inference_service is not None,
            'model_path': self.model_path if self.model_path else None,
            'timestamp': datetime.now().isoformat()
        }


# Global service instance
_dat_service: Optional[DaTScanAnalysisService] = None


def get_dat_service(model_path: Optional[str] = None) -> DaTScanAnalysisService:
    """
    Get or create global DaT scan analysis service
    
    Args:
        model_path: Optional model path
        
    Returns:
        DaTScanAnalysisService instance
    """
    global _dat_service
    
    if _dat_service is None:
        _dat_service = DaTScanAnalysisService(model_path)
    
    return _dat_service


def main():
    """Test service"""
    service = get_dat_service()
    
    print("="*80)
    print("DaT SCAN ANALYSIS SERVICE")
    print("="*80)
    
    # Print status
    status = service.get_service_status()
    print("\nService Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if service.is_available():
        print("\n✅ Service is ready!")
        
        # Print model info
        info = service.get_model_info()
        print("\nModel Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("\n⚠️  Service not available. Train model first.")


if __name__ == "__main__":
    main()
