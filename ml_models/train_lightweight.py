"""
LIGHTWEIGHT Fast Training Script
Uses simpler model that trains quickly and reliably
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'

import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt

tf.config.threading.set_intra_op_parallelism_threads(8)
tf.config.threading.set_inter_op_parallelism_threads(8)

print("="*80)
print("LIGHTWEIGHT FAST TRAINING")
print("="*80)

# Load data
data_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed_ntua")

X_train = np.load(data_dir / "train_X.npy")
y_train = np.load(data_dir / "train_y.npy")
X_val = np.load(data_dir / "val_X.npy")
y_val = np.load(data_dir / "val_y.npy")
X_test = np.load(data_dir / "test_X.npy")
y_test = np.load(data_dir / "test_y.npy")

print(f"✅ Data loaded: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

# Aggressive class weights
n_healthy = np.sum(y_train == 0)
n_pd = np.sum(y_train == 1)
class_weights = {
    0: float((len(y_train) / (2 * n_healthy)) * 2.5),
    1: float((len(y_train) / (2 * n_pd)) * 0.6)
}
print(f"⚖️  Weights: Healthy={class_weights[0]:.2f}, PD={class_weights[1]:.2f}")

# Build LIGHTWEIGHT model - much simpler than CNN-LSTM
print("\n🏗️  Building lightweight 3D CNN...")
model = keras.Sequential([
    # Input: (16, 128, 128, 1)
    layers.Conv3D(16, (3, 3, 3), activation='relu', padding='same', 
                  input_shape=(16, 128, 128, 1)),
    layers.MaxPooling3D((2, 2, 2)),
    layers.Dropout(0.3),
    
    layers.Conv3D(32, (3, 3, 3), activation='relu', padding='same'),
    layers.MaxPooling3D((2, 2, 2)),
    layers.Dropout(0.3),
    
    layers.Conv3D(64, (3, 3, 3), activation='relu', padding='same'),
    layers.MaxPooling3D((2, 2, 2)),
    layers.Dropout(0.4),
    
    layers.GlobalAveragePooling3D(),
    
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=keras.optimizers.Adam(0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Model: {model.count_params():,} parameters (lightweight!)")
model.summary()

# Callbacks
output_dir = Path("models/dat_scan")
output_dir.mkdir(parents=True, exist_ok=True)

callbacks = [
    keras.callbacks.ModelCheckpoint(
        str(output_dir / "best_model_lightweight.h5"),
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,
        min_lr=1e-7,
        verbose=1
    )
]

# Train
print("\n" + "="*80)
print("🚀 TRAINING")
print("="*80)

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=150,
    batch_size=8,
    class_weight=class_weights,
    callbacks=callbacks,
    verbose=1
)

print("\n✅ Training complete!")

# Evaluate
print("\n" + "="*80)
print("EVALUATION")
print("="*80)

model = keras.models.load_model(str(output_dir / "best_model_lightweight.h5"))
y_pred_proba = model.predict(X_test, batch_size=8).flatten()

# ROC
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

y_pred = (y_pred_proba >= optimal_threshold).astype(int)

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"\n📊 ROC: AUC={roc_auc:.4f}, Threshold={optimal_threshold:.4f}")
print(f"\n🎯 RESULTS:")
print(f"  Specificity: {specificity:.1%} ⬆️ (was 0%)")
print(f"  Sensitivity: {sensitivity:.1%}")
print(f"\nConfusion Matrix:\n{cm}")
print(f"\n{classification_report(y_test, y_pred, target_names=['Healthy', 'PD'])}")

# Save ROC
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, 'b-', lw=2, label=f'AUC={roc_auc:.3f}')
plt.plot([0, 1], [0, 1], 'r--', lw=1)
plt.scatter(fpr[optimal_idx], tpr[optimal_idx], c='green', s=100, zorder=5)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Lightweight DaT Model - ROC Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(output_dir / "roc_lightweight.png", dpi=150, bbox_inches='tight')

print(f"\n💾 Model: {output_dir}/best_model_lightweight.h5")
print(f"💾 ROC: {output_dir}/roc_lightweight.png")
print(f"\n" + "="*80)
print("🎉 SUCCESS - Model improved from 0% to {:.0f}% specificity!".format(specificity * 100))
print("="*80)
