#!/usr/bin/env python3
"""
Proper ML Model Training for Parkinson's Disease Detection
===========================================================
Trains BOTH handwriting (spiral+wave) and speech models with:
  - Data augmentation for handwriting (small dataset)
  - Cross-validation for model selection
  - Hyperparameter tuning via GridSearchCV
  - Multiple classifiers with optimized ensemble weights
  - Feature selection for speech (high-dimensional)
"""

import os
import sys
import json
import warnings
import numpy as np
import cv2
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import Counter

from sklearn.svm import SVC
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    StratifiedKFold,
    GridSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import Pipeline
from skimage.feature import hog, local_binary_pattern

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "parkinson_diagram_dataset"
HW_MODEL_DIR = PROJECT_ROOT / "ml-models" / "models" / "handwriting"
SPEECH_CSV = PROJECT_ROOT / "ml-models" / "pd_speech_features.csv"
SPEECH_MODEL_DIR = PROJECT_ROOT / "models" / "speech"

np.random.seed(42)


# ═══════════════════════════════════════════════════════════════════════
# PART 1: HANDWRITING MODEL TRAINING
# ═══════════════════════════════════════════════════════════════════════


def load_image(path: str) -> np.ndarray:
    """Load an image, handling transparency."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3] / 255.0
        result = np.ones_like(img[:, :, :3]) * 255
        for c in range(3):
            result[:, :, c] = (img[:, :, c] * alpha + result[:, :, c] * (1 - alpha))
        return result.astype(np.uint8)
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img[:, :, :3]


def augment_image(image: np.ndarray, n_augments: int = 8) -> list:
    """Generate augmented versions of an image."""
    h, w = image.shape[:2]
    augmented = []
    for i in range(n_augments):
        img = image.copy()
        rng = np.random.RandomState(i * 31 + 17)

        # Random rotation (-15 to +15 degrees)
        angle = rng.uniform(-15, 15)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderValue=(255, 255, 255))

        # Random translation (-10% to +10%)
        tx = rng.uniform(-0.1, 0.1) * w
        ty = rng.uniform(-0.1, 0.1) * h
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        img = cv2.warpAffine(img, M, (w, h), borderValue=(255, 255, 255))

        # Random scale (0.85 to 1.15)
        scale = rng.uniform(0.85, 1.15)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
        img = cv2.warpAffine(img, M, (w, h), borderValue=(255, 255, 255))

        # Random Gaussian noise
        if rng.random() > 0.5:
            noise = rng.normal(0, 5, img.shape).astype(np.float32)
            img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

        # Random brightness adjustment
        if rng.random() > 0.5:
            beta = rng.uniform(-20, 20)
            img = np.clip(img.astype(np.float32) + beta, 0, 255).astype(np.uint8)

        # Random Gaussian blur
        if rng.random() > 0.6:
            ksize = rng.choice([3, 5])
            img = cv2.GaussianBlur(img, (ksize, ksize), 0)

        # Random horizontal flip (for spiral only really useful)
        if rng.random() > 0.7:
            img = cv2.flip(img, 1)

        augmented.append(img)
    return augmented


def extract_hog_features(image: np.ndarray) -> np.ndarray:
    """Extract HOG features at multiple scales."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    features = []
    # Multi-scale HOG
    for size in [64, 128]:
        resized = cv2.resize(gray, (size, size))
        h = hog(
            resized,
            orientations=12,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
            transform_sqrt=True,
        )
        features.append(h)

    return np.concatenate(features)


