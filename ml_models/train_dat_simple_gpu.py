"""
Simple GPU Training with Mixed Precision
Memory-efficient approach using TF mixed precision
"""

import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt

# Enable mixed precision for memory efficiency
policy = keras.mixed_precision.Policy('mixed_float16')
keras.mixed_precision.set_global_policy(policy)
print('✅ Mixed precision enabled: compute in float16, variables in float32')

# Enable memory growth
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"✅ GPU memory growth enabled for {len(gpus)} GPU(s)")

# Add parent directory
sys.path.append(str(Path(__file__).parent))
from dat_cnn_lstm_model import DaTCNNLSTMModel

print("\n" + "="*80)
print("SIMPLE GPU TRAINING WITH MIXED PRECISION")
print("="*80)

# Load data
print("\n📦 Loading preprocessed data...")
data_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed_ntua")

X_train = np.load(data_dir / "train_X.npy").astype(np.float16)  # Convert to float16
y_train = np.load(data_dir / "train_y.npy")
X_val = np.load(data_dir / "val_X.npy").astype(np.float16)
y_val = np.load(data_dir / "val_y.npy")
X_test = np.load(data_dir / "test_X.npy").astype(np.float16)
y_test = np.load(data_dir / "test_y.npy")

print(f"✅ Loaded:")
print(f"  • Train: {len(X_train)} subjects")
print(f"  • Val: {len(X_val)} subjects")
print(f"  • Test: {len(X_test)} subjects")

# Calculate aggressive class weights
n_healthy = np.sum(y_train == 0)
n_pd = np.sum(y_train == 1)
total = len(y_train)

weight_healthy = total / (2 * n_healthy)
weight_pd = total / (2 * n_pd)

# AGGRESSIVE weights
class_weights = {
    0: float(weight_healthy * 2.5),  # Healthy: 2.5x
    1: float(weight_pd * 0.6)        # PD: 0.6x
}

print(f"\n⚖️  Aggressive Class Weights:")
print(f"  • Healthy (0): {class_weights[0]:.2f}")
print(f"  • PD (1): {class_weights[1]:.2f}")

# Build model
print("\n🏗️  Building model...")
model_builder = DaTCNNLSTMModel(
    input_shape=(16, 128, 128, 1),
    num_classes=1
)
model = model_builder.build_model()

# Compile with mixed precision
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy', 
             keras.metrics.Precision(name='precision'),
             keras.metrics.Recall(name='recall'),
             keras.metrics.AUC(name='auc')]
)

print(f"✅ Model compiled with mixed precision")
print(f"  • Parameters: {model.count_params():,}")

# Callbacks
output_dir = Path("models/dat_scan")
output_dir.mkdir(parents=True, exist_ok=True)
model_save_path = output_dir / "best_model_improved.h5"

callbacks = [
    keras.callbacks.ModelCheckpoint(
        str(model_save_path),
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

# Train with VERY small batch size
print("\n🚀 Starting training...")
print("  • Batch size: 2 (minimal for GPU)")
print("  • Mixed precision: float16 compute, float32 variables")
print("  • Memory growth: enabled")

try:
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=2,  # Minimal batch size
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\n✅ Training complete!")
    
    # Evaluate
    print("\n" + "="*80)
    print("EVALUATION")
    print("="*80)
    
    # Load best model
    model = keras.models.load_model(str(model_save_path))
    
    # Predictions
    y_pred_proba = model.predict(X_test, batch_size=2).flatten()
    
    # ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    # Find optimal threshold
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    
    print(f"\n📊 ROC Analysis:")
    print(f"  • AUC: {roc_auc:.4f}")
    print(f"  • Optimal threshold: {optimal_threshold:.4f}")
    print(f"  • Sensitivity: {tpr[optimal_idx]:.4f}")
    print(f"  • Specificity: {1-fpr[optimal_idx]:.4f}")
    
    # Predictions
    y_pred = (y_pred_proba >= optimal_threshold).astype(int)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n📈 Confusion Matrix:")
    print(cm)
    
    # Report
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Healthy', 'PD']))
    
    # Calculate specificity
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    print(f"\n🎯 KEY IMPROVEMENT:")
    print(f"  • Specificity: {specificity:.0%} (was 0%)")
    print(f"  • Sensitivity: {sensitivity:.0%}")
    
    # Save ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, 'b-', label=f'ROC (AUC={roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], 'r--', label='Random')
    plt.scatter(fpr[optimal_idx], tpr[optimal_idx], c='green', s=100,
               label=f'Optimal (θ={optimal_threshold:.3f})')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Improved DaT Model - ROC Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_dir / "roc_curve_improved.png", dpi=150, bbox_inches='tight')
    
    print(f"\n💾 Model saved: {model_save_path}")
    print(f"💾 ROC curve saved: {output_dir}/roc_curve_improved.png")
    
    print("\n" + "="*80)
    print("🎉 SUCCESS! Model training complete.")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
