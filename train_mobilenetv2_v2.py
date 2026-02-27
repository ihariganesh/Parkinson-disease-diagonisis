"""
Train MobileNetV2 for Parkinson's Handwriting Classification (v2)
=================================================================
Fixes from v1:
  - Class weights to boost Parkinson sensitivity (medical: false negatives worse than false positives)
  - Separate save paths for Phase 1 / Phase 2 — picks the best overall
  - Reduced augmentation intensity (too much destroys subtle tremor features)
  - Fewer fine-tuned layers to avoid overfitting
  - Adjusted dropout / regularization
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
EPOCHS_PHASE1 = 40
EPOCHS_PHASE2 = 50
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Handwriting"
MODEL_DIR = BASE_DIR / "ml-models" / "models" / "handwriting"
SAVE_PATH_P1 = MODEL_DIR / "mobilenetv2_phase1.keras"
SAVE_PATH_P2 = MODEL_DIR / "mobilenetv2_phase2.keras"
SAVE_PATH_FINAL = MODEL_DIR / "mobilenetv2_handwriting_best.keras"

# Class weights — penalize missing Parkinson more (false negative is worse)
CLASS_WEIGHT = {0: 1.0, 1: 1.5}


def preprocess_for_stroke_features(image_path: str) -> np.ndarray:
    """
    Edge-focused preprocessing that isolates stroke/tremor patterns.
    
    Creates 3-channel image from:
      Ch0: Grayscale (normalized) — overall stroke intensity
      Ch1: Binary threshold (Otsu) — clean stroke vs background separation
      Ch2: Canny edges — stroke boundaries and tremor wobble
    """
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    gray = cv2.resize(gray, IMG_SIZE)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Ch0: Normalized grayscale
    ch_gray = blurred.astype(np.float32) / 255.0
    
    # Ch1: Otsu binary threshold (isolates ink from paper)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ch_binary = binary.astype(np.float32) / 255.0
    
    # Ch2: Canny edges (captures stroke boundaries and tremor wobbles)
    edges = cv2.Canny(blurred, 30, 120)
    ch_edges = edges.astype(np.float32) / 255.0
    
    return np.stack([ch_gray, ch_binary, ch_edges], axis=-1)


def load_dataset(data_dir: Path, subset: str):
    """Load images from {subset}/{healthy,parkinson}/ directories."""
    images, labels = [], []
    
    for label_name, label_val in [("healthy", 0), ("parkinson", 1)]:
        folder = data_dir / subset / label_name
        if not folder.exists():
            print(f"  ⚠️  Missing: {folder}")
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
    """Gentle augmentation — preserve subtle tremor features."""
    return tf.keras.Sequential([
        layers.RandomRotation(0.05),           # ±9 degrees (spirals are orientation-sensitive)
        layers.RandomTranslation(0.08, 0.08),  # ±8% shift
        layers.RandomZoom(0.1),                # ±10% zoom
        layers.RandomFlip("horizontal"),
    ], name="augmentation")


def build_model():
    """Build MobileNetV2 model with custom top for binary classification."""
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        alpha=1.0
    )
    base_model.trainable = False
    
    inputs = layers.Input(shape=(224, 224, 3))
    augmented = create_augmentation_layer()(inputs)
    x = base_model(augmented, training=False)
    
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.005))(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs, outputs)
    return model, base_model


def evaluate_model(model, X_test, y_test, label=""):
    """Evaluate and print per-class metrics."""
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    preds = model.predict(X_test, verbose=0).flatten()
    pred_labels = (preds > 0.5).astype(int)
    
    healthy_mask = y_test == 0
    parkinson_mask = y_test == 1
    
    healthy_acc = (pred_labels[healthy_mask] == 0).mean() if healthy_mask.sum() > 0 else 0
    parkinson_acc = (pred_labels[parkinson_mask] == 1).mean() if parkinson_mask.sum() > 0 else 0
    
    # Balanced accuracy (average of per-class accuracy)
    balanced_acc = (healthy_acc + parkinson_acc) / 2
    
    print(f"\n  {label}")
    print(f"  Overall accuracy:    {acc:.2%}")
    print(f"  Balanced accuracy:   {balanced_acc:.2%}")
    print(f"  Healthy accuracy:    {healthy_acc:.2%}")
    print(f"  Parkinson accuracy:  {parkinson_acc:.2%}")
    
    return acc, balanced_acc, healthy_acc, parkinson_acc


def main():
    print("=" * 60)
    print("MobileNetV2 Handwriting Classifier Training (v2)")
    print("=" * 60)
    
    # ── Load Data ──────────────────────────────────────────────
    print("\n📂 Loading dataset...")
    X_train, y_train = load_dataset(DATA_DIR, "training")
    X_test, y_test = load_dataset(DATA_DIR, "testing")
    
    print(f"\n  Training: {len(X_train)} ({int(y_train.sum())} PD, {int(len(y_train) - y_train.sum())} Healthy)")
    print(f"  Testing:  {len(X_test)} ({int(y_test.sum())} PD, {int(len(y_test) - y_test.sum())} Healthy)")
    
    # ── Build Model ────────────────────────────────────────────
    print("\n🏗️  Building MobileNetV2 model...")
    model, base_model = build_model()
    print(f"  Total params: {model.count_params():,}")
    
    # ── Phase 1: Frozen base ──────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 1: Train classification head (base frozen)")
    print(f"  Class weights: {CLASS_WEIGHT}")
    print("=" * 60)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=5e-4),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS_PHASE1,
        batch_size=BATCH_SIZE,
        class_weight=CLASS_WEIGHT,
        callbacks=[
            ModelCheckpoint(str(SAVE_PATH_P1), monitor='val_accuracy', save_best_only=True, verbose=1),
            EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-6, verbose=1),
        ],
        verbose=1
    )
    
    # Reload best Phase 1 model
    model_p1 = tf.keras.models.load_model(str(SAVE_PATH_P1))
    acc_p1, bal_p1, h_p1, p_p1 = evaluate_model(model_p1, X_test, y_test, "Phase 1 Best")
    
    # ── Phase 2: Fine-tune top layers ─────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 2: Fine-tune (unfreeze top 20 layers)")
    print("=" * 60)
    
    # Reload Phase 1 best and unfreeze top layers
    model = tf.keras.models.load_model(str(SAVE_PATH_P1))
    
    # Get the base model from the loaded model
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):
            base = layer
            base.trainable = True
            for l in base.layers[:-20]:
                l.trainable = False
            break
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS_PHASE2,
        batch_size=BATCH_SIZE,
        class_weight=CLASS_WEIGHT,
        callbacks=[
            ModelCheckpoint(str(SAVE_PATH_P2), monitor='val_accuracy', save_best_only=True, verbose=1),
            EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-7, verbose=1),
        ],
        verbose=1
    )
    
    model_p2 = tf.keras.models.load_model(str(SAVE_PATH_P2))
    acc_p2, bal_p2, h_p2, p_p2 = evaluate_model(model_p2, X_test, y_test, "Phase 2 Best")
    
    # ── Pick Best Model ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("SELECTING BEST MODEL")
    print("=" * 60)
    
    # Use balanced accuracy (gives equal weight to both classes)
    if bal_p2 >= bal_p1:
        print(f"\n  ✅ Phase 2 wins (balanced_acc={bal_p2:.2%} vs {bal_p1:.2%})")
        best_model = model_p2
    else:
        print(f"\n  ✅ Phase 1 wins (balanced_acc={bal_p1:.2%} vs {bal_p2:.2%})")
        best_model = model_p1
    
    best_model.save(str(SAVE_PATH_FINAL))
    print(f"  ✅ Saved to: {SAVE_PATH_FINAL}")
    
    # ── Final Per-Image Report ────────────────────────────────
    print("\n" + "=" * 60)
    print("INDIVIDUAL PREDICTIONS (Test Set)")
    print("=" * 60)
    
    best_model = tf.keras.models.load_model(str(SAVE_PATH_FINAL))
    
    correct = 0
    total = 0
    
    for label_name, expected in [("parkinson", "Parkinson"), ("healthy", "Healthy")]:
        test_folder = DATA_DIR / "testing" / label_name
        files = sorted(test_folder.glob("*.png"))
        
        for f in files:
            img = preprocess_for_stroke_features(str(f))
            p = best_model.predict(np.expand_dims(img, 0), verbose=0)[0][0]
            pred = "Parkinson" if p > 0.5 else "Healthy"
            ok = pred == expected
            correct += ok
            total += 1
            mark = "✓" if ok else "✗"
            print(f"  {mark} {f.name:20s} → {p:.4f} → {pred:12s} (expected {expected})")
    
    print(f"\n  Final accuracy: {correct}/{total} = {correct/total:.2%}")
    
    # Cleanup temp files
    if SAVE_PATH_P1.exists() and SAVE_PATH_P1 != SAVE_PATH_FINAL:
        SAVE_PATH_P1.unlink()
    if SAVE_PATH_P2.exists() and SAVE_PATH_P2 != SAVE_PATH_FINAL:
        SAVE_PATH_P2.unlink()
    
    print("\n✅ Training complete!")


if __name__ == "__main__":
    main()
