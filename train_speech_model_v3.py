#!/usr/bin/env python3
"""
Speech Model Retraining for Parkinson's Disease Detection
==========================================================
Retrains the RandomForest model on pd_speech_features.csv with:
- Proper stratified train/test split (80/20)
- SMOTE oversampling to fix class imbalance (564 PD vs 192 healthy)
- 5-fold stratified cross-validation
- Hyperparameter tuning via GridSearchCV
- Comprehensive evaluation metrics
- Feature importance analysis
"""

import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)

# Try to import SMOTE for oversampling
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    print("⚠️  imblearn not available — will use class_weight='balanced' instead of SMOTE")

# ─── Configuration ───────────────────────────────────────────────────────────

SPEECH_CSV = Path(__file__).parent / "ml-models" / "pd_speech_features.csv"
MODELS_OUTPUT = Path(__file__).parent / "models" / "speech"
MODELS_OUTPUT.mkdir(parents=True, exist_ok=True)

TEST_SIZE = 0.20
RANDOM_STATE = 42


# ─── Data Loading ────────────────────────────────────────────────────────────

def load_speech_data():
    """Load and validate the speech features dataset."""
    print(f"📂 Loading speech dataset: {SPEECH_CSV}")
    
    # The CSV has a header row that might be metadata — try both ways
    try:
        df = pd.read_csv(SPEECH_CSV, header=1)
        if 'class' not in df.columns:
            df = pd.read_csv(SPEECH_CSV, header=0)
    except Exception:
        df = pd.read_csv(SPEECH_CSV, header=0)
    
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {list(df.columns[:5])} ... {list(df.columns[-3:])}")
    
    # Check class column
    if 'class' not in df.columns:
        raise ValueError(f"'class' column not found. Available: {list(df.columns)}")
    
    # Features and target
    drop_cols = ['id', 'class']
    feature_cols = [c for c in df.columns if c not in drop_cols]
    
    X = df[feature_cols].values.astype(np.float64)
    y = df['class'].values.astype(int)
    
    # Handle any NaN/Inf
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    
    n_healthy = np.sum(y == 0)
    n_pd = np.sum(y == 1)
    print(f"   Classes: {n_healthy} healthy (class 0), {n_pd} PD (class 1)")
    print(f"   Imbalance ratio: {n_pd / n_healthy:.2f}")
    print(f"   Features: {X.shape[1]}")
    
    return X, y, feature_cols


# ─── Training ────────────────────────────────────────────────────────────────

