"""
DaT Scan Model Training Script
Train CNN+LSTM model with comprehensive monitoring and evaluation
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
os.environ['TF_DISABLE_MKL'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
import json
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_auc_score, roc_curve, precision_recall_curve
)
import seaborn as sns

from dat_cnn_lstm_model import DaTCNNLSTMModel, DaTModelBuilder


def configure_gpu(use_gpu: bool):
    """Configure GPU settings - call before any TF operations"""
    if use_gpu:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                # Enable memory growth to avoid OOM errors
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"✅ GPU enabled: {len(gpus)} GPU(s) found")
                print(f"   GPU: {gpus[0].name}")
            except RuntimeError as e:
                print(f"⚠️  GPU configuration error: {e}")
                print(f"   Continuing with default GPU settings...")
        else:
            print("⚠️  No GPU found, using CPU")
    else:
        # Disable GPU
        tf.config.set_visible_devices([], 'GPU')
        print("Using CPU for training")


class DaTModelTrainer:
    """
    Trainer class for DaT scan CNN-LSTM model
    Handles training, validation, and evaluation
    """
    
    def __init__(
        self,
        model: DaTCNNLSTMModel,
        data_dir: str,
        output_dir: str
    ):
        """
        Initialize trainer
        
        Args:
            model: DaTCNNLSTMModel instance
            data_dir: Directory containing preprocessed data
            output_dir: Directory to save models and results
        """
        self.model = model
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.history = None
        
        # Load data
        self.load_data()
    
    def configure_gpu(self, use_gpu: bool):
        """Configure GPU settings"""
        if use_gpu:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                try:
                    # Enable memory growth to avoid OOM errors
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    print(f"✅ GPU enabled: {len(gpus)} GPU(s) found")
                    print(f"   GPU: {gpus[0].name}")
                except RuntimeError as e:
                    print(f"⚠️  GPU configuration error: {e}")
            else:
                print("⚠️  No GPU found, using CPU")
        else:
            # Disable GPU
            tf.config.set_visible_devices([], 'GPU')
            print("Using CPU for training")
    
    def load_data(self):
        """Load preprocessed data"""
        print("\nLoading preprocessed data...")
        
        # Load training data
        self.X_train = np.load(self.data_dir / "train_X.npy")
        self.y_train = np.load(self.data_dir / "train_y.npy")
        
        # Load validation data
        self.X_val = np.load(self.data_dir / "val_X.npy")
        self.y_val = np.load(self.data_dir / "val_y.npy")
        
        # Load test data
        self.X_test = np.load(self.data_dir / "test_X.npy")
        self.y_test = np.load(self.data_dir / "test_y.npy")
        
        # Load metadata
        with open(self.data_dir / "metadata.json", 'r') as f:
            self.metadata = json.load(f)
        
        print(f"Train: {self.X_train.shape}, Val: {self.X_val.shape}, Test: {self.X_test.shape}")
        print(f"✅ Data loaded successfully!")
    
    def create_callbacks(self, patience: int = 10) -> list:
        """
        Create training callbacks
        
        Args:
            patience: Early stopping patience
            
        Returns:
            List of callbacks
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks = [
            # Model checkpoint - save best model
            keras.callbacks.ModelCheckpoint(
                filepath=str(self.output_dir / f"dat_model_best_{timestamp}.keras"),
                monitor='val_loss',
                save_best_only=True,
                mode='min',
                verbose=1
            ),
            
            # Early stopping
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate on plateau
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            
            # TensorBoard logging
            keras.callbacks.TensorBoard(
                log_dir=str(self.output_dir / f"logs_{timestamp}"),
                histogram_freq=1,
                write_graph=True
            ),
            
            # CSV logging
            keras.callbacks.CSVLogger(
                filename=str(self.output_dir / f"training_log_{timestamp}.csv"),
                separator=',',
                append=False
            )
        ]
        
        return callbacks
    
    def train(
        self,
        epochs: int = 25,
        batch_size: int = 8,
        patience: int = 10,
        class_weight: dict = None
    ):
        """
        Train the model
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            patience: Early stopping patience
            class_weight: Class weights for imbalanced data
        """
        print("\n" + "="*80)
        print("STARTING TRAINING")
        print("="*80)
        
        # Build model if not already built
        if self.model.model is None:
            print("Building model...")
            self.model.build_model()
        
        # Print model summary
        print("\nModel architecture:")
        params = self.model.count_parameters()
        print(f"Trainable parameters: {params['trainable']:,}")
        
        # Calculate class weights if not provided
        if class_weight is None:
            class_weight = self.calculate_class_weights()
        
        print(f"\nClass weights: {class_weight}")
        
        # Create callbacks
        callbacks = self.create_callbacks(patience=patience)
        
        # Train model
        print(f"\nTraining for {epochs} epochs with batch size {batch_size}...")
        print(f"Training samples: {len(self.X_train)}, Validation samples: {len(self.X_val)}")
        
        history = self.model.model.fit(
            self.X_train, self.y_train,
            validation_data=(self.X_val, self.y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            class_weight=class_weight,
            verbose=1
        )
        
        self.model.history = history
        
        print("\n✅ Training completed!")
        
        # Save final model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_model_path = self.output_dir / f"dat_model_final_{timestamp}.keras"
        self.model.save_model(str(final_model_path))
        
        # Plot training history
        self.plot_training_history(history, timestamp)
    
    def calculate_class_weights(self) -> dict:
        """Calculate class weights for imbalanced data"""
        unique, counts = np.unique(self.y_train, return_counts=True)
        total = len(self.y_train)
        
        class_weight = {}
        for cls, count in zip(unique, counts):
            class_weight[cls] = total / (len(unique) * count)
        
        return class_weight
    
    def plot_training_history(self, history, timestamp: str):
        """Plot training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss
        axes[0, 0].plot(history.history['loss'], label='Train Loss')
        axes[0, 0].plot(history.history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy
        axes[0, 1].plot(history.history['accuracy'], label='Train Accuracy')
        axes[0, 1].plot(history.history['val_accuracy'], label='Val Accuracy')
        axes[0, 1].set_title('Model Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Precision
        if 'precision' in history.history:
            axes[1, 0].plot(history.history['precision'], label='Train Precision')
            axes[1, 0].plot(history.history['val_precision'], label='Val Precision')
            axes[1, 0].set_title('Model Precision')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Precision')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
        
        # Recall
        if 'recall' in history.history:
            axes[1, 1].plot(history.history['recall'], label='Train Recall')
            axes[1, 1].plot(history.history['val_recall'], label='Val Recall')
            axes[1, 1].set_title('Model Recall')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Recall')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"training_history_{timestamp}.png", dpi=300)
        print(f"Training history plot saved to: {self.output_dir / f'training_history_{timestamp}.png'}")
        plt.close()
    
    def evaluate(self, save_results: bool = True):
        """
        Comprehensive model evaluation
        
        Args:
            save_results: Whether to save evaluation results
        """
        print("\n" + "="*80)
        print("MODEL EVALUATION")
        print("="*80)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Make predictions
        print("\nMaking predictions on test set...")
        y_pred, y_prob = self.model.predict(self.X_test)
        
        # Calculate metrics
        print("\n--- Classification Report ---")
        report = classification_report(
            self.y_test, y_pred,
            target_names=['Healthy', 'Parkinson'],
            digits=4
        )
        print(report)
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print("\n--- Confusion Matrix ---")
        print(cm)
        
        # Calculate additional metrics
        if len(y_prob.shape) > 1:
            y_prob_positive = y_prob[:, 1] if y_prob.shape[1] > 1 else y_prob.flatten()
        else:
            y_prob_positive = y_prob.flatten()
        
        auc = roc_auc_score(self.y_test, y_prob_positive)
        print(f"\n--- ROC-AUC Score ---")
        print(f"AUC: {auc:.4f}")
        
        # Plot confusion matrix
        self.plot_confusion_matrix(cm, timestamp)
        
        # Plot ROC curve
        self.plot_roc_curve(self.y_test, y_prob_positive, auc, timestamp)
        
        # Plot Precision-Recall curve
        self.plot_precision_recall_curve(self.y_test, y_prob_positive, timestamp)
        
        # Save results
        if save_results:
            results = {
                'timestamp': timestamp,
                'test_samples': len(self.y_test),
                'classification_report': classification_report(
                    self.y_test, y_pred,
                    target_names=['Healthy', 'Parkinson'],
                    output_dict=True
                ),
                'confusion_matrix': cm.tolist(),
                'roc_auc': float(auc),
                'predictions': {
                    'y_true': self.y_test.tolist(),
                    'y_pred': y_pred.tolist(),
                    'y_prob': y_prob_positive.tolist()
                }
            }
            
            with open(self.output_dir / f"evaluation_results_{timestamp}.json", 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ Evaluation results saved to: {self.output_dir}")
        
        return {
            'accuracy': (y_pred == self.y_test).mean(),
            'auc': auc,
            'confusion_matrix': cm
        }
    
    def plot_confusion_matrix(self, cm: np.ndarray, timestamp: str):
        """Plot confusion matrix heatmap"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Healthy', 'Parkinson'],
            yticklabels=['Healthy', 'Parkinson']
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(self.output_dir / f"confusion_matrix_{timestamp}.png", dpi=300)
        plt.close()
    
    def plot_roc_curve(self, y_true: np.ndarray, y_prob: np.ndarray, auc: float, timestamp: str):
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / f"roc_curve_{timestamp}.png", dpi=300)
        plt.close()
    
    def plot_precision_recall_curve(self, y_true: np.ndarray, y_prob: np.ndarray, timestamp: str):
        """Plot Precision-Recall curve"""
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / f"precision_recall_curve_{timestamp}.png", dpi=300)
        plt.close()


