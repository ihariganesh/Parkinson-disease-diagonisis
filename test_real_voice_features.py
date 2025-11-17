"""
Test Real Voice Feature Extraction
Tests the complete pipeline with real audio feature extraction
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.speech_service import SpeechService

def test_voice_analysis():
    """Test voice analysis with real feature extraction"""
    print("=" * 70)
    print("TESTING VOICE ANALYSIS WITH REAL FEATURE EXTRACTION")
    print("=" * 70)
    
    # Initialize service
    print("\n1. Initializing Speech Service...")
    service = SpeechService()
    
    if not service.is_available():
        print("❌ Speech service not available!")
        return False
    
    print("✓ Speech service initialized")
    print(f"✓ Feature extractor: {'Available' if service.feature_extractor else 'Not available'}")
    print(f"✓ Predictor: {'Available' if service.predictor else 'Not available'}")
    
    # Test with audio file
    audio_path = "/home/hari/Downloads/parkinson/test_audio.wav"
    
    if not Path(audio_path).exists():
        print(f"❌ Test audio file not found: {audio_path}")
        return False
    
    print(f"\n2. Analyzing audio file: {audio_path}")
    print("-" * 70)
    
    result = service.analyze_voice(audio_path)
    
    print("\n3. Analysis Results:")
    print("-" * 70)
    print(f"Success: {result.get('success')}")
    print(f"Diagnosis: {result.get('diagnosis')}")
    print(f"Prediction: {result.get('prediction')}")
    print(f"PD Probability: {result.get('pd_probability', 0):.2%}")
    print(f"Healthy Probability: {result.get('probability', 0):.2%}")
    print(f"Confidence: {result.get('confidence', 0):.2%}")
    print(f"Modality: {result.get('modality')}")
    print(f"Note: {result.get('note')}")
    
    # Check if we used real features
    if "Real acoustic features" in result.get('note', ''):
        print("\n✅ SUCCESS! Using real feature extraction!")
    elif "simulated" in result.get('note', '').lower():
        print("\n⚠️  WARNING: Still using simulated features")
    
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    success = test_voice_analysis()
    sys.exit(0 if success else 1)
