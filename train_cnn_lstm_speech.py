"""
Train CNN+LSTM Speech Model for Parkinson's Disease Detection
==============================================================
Architecture: CNN+LSTM (Deep Learning)
Preprocessing: Simple scaling and label encoding
Training: Simple train-test split

Dataset: ml-models/pd_speech_features.csv
  - 756 samples, 753 features
  - Class 1 = Parkinson (564), Class 0 = Healthy (192)
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path
import joblib

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "ml-models" / "pd_speech_features.csv"
SAVE_DIR = BASE_DIR / "ml-models" / "models" / "speech"
MODEL_PATH = SAVE_DIR / "cnn_lstm_speech_best.keras"
SCALER_PATH = SAVE_DIR / "cnn_lstm_scaler.pkl"

TEST_SIZE = 0.2
RANDOM_STATE = 42
BATCH_SIZE = 32
EPOCHS = 100


def load_and_preprocess():
    """Load CSV, simple scaling + label encoding, train-test split."""
    print("📂 Loading dataset...")
    df = pd.read_csv(CSV_PATH)
    print(f"   Shape: {df.shape}")
    print(f"   Class distribution: {dict(df['class'].value_counts())}")

    # Features: drop 'id' and 'class'
    X = df.drop(columns=['id', 'class']).values.astype(np.float32)
    
    # Label encoding (already 0/1, but ensure it)
    le = LabelEncoder()
    y = le.fit_transform(df['class'].values).astype(np.float32)
    
    print(f"   Features: {X.shape[1]}, Samples: {X.shape[0]}")
    print(f"   Labels: {le.classes_} → encoded as [0, 1]")

    # Handle NaN / inf
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    # Simple scaling (StandardScaler)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Simple train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"\n   Train: {X_train.shape[0]} ({int(y_train.sum())} PD, {int(len(y_train) - y_train.sum())} Healthy)")
    print(f"   Test:  {X_test.shape[0]} ({int(y_test.sum())} PD, {int(len(y_test) - y_test.sum())} Healthy)")

    return X_train, X_test, y_train, y_test, scaler


def build_cnn_lstm_model(n_features: int):
    """
    Build CNN+LSTM model for tabular speech features.
    
    The 753 features are reshaped into a 2D sequence:
      - Reshape to (segments, features_per_segment) → treat as temporal sequence
      - 1D CNN extracts local feature patterns
      - LSTM captures sequential dependencies across feature groups
    """
    # Reshape 753 features into segments
    # 753 = 3 × 251 — split into 3 segments of 251 features each
    # This groups related feature blocks (jitter, shimmer, TQWT etc.)
    n_segments = 3
    features_per_segment = n_features // n_segments
    remainder = n_features % n_segments
    
    # Pad features to make evenly divisible
    padded_features = n_features + (n_segments - remainder) if remainder > 0 else n_features
    features_per_segment = padded_features // n_segments
    
    inputs = layers.Input(shape=(n_features,), name="speech_features")
    
    # Pad if needed and reshape to (n_segments, features_per_segment)
    if remainder > 0:
        x = layers.ZeroPadding1D(padding=(0, n_segments - remainder))(
            layers.Reshape((n_features, 1))(inputs)
        )
        x = layers.Reshape((n_segments, features_per_segment))(
            layers.Reshape((padded_features,))(layers.Reshape((padded_features, 1))(x))
        )
    else:
        x = layers.Reshape((n_segments, features_per_segment))(inputs)
    
    # --- CNN Block: extract local patterns within each segment ---
    x = layers.Conv1D(64, kernel_size=1, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv1D(128, kernel_size=1, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    
    # --- LSTM Block: capture sequential dependencies ---
    x = layers.LSTM(64, return_sequences=True)(x)
    x = layers.Dropout(0.3)(x)
    x = layers.LSTM(32, return_sequences=False)(x)
    x = layers.Dropout(0.3)(x)
    
    # --- Classification head ---
    x = layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(32, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation='sigmoid', name="prediction")(x)
    
    model = Model(inputs, outputs, name="CNN_LSTM_Speech")
    return model


def build_cnn_lstm_model_v2(n_features: int):
    """
    Alternative: treat each feature as a timestep in a 1D sequence.
    
    Reshape (753,) → (753, 1) → Conv1D extracts patterns → Pool → LSTM
    """
    inputs = layers.Input(shape=(n_features,), name="speech_features")
    
    # Reshape to sequence: each feature is a timestep with 1 channel
    x = layers.Reshape((n_features, 1))(inputs)
    
    # --- CNN Block: extract local feature patterns ---
    x = layers.Conv1D(32, kernel_size=7, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(pool_size=3)(x)
    
    x = layers.Conv1D(64, kernel_size=5, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(pool_size=3)(x)
    
    x = layers.Conv1D(128, kernel_size=3, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(pool_size=3)(x)
    x = layers.Dropout(0.3)(x)
    
    # --- LSTM Block ---
    x = layers.LSTM(64, return_sequences=True)(x)
    x = layers.Dropout(0.3)(x)
    x = layers.LSTM(32, return_sequences=False)(x)
    x = layers.Dropout(0.3)(x)
    
    # --- Classification ---
    x = layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(1, activation='sigmoid', name="prediction")(x)
    
    model = Model(inputs, outputs, name="CNN_LSTM_Speech_v2")
    return model


def main():
    print("=" * 60)
    print("CNN+LSTM Speech Model Training")
    print("=" * 60)

    # ── Load & Preprocess ──────────────────────────────────────
    X_train, X_test, y_train, y_test, scaler = load_and_preprocess()
    n_features = X_train.shape[1]

    # ── Class weights (imbalanced dataset) ─────────────────────
    n_healthy = int((y_train == 0).sum())
    n_pd = int((y_train == 1).sum())
    total = n_healthy + n_pd
    class_weight = {
        0: total / (2 * n_healthy),
        1: total / (2 * n_pd)
    }
    print(f"\n   Class weights: {class_weight}")

    # ── Build Model ────────────────────────────────────────────
    print("\n🏗️  Building CNN+LSTM model...")
    model = build_cnn_lstm_model_v2(n_features)
    model.summary()

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    # ── Train ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("TRAINING")
    print("=" * 60)

    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    callbacks = [
        ModelCheckpoint(str(MODEL_PATH), monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_accuracy', patience=20, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=1e-6, verbose=1),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1
    )

    # ── Save scaler ────────────────────────────────────────────
    joblib.dump(scaler, str(SCALER_PATH))
    print(f"\n   Scaler saved to {SCALER_PATH}")

    # ── Final Evaluation ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    best_model = tf.keras.models.load_model(str(MODEL_PATH))
    loss, acc = best_model.evaluate(X_test, y_test, verbose=0)

    preds = best_model.predict(X_test, verbose=0).flatten()
    pred_labels = (preds > 0.5).astype(int)

    healthy_mask = y_test == 0
    parkinson_mask = y_test == 1

    healthy_acc = (pred_labels[healthy_mask] == 0).mean() if healthy_mask.sum() > 0 else 0
    parkinson_acc = (pred_labels[parkinson_mask] == 1).mean() if parkinson_mask.sum() > 0 else 0
    balanced_acc = (healthy_acc + parkinson_acc) / 2

    # Precision, Recall, F1
    tp = ((pred_labels == 1) & (y_test == 1)).sum()
    fp = ((pred_labels == 1) & (y_test == 0)).sum()
    fn = ((pred_labels == 0) & (y_test == 1)).sum()
    tn = ((pred_labels == 0) & (y_test == 0)).sum()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n  ✅ Overall accuracy:    {acc:.2%}")
    print(f"  ✅ Balanced accuracy:   {balanced_acc:.2%}")
    print(f"  ✅ Healthy accuracy:    {healthy_acc:.2%} (Specificity)")
    print(f"  ✅ Parkinson accuracy:  {parkinson_acc:.2%} (Sensitivity/Recall)")
    print(f"  ✅ Precision:           {precision:.2%}")
    print(f"  ✅ F1 Score:            {f1:.2%}")
    print(f"\n  Confusion Matrix:")
    print(f"              Pred Healthy  Pred PD")
    print(f"  Healthy     {tn:>5}        {fp:>5}")
    print(f"  Parkinson   {fn:>5}        {tp:>5}")
    print(f"\n  ✅ Model saved to: {MODEL_PATH}")
    print(f"  ✅ Scaler saved to: {SCALER_PATH}")

    print("\n✅ Training complete!")


if __name__ == "__main__":
    main()
