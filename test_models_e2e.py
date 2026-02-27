#!/usr/bin/env python3
"""End-to-end test for retrained handwriting and speech models."""

import sys, os
sys.path.insert(0, 'backend')

print("=" * 60)
print("END-TO-END MODEL TESTS")
print("=" * 60)

# --- Handwriting Tests ---
from ml_enhanced_analyzer import get_analyzer
analyzer = get_analyzer()

for dtype in ["spiral", "wave"]:
    correct, total = 0, 0
    print(f"\n--- {dtype.upper()} TEST ---")
    for label, expected in [("healthy", "Healthy"), ("parkinson", "Parkinson")]:
        folder = f"parkinson_diagram_dataset/{dtype}/testing/{label}"
        for f in sorted(os.listdir(folder)):
            path = os.path.join(folder, f)
            result = analyzer.analyze_handwriting(path, dtype)
            pred = result["prediction_summary"]["final_diagnosis"]
            ok = pred == expected
            correct += ok
            total += 1
            mark = "✅" if ok else "❌"
            conf = result["prediction_summary"]["confidence_score"]
            print(f"  {mark} {f}: {pred} (conf={conf})")
    print(f"  >> {dtype} accuracy: {correct}/{total} = {correct/total:.0%}")

# --- Speech Test ---
print("\n--- SPEECH MODEL TEST ---")
sys.path.insert(0, 'backend/app/services')
from simple_speech_predictor import SimpleSpeechPredictor
import numpy as np
import pandas as pd

predictor = SimpleSpeechPredictor("models/speech")
if predictor.is_available():
    df = pd.read_csv("ml-models/pd_speech_features.csv")
    feature_cols = [c for c in df.columns if c.lower() not in ("id", "gender", "class")]
    X = df[feature_cols].values
    y = df["class"].values

    # Test on a sample of 20 (10 PD, 10 Healthy)
    pd_idx = np.where(y == 1)[0][:10]
    healthy_idx = np.where(y == 0)[0][:10]
    test_idx = np.concatenate([pd_idx, healthy_idx])

    correct = 0
    for i in test_idx:
        result = predictor.predict_from_features(X[i])
        expected = "Parkinson's Disease" if y[i] == 1 else "Healthy"
        pred = result.get("prediction", "")
        ok = pred == expected
        correct += ok
        mark = "✅" if ok else "❌"
        prob = result.get("pd_probability", 0)
        print(f"  {mark} Sample {i}: expected={expected}, got={pred} (prob={prob:.3f})")
    print(f"  >> Speech accuracy: {correct}/{len(test_idx)} = {correct/len(test_idx):.0%}")
else:
    print("  ❌ Speech model not loaded!")

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
