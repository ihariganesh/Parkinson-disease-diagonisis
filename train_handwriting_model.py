#!/usr/bin/env python3
"""
Train Parkinson's Handwriting Detection Models

Uses Transfer Learning with MobileNetV2 on the parkinson_diagram_dataset.
Trains two separate models:
  1. Spiral drawing classifier
  2. Wave drawing classifier

Given the small dataset (36 train + 15 test per class), we use:
  - Heavy data augmentation
  - Transfer learning (MobileNetV2 pretrained on ImageNet)
  - Fine-tuning top layers
  - Early stopping + reduce LR on plateau
"""

import os
import sys
import json
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix

# ── Configuration ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DATASET_DIR = PROJECT_ROOT / "parkinson_diagram_dataset"
MODEL_DIR = PROJECT_ROOT / "ml-models" / "models" / "handwriting"
IMG_SIZE = 224  # MobileNetV2 input
BATCH_SIZE = 8
EPOCHS = 80
SEED = 42

np.random.seed(SEED)
tf.random.set_seed(SEED)


def load_images_from_dir(directory: Path, label: int, img_size: int = IMG_SIZE):
    """Load all images from a directory and assign a label."""
    images, labels = [], []
    if not directory.exists():
        print(f"  ⚠ Directory not found: {directory}")
        return np.array([]), np.array([])

    for img_file in sorted(directory.glob("*.png")):
        img = cv2.imread(str(img_file))
        if img is None:
            continue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (img_size, img_size))
        images.append(img)
        labels.append(label)

    # Also try jpg files
    for img_file in sorted(directory.glob("*.jpg")):
        img = cv2.imread(str(img_file))
        if img is None:
            continue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (img_size, img_size))
        images.append(img)
        labels.append(label)

    return np.array(images), np.array(labels)


def load_dataset(drawing_type: str):
    """Load training and testing datasets for a drawing type (spiral/wave)."""
    base = DATASET_DIR / drawing_type

    print(f"\n📂 Loading {drawing_type} dataset...")

    # Training
    X_train_h, y_train_h = load_images_from_dir(base / "training" / "healthy", 0)
    X_train_p, y_train_p = load_images_from_dir(base / "training" / "parkinson", 1)

    # Testing
    X_test_h, y_test_h = load_images_from_dir(base / "testing" / "healthy", 0)
    X_test_p, y_test_p = load_images_from_dir(base / "testing" / "parkinson", 1)

    X_train = np.concatenate([X_train_h, X_train_p], axis=0)
    y_train = np.concatenate([y_train_h, y_train_p], axis=0)
    X_test = np.concatenate([X_test_h, X_test_p], axis=0)
    y_test = np.concatenate([y_test_h, y_test_p], axis=0)

    # Shuffle training data
    perm = np.random.permutation(len(X_train))
    X_train, y_train = X_train[perm], y_train[perm]

    print(f"  Train: {len(X_train)} images (healthy={len(X_train_h)}, parkinson={len(X_train_p)})")
    print(f"  Test:  {len(X_test)} images (healthy={len(X_test_h)}, parkinson={len(X_test_p)})")

    return X_train, y_train, X_test, y_test


def create_augmentation_layer():
    """Create a data augmentation pipeline for small dataset."""
    return keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.3),
        layers.RandomZoom((-0.2, 0.2)),
        layers.RandomTranslation(0.15, 0.15),
        layers.RandomContrast(0.3),
        layers.RandomBrightness(0.2),
    ], name="augmentation")


def build_model():
    """Build transfer learning model with MobileNetV2 backbone."""
    # MobileNetV2 backbone (frozen initially)
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
    )
    base_model.trainable = False

    # Build model
    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))

    # Preprocessing: scale to [-1, 1] for MobileNetV2
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)

    # Augmentation (only during training)
    augment = create_augmentation_layer()
    x = augment(x)

    # Feature extraction
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = Model(inputs, outputs, name="parkinson_detector")
    return model, base_model


def train_model(drawing_type: str):
    """Train a model for a specific drawing type."""
    print(f"\n{'='*60}")
    print(f"  TRAINING: {drawing_type.upper()} MODEL")
    print(f"{'='*60}")

    # Load data
    X_train, y_train, X_test, y_test = load_dataset(drawing_type)

    if len(X_train) == 0:
        print(f"❌ No training data found for {drawing_type}")
        return None

    # Normalize to [0, 255] float (MobileNetV2 preprocess_input handles the rest)
    X_train = X_train.astype("float32")
    X_test = X_test.astype("float32")

    # Build model
    model, base_model = build_model()
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    print(f"\n📊 Model summary:")
    print(f"   Total params: {model.count_params():,}")

    # Callbacks
    model_path = MODEL_DIR / f"{drawing_type}_model.keras"
    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=15,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1,
        ),
        ModelCheckpoint(
            str(model_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]

    # Phase 1: Train top layers (backbone frozen)
    print(f"\n🔒 Phase 1: Training top layers ({EPOCHS // 2} epochs)...")
    history1 = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS // 2,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    # Phase 2: Fine-tune - unfreeze last 30 layers of backbone
    print(f"\n🔓 Phase 2: Fine-tuning backbone ({EPOCHS // 2} epochs)...")
    base_model.trainable = True
    # Freeze all except the last 30 layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    history2 = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        initial_epoch=len(history1.history["loss"]),
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    print(f"\n📈 Final Evaluation on Test Set:")
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"   Loss: {test_loss:.4f}")
    print(f"   Accuracy: {test_acc:.4f}")

    # Detailed classification report
    y_pred_probs = model.predict(X_test, verbose=0).flatten()
    y_pred = (y_pred_probs > 0.5).astype(int)

    print(f"\n📋 Classification Report:")
    report = classification_report(
        y_test, y_pred,
        target_names=["Healthy", "Parkinson"],
        output_dict=True,
    )
    print(classification_report(y_test, y_pred, target_names=["Healthy", "Parkinson"]))

    cm = confusion_matrix(y_test, y_pred)
    print(f"Confusion Matrix:")
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    # Save model metadata
    metadata = {
        "drawing_type": drawing_type,
        "test_accuracy": float(test_acc),
        "test_loss": float(test_loss),
        "classification_report": {k: v for k, v in report.items() if isinstance(v, dict)},
        "confusion_matrix": cm.tolist(),
        "img_size": IMG_SIZE,
        "architecture": "MobileNetV2_transfer_learning",
        "trained_at": datetime.now().isoformat(),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "epochs_run": len(history1.history["loss"]) + len(history2.history["loss"]),
    }

    meta_path = MODEL_DIR / f"{drawing_type}_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Model saved to: {model_path}")
    print(f"   Metadata saved to: {meta_path}")

    return metadata


def main():
    # Create model directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("🧠 Parkinson's Handwriting Detection - Model Training")
    print(f"   Dataset: {DATASET_DIR}")
    print(f"   Models:  {MODEL_DIR}")
    print(f"   TensorFlow: {tf.__version__}")
    print(f"   GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")

    results = {}

    # Train spiral model
    spiral_result = train_model("spiral")
    if spiral_result:
        results["spiral"] = spiral_result

    # Train wave model
    wave_result = train_model("wave")
    if wave_result:
        results["wave"] = wave_result

    # Save combined results
    combined_path = MODEL_DIR / "training_results.json"
    with open(combined_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print("  TRAINING COMPLETE")
    print(f"{'='*60}")
    for dtype, res in results.items():
        print(f"  {dtype.upper()}: accuracy={res['test_accuracy']:.4f}")
    print(f"\n  Models saved in: {MODEL_DIR}")


if __name__ == "__main__":
    main()
