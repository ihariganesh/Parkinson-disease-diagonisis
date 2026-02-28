import sys
sys.path.append('backend')
from ml_enhanced_analyzer import get_analyzer
import os
import glob

analyzer = get_analyzer()
base_dir = "parkinson_diagram_dataset/spiral/testing"

for category in ["healthy", "parkinson"]:
    files = glob.glob(os.path.join(base_dir, category, "*.png"))
    for f in files[:2]:
        print(f"\nEvaluating: {f} (Expected: {category})")
        res = analyzer.analyze_handwriting(f, "spiral")
        
        # print specific predictions if they exist
        print(f"Final score: {res.get('ensemble_prediction', {}).get('raw_prediction')}")
        preds = res.get('individual_models', {})
        for name, p in preds.items():
            print(f"- {name}: {p['confidence']} ({p['predicted_label']})")
