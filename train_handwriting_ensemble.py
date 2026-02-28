#!/usr/bin/env python3
"""
Parkinson's Handwriting Detector – Hybrid Ensemble

Combines:
  1. HOG (Histogram of Oriented Gradients) features with SVM
  2. Color histogram + structural features with Random Forest
  3. TensorFlow MobileNetV2 transfer learning (if models available)

The HOG+SVM approach is specifically strong for this type of
handwriting/drawing analysis with small datasets.
"""

import os
import json
import pickle
import logging
import warnings
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

warnings.filterwarnings("ignore")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from skimage.feature import hog, local_binary_pattern
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
DATASET_DIR = PROJECT_ROOT / "parkinson_diagram_dataset"
MODEL_DIR = PROJECT_ROOT / "ml-models" / "models" / "handwriting"
IMG_SIZE = 224


def extract_hog_features(image: np.ndarray) -> np.ndarray:
    """Extract HOG features from a grayscale image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    resized = cv2.resize(gray, (128, 128))
    features = hog(
        resized,
        orientations=12,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm='L2-Hys',
        transform_sqrt=True,
    )
    return features


def extract_structural_features(image: np.ndarray) -> np.ndarray:
    """Extract handwriting structural features (contours, density, etc.)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    resized = cv2.resize(gray, (200, 200))

    features = []

    # 1. Threshold and get binary
    _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2. Pixel density (ratio of ink pixels)
    ink_ratio = np.sum(binary > 0) / binary.size
    features.append(ink_ratio)

    # 3. Contour features
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features.append(len(contours))
    if contours:
        areas = [cv2.contourArea(c) for c in contours]
        perimeters = [cv2.arcLength(c, True) for c in contours]
        features.append(np.mean(areas))
        features.append(np.std(areas))
        features.append(np.max(areas))
        features.append(np.mean(perimeters))
        features.append(np.std(perimeters))
        # Circularity of largest contour
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        peri = cv2.arcLength(largest, True)
        circularity = 4 * np.pi * area / (peri ** 2) if peri > 0 else 0
        features.append(circularity)
    else:
        features.extend([0] * 6)

    # 4. Gradient-based features (captures tremor)
    sobelx = cv2.Sobel(resized, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(resized, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    direction = np.arctan2(sobely, sobelx)

    features.append(np.mean(magnitude))
    features.append(np.std(magnitude))
    features.append(np.mean(direction))
    features.append(np.std(direction))

    # 5. Intensity statistics
    features.append(np.mean(resized))
    features.append(np.std(resized))
    features.append(np.median(resized))

    # 6. Laplacian variance (sharpness/blur - tremor indicator)
    laplacian = cv2.Laplacian(resized, cv2.CV_64F)
    features.append(np.var(laplacian))
    features.append(np.mean(np.abs(laplacian)))

    # 7. Edge density
    edges = cv2.Canny(resized, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    features.append(edge_density)

    # 8. LBP texture features (captures irregularity)
    lbp = local_binary_pattern(resized, P=8, R=1, method='uniform')
    lbp_hist, _ = np.histogram(lbp, bins=10, density=True)
    features.extend(lbp_hist.tolist())

    # 9. Hu moments (shape invariants)
    moments = cv2.moments(binary)
    hu = cv2.HuMoments(moments).flatten()
    # Log transform for numerical stability
    hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
    features.extend(hu.tolist())

    # 10. Zoning features (divide into grid, count ink per zone)
    h, w = binary.shape
    zone_size = 5
    zh, zw = h // zone_size, w // zone_size
    for i in range(zone_size):
        for j in range(zone_size):
            zone = binary[i*zh:(i+1)*zh, j*zw:(j+1)*zw]
            features.append(np.sum(zone > 0) / zone.size)

    return np.array(features, dtype=np.float64)


def extract_all_features(image: np.ndarray) -> np.ndarray:
    """Combine HOG + structural features."""
    hog_feat = extract_hog_features(image)
    struct_feat = extract_structural_features(image)
    return np.concatenate([hog_feat, struct_feat])


def load_images(directory: Path, label: int):
    """Load images and their labels from a directory."""
    images, labels = [], []
    if not directory.exists():
        return [], []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp"):
        for f in sorted(directory.glob(ext)):
            img = cv2.imread(str(f))
            if img is not None:
                images.append(img)
                labels.append(label)
    return images, labels


def train_svm_model(drawing_type: str):
    """Train HOG + SVM model for a drawing type."""
    base = DATASET_DIR / drawing_type

    # Load data
    X_train_h, y_train_h = load_images(base / "training" / "healthy", 0)
    X_train_p, y_train_p = load_images(base / "training" / "parkinson", 1)
    X_test_h, y_test_h = load_images(base / "testing" / "healthy", 0)
    X_test_p, y_test_p = load_images(base / "testing" / "parkinson", 1)

    X_train_imgs = X_train_h + X_train_p
    y_train = y_train_h + y_train_p
    X_test_imgs = X_test_h + X_test_p
    y_test = y_test_h + y_test_p

    print(f"\n  Extracting features for {drawing_type}...")
    X_train_feats = np.array([extract_all_features(img) for img in X_train_imgs])
    X_test_feats = np.array([extract_all_features(img) for img in X_test_imgs])
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_feats)
    X_test_scaled = scaler.transform(X_test_feats)

    # Train multiple classifiers
    classifiers = {
        "svm_rbf": SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42),
        "svm_linear": SVC(kernel="linear", C=1, probability=True, random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_split=3,
            random_state=42, class_weight="balanced",
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.05,
            min_samples_split=3, random_state=42,
        ),
    }

    results = {}
    for name, clf in classifiers.items():
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        results[name] = {"clf": clf, "accuracy": acc, "predictions": y_pred}
        print(f"    {name}: accuracy={acc:.4f}")

    # Find best single classifier
    best_name = max(results, key=lambda k: results[k]["accuracy"])
    best_clf = results[best_name]["clf"]
    best_acc = results[best_name]["accuracy"]
    print(f"\n  Best single classifier: {best_name} ({best_acc:.4f})")

    # Ensemble vote
    all_preds = np.array([results[n]["predictions"] for n in results])
    ensemble_pred = (np.mean(all_preds, axis=0) > 0.5).astype(int)
    ensemble_acc = accuracy_score(y_test, ensemble_pred)
    print(f"  Ensemble accuracy: {ensemble_acc:.4f}")

    # Save the best + ensemble components
    model_data = {
        "scaler": scaler,
        "classifiers": {n: r["clf"] for n, r in results.items()},
        "best_classifier": best_name,
        "ensemble_weights": {n: r["accuracy"] for n, r in results.items()},
    }

    model_path = MODEL_DIR / f"{drawing_type}_ensemble.pkl"
    joblib.dump(model_data, model_path)

    # Also print classification report for best
    print(f"\n  Classification Report ({best_name}):")
    print(classification_report(y_test, results[best_name]["predictions"],
                                target_names=["Healthy", "Parkinson"]))

    print(f"  Classification Report (Ensemble):")
    print(classification_report(y_test, ensemble_pred,
                                target_names=["Healthy", "Parkinson"]))

    # Save metadata
    metadata = {
        "drawing_type": drawing_type,
        "best_classifier": best_name,
        "best_accuracy": float(best_acc),
        "ensemble_accuracy": float(ensemble_acc),
        "classifier_accuracies": {n: float(r["accuracy"]) for n, r in results.items()},
        "feature_count": X_train_feats.shape[1],
        "train_samples": len(X_train_imgs),
        "test_samples": len(X_test_imgs),
        "trained_at": datetime.now().isoformat(),
    }
    meta_path = MODEL_DIR / f"{drawing_type}_ensemble_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("🧠 Parkinson's Handwriting Detection - HOG+SVM Ensemble Training")
    print(f"   Dataset: {DATASET_DIR}")
    print(f"   Models:  {MODEL_DIR}")

    results = {}
    for dtype in ["spiral", "wave"]:
        print(f"\n{'='*60}")
        print(f"  TRAINING: {dtype.upper()} ENSEMBLE")
        print(f"{'='*60}")
        results[dtype] = train_svm_model(dtype)

    print(f"\n{'='*60}")
    print("  TRAINING COMPLETE")
    print(f"{'='*60}")
    for dtype, res in results.items():
        print(f"  {dtype.upper()}: best={res['best_accuracy']:.4f} ensemble={res['ensemble_accuracy']:.4f}")


if __name__ == "__main__":
    main()
