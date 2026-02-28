#!/usr/bin/env python3
"""
Handwriting Model Training for Parkinson's Disease Detection
=============================================================
Trains SVM classifiers with HOG (Histogram of Oriented Gradients) features
on spiral and wave drawings from the parkinson_diagram_dataset.

Includes:
- Data augmentation to boost the small dataset
- Proper train/test split (uses the dataset's own split)
- Cross-validation on training set
- Comprehensive evaluation metrics
- Model serialization with joblib
"""

import os
import sys
import numpy as np
import cv2
import joblib
import json
from pathlib import Path
from datetime import datetime
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from skimage.feature import hog
from skimage.filters import threshold_otsu
from scipy.ndimage import rotate as scipy_rotate

# ─── Configuration ───────────────────────────────────────────────────────────

DATASET_ROOT = Path(__file__).parent / "parkinson_diagram_dataset"
MODELS_OUTPUT = Path(__file__).parent / "models"
MODELS_OUTPUT.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (128, 128)  # Resize target for HOG
HOG_PARAMS = {
    "orientations": 12,
    "pixels_per_cell": (8, 8),
    "cells_per_block": (3, 3),
    "block_norm": "L2-Hys",
    "transform_sqrt": True,
    "feature_vector": True,
}

# Augmentation settings
AUGMENTATION_FACTOR = 8  # Number of augmented copies per original image


# ─── Feature Extraction ─────────────────────────────────────────────────────

def load_and_preprocess(image_path: str, size: tuple = IMAGE_SIZE) -> np.ndarray:
    """Load image, convert to grayscale, resize, and normalize."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    # Normalize to 0-1
    normalized = blurred.astype(np.float64) / 255.0
    return normalized


def extract_hog_features(image: np.ndarray) -> np.ndarray:
    """Extract HOG features from a preprocessed grayscale image."""
    features = hog(image, **HOG_PARAMS)
    return features


def extract_geometric_features(image: np.ndarray) -> np.ndarray:
    """Extract additional geometric/statistical features from the image."""
    features = []
    
    # 1. Intensity statistics
    features.append(np.mean(image))
    features.append(np.std(image))
    features.append(np.median(image))
    features.append(np.percentile(image, 25))
    features.append(np.percentile(image, 75))
    
    # 2. Binarize and compute drawing properties
    try:
        thresh_val = threshold_otsu(image)
    except ValueError:
        thresh_val = 0.5
    binary = (image < thresh_val).astype(np.uint8)  # ink pixels
    
    ink_ratio = np.sum(binary) / binary.size
    features.append(ink_ratio)
    
    # 3. Edge density (Canny-like via Sobel)
    sobelx = cv2.Sobel((image * 255).astype(np.uint8), cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel((image * 255).astype(np.uint8), cv2.CV_64F, 0, 1, ksize=3)
    edge_magnitude = np.sqrt(sobelx**2 + sobely**2)
    features.append(np.mean(edge_magnitude))
    features.append(np.std(edge_magnitude))
    
    # 4. Contour-based features
    contours, _ = cv2.findContours(
        binary * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    features.append(len(contours))  # number of contours - tremor = more fragments
    
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        features.append(area)
        features.append(perimeter)
        # Circularity
        circularity = (4 * np.pi * area) / (perimeter**2 + 1e-8)
        features.append(circularity)
    else:
        features.extend([0.0, 0.0, 0.0])
    
    # 5. Symmetry (horizontal)
    h = image.shape[0]
    top_half = image[:h//2, :]
    bottom_half = np.flipud(image[h//2:, :])
    min_h = min(top_half.shape[0], bottom_half.shape[0])
    symmetry = 1.0 - np.mean(np.abs(top_half[:min_h] - bottom_half[:min_h]))
    features.append(symmetry)
    
    # 6. Texture: Local Binary Pattern approximation via variance
    # Window-based variance as proxy for texture roughness
    from scipy.ndimage import uniform_filter
    local_mean = uniform_filter(image, size=5)
    local_var = uniform_filter((image - local_mean)**2, size=5)
    features.append(np.mean(local_var))
    features.append(np.max(local_var))
    
    return np.array(features, dtype=np.float64)


def extract_all_features(image: np.ndarray) -> np.ndarray:
    """Combine HOG + geometric features into a single feature vector."""
    hog_feat = extract_hog_features(image)
    geo_feat = extract_geometric_features(image)
    return np.concatenate([hog_feat, geo_feat])


# ─── Data Augmentation ──────────────────────────────────────────────────────

def augment_image(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Apply random augmentation to an image."""
    augmented = image.copy()
    
    # 1. Random rotation (-15 to +15 degrees)
    angle = rng.uniform(-15, 15)
    augmented = scipy_rotate(augmented, angle, reshape=False, mode='constant', cval=1.0)
    
    # 2. Random horizontal flip (50% chance)
    if rng.random() > 0.5:
        augmented = np.fliplr(augmented)
    
    # 3. Random vertical flip (50% chance)
    if rng.random() > 0.5:
        augmented = np.flipud(augmented)
    
    # 4. Random brightness adjustment
    brightness = rng.uniform(0.85, 1.15)
    augmented = np.clip(augmented * brightness, 0, 1)
    
    # 5. Random Gaussian noise
    if rng.random() > 0.5:
        noise = rng.normal(0, 0.02, augmented.shape)
        augmented = np.clip(augmented + noise, 0, 1)
    
    # 6. Random translation (shift)
    tx, ty = rng.integers(-5, 6, size=2)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    h, w = augmented.shape
    augmented = cv2.warpAffine(
        (augmented * 255).astype(np.uint8), M, (w, h),
        borderMode=cv2.BORDER_CONSTANT, borderValue=255
    ).astype(np.float64) / 255.0
    
    return augmented


