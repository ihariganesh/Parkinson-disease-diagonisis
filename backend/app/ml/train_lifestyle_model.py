"""
Lifestyle Recommendation Model Training Script
Trains a multi-output Random Forest classifier from the 12,000-record Parkinson's dataset.

Input features: gender, age, address (city/state), previous_condition, parkinson_status, parkinson_stage
Output targets: recommended_exercise, recommended_diet, recommended_sleep, recommended_stress_management
"""

import os
import sys
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATASET_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), "parkinson_lifestyle_recommendation_dataset_12000.csv")
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "lifestyle_model.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "lifestyle_encoders.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "lifestyle_model_metadata.json")


def extract_location_features(address: str) -> dict:
    """Extract city/region from address string like 'Salem TN India'"""
    parts = str(address).strip().split()
    city = parts[0] if len(parts) >= 1 else "Unknown"
    state = parts[1] if len(parts) >= 2 else "Unknown"
    return {"city": city, "state": state}


def create_age_group(age: int) -> str:
    """Bucket age into groups for better generalization"""
    if age < 45:
        return "young"
    elif age < 55:
        return "middle"
    elif age < 65:
        return "senior"
    elif age < 75:
        return "elderly"
    else:
        return "very_elderly"


def train_model():
    print("=" * 60)
    print(" Lifestyle Recommendation Model Training (12K Dataset)")
    print("=" * 60)

    # --- Load dataset ---
    print(f"\n Loading dataset from: {DATASET_PATH}")
    if not os.path.exists(DATASET_PATH):
        print(f" Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"   Loaded {len(df)} records with columns: {list(df.columns)}")

    # --- Preprocess ---
    print("\n Preprocessing data...")

    # Handle missing previous_condition (1736 nulls -> label as 'None')
    df["previous_condition"] = df["previous_condition"].fillna("None")

    # Extract location features
    location_data = df["address"].apply(extract_location_features)
    df["city"] = location_data.apply(lambda x: x["city"])
    df["state"] = location_data.apply(lambda x: x["state"])

    # Create age groups
    df["age_group"] = df["age"].apply(create_age_group)

    # --- Encode categorical features ---
    print("\n Encoding features...")
    
    # Feature columns (including parkinson_status and parkinson_stage)
    categorical_features = ["gender", "age_group", "city", "state", "previous_condition"]
    # parkinson_status (0/1) and parkinson_stage (0-3) are already numeric
    
    target_columns = [
        "recommended_exercise",
        "recommended_diet",
        "recommended_sleep",
        "recommended_stress_management"
    ]

    encoders = {}

    # Encode categorical features
    for col in categorical_features:
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"   {col}: {len(le.classes_)} classes -> {list(le.classes_)}")

    # Encode targets
    for col in target_columns:
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"   {col}: {len(le.classes_)} classes -> {list(le.classes_)}")

    # --- Build feature matrix ---
    encoded_cat_cols = [f"{col}_encoded" for col in categorical_features]
    encoded_target_cols = [f"{col}_encoded" for col in target_columns]

    # Combine: encoded categoricals + raw numeric features (age, parkinson_status, parkinson_stage)
    X = df[encoded_cat_cols].values
    X = np.column_stack([
        X,
        df["age"].values,
        df["parkinson_status"].values,
        df["parkinson_stage"].values
    ])
    feature_names = categorical_features + ["age", "parkinson_status", "parkinson_stage"]

    y = df[encoded_target_cols].values

    print(f"\n Feature matrix: {X.shape} ({len(feature_names)} features)")
    print(f"   Features: {feature_names}")
    print(f"   Target matrix: {y.shape}")

    # --- Parkinson distribution ---
    print(f"\n Parkinson Distribution:")
    print(f"   Status 0 (No PD): {(df['parkinson_status']==0).sum()}")
    print(f"   Status 1 (Has PD): {(df['parkinson_status']==1).sum()}")
    print(f"   Stage 0: {(df['parkinson_stage']==0).sum()}")
    print(f"   Stage 1: {(df['parkinson_stage']==1).sum()}")
    print(f"   Stage 2: {(df['parkinson_stage']==2).sum()}")
    print(f"   Stage 3: {(df['parkinson_stage']==3).sum()}")

    # --- Split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=df["parkinson_stage"]
    )
    print(f"\n   Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # --- Train ---
    print("\n Training Random Forest Multi-Output Classifier...")
    base_clf = RandomForestClassifier(
        n_estimators=250,
        max_depth=25,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model = MultiOutputClassifier(base_clf)
    model.fit(X_train, y_train)
    print("    Training complete!")

    # --- Evaluate ---
    print("\n Evaluating model...")
    y_pred = model.predict(X_test)

    for i, col in enumerate(target_columns):
        acc = accuracy_score(y_test[:, i], y_pred[:, i])
        print(f"   {col}: Accuracy = {acc:.4f}")

    overall_acc = np.mean([
        accuracy_score(y_test[:, i], y_pred[:, i])
        for i in range(len(target_columns))
    ])
    print(f"\n    Overall Average Accuracy: {overall_acc:.4f}")

    # --- Save model ---
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"\n Saving model to: {MODEL_PATH}")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f" Saving encoders to: {ENCODERS_PATH}")
    with open(ENCODERS_PATH, "wb") as f:
        pickle.dump(encoders, f)

    # Save metadata
    metadata = {
        "dataset": "parkinson_lifestyle_recommendation_dataset_12000.csv",
        "feature_names": feature_names,
        "categorical_features": categorical_features,
        "numeric_features": ["age", "parkinson_status", "parkinson_stage"],
        "target_columns": target_columns,
        "accuracy": {
            col: float(accuracy_score(y_test[:, i], y_pred[:, i]))
            for i, col in enumerate(target_columns)
        },
        "overall_accuracy": float(overall_acc),
        "train_size": int(X_train.shape[0]),
        "test_size": int(X_test.shape[0]),
        "total_records": len(df),
        "unique_values": {
            "gender": list(encoders["gender"].classes_),
            "previous_condition": list(encoders["previous_condition"].classes_),
            "city": list(encoders["city"].classes_),
            "state": list(encoders["state"].classes_),
            "age_group": list(encoders["age_group"].classes_),
        },
        "parkinson_labels": {
            "parkinson_status": {0: "No Parkinson", 1: "Has Parkinson"},
            "parkinson_stage": {
                0: "No Parkinson (healthy)",
                1: "Early Stage (mild symptoms)",
                2: "Moderate Stage",
                3: "Advanced Stage"
            }
        },
        "target_labels": {
            col: list(encoders[col].classes_) for col in target_columns
        }
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f" Saving metadata to: {METADATA_PATH}")

    print("\n" + "=" * 60)
    print(" MODEL TRAINING COMPLETE")
    print(f"   Dataset: 12,000 records")
    print(f"   Model: {MODEL_PATH}")
    print(f"   Overall Accuracy: {overall_acc:.2%}")
    print("=" * 60)

    return model, encoders, metadata


if __name__ == "__main__":
    train_model()