def main():
    """Main training script"""
    parser = argparse.ArgumentParser(description='Train DaT scan CNN-LSTM model')
    parser.add_argument('--data_dir', type=str,
                       default='/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed_ntua',
                       help='Directory containing preprocessed data')
    parser.add_argument('--output_dir', type=str,
                       default='/home/hari/Downloads/parkinson/parkinson-app/models/dat_scan',
                       help='Directory to save trained model and results')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=8,
                       help='Batch size for training')
    parser.add_argument('--patience', type=int, default=15,
                       help='Early stopping patience')
    
    args = parser.parse_args()
    
    # Configuration
    DATA_DIR = args.data_dir
    OUTPUT_DIR = args.output_dir
    EPOCHS = args.epochs
    BATCH_SIZE = args.batch_size
    PATIENCE = args.patience
    
    print("="*80)
    print("DaT SCAN MODEL TRAINING")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Data directory: {DATA_DIR}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Patience: {PATIENCE}")
    
    # Configure GPU first (before any TF operations)
    print("\nConfiguring GPU...")
    configure_gpu(use_gpu=True)
    
    # Build model
    print("\nBuilding model...")
    model = DaTModelBuilder.build_standard_model(
        input_shape=(16, 128, 128, 1)
    )
    model.build_model()
    
    # Initialize trainer
    print("\nInitializing trainer...")
    trainer = DaTModelTrainer(
        model=model,
        data_dir=DATA_DIR,
        output_dir=OUTPUT_DIR
    )
    
    # Train model
    trainer.train(
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        patience=PATIENCE
    )
    
    # Evaluate model
    trainer.evaluate(save_results=True)
    
    print("\n" + "="*80)
    print("✅ TRAINING AND EVALUATION COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