# ─── Dataset Loading ─────────────────────────────────────────────────────────

def load_dataset(drawing_type: str, augment: bool = True):
    """
    Load images from the dataset directory structure:
        {drawing_type}/training/{healthy,parkinson}/*.png
        {drawing_type}/testing/{healthy,parkinson}/*.png
    
    Returns:
        X_train, y_train, X_test, y_test (feature arrays and labels)
    """
    rng = np.random.default_rng(42)
    
    train_dir = DATASET_ROOT / drawing_type / "training"
    test_dir = DATASET_ROOT / drawing_type / "testing"
    
    if not train_dir.exists():
        raise FileNotFoundError(f"Training directory not found: {train_dir}")
    if not test_dir.exists():
        raise FileNotFoundError(f"Testing directory not found: {test_dir}")
    
    def load_from_dir(base_dir, do_augment=False):
        features_list = []
        labels_list = []
        
        for label_name, label_val in [("healthy", 0), ("parkinson", 1)]:
            class_dir = base_dir / label_name
            if not class_dir.exists():
                print(f"  ⚠️  Directory not found: {class_dir}")
                continue
            
            image_files = sorted([
                f for f in class_dir.iterdir()
                if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
            ])
            
            for img_path in image_files:
                try:
                    img = load_and_preprocess(str(img_path))
                    feat = extract_all_features(img)
                    features_list.append(feat)
                    labels_list.append(label_val)
                    
                    # Augment training data
                    if do_augment:
                        for _ in range(AUGMENTATION_FACTOR):
                            aug_img = augment_image(img, rng)
                            aug_feat = extract_all_features(aug_img)
                            features_list.append(aug_feat)
                            labels_list.append(label_val)
                            
                except Exception as e:
                    print(f"  ⚠️  Error processing {img_path.name}: {e}")
        
        return np.array(features_list), np.array(labels_list)
    
    print(f"\n📂 Loading {drawing_type} training data...")
    X_train, y_train = load_from_dir(train_dir, do_augment=augment)
    print(f"   Training: {len(X_train)} samples "
          f"({np.sum(y_train == 0)} healthy, {np.sum(y_train == 1)} parkinson)")
    
    print(f"📂 Loading {drawing_type} testing data...")
    X_test, y_test = load_from_dir(test_dir, do_augment=False)
    print(f"   Testing:  {len(X_test)} samples "
          f"({np.sum(y_test == 0)} healthy, {np.sum(y_test == 1)} parkinson)")
    
    return X_train, y_train, X_test, y_test


# ─── Model Training ─────────────────────────────────────────────────────────

