from app.services.handwriting_service import HandwritingService
from app.services.speech_service import SpeechService

print("Testing Handwriting Service...")
hw = HandwritingService()
print("Spiral SVM loaded:", getattr(hw, 'spiral_svm', None) is not None)
print("Wave SVM loaded:", getattr(hw, 'wave_svm', None) is not None)

print("\nTesting Speech Service...")
sp = SpeechService()
print("Speech model available:", sp.is_available())
