"""
Train DaT Scan Model with NTUA Dataset
High-quality training for clinical-grade accuracy
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_DISABLE_MKL'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
import json
from datetime import datetime
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

# Import model
from dat_cnn_lstm_model import DaTCNNLSTMModel

print("=" * 80)
print("DaT SCAN MODEL TRAINING - NTUA DATASET (CLINICAL-GRADE)")
print("=" * 80)


class NTUADaTModelTrainer:
    """Trainer for NTUA dataset"""
    
    def __init__(self,
                 preprocessed_dir: str = "ml_models/dat_preprocessed_ntua",
                 model_output_dir: str = "models/dat_scan",
                 batch_size: int = 8,
                 epochs: int = 100):
        """Initialize trainer"""
        self.preprocessed_dir = Path(preprocessed_dir)
        self.model_output_dir = Path(model_output_dir)
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_size = batch_size
        self.epochs = epochs
        
        # Training configuration
        self.config = {
            'input_shape': (16, 128, 128, 1),
            'num_classes': 1,
            'learning_rate': 0.0001,
            'patience': 15,
            'batch_size': batch_size,
            'epochs': epochs
        }
        
        self.model = None
        self.history = None
    
    def train(self):
        """Train the model"""
        print("\n📦 Loading NTUA preprocessed data...")
        
        # Load data
        X_train = np.load(self.preprocessed_dir / "train_X.npy")
        y_train = np.load(self.preprocessed_dir / "train_y.npy")
        X_val = np.load(self.preprocessed_dir / "val_X.npy")
        y_val = np.load(self.preprocessed_dir / "val_y.npy")
        X_test = np.load(self.preprocessed_dir / "test_X.npy")
        y_test = np.load(self.preprocessed_dir / "test_y.npy")
        
        print(f"✅ Data loaded:")
        print(f"   Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Class distribution
        unique_train, counts_train = np.unique(y_train, return_counts=True)
        print(f"\nTraining class distribution:")
        for cls, count in zip(unique_train, counts_train):
            print(f"   Class {cls}: {count} samples ({count/len(y_train)*100:.1f}%)")
        
        # Compute class weights
        class_weights_array = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weights = {i: class_weights_array[i] for i in range(len(class_weights_array))}
        print(f"\nClass weights: {class_weights}")
        
        # Build model
        print("\n🤖 Building CNN-LSTM model...")
        model_builder = DaTCNNLSTMModel(
            input_shape=self.config['input_shape'],
            num_classes=self.config['num_classes']
        )
        self.model = model_builder.build_model()
        
        # Compile
        optimizer = keras.optimizers.Adam(learning_rate=self.config['learning_rate'])
        
        self.model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.AUC(name='auc'),
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall')
            ]
        )
        
        print("\n📊 Model summary:")
        self.model.summary()
        
        # Callbacks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.model_output_dir / f"dat_model_ntua_{timestamp}.keras"
        
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                filepath=str(model_path),
                monitor='val_auc',
                mode='max',
                save_best_only=True,
                verbose=1
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_auc',
                mode='max',
                patience=self.config['patience'],
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Train
        print("\n🚀 Starting training...")
        print(f"Training on {len(X_train)} subjects with {self.batch_size} batch size for up to {self.epochs} epochs")
        print(f"Model will be saved to: {model_path}")
        print("-" * 80)
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            class_weight=class_weights,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate on test set
        print("\n" + "=" * 80)
        print("EVALUATING ON TEST SET")
        print("=" * 80)
        
        test_loss, test_acc, test_auc, test_precision, test_recall = self.model.evaluate(
            X_test, y_test, verbose=0
        )
        
        # Predictions
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).reshape(-1)
        
        print(f"\n📈 Test Set Metrics:")
        print(f"   Loss: {test_loss:.4f}")
        print(f"   Accuracy: {test_acc:.4f} ({test_acc*100:.1f}%)")
        print(f"   AUC: {test_auc:.4f}")
        print(f"   Precision: {test_precision:.4f}")
        print(f"   Recall: {test_recall:.4f}")
        
        # F1 Score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_test, y_pred)
        print(f"   F1 Score: {f1:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n📊 Confusion Matrix:")
        print(f"   TN: {cm[0,0]}, FP: {cm[0,1]}")
        print(f"   FN: {cm[1,0]}, TP: {cm[1,1]}")
        
        # Sensitivity and Specificity
        sensitivity = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
        specificity = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
        print(f"\n🎯 Clinical Metrics:")
        print(f"   Sensitivity (Recall): {sensitivity:.4f} ({sensitivity*100:.1f}%)")
        print(f"   Specificity: {specificity:.4f} ({specificity*100:.1f}%)")
        
        # Classification Report
        print(f"\n📋 Detailed Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Healthy', 'Parkinson']))
        
        # Save training history
        history_path = self.model_output_dir / f"training_history_ntua_{timestamp}.json"
        history_dict = {
            'history': {k: [float(v) for v in vals] for k, vals in self.history.history.items()},
            'test_metrics': {
                'loss': float(test_loss),
                'accuracy': float(test_acc),
                'auc': float(test_auc),
                'precision': float(test_precision),
                'recall': float(test_recall),
                'f1_score': float(f1),
                'sensitivity': float(sensitivity),
                'specificity': float(specificity)
            },
            'config': self.config
        }
        
        with open(history_path, 'w') as f:
            json.dump(history_dict, f, indent=2)
        
        print(f"\n💾 Training history saved to: {history_path}")
        
        # Plot training history
        self.plot_training_history(timestamp)
        
        # Clinical readiness assessment
        print("\n" + "=" * 80)
        print("CLINICAL READINESS ASSESSMENT")
        print("=" * 80)
        
        clinical_ready = (
            test_acc >= 0.80 and
            test_auc >= 0.85 and
            sensitivity >= 0.80 and
            specificity >= 0.80
        )
        
        if clinical_ready:
            print("\n✅ MODEL READY FOR CLINICAL USE!")
            print(f"   ✓ Accuracy: {test_acc*100:.1f}% (target: ≥80%)")
            print(f"   ✓ AUC: {test_auc:.3f} (target: ≥0.85)")
            print(f"   ✓ Sensitivity: {sensitivity*100:.1f}% (target: ≥80%)")
            print(f"   ✓ Specificity: {specificity*100:.1f}% (target: ≥80%)")
        else:
            print("\n⚠️  MODEL NOT YET READY FOR CLINICAL USE")
            print("   Current vs Target:")
            print(f"   Accuracy: {test_acc*100:.1f}% (target: ≥80%) {'✓' if test_acc >= 0.80 else '✗'}")
            print(f"   AUC: {test_auc:.3f} (target: ≥0.85) {'✓' if test_auc >= 0.85 else '✗'}")
            print(f"   Sensitivity: {sensitivity*100:.1f}% (target: ≥80%) {'✓' if sensitivity >= 0.80 else '✗'}")
            print(f"   Specificity: {specificity*100:.1f}% (target: ≥80%) {'✓' if specificity >= 0.80 else '✗'}")
            print("\n   Recommendations:")
            if test_acc < 0.80:
                print("   - Collect more training data")
            if test_auc < 0.85:
                print("   - Try different model architectures")
            if sensitivity < 0.80:
                print("   - Adjust classification threshold")
            if specificity < 0.80:
                print("   - Balance false positive/negative trade-offs")
        
        return history_dict['test_metrics']
    
    def plot_training_history(self, timestamp):
        """Plot and save training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0, 0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation')
        axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # AUC
        axes[1, 0].plot(self.history.history['auc'], label='Train')
        axes[1, 0].plot(self.history.history['val_auc'], label='Validation')
        axes[1, 0].set_title('Model AUC', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('AUC')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Precision & Recall
        axes[1, 1].plot(self.history.history['precision'], label='Train Precision')
        axes[1, 1].plot(self.history.history['val_precision'], label='Val Precision')
        axes[1, 1].plot(self.history.history['recall'], label='Train Recall')
        axes[1, 1].plot(self.history.history['val_recall'], label='Val Recall')
        axes[1, 1].set_title('Precision & Recall', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        plot_path = self.model_output_dir / f'training_history_ntua_{timestamp}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"📊 Training plots saved to: {plot_path}")
        
        plt.close()


def main():
    """Main training function"""
    # Check GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"\n✅ GPU detected: {gpus}")
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(f"⚠️  GPU configuration error: {e}")
    else:
        print("\n⚠️  No GPU detected, using CPU (training will be slower)")
    
    # Initialize trainer
    trainer = NTUADaTModelTrainer(
        preprocessed_dir="ml_models/dat_preprocessed_ntua",
        model_output_dir="models/dat_scan",
        batch_size=8,  # Can use 8 with 66 subjects
        epochs=100
    )
    
    # Train
    metrics = trainer.train()
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\nFinal Test Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    print("\n✅ Model training finished successfully!")
    print("\nNext steps:")
    print("  1. Update backend to use the new model")
    print("  2. Test with real DaT scan uploads")
    print("  3. Build unified multi-modal analysis system")


if __name__ == "__main__":
    main()