def train_and_evaluate(drawing_type: str):
    """Train SVM model for a specific drawing type and evaluate."""
    print(f"\n{'='*70}")
    print(f"  Training {drawing_type.upper()} Model")
    print(f"{'='*70}")
    
    # Load data
    X_train, y_train, X_test, y_test = load_dataset(drawing_type, augment=True)
    
    if len(X_train) == 0 or len(X_test) == 0:
        print(f"❌ Not enough data for {drawing_type}!")
        return None
    
    # Handle NaN/Inf
    X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
    X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ── Cross-validation on training set ──
    print(f"\n🔄 Running 5-fold cross-validation on training set...")
    svm = SVC(
        kernel='rbf',
        C=10.0,
        gamma='scale',
        class_weight='balanced',
        probability=True,
        random_state=42,
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(svm, X_train_scaled, y_train, cv=cv, scoring='accuracy')
    print(f"   CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"   CV Scores:   {[f'{s:.4f}' for s in cv_scores]}")
    
    cv_f1 = cross_val_score(svm, X_train_scaled, y_train, cv=cv, scoring='f1')
    print(f"   CV F1:       {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")
    
    # ── Train final model on full training set ──
    print(f"\n🏋️ Training final model on full training set...")
    svm.fit(X_train_scaled, y_train)
    
    # ── Evaluate on test set ──
    y_pred = svm.predict(X_test_scaled)
    y_proba = svm.predict_proba(X_test_scaled)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    try:
        auc = roc_auc_score(y_test, y_proba)
    except ValueError:
        auc = 0.0
    
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\n📊 Test Set Results ({drawing_type}):")
    print(f"   Accuracy:  {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall:    {recall:.4f}")
    print(f"   F1 Score:  {f1:.4f}")
    print(f"   AUC-ROC:   {auc:.4f}")
    print(f"\n   Confusion Matrix:")
    print(f"   {'':>12} Pred Healthy  Pred PD")
    print(f"   {'True Healthy':>12}    {cm[0][0]:>5}      {cm[0][1]:>5}")
    print(f"   {'True PD':>12}    {cm[1][0]:>5}      {cm[1][1]:>5}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Healthy', 'Parkinson'])}")
    
    # ── Save model ──
    model_path = MODELS_OUTPUT / f"{drawing_type}_svm_model_svm.pkl"
    scaler_path = MODELS_OUTPUT / f"{drawing_type}_svm_model_scaler.pkl"
    
    joblib.dump(svm, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"   ✅ Model saved:  {model_path}")
    print(f"   ✅ Scaler saved: {scaler_path}")
    
    return {
        "drawing_type": drawing_type,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "feature_count": int(X_train.shape[1]),
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "cv_f1_mean": float(cv_f1.mean()),
        "test_accuracy": float(accuracy),
        "test_precision": float(precision),
        "test_recall": float(recall),
        "test_f1": float(f1),
        "test_auc_roc": float(auc),
        "confusion_matrix": cm.tolist(),
        "model_path": str(model_path),
        "scaler_path": str(scaler_path),
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  Parkinson's Disease Handwriting Model Training")
    print(f"  Dataset: {DATASET_ROOT}")
    print(f"  Output:  {MODELS_OUTPUT}")
    print(f"  Time:    {datetime.now().isoformat()}")
    print("=" * 70)
    
    results = {}
    
    for drawing_type in ["spiral", "wave"]:
        result = train_and_evaluate(drawing_type)
        if result:
            results[drawing_type] = result
    
    # Save training report
    report_path = MODELS_OUTPUT / "handwriting_training_report.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset": str(DATASET_ROOT),
        "image_size": list(IMAGE_SIZE),
        "hog_params": HOG_PARAMS,
        "augmentation_factor": AUGMENTATION_FACTOR,
        "results": results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Training report saved: {report_path}")
    
    # Summary
    print(f"\n{'='*70}")
    print("  TRAINING SUMMARY")
    print(f"{'='*70}")
    for dtype, res in results.items():
        print(f"  {dtype.upper():>8}: Test Acc={res['test_accuracy']:.4f}, "
              f"F1={res['test_f1']:.4f}, AUC={res['test_auc_roc']:.4f}, "
              f"CV Acc={res['cv_accuracy_mean']:.4f}±{res['cv_accuracy_std']:.4f}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