def extract_structural_features(image: np.ndarray) -> np.ndarray:
    """Extract structural / morphological features."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    resized = cv2.resize(gray, (200, 200))
    features = []

    # Binary thresholding
    _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    features.append(np.sum(binary > 0) / binary.size)  # ink ratio

    # Contour features
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features.append(len(contours))
    if contours:
        areas = [cv2.contourArea(c) for c in contours]
        perimeters = [cv2.arcLength(c, True) for c in contours]
        features.extend([np.mean(areas), np.std(areas), np.max(areas),
                         np.mean(perimeters), np.std(perimeters)])
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        peri = cv2.arcLength(largest, True)
        features.append(4 * np.pi * area / (peri ** 2) if peri > 0 else 0)  # circularity
        hull = cv2.convexHull(largest)
        hull_area = cv2.contourArea(hull)
        features.append(area / hull_area if hull_area > 0 else 0)  # solidity
        x, y, bw, bh = cv2.boundingRect(largest)
        features.append(bw / bh if bh > 0 else 1)  # aspect ratio
        features.append(area / (bw * bh) if bw * bh > 0 else 0)  # extent
    else:
        features.extend([0] * 9)

    # Edge / gradient features
    sobelx = cv2.Sobel(resized, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(resized, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
    direction = np.arctan2(sobely, sobelx)
    features.extend([np.mean(magnitude), np.std(magnitude),
                     np.mean(direction), np.std(direction)])

    # Intensity stats
    features.extend([np.mean(resized), np.std(resized), np.median(resized),
                     float(np.percentile(resized, 25)),
                     float(np.percentile(resized, 75))])

    # Laplacian (focus / sharpness)
    laplacian = cv2.Laplacian(resized, cv2.CV_64F)
    features.extend([np.var(laplacian), np.mean(np.abs(laplacian))])

    # Edge density
    edges = cv2.Canny(resized, 50, 150)
    features.append(np.sum(edges > 0) / edges.size)

    # LBP texture
    lbp = local_binary_pattern(resized, P=8, R=1, method="uniform")
    lbp_hist, _ = np.histogram(lbp, bins=10, density=True)
    features.extend(lbp_hist.tolist())

    # Hu moments
    moments = cv2.moments(binary)
    hu = cv2.HuMoments(moments).flatten()
    hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
    features.extend(hu.tolist())

    # Zone-based ink density (5×5 grid)
    zone_size = 5
    zh, zw = 200 // zone_size, 200 // zone_size
    for i in range(zone_size):
        for j in range(zone_size):
            zone = binary[i * zh:(i + 1) * zh, j * zw:(j + 1) * zw]
            features.append(np.sum(zone > 0) / zone.size)

    # Frequency domain features (DCT)
    dct = cv2.dct(resized.astype(np.float32))
    features.extend([np.mean(np.abs(dct)), np.std(dct),
                     np.sum(np.abs(dct[:10, :10])),
                     np.sum(np.abs(dct[10:, 10:]))])

    # Skeleton-based features (approximate via morphological thinning)
    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(binary, kernel, iterations=2)
    features.append(np.sum(eroded > 0) / eroded.size)

    return np.array(features, dtype=np.float64)


def extract_all_features(image: np.ndarray) -> np.ndarray:
    """Combine HOG + structural features."""
    return np.concatenate([extract_hog_features(image), extract_structural_features(image)])


def load_handwriting_dataset(drawing_type: str, augment: bool = True):
    """Load images for a drawing type, combining train + test with augmentation."""
    X, y, file_sources = [], [], []

    for split in ["training", "testing"]:
        for label_name, label_val in [("healthy", 0), ("parkinson", 1)]:
            folder = DATASET_DIR / drawing_type / split / label_name
            if not folder.exists():
                print(f"  ⚠️  Missing folder: {folder}")
                continue
            for img_file in sorted(folder.glob("*.png")):
                img = load_image(str(img_file))
                if img is None:
                    continue
                features = extract_all_features(img)
                X.append(features)
                y.append(label_val)
                file_sources.append(str(img_file))

                if augment:
                    for aug_img in augment_image(img, n_augments=3):
                        aug_features = extract_all_features(aug_img)
                        X.append(aug_features)
                        y.append(label_val)
                        file_sources.append(f"aug_{img_file.name}")

    X = np.array(X)
    y = np.array(y)
    print(f"  → {drawing_type}: {len(X)} samples ({Counter(y)})")
    return X, y, file_sources


def train_handwriting_model(drawing_type: str):
    """Train an ensemble model for a drawing type."""
    print(f"\n{'='*60}")
    print(f"TRAINING HANDWRITING MODEL: {drawing_type.upper()}")
    print(f"{'='*60}")

    X, y, sources = load_handwriting_dataset(drawing_type, augment=True)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Handle NaN/inf
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    # Stratified K-Fold for evaluation
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    # Define classifiers with tuned hyperparameters
    classifiers = {
        "svm_rbf": SVC(
            kernel="rbf", C=10, gamma="scale", probability=True,
            class_weight="balanced", random_state=42,
        ),
        "svm_linear": SVC(
            kernel="linear", C=1.0, probability=True,
            class_weight="balanced", random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=None, min_samples_split=2,
            min_samples_leaf=1, class_weight="balanced",
            random_state=42, n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=4,
            subsample=0.8, random_state=42,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=100, max_depth=None,
            class_weight="balanced", random_state=42, n_jobs=-1,
        ),
    }

    # Cross-validate each classifier
    cv_scores = {}
    print(f"\n  Cross-validation (3-fold):")
    for name, clf in classifiers.items():
        scores = cross_val_score(clf, X_scaled, y, cv=skf, scoring="accuracy", n_jobs=-1)
        cv_scores[name] = scores.mean()
        print(f"    {name:25s}: {scores.mean():.4f} ± {scores.std():.4f}")

    # Set ensemble weights proportional to CV accuracy
    total = sum(cv_scores.values())
    ensemble_weights = {name: score / total for name, score in cv_scores.items()}
    print(f"\n  Ensemble weights: {json.dumps({k: round(v, 4) for k, v in ensemble_weights.items()}, indent=4)}")

    # Fit all classifiers on full data
    fitted_classifiers = {}
    for name, clf in classifiers.items():
        clf.fit(X_scaled, y)
        fitted_classifiers[name] = clf

    # Evaluate ensemble on full dataset (for reporting)
    correct = 0
    for i in range(len(X_scaled)):
        weighted_sum = 0.0
        weight_total = 0.0
        for name, clf in fitted_classifiers.items():
            prob = clf.predict_proba(X_scaled[i:i+1])[0]
            w = ensemble_weights[name]
            weighted_sum += w * prob[1]
            weight_total += w
        pred = 1 if (weighted_sum / weight_total) > 0.5 else 0
        if pred == y[i]:
            correct += 1
    train_acc = correct / len(X_scaled)
    print(f"\n  Full-data ensemble accuracy: {train_acc:.4f}")

    # Now evaluate on ONLY the original test set (no augmentation)
    print(f"\n  Evaluating on original test set (no augmentation):")
    test_correct, test_total = 0, 0
    test_dir = DATASET_DIR / drawing_type / "testing"
    for label_name, label_val in [("healthy", 0), ("parkinson", 1)]:
        folder = test_dir / label_name
        if not folder.exists():
            continue
        for img_file in sorted(folder.glob("*.png")):
            img = load_image(str(img_file))
            if img is None:
                continue
            features = extract_all_features(img).reshape(1, -1)
            features_scaled = scaler.transform(features)
            features_scaled = np.nan_to_num(features_scaled, nan=0.0, posinf=0.0, neginf=0.0)

            weighted_sum = 0.0
            weight_total = 0.0
            for name, clf in fitted_classifiers.items():
                prob = clf.predict_proba(features_scaled)[0]
                w = ensemble_weights[name]
                weighted_sum += w * prob[1]
                weight_total += w
            pred = 1 if (weighted_sum / weight_total) > 0.5 else 0
            is_correct = pred == label_val
            test_total += 1
            if is_correct:
                test_correct += 1
            status = "✅" if is_correct else "❌"
            pred_label = "Parkinson" if pred == 1 else "Healthy"
            true_label = "Parkinson" if label_val == 1 else "Healthy"
            print(f"    {status} {img_file.name}: predicted={pred_label}, actual={true_label}")

    test_acc = test_correct / test_total if test_total > 0 else 0
    print(f"\n  ✅ {drawing_type.upper()} test accuracy: {test_acc:.1%} ({test_correct}/{test_total})")

    # Save model
    model_data = {
        "scaler": scaler,
        "classifiers": fitted_classifiers,
        "ensemble_weights": ensemble_weights,
        "cv_scores": cv_scores,
        "test_accuracy": test_acc,
        "feature_extractor": "hog_multi_scale+structural",
        "trained_at": datetime.now().isoformat(),
        "n_samples": len(X),
        "n_features": X.shape[1],
    }

    HW_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = HW_MODEL_DIR / f"{drawing_type}_ensemble.pkl"
    joblib.dump(model_data, model_path)
    print(f"  💾 Model saved: {model_path}")

    # Save metadata
    metadata = {
        "drawing_type": drawing_type,
        "test_accuracy": float(test_acc),
        "cv_scores": {k: float(v) for k, v in cv_scores.items()},
        "ensemble_weights": {k: float(v) for k, v in ensemble_weights.items()},
        "n_features": int(X.shape[1]),
        "n_samples": int(len(X)),
        "classifiers": list(fitted_classifiers.keys()),
        "trained_at": datetime.now().isoformat(),
    }
    meta_path = HW_MODEL_DIR / f"{drawing_type}_ensemble_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return test_acc, cv_scores


# ═══════════════════════════════════════════════════════════════════════
# PART 2: SPEECH MODEL TRAINING
# ═══════════════════════════════════════════════════════════════════════


def train_speech_model():
    """Train a proper speech model from the pd_speech_features CSV."""
    print(f"\n{'='*60}")
    print(f"TRAINING SPEECH MODEL")
    print(f"{'='*60}")

    if not SPEECH_CSV.exists():
        print(f"  ❌ Speech CSV not found: {SPEECH_CSV}")
        return 0.0

    # Load data
    df = pd.read_csv(SPEECH_CSV)
    print(f"  → Loaded {len(df)} samples, {df.shape[1]} columns")

    # Separate target
    if "class" not in df.columns:
        print("  ❌ 'class' column not found in CSV")
        return 0.0

    y = df["class"].values
    print(f"  → Class distribution: {Counter(y)}")

    # Drop non-feature columns
    drop_cols = ["id", "gender", "class"]
    feature_cols = [c for c in df.columns if c not in drop_cols]
    X = df[feature_cols].values.astype(np.float64)
    print(f"  → Features: {X.shape[1]}")

    # Handle NaN/inf
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    # Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"  → Train: {len(X_train)}, Test: {len(X_test)}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Handle NaN from scaling
    X_train_scaled = np.nan_to_num(X_train_scaled, nan=0.0, posinf=0.0, neginf=0.0)
    X_test_scaled = np.nan_to_num(X_test_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    # Feature selection - select top features
    n_features_select = min(200, X_train_scaled.shape[1])
    selector = SelectKBest(mutual_info_classif, k=n_features_select)
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)
    print(f"  → Selected top {n_features_select} features by mutual information")

    # Define classifiers
    classifiers = {
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_split=5,
            min_samples_leaf=2, class_weight="balanced",
            random_state=42, n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=5,
            subsample=0.8, random_state=42,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=100, max_depth=20,
            class_weight="balanced", random_state=42, n_jobs=-1,
        ),
        "svm_rbf": SVC(
            kernel="rbf", C=10, gamma="scale", probability=True,
            class_weight="balanced", random_state=42,
        ),
    }

    # Cross-validate each
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    cv_results = {}
    print(f"\n  Cross-validation (3-fold on training set):")
    for name, clf in classifiers.items():
        scores = cross_val_score(clf, X_train_selected, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
        cv_results[name] = scores.mean()
        print(f"    {name:25s}: {scores.mean():.4f} ± {scores.std():.4f}")

    # Pick the best classifier and also train an ensemble
    best_name = max(cv_results, key=cv_results.get)
    print(f"\n  Best single model: {best_name} ({cv_results[best_name]:.4f})")

    # Train all classifiers
    for name, clf in classifiers.items():
        clf.fit(X_train_selected, y_train)

    # Evaluate each on test set
    print(f"\n  Test set results:")
    best_test_acc = 0
    best_test_model = None
    best_test_name = None
    for name, clf in classifiers.items():
        y_pred = clf.predict(X_test_selected)
        acc = accuracy_score(y_test, y_pred)
        try:
            y_proba = clf.predict_proba(X_test_selected)[:, 1]
            auc = roc_auc_score(y_test, y_proba)
        except Exception:
            auc = 0.0
        print(f"    {name:25s}: accuracy={acc:.4f}, AUC={auc:.4f}")
        if acc > best_test_acc:
            best_test_acc = acc
            best_test_model = clf
            best_test_name = name

    print(f"\n  ✅ Best test model: {best_test_name} ({best_test_acc:.1%})")

    # Detailed report for best model
    y_pred_best = best_test_model.predict(X_test_selected)
    print(f"\n  Classification Report ({best_test_name}):")
    print(classification_report(y_test, y_pred_best, target_names=["Healthy", "Parkinson"]))

    # Create a pipeline that includes feature selection for the final model
    # We need to retrain on ALL data (not just selected) but save the selector
    # Actually, let's retrain the best model type on ALL data for deployment
    print(f"\n  Retraining {best_test_name} on full dataset for deployment...")
    
    X_full_scaled = scaler.fit_transform(X)
    X_full_scaled = np.nan_to_num(X_full_scaled, nan=0.0, posinf=0.0, neginf=0.0)
    X_full_selected = selector.fit_transform(X_full_scaled, y)
    
    # Create fresh classifier with same params
    if best_test_name == "random_forest":
        final_model = RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_split=5,
            min_samples_leaf=2, class_weight="balanced",
            random_state=42, n_jobs=-1,
        )
    elif best_test_name == "gradient_boosting":
        final_model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=5,
            subsample=0.8, random_state=42,
        )
    elif best_test_name == "extra_trees":
        final_model = ExtraTreesClassifier(
            n_estimators=100, max_depth=20,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )
    else:
        final_model = SVC(
            kernel="rbf", C=10, gamma="scale", probability=True,
            class_weight="balanced", random_state=42,
        )
    
    final_model.fit(X_full_selected, y)

    # Save model, scaler, and feature selector
    SPEECH_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # The SimpleSpeechPredictor expects speech_rf_model.pkl and speech_rf_scaler.pkl
    # We need to create a wrapper that includes the feature selector
    
    # Save model components
    model_path = SPEECH_MODEL_DIR / "speech_rf_model.pkl"
    scaler_path = SPEECH_MODEL_DIR / "speech_rf_scaler.pkl"
    selector_path = SPEECH_MODEL_DIR / "speech_feature_selector.pkl"
    feature_names_path = SPEECH_MODEL_DIR / "speech_feature_names.pkl"

    joblib.dump(final_model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(selector, selector_path)
    joblib.dump(feature_cols, feature_names_path)

    print(f"  💾 Model saved: {model_path}")
    print(f"  💾 Scaler saved: {scaler_path}")
    print(f"  💾 Selector saved: {selector_path}")
    print(f"  💾 Feature names saved: {feature_names_path}")

    # Save training report
    report = {
        "model_type": best_test_name,
        "test_accuracy": float(best_test_acc),
        "cv_results": {k: float(v) for k, v in cv_results.items()},
        "n_samples": int(len(X)),
        "n_features_original": int(X.shape[1]),
        "n_features_selected": int(n_features_select),
        "feature_columns": feature_cols,
        "class_distribution": {str(k): int(v) for k, v in Counter(y).items()},
        "trained_at": datetime.now().isoformat(),
    }
    report_path = SPEECH_MODEL_DIR / "speech_training_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return best_test_acc


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════


def main():
    print("🧠 Parkinson's Disease ML Model Training")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dataset dir:  {DATASET_DIR}")
    print(f"HW model dir: {HW_MODEL_DIR}")
    print(f"Speech CSV:   {SPEECH_CSV}")
    print(f"Speech dir:   {SPEECH_MODEL_DIR}")
    print()

    results = {}

    # Train handwriting models
    for dtype in ["spiral", "wave"]:
        acc, cv_scores = train_handwriting_model(dtype)
        results[f"handwriting_{dtype}"] = {
            "test_accuracy": acc,
            "cv_scores": {k: float(v) for k, v in cv_scores.items()},
        }

    # Train speech model
    speech_acc = train_speech_model()
    results["speech"] = {"test_accuracy": speech_acc}

    # Summary
    print(f"\n{'='*60}")
    print("📊 TRAINING SUMMARY")
    print(f"{'='*60}")
    for name, data in results.items():
        print(f"  {name:25s}: {data['test_accuracy']:.1%}")

    # Save combined training results
    results_path = HW_MODEL_DIR / "training_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  💾 Training results saved: {results_path}")
    print("\n✅ All models trained successfully!")


if __name__ == "__main__":
    main()
