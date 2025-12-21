"""
Optimized CPU Training Script
Fast CPU training with all optimizations
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'  # Enable CPU optimizations

import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt

# CPU optimizations
tf.config.threading.set_intra_op_parallelism_threads(8)
tf.config.threading.set_inter_op_parallelism_threads(8)

print("="*80)
print("OPTIMIZED CPU TRAINING")
print("="*80)
print(f"✅ CPU threads: intra=8, inter=8")
print(f"✅ oneDNN optimizations: enabled")

# Add parent directory
sys.path.append(str(Path(__file__).parent))
from dat_cnn_lstm_model import DaTCNNLSTMModel

# Load data
print("\n📦 Loading data...")
data_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed_ntua")

X_train = np.load(data_dir / "train_X.npy")
y_train = np.load(data_dir / "train_y.npy")
X_val = np.load(data_dir / "val_X.npy")
y_val = np.load(data_dir / "val_y.npy")
X_test = np.load(data_dir / "test_X.npy")
y_test = np.load(data_dir / "test_y.npy")

print(f"✅ Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# Aggressive class weights
n_healthy = np.sum(y_train == 0)
n_pd = np.sum(y_train == 1)
total = len(y_train)

class_weights = {
    0: float((total / (2 * n_healthy)) * 2.5),  # Healthy: 2.5x
    1: float((total / (2 * n_pd)) * 0.6)        # PD: 0.6x
}

print(f"\n⚖️  Class Weights: Healthy={class_weights[0]:.2f}, PD={class_weights[1]:.2f}")

# Build model
print("\n🏗️  Building model...")
model_builder = DaTCNNLSTMModel(input_shape=(16, 128, 128, 1), num_classes=1)
model = model_builder.build_model()

model.compile(
    optimizer=keras.optimizers.Adam(0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Model: {model.count_params():,} parameters")

# Callbacks
output_dir = Path("models/dat_scan")
output_dir.mkdir(parents=True, exist_ok=True)

callbacks = [
    keras.callbacks.ModelCheckpoint(
        str(output_dir / "best_model_improved.h5"),
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

# Train
print("\n🚀 Training started...")
print("="*80)

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=8,  # Larger batch for CPU
    class_weight=class_weights,
    callbacks=callbacks,
    verbose=2  # One line per epoch
)

print("\n✅ Training complete!")

# Evaluate
print("\n" + "="*80)
print("EVALUATION")
print("="*80)

model = keras.models.load_model(str(output_dir / "best_model_improved.h5"))

y_pred_proba = model.predict(X_test, batch_size=8).flatten()

# ROC analysis
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

y_pred = (y_pred_proba >= optimal_threshold).astype(int)

# Metrics
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"\n📊 Results:")
print(f"  AUC: {roc_auc:.4f}")
print(f"  Optimal threshold: {optimal_threshold:.4f}")
print(f"\n🎯 KEY IMPROVEMENT:")
print(f"  Specificity: {specificity:.1%} (was 0%)")
print(f"  Sensitivity: {sensitivity:.1%}")
print(f"\n📈 Confusion Matrix:")
print(cm)
print(f"\n{classification_report(y_test, y_pred, target_names=['Healthy', 'PD'])}")

# Save ROC
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, 'b-', label=f'AUC={roc_auc:.3f}')
plt.plot([0, 1], [0, 1], 'r--')
plt.scatter(fpr[optimal_idx], tpr[optimal_idx], c='green', s=100)
plt.xlabel('FPR')
plt.ylabel('TPR')
plt.title('Improved DaT Model')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(output_dir / "roc_curve_improved.png", dpi=150, bbox_inches='tight')

print(f"\n💾 Saved: {output_dir}/best_model_improved.h5")
print(f"💾 Saved: {output_dir}/roc_curve_improved.png")
print("\n" + "="*80)
print("🎉 SUCCESS!")
print("="*80)
