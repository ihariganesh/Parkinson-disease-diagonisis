"""
Multi-Modal Parkinson's Disease Analysis Service
Combines DaT scan, handwriting, and voice analysis for comprehensive diagnosis
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime

from app.services.dat_service_direct import DaTService
from app.services.handwriting_service import HandwritingService
from app.services.speech_service import SpeechService


class MultiModalAnalysisService:
    """
    Multi-modal Parkinson's disease analysis service
    Combines three modalities: DaT scan, handwriting, voice
    """
    
    def __init__(self):
        """Initialize all modality services"""
        self.dat_service = DaTService()
        self.handwriting_service = HandwritingService()
        self.speech_service = SpeechService()
        
        # Weights for each modality in final decision
        self.weights = {
            'dat': 0.50,          # 50% - Most reliable indicator
            'handwriting': 0.25,  # 25% - Motor symptoms
            'voice': 0.25         # 25% - Speech characteristics
        }
        
        # Thresholds
        self.diagnosis_threshold = 0.5
        self.high_confidence_threshold = 0.80
        self.moderate_confidence_threshold = 0.60
        
    def analyze_comprehensive(
        self,
        dat_scans: Optional[List[Path]] = None,
        handwriting_spiral: Optional[Path] = None,
        handwriting_wave: Optional[Path] = None,
        voice_file: Optional[Path] = None,
        patient_id: Optional[str] = None
    ) -> Dict:
        """
        Perform comprehensive multi-modal analysis
        
        Args:
            dat_scans: List of DaT scan image paths (12-16 images)
            handwriting_spiral: Path to spiral drawing
            handwriting_wave: Path to wave drawing
            voice_file: Path to voice recording
            patient_id: Optional patient identifier
            
        Returns:
            Comprehensive analysis results with multi-modal fusion
        """
        
        print("\n" + "="*80)
        print("MULTI-MODAL PARKINSON'S ANALYSIS")
        print("="*80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient_id,
            'modalities_analyzed': [],
            'modality_results': {},
            'fusion_results': {},
            'clinical_interpretation': '',
            'recommendations': []
        }
        
        # Track which modalities are available
        available_modalities = []
        modality_predictions = {}
        modality_confidences = {}
        
        # 1. DaT Scan Analysis
        if dat_scans and len(dat_scans) > 0:
            print("\n[1/3] Analyzing DaT scans...")
            try:
                # Create temporary directory for DaT scans
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Copy scans to temp directory
                    for i, scan_path in enumerate(dat_scans):
                        dest_path = Path(temp_dir) / f"scan_{i:03d}.png"
                        import shutil
                        shutil.copy(scan_path, dest_path)
                    
                    # Analyze
                    dat_result = self.dat_service.predict(temp_dir)
                    
                    results['modality_results']['dat'] = dat_result
                    available_modalities.append('dat')
                    
                    # Extract probability (handle both formats)
                    if 'probabilities' in dat_result:
                        dat_prob = dat_result['probabilities'].get('Parkinson', 0.5)
                    else:
                        dat_prob = 0.5
                    
                    modality_predictions['dat'] = dat_prob
                    modality_confidences['dat'] = dat_result.get('confidence', 0.5)
                    
                    print(f"   ✓ DaT Analysis: {dat_result.get('prediction', 'Unknown')} "
                          f"({dat_prob*100:.1f}% PD probability)")
                    
            except Exception as e:
                print(f"   ✗ DaT Analysis failed: {str(e)}")
                results['modality_results']['dat'] = {'error': str(e)}
        
        # 2. Handwriting Analysis
        if handwriting_spiral or handwriting_wave:
            print("\n[2/3] Analyzing handwriting...")
            try:
                handwriting_files = []
                if handwriting_spiral:
                    handwriting_files.append(handwriting_spiral)
                if handwriting_wave:
                    handwriting_files.append(handwriting_wave)
                
                # Analyze each drawing
                handwriting_predictions = []
                for hw_file in handwriting_files:
                    hw_result = self.handwriting_service.predict(str(hw_file))
                    handwriting_predictions.append(hw_result.get('pd_probability', 0.5))
                
                # Average the predictions
                hw_prob = np.mean(handwriting_predictions)
                hw_confidence = 0.70  # Placeholder - should come from model
                
                results['modality_results']['handwriting'] = {
                    'prediction': 'Parkinson' if hw_prob > 0.5 else 'Healthy',
                    'probability': float(hw_prob),
                    'confidence': hw_confidence,
                    'files_analyzed': len(handwriting_files)
                }
                
                available_modalities.append('handwriting')
                modality_predictions['handwriting'] = hw_prob
                modality_confidences['handwriting'] = hw_confidence
                
                print(f"   ✓ Handwriting Analysis: "
                      f"{'Parkinson' if hw_prob > 0.5 else 'Healthy'} "
                      f"({hw_prob*100:.1f}% PD probability)")
                
            except Exception as e:
                print(f"   ✗ Handwriting Analysis failed: {str(e)}")
                results['modality_results']['handwriting'] = {'error': str(e)}
        
        # 3. Voice Analysis
        if voice_file:
            print("\n[3/3] Analyzing voice...")
            try:
                voice_result = self.speech_service.predict(str(voice_file))
                
                results['modality_results']['voice'] = voice_result
                available_modalities.append('voice')
                
                voice_prob = voice_result.get('pd_probability', 0.5)
                voice_confidence = voice_result.get('confidence', 0.5)
                
                modality_predictions['voice'] = voice_prob
                modality_confidences['voice'] = voice_confidence
                
                print(f"   ✓ Voice Analysis: {voice_result.get('prediction', 'Unknown')} "
                      f"({voice_prob*100:.1f}% PD probability)")
                
            except Exception as e:
                print(f"   ✗ Voice Analysis failed: {str(e)}")
                results['modality_results']['voice'] = {'error': str(e)}
        
        # 4. Multi-Modal Fusion
        print(f"\n[4/4] Performing multi-modal fusion...")
        print(f"   Available modalities: {', '.join(available_modalities)}")
        
        if len(available_modalities) == 0:
            results['fusion_results'] = {
                'error': 'No modalities available for analysis'
            }
            return results
        
        # Calculate weighted average
        total_weight = sum(self.weights[m] for m in available_modalities)
        weighted_sum = sum(
            modality_predictions[m] * self.weights[m] 
            for m in available_modalities
        )
        final_probability = weighted_sum / total_weight
        
        # Calculate minimum confidence (conservative approach)
        final_confidence = min(modality_confidences.values()) if modality_confidences else 0.5
        
        # Make final diagnosis
        final_diagnosis = 'Parkinson\'s Disease' if final_probability > self.diagnosis_threshold else 'Healthy'
        
        # Calculate agreement score (how much modalities agree)
        if len(available_modalities) > 1:
            predictions = list(modality_predictions.values())
            agreement_score = 1.0 - (np.std(predictions) / 0.5)  # Normalized std dev
        else:
            agreement_score = 1.0
        
        # Determine confidence level
        if final_confidence > self.high_confidence_threshold and agreement_score > 0.85:
            confidence_level = 'High'
        elif final_confidence > self.moderate_confidence_threshold:
            confidence_level = 'Moderate'
        else:
            confidence_level = 'Low'
        
        # Build fusion results
        results['fusion_results'] = {
            'final_diagnosis': final_diagnosis,
            'final_probability': float(final_probability),
            'confidence': float(final_confidence),
            'confidence_level': confidence_level,
            'agreement_score': float(agreement_score),
            'modalities_used': available_modalities,
            'weights_applied': {m: self.weights[m] for m in available_modalities}
        }
        
        print(f"\n   Final Diagnosis: {final_diagnosis}")
        print(f"   Probability: {final_probability*100:.1f}%")
        print(f"   Confidence: {confidence_level} ({final_confidence*100:.1f}%)")
        print(f"   Agreement: {agreement_score*100:.1f}%")
        
        # 5. Generate Clinical Interpretation
        results['clinical_interpretation'] = self._generate_interpretation(
            final_diagnosis,
            final_probability,
            confidence_level,
            agreement_score,
            available_modalities,
            modality_predictions
        )
        
        # 6. Generate Recommendations
        results['recommendations'] = self._generate_recommendations(
            final_diagnosis,
            confidence_level,
            available_modalities
        )
        
        results['modalities_analyzed'] = available_modalities
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80 + "\n")
        
        return results
    
    def _generate_interpretation(
        self,
        diagnosis: str,
        probability: float,
        confidence_level: str,
        agreement_score: float,
        modalities: List[str],
        predictions: Dict[str, float]
    ) -> str:
        """Generate clinical interpretation text"""
        
        interpretation = f"Multi-modal analysis using {len(modalities)} modality(ies) "
        interpretation += f"({', '.join(modalities)}) "
        
        if diagnosis == 'Parkinson\'s Disease':
            interpretation += f"indicates Parkinson's disease with {probability*100:.1f}% probability. "
        else:
            interpretation += f"suggests healthy status with {(1-probability)*100:.1f}% confidence. "
        
        # Agreement analysis
        if len(modalities) > 1:
            if agreement_score > 0.85:
                interpretation += "All modalities show strong agreement. "
            elif agreement_score > 0.70:
                interpretation += "Modalities show moderate agreement. "
            else:
                interpretation += "Modalities show some disagreement, suggesting need for additional evaluation. "
        
        # Confidence analysis
        if confidence_level == 'High':
            interpretation += "The analysis shows high confidence in the diagnosis. "
        elif confidence_level == 'Moderate':
            interpretation += "The analysis shows moderate confidence. Additional clinical evaluation is recommended. "
        else:
            interpretation += "The analysis shows low confidence. Clinical confirmation is strongly recommended. "
        
        # Modality-specific insights
        if 'dat' in modalities:
            dat_prob = predictions['dat']
            if dat_prob > 0.7:
                interpretation += "DaT scan shows reduced dopamine transporter binding consistent with PD. "
            elif dat_prob < 0.3:
                interpretation += "DaT scan shows normal dopamine transporter binding. "
        
        if 'handwriting' in modalities:
            hw_prob = predictions['handwriting']
            if hw_prob > 0.7:
                interpretation += "Handwriting analysis reveals motor control difficulties typical of PD. "
            elif hw_prob < 0.3:
                interpretation += "Handwriting analysis shows normal motor control. "
        
        if 'voice' in modalities:
            voice_prob = predictions['voice']
            if voice_prob > 0.7:
                interpretation += "Voice analysis detects speech characteristics associated with PD. "
            elif voice_prob < 0.3:
                interpretation += "Voice analysis shows normal speech characteristics. "
        
        return interpretation
    
    def _generate_recommendations(
        self,
        diagnosis: str,
        confidence_level: str,
        modalities: List[str]
    ) -> List[str]:
        """Generate clinical recommendations"""
        
        recommendations = []
        
        # Always recommend clinical confirmation
        recommendations.append(
            "Consult with a qualified neurologist for clinical confirmation and diagnosis"
        )
        
        if diagnosis == 'Parkinson\'s Disease':
            recommendations.append(
                "Consider comprehensive neurological examination including motor function assessment"
            )
            
            if 'dat' not in modalities:
                recommendations.append(
                    "Consider dopamine transporter (DaT) scan imaging for confirmation"
                )
            
            recommendations.append(
                "Monitor for progression of motor and non-motor symptoms"
            )
            
            recommendations.append(
                "Discuss treatment options including medication and lifestyle modifications"
            )
            
            if confidence_level != 'High':
                recommendations.append(
                    "Consider repeat assessment in 6-12 months to monitor progression"
                )
        else:
            recommendations.append(
                "Continue regular health monitoring and maintain healthy lifestyle"
            )
            
            if confidence_level == 'Low':
                recommendations.append(
                    "Consider repeat screening if symptoms develop or worsen"
                )
            
            recommendations.append(
                "Be aware of early Parkinson's symptoms: tremor, rigidity, bradykinesia, postural instability"
            )
        
        # If missing modalities, recommend complete assessment
        all_modalities = ['dat', 'handwriting', 'voice']
        missing = [m for m in all_modalities if m not in modalities]
        
        if missing:
            modality_names = {
                'dat': 'DaT scan imaging',
                'handwriting': 'handwriting analysis',
                'voice': 'voice analysis'
            }
            recommendations.append(
                f"For comprehensive assessment, consider adding: {', '.join([modality_names[m] for m in missing])}"
            )
        
        return recommendations


# Global service instance
_multimodal_service = None

def get_multimodal_service() -> MultiModalAnalysisService:
    """Get or create multi-modal service singleton"""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultiModalAnalysisService()
    return _multimodal_service
