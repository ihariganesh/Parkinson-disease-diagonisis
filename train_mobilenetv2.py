"""
Train MobileNetV2 for Parkinson's Handwriting Classification
=============================================================
MobileNetV2 has ~3.4M params (vs ResNet50's 23M+), much better for small datasets.

Key preprocessing: grayscale → threshold → edges → 3-channel stack
This forces the CNN to learn stroke/tremor patterns, NOT background/paper/lighting.

Dataset: Handwriting/{training,testing}/{healthy,parkinson}/ — 144 train, 60 test
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS_PHASE1 = 30   # Frozen base
EPOCHS_PHASE2 = 40   # Fine-tune
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Handwriting"
SAVE_PATH = BASE_DIR / "ml-models" / "models" / "handwriting" / "mobilenetv2_handwriting_best.keras"


def preprocess_for_stroke_features(image_path: str) -> np.ndarray:
    """
    Edge-focused preprocessing that isolates stroke/tremor patterns.
    
    Creates 3-channel image from:
      Ch0: Grayscale (normalized) — overall stroke intensity
      Ch1: Binary threshold (Otsu) — clean stroke vs background separation
      Ch2: Canny edges — stroke boundaries and tremor wobble
    
    This eliminates background color, paper texture, lighting variation.
    """
    # Read as grayscale
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    # Resize
    gray = cv2.resize(gray, IMG_SIZE)
    
    # Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Channel 0: Normalized grayscale
    ch_gray = blurred.astype(np.float32) / 255.0
    
    # Channel 1: Otsu binary threshold (isolates ink from paper)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ch_binary = binary.astype(np.float32) / 255.0
    
    # Channel 2: Canny edges (captures stroke boundaries, tremor wobbles)
    edges = cv2.Canny(blurred, 50, 150)
    ch_edges = edges.astype(np.float32) / 255.0
    
    # Stack into 3-channel image
    return np.stack([ch_gray, ch_binary, ch_edges], axis=-1)


def load_dataset(data_dir: Path, subset: str):
    """Load images from {subset}/{healthy,parkinson}/ directories."""
    images = []
    labels = []
    
    for label_name, label_val in [("healthy", 0), ("parkinson", 1)]:
        folder = data_dir / subset / label_name
        if not folder.exists():
            print(f"  ⚠️  Missing folder: {folder}")
            continue
        
        files = sorted([f for f in folder.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg')])
        print(f"  {subset}/{label_name}: {len(files)} images")
        
        for fpath in files:
            try:
                img = preprocess_for_stroke_features(str(fpath))
                images.append(img)
                labels.append(label_val)
            except Exception as e:
                print(f"  ⚠️  Skipping {fpath.name}: {e}")
    
    return np.array(images, dtype=np.float32), np.array(labels, dtype=np.float32)


def create_augmentation_layer():
    """Create data augmentation pipeline for training."""
    return tf.keras.Sequential([
        layers.RandomRotation(0.1),            # ±18 degrees
        layers.RandomTranslation(0.1, 0.1),    # ±10% shift
        layers.RandomZoom(0.15),                # ±15% zoom
        layers.RandomFlip("horizontal"),
        layers.RandomContrast(0.2),             # ±20% contrast
    ], name="augmentation")


def build_model():
    """Build MobileNetV2 model with custom top for binary classification."""
    # MobileNetV2 base (pretrained on ImageNet, ~3.4M params)
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        alpha=1.0  # Full width
    )
    
    # Freeze all base layers initially
    base_model.trainable = False
    
    # Custom classification head
    inputs = layers.Input(shape=(224, 224, 3))
    
    # Augmentation (only during training)
    augmented = create_augmentation_layer()(inputs)
    
    # Base model features
    x = base_model(augmented, training=False)
    
    # Global pooling + classification
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs, outputs)
    return model, base_model


def main():
    print("=" * 60)
    print("MobileNetV2 Handwriting Classifier Training")
    print("=" * 60)
    
    # ── Load Data ──────────────────────────────────────────────
    print("\n📂 Loading dataset...")
    X_train, y_train = load_dataset(DATA_DIR, "training")
    X_test, y_test = load_dataset(DATA_DIR, "testing")
    
    print(f"\n  Training: {len(X_train)} images ({int(y_train.sum())} PD, {int(len(y_train) - y_train.sum())} Healthy)")
    print(f"  Testing:  {len(X_test)} images ({int(y_test.sum())} PD, {int(len(y_test) - y_test.sum())} Healthy)")
    
    # ── Build Model ────────────────────────────────────────────
    print("\n🏗️  Building MobileNetV2 model...")
    model, base_model = build_model()
    
    total_params = model.count_params()
    trainable_params = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    print(f"  Total params: {total_params:,}")
    print(f"  Trainable params (Phase 1): {trainable_params:,}")
    
    # ── Phase 1: Train top layers only (base frozen) ──────────
    print("\n" + "=" * 60)
    print("PHASE 1: Training classification head (base frozen)")
    print("=" * 60)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks_p1 = [
        ModelCheckpoint(str(SAVE_PATH), monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6, verbose=1),
    ]
    
    history_p1 = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS_PHASE1,
        batch_size=BATCH_SIZE,
        callbacks=callbacks_p1,
        verbose=1
    )
    
    # Evaluate Phase 1
    loss1, acc1 = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Phase 1 Results: val_accuracy = {acc1:.4f}, val_loss = {loss1:.4f}")
    
    # ── Phase 2: Fine-tune top layers of base model ───────────
    print("\n" + "=" * 60)
    print("PHASE 2: Fine-tuning (unfreezing top 30 layers)")
    print("=" * 60)
    
    # Unfreeze the last 30 layers of MobileNetV2
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    trainable_params = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    print(f"  Trainable params (Phase 2): {trainable_params:,}")
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),  # Lower LR for fine-tuning
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks_p2 = [
        ModelCheckpoint(str(SAVE_PATH), monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_accuracy', patience=12, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7, verbose=1),
    ]
    
    history_p2 = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS_PHASE2,
        batch_size=BATCH_SIZE,
        callbacks=callbacks_p2,
        verbose=1
    )
    
    # ── Final Evaluation ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)
    
    # Load best saved model
    best_model = tf.keras.models.load_model(str(SAVE_PATH))
    loss_final, acc_final = best_model.evaluate(X_test, y_test, verbose=0)
    
    print(f"\n  ✅ Best model accuracy: {acc_final:.4f}")
    print(f"  ✅ Best model loss:     {loss_final:.4f}")
    print(f"  ✅ Saved to: {SAVE_PATH}")
    
    # Per-class accuracy
    preds = best_model.predict(X_test, verbose=0).flatten()
    pred_labels = (preds > 0.5).astype(int)
    
    healthy_mask = y_test == 0
    parkinson_mask = y_test == 1
    
    healthy_acc = (pred_labels[healthy_mask] == 0).mean()
    parkinson_acc = (pred_labels[parkinson_mask] == 1).mean()
    
    print(f"\n  Healthy accuracy:    {healthy_acc:.2%} ({pred_labels[healthy_mask].sum()} misclassified as PD)")
    print(f"  Parkinson accuracy:  {parkinson_acc:.2%} ({(1 - pred_labels[parkinson_mask]).sum()} misclassified as Healthy)")
    
    # Show individual predictions
    print(f"\n  Individual predictions (first 10):")
    test_files_h = sorted((DATA_DIR / "testing" / "healthy").glob("*.png"))[:5]
    test_files_p = sorted((DATA_DIR / "testing" / "parkinson").glob("*.png"))[:5]
    
    for f in test_files_p:
        img = preprocess_for_stroke_features(str(f))
        p = best_model.predict(np.expand_dims(img, 0), verbose=0)[0][0]
        status = "✓" if p > 0.5 else "✗"
        print(f"    {status} {f.name:20s} → {p:.4f} → {'Parkinson' if p > 0.5 else 'Healthy':12s} (expected Parkinson)")
    
    for f in test_files_h:
        img = preprocess_for_stroke_features(str(f))
        p = best_model.predict(np.expand_dims(img, 0), verbose=0)[0][0]
        status = "✓" if p <= 0.5 else "✗"
        print(f"    {status} {f.name:20s} → {p:.4f} → {'Parkinson' if p > 0.5 else 'Healthy':12s} (expected Healthy)")
    
    print("\n✅ Training complete!")


if __name__ == "__main__":
    main()