def train_speech_model():
    """Full training pipeline with evaluation."""
    print("=" * 70)
    print("  Parkinson's Disease Speech Model Training")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    X, y, feature_names = load_speech_data()
    
    # ── Stratified train/test split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\n📊 Split:")
    print(f"   Train: {len(X_train)} (healthy={np.sum(y_train==0)}, PD={np.sum(y_train==1)})")
    print(f"   Test:  {len(X_test)} (healthy={np.sum(y_test==0)}, PD={np.sum(y_test==1)})")
    
    # ── Scale features ──
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ── Apply SMOTE on training data ──
    if SMOTE_AVAILABLE:
        print("\n⚖️  Applying SMOTE oversampling to balance training data...")
        smote = SMOTE(random_state=RANDOM_STATE)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
        print(f"   After SMOTE: {len(X_train_balanced)} "
              f"(healthy={np.sum(y_train_balanced==0)}, PD={np.sum(y_train_balanced==1)})")
    else:
        X_train_balanced = X_train_scaled
        y_train_balanced = y_train
    
    # ── Model 1: Random Forest with tuning ──
    print("\n🔄 Training Random Forest with GridSearchCV...")
    rf_params = {
        'n_estimators': [200, 300, 500],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
    }
    
    rf_base = RandomForestClassifier(
        random_state=RANDOM_STATE,
        class_weight='balanced',
        n_jobs=-1,
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    
    rf_search = GridSearchCV(
        rf_base, rf_params, cv=cv, scoring='f1', n_jobs=-1, verbose=0
    )
    rf_search.fit(X_train_balanced, y_train_balanced)
    rf_best = rf_search.best_estimator_
    
    print(f"   Best RF params: {rf_search.best_params_}")
    print(f"   Best RF CV F1:  {rf_search.best_score_:.4f}")
    
    # ── Model 2: Gradient Boosting ──
    print("\n🔄 Training Gradient Boosting...")
    gb = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=RANDOM_STATE,
    )
    gb.fit(X_train_balanced, y_train_balanced)
    
    gb_cv = cross_val_score(gb, X_train_balanced, y_train_balanced, cv=cv, scoring='f1')
    print(f"   GB CV F1: {gb_cv.mean():.4f} ± {gb_cv.std():.4f}")
    
    # ── Model 3: SVM ──
    print("\n🔄 Training SVM...")
    svm = SVC(
        kernel='rbf', C=10.0, gamma='scale',
        class_weight='balanced', probability=True,
        random_state=RANDOM_STATE,
    )
    svm.fit(X_train_balanced, y_train_balanced)
    
    svm_cv = cross_val_score(svm, X_train_balanced, y_train_balanced, cv=cv, scoring='f1')
    print(f"   SVM CV F1: {svm_cv.mean():.4f} ± {svm_cv.std():.4f}")
    
    # ── Ensemble Voting Classifier ──
    print("\n🔄 Training Ensemble (Soft Voting)...")
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf_best),
            ('gb', gb),
            ('svm', svm),
        ],
        voting='soft',
        weights=[2, 1, 1],  # RF gets double weight
    )
    ensemble.fit(X_train_balanced, y_train_balanced)
    
    ens_cv = cross_val_score(ensemble, X_train_balanced, y_train_balanced, cv=cv, scoring='f1')
    print(f"   Ensemble CV F1: {ens_cv.mean():.4f} ± {ens_cv.std():.4f}")
    
    # ── Evaluate all models on test set ──
    models = {
        'Random Forest': rf_best,
        'Gradient Boosting': gb,
        'SVM': svm,
        'Ensemble': ensemble,
    }
    
    best_f1 = 0
    best_model_name = None
    best_model = None
    eval_results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = 0.0
        
        eval_results[name] = {
            'accuracy': float(acc),
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1),
            'auc_roc': float(auc),
        }
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model
    
    # ── Print results ──
    print(f"\n{'='*70}")
    print("  TEST SET RESULTS")
    print(f"{'='*70}")
    print(f"  {'Model':>20} | {'Accuracy':>8} | {'Precision':>9} | {'Recall':>6} | {'F1':>8} | {'AUC':>8}")
    print(f"  {'-'*20}-+-{'-'*8}-+-{'-'*9}-+-{'-'*6}-+-{'-'*8}-+-{'-'*8}")
    for name, res in eval_results.items():
        marker = " ★" if name == best_model_name else ""
        print(f"  {name:>20} | {res['accuracy']:>8.4f} | {res['precision']:>9.4f} | "
              f"{res['recall']:>6.4f} | {res['f1']:>8.4f} | {res['auc_roc']:>8.4f}{marker}")
    
    print(f"\n  🏆 Best model: {best_model_name} (F1={best_f1:.4f})")
    
    # Detailed report for best model
    y_pred_best = best_model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred_best)
    print(f"\n   Confusion Matrix ({best_model_name}):")
    print(f"   {'':>12} Pred Healthy  Pred PD")
    print(f"   {'True Healthy':>12}    {cm[0][0]:>5}      {cm[0][1]:>5}")
    print(f"   {'True PD':>12}    {cm[1][0]:>5}      {cm[1][1]:>5}")
    print(f"\n{classification_report(y_test, y_pred_best, target_names=['Healthy', 'PD'])}")
    
    # ── Save best model as the production model ──
    # Save as speech_rf_model.pkl for backward compatibility
    model_path = MODELS_OUTPUT / "speech_rf_model.pkl"
    scaler_path = MODELS_OUTPUT / "speech_rf_scaler.pkl"
    feature_names_path = MODELS_OUTPUT / "speech_feature_names.pkl"
    
    joblib.dump(best_model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(feature_names, feature_names_path)
    
    print(f"\n   ✅ Model saved:  {model_path}")
    print(f"   ✅ Scaler saved: {scaler_path}")
    print(f"   ✅ Feature names saved: {feature_names_path}")
    
    # ── Feature importance (from RF) ──
    print("\n📊 Top 20 Most Important Features (Random Forest):")
    importances = rf_best.feature_importances_
    indices = np.argsort(importances)[::-1][:20]
    for i, idx in enumerate(indices):
        print(f"   {i+1:>2}. {feature_names[idx]:>40} = {importances[idx]:.4f}")
    
    # ── Save training report ──
    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset": str(SPEECH_CSV),
        "dataset_shape": [int(s) for s in [len(y), len(feature_names)]],
        "class_distribution": {
            "healthy": int(np.sum(y == 0)),
            "parkinson": int(np.sum(y == 1)),
        },
        "test_size": TEST_SIZE,
        "smote_applied": SMOTE_AVAILABLE,
        "best_model": best_model_name,
        "best_rf_params": rf_search.best_params_,
        "evaluation": eval_results,
        "top_features": [
            {"name": feature_names[idx], "importance": float(importances[idx])}
            for idx in indices
        ],
    }
    
    report_path = MODELS_OUTPUT / "speech_training_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Training report saved: {report_path}")
    
    return report


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    train_speech_model()
