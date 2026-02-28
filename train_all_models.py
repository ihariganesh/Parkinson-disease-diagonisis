#!/usr/bin/env python3
"""
Comprehensive ML Model Training for Parkinson's Disease Detection
Trains both Handwriting (HOG+SVM Ensemble) and Speech (RF/GBT) models properly.

Usage:
    python train_all_models.py
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

from sklearn.svm import SVC
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    BaggingClassifier,
    AdaBoostClassifier,
)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    GridSearchCV,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from skimage.feature import hog, local_binary_pattern

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent


# ═══════════════════════════════════════════════════════════════════════
# PART 1: HANDWRITING MODEL TRAINING
# ═══════════════════════════════════════════════════════════════════════

class HandwritingTrainer:
    """Train HOG + SVM ensemble for spiral/wave handwriting analysis."""

    DATASET_DIR = PROJECT_ROOT / "parkinson_diagram_dataset"
    OUTPUT_DIR = PROJECT_ROOT / "ml-models" / "models" / "handwriting"

    def __init__(self):
        self.img_size = 128  # For HOG feature extraction
        self.augmentations_per_image = 8  # Data augmentation multiplier

    # ── Image loading & augmentation ─────────────────────────────────

    def load_image(self, path: str) -> np.ndarray:
        """Load and preprocess an image to BGR."""
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            return None
        # Handle alpha channel
        if len(img.shape) == 3 and img.shape[2] == 4:
            alpha = img[:, :, 3] / 255.0
            bgr = np.ones_like(img[:, :, :3], dtype=np.float64) * 255
            for c in range(3):
                bgr[:, :, c] = img[:, :, c] * alpha + bgr[:, :, c] * (1 - alpha)
            img = bgr.astype(np.uint8)
        elif len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img = img[:, :, :3]
        return img

    def augment_image(self, image: np.ndarray) -> list:
        """Generate augmented versions of an image."""
        h, w = image.shape[:2]
        augmented = [image.copy()]

        # 1. Slight rotations (-15 to +15 degrees)
        for angle in [-12, -6, 6, 12]:
            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), borderValue=(255, 255, 255))
            augmented.append(rotated)

        # 2. Small translations
        for dx, dy in [(10, 0), (-10, 0), (0, 10), (0, -10)]:
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            shifted = cv2.warpAffine(image, M, (w, h), borderValue=(255, 255, 255))
            augmented.append(shifted)

        # 3. Zoom in/out
        for scale in [0.9, 1.1]:
            M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
            zoomed = cv2.warpAffine(image, M, (w, h), borderValue=(255, 255, 255))
            augmented.append(zoomed)

        # 4. Brightness adjustments
        for beta in [-30, 30]:
            adjusted = cv2.convertScaleAbs(image, alpha=1.0, beta=beta)
            augmented.append(adjusted)

        # 5. Gaussian noise
        noise = np.random.normal(0, 10, image.shape).astype(np.uint8)
        noisy = cv2.add(image, noise)
        augmented.append(noisy)

        # 6. Horizontal flip (for wave patterns this is valid)
        augmented.append(cv2.flip(image, 1))

        # 7. Slight perspective warp
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        offset = 8
        pts2 = np.float32([
            [offset, offset], [w - offset, 0],
            [0, h - offset], [w - offset, h - offset]
        ])
        M_persp = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(image, M_persp, (w, h), borderValue=(255, 255, 255))
        augmented.append(warped)

        return augmented

    # ── Feature extraction ───────────────────────────────────────────

    def extract_hog_features(self, image: np.ndarray) -> np.ndarray:
        """Extract HOG features from BGR image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        resized = cv2.resize(gray, (self.img_size, self.img_size))
        return hog(
            resized,
            orientations=12,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
            transform_sqrt=True,
        )

    def extract_structural_features(self, image: np.ndarray) -> np.ndarray:
        """Extract structural features from handwriting image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        resized = cv2.resize(gray, (200, 200))
        features = []

        # Binary threshold
        _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        features.append(np.sum(binary > 0) / binary.size)  # ink density

        # Contour features
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        features.append(len(contours))
        if contours:
            areas = [cv2.contourArea(c) for c in contours]
            perimeters = [cv2.arcLength(c, True) for c in contours]
            features.extend([
                np.mean(areas), np.std(areas), np.max(areas),
                np.mean(perimeters), np.std(perimeters),
            ])
            largest = max(contours, key=cv2.contourArea)
            area, peri = cv2.contourArea(largest), cv2.arcLength(largest, True)
            features.append(4 * np.pi * area / (peri ** 2) if peri > 0 else 0)
        else:
            features.extend([0] * 6)

        # Gradient features
        sobelx = cv2.Sobel(resized, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(resized, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        direction = np.arctan2(sobely, sobelx)
        features.extend([
            np.mean(magnitude), np.std(magnitude),
            np.mean(direction), np.std(direction),
        ])

        # Pixel stats
        features.extend([np.mean(resized), np.std(resized), np.median(resized)])

        # Laplacian (blur/sharpness)
        laplacian = cv2.Laplacian(resized, cv2.CV_64F)
        features.extend([np.var(laplacian), np.mean(np.abs(laplacian))])

        # Edge density
        edges = cv2.Canny(resized, 50, 150)
        features.append(np.sum(edges > 0) / edges.size)

        # LBP histogram
        lbp = local_binary_pattern(resized, P=8, R=1, method="uniform")
        lbp_hist, _ = np.histogram(lbp, bins=10, density=True)
        features.extend(lbp_hist.tolist())

        # Hu moments
        moments = cv2.moments(binary)
        hu = cv2.HuMoments(moments).flatten()
        hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
        features.extend(hu.tolist())

        # Zoning features (5×5)
        zone_size = 5
        zh, zw = 200 // zone_size, 200 // zone_size
        for i in range(zone_size):
            for j in range(zone_size):
                zone = binary[i * zh:(i + 1) * zh, j * zw:(j + 1) * zw]
                features.append(np.sum(zone > 0) / zone.size)

        return np.array(features, dtype=np.float64)

    def extract_all_features(self, image: np.ndarray) -> np.ndarray:
        """Combine HOG + structural features."""
        return np.concatenate([
            self.extract_hog_features(image),
            self.extract_structural_features(image),
        ])

    # ── Dataset loading ──────────────────────────────────────────────

    def load_dataset(self, drawing_type: str):
        """Load training and testing sets for a drawing type."""
        train_dir = self.DATASET_DIR / drawing_type / "training"
        test_dir = self.DATASET_DIR / drawing_type / "testing"

        X_train, y_train = [], []
        X_test, y_test = [], []

        for label, class_name in enumerate(["healthy", "parkinson"]):
            # Training set with augmentation
            train_class_dir = train_dir / class_name
            if train_class_dir.exists():
                for img_path in sorted(train_class_dir.glob("*.png")):
                    img = self.load_image(str(img_path))
                    if img is None:
                        continue
                    # Original + augmented
                    augmented_images = self.augment_image(img)
                    for aug_img in augmented_images:
                        try:
                            feats = self.extract_all_features(aug_img)
                            X_train.append(feats)
                            y_train.append(label)
                        except Exception:
                            pass

            # Testing set (no augmentation)
            test_class_dir = test_dir / class_name
            if test_class_dir.exists():
                for img_path in sorted(test_class_dir.glob("*.png")):
                    img = self.load_image(str(img_path))
                    if img is None:
                        continue
                    try:
                        feats = self.extract_all_features(img)
                        X_test.append(feats)
                        y_test.append(label)
                    except Exception:
                        pass

        return (
            np.array(X_train), np.array(y_train),
            np.array(X_test), np.array(y_test),
        )

    # ── Model training ───────────────────────────────────────────────

    def train_drawing_type(self, drawing_type: str) -> dict:
        """Train ensemble for a specific drawing type."""
        print(f"\n{'='*60}")
        print(f"  TRAINING {drawing_type.upper()} MODEL")
        print(f"{'='*60}")

        X_train, y_train, X_test, y_test = self.load_dataset(drawing_type)
        print(f"  Training samples: {len(X_train)} ({sum(y_train==0)} healthy, {sum(y_train==1)} parkinson)")
        print(f"  Test samples:     {len(X_test)} ({sum(y_test==0)} healthy, {sum(y_test==1)} parkinson)")
        print(f"  Feature vector:   {X_train.shape[1]} dimensions")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Cross-validation on training set
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Define classifiers with tuned hyperparameters
        classifiers = {
            "svm_rbf": SVC(
                kernel="rbf", C=10.0, gamma="scale",
                probability=True, random_state=42, class_weight="balanced",
            ),
            "svm_linear": SVC(
                kernel="linear", C=1.0,
                probability=True, random_state=42, class_weight="balanced",
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=300, max_depth=15, min_samples_split=3,
                min_samples_leaf=2, random_state=42, class_weight="balanced",
                max_features="sqrt",
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200, max_depth=5, learning_rate=0.05,
                subsample=0.8, random_state=42,
            ),
            "adaboost": AdaBoostClassifier(
                n_estimators=100, learning_rate=0.1, random_state=42,
            ),
            "bagging_svm": BaggingClassifier(
                estimator=SVC(kernel="rbf", C=10.0, gamma="scale",
                              probability=True, class_weight="balanced"),
                n_estimators=10, random_state=42,
            ),
        }

        # Train each classifier & evaluate with CV
        trained = {}
        cv_scores = {}
        test_scores = {}
        print(f"\n  {'Classifier':<20} {'CV Mean±Std':<20} {'Test Acc':<12}")
        print(f"  {'-'*52}")

        for name, clf in classifiers.items():
            # Cross-validation
            scores = cross_val_score(clf, X_train_scaled, y_train, cv=cv, scoring="accuracy")
            cv_scores[name] = float(np.mean(scores))

            # Train on full training set
            clf.fit(X_train_scaled, y_train)
            trained[name] = clf

            # Test accuracy
            y_pred = clf.predict(X_test_scaled)
            test_acc = accuracy_score(y_test, y_pred)
            test_scores[name] = test_acc

            print(f"  {name:<20} {np.mean(scores):.3f}±{np.std(scores):.3f}       {test_acc:.3f}")

        # Compute ensemble weights based on CV performance
        total_cv = sum(cv_scores.values())
        ensemble_weights = {name: score / total_cv for name, score in cv_scores.items()}

        # Weighted ensemble prediction on test set
        weighted_preds = np.zeros(len(X_test_scaled))
        for name, clf in trained.items():
            probs = clf.predict_proba(X_test_scaled)[:, 1]
            weighted_preds += ensemble_weights[name] * probs

        ensemble_pred = (weighted_preds > 0.5).astype(int)
        ensemble_acc = accuracy_score(y_test, ensemble_pred)

        print(f"\n  {'ENSEMBLE':<20} {'—':<20} {ensemble_acc:.3f}")
        print(f"\n  Classification Report (Ensemble on Test Set):")
        print(classification_report(
            y_test, ensemble_pred,
            target_names=["Healthy", "Parkinson"],
            indent=4,
        ))

        # Save model
        model_data = {
            "scaler": scaler,
            "classifiers": trained,
            "ensemble_weights": ensemble_weights,
            "feature_dim": X_train.shape[1],
            "drawing_type": drawing_type,
            "cv_scores": cv_scores,
            "test_scores": test_scores,
            "ensemble_accuracy": ensemble_acc,
            "trained_at": datetime.now().isoformat(),
        }

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        model_path = self.OUTPUT_DIR / f"{drawing_type}_ensemble.pkl"
        joblib.dump(model_data, model_path)
        print(f"\n  ✅ Model saved: {model_path}")

        # Save metadata
        metadata = {
            "drawing_type": drawing_type,
            "ensemble_accuracy": ensemble_acc,
            "cv_scores": cv_scores,
            "test_scores": test_scores,
            "ensemble_weights": ensemble_weights,
            "feature_dim": int(X_train.shape[1]),
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "augmentation_factor": self.augmentations_per_image,
            "trained_at": datetime.now().isoformat(),
        }
        meta_path = self.OUTPUT_DIR / f"{drawing_type}_ensemble_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def train_all(self):
        """Train both spiral and wave models."""
        print("\n" + "=" * 60)
        print("  HANDWRITING MODEL TRAINING")
        print("  Dataset: parkinson_diagram_dataset")
        print("  Method:  HOG + Structural Features → SVM/RF/GBT Ensemble")
        print("=" * 60)

        results = {}
        for dtype in ["spiral", "wave"]:
            results[dtype] = self.train_drawing_type(dtype)

        print(f"\n{'='*60}")
        print(f"  HANDWRITING TRAINING SUMMARY")
        print(f"{'='*60}")
        for dtype, meta in results.items():
            print(f"  {dtype.upper()}: Ensemble={meta['ensemble_accuracy']:.1%}")
            for clf_name, acc in meta["test_scores"].items():
                print(f"    {clf_name}: {acc:.1%}")

        return results


# ═══════════════════════════════════════════════════════════════════════
# PART 2: SPEECH MODEL TRAINING
# ═══════════════════════════════════════════════════════════════════════

class SpeechTrainer:
    """Train Random Forest + GBT for speech-based PD detection."""

    CSV_PATH = PROJECT_ROOT / "ml-models" / "pd_speech_features.csv"
    OUTPUT_DIR = PROJECT_ROOT / "models" / "speech"

    def train(self) -> dict:
        print("\n" + "=" * 60)
        print("  SPEECH MODEL TRAINING")
        print("  Dataset: pd_speech_features.csv")
        print("  Method:  RF + GBT Ensemble with 5-fold CV")
        print("=" * 60)

        # Load dataset
        df = pd.read_csv(self.CSV_PATH)
        print(f"\n  Dataset shape: {df.shape}")
        print(f"  Columns: {list(df.columns[:10])}... + {len(df.columns)-10} more")

        # Check for 'class' column (target)
        if "class" not in df.columns:
            # Try reading with header on row 1
            df = pd.read_csv(self.CSV_PATH, header=1)

        if "class" not in df.columns:
            print("  ❌ Could not find 'class' column in speech dataset!")
            return {}

        y = df["class"].values
        print(f"  Class distribution: Healthy={sum(y == 0)}, Parkinson={sum(y == 1)}")

        # Drop non-feature columns
        drop_cols = ["id", "class", "gender"]
        X = df.drop([c for c in drop_cols if c in df.columns], axis=1).values
        feature_names = [c for c in df.columns if c not in drop_cols]
        print(f"  Features: {X.shape[1]}")

        # Handle NaN/inf
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Stratified 5-fold CV
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        classifiers = {
            "random_forest": RandomForestClassifier(
                n_estimators=500, max_depth=20, min_samples_split=3,
                min_samples_leaf=1, random_state=42, class_weight="balanced",
                max_features="sqrt",
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=300, max_depth=5, learning_rate=0.05,
                subsample=0.8, random_state=42,
            ),
            "svm_rbf": SVC(
                kernel="rbf", C=10.0, gamma="scale",
                probability=True, random_state=42, class_weight="balanced",
            ),
        }

        print(f"\n  {'Classifier':<25} {'5-Fold CV Accuracy':<20}")
        print(f"  {'-'*45}")

        trained = {}
        cv_scores_all = {}
        for name, clf in classifiers.items():
            scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="accuracy")
            cv_scores_all[name] = {
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "folds": scores.tolist(),
            }
            print(f"  {name:<25} {np.mean(scores):.4f} ± {np.std(scores):.4f}")

            # Train on full data
            clf.fit(X_scaled, y)
            trained[name] = clf

        # Pick the best single model by CV score
        best_name = max(cv_scores_all, key=lambda k: cv_scores_all[k]["mean"])
        best_clf = trained[best_name]
        best_cv = cv_scores_all[best_name]["mean"]
        print(f"\n  Best model: {best_name} (CV={best_cv:.4f})")

        # Detailed CV report for best model
        y_pred_cv = np.zeros_like(y)
        for train_idx, val_idx in cv.split(X_scaled, y):
            clone = type(best_clf)(**best_clf.get_params())
            clone.fit(X_scaled[train_idx], y[train_idx])
            y_pred_cv[val_idx] = clone.predict(X_scaled[val_idx])

        print(f"\n  Cross-validated Classification Report ({best_name}):")
        print(classification_report(
            y, y_pred_cv,
            target_names=["Healthy", "Parkinson"],
            indent=4,
        ))
        print(f"  Confusion Matrix:")
        cm = confusion_matrix(y, y_pred_cv)
        print(f"    TN={cm[0][0]}, FP={cm[0][1]}")
        print(f"    FN={cm[1][0]}, TP={cm[1][1]}")

        # Save the best model
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        joblib.dump(best_clf, self.OUTPUT_DIR / "speech_rf_model.pkl")
        joblib.dump(scaler, self.OUTPUT_DIR / "speech_rf_scaler.pkl")
        joblib.dump(feature_names, self.OUTPUT_DIR / "speech_feature_names.pkl")

        # Save training report
        report = {
            "best_model": best_name,
            "best_cv_accuracy": best_cv,
            "cv_scores": cv_scores_all,
            "n_features": int(X.shape[1]),
            "n_samples": int(len(y)),
            "class_distribution": {
                "healthy": int(sum(y == 0)),
                "parkinson": int(sum(y == 1)),
            },
            "feature_names_count": len(feature_names),
            "trained_at": datetime.now().isoformat(),
        }
        with open(self.OUTPUT_DIR / "speech_training_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n  ✅ Models saved to {self.OUTPUT_DIR}")
        return report


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Parkinson's Disease ML Model Training                  ║")
    print("║  Training: Handwriting + Speech models                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Train handwriting models
    hw_trainer = HandwritingTrainer()
    hw_results = hw_trainer.train_all()

    # Train speech model
    sp_trainer = SpeechTrainer()
    sp_results = sp_trainer.train()

    print("\n" + "=" * 60)
    print("  ALL TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Handwriting Spiral:  {hw_results.get('spiral', {}).get('ensemble_accuracy', 'N/A')}")
    print(f"  Handwriting Wave:    {hw_results.get('wave', {}).get('ensemble_accuracy', 'N/A')}")
    print(f"  Speech:              {sp_results.get('best_cv_accuracy', 'N/A')}")
    print(f"\n  Models saved to:")
    print(f"    ml-models/models/handwriting/  (spiral_ensemble.pkl, wave_ensemble.pkl)")
    print(f"    models/speech/                 (speech_rf_model.pkl, speech_rf_scaler.pkl)")
    print()
