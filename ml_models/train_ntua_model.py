"""
Train DaT Scan Model with NTUA Dataset
Uses 66 subjects from NTUA dataset with data augmentation
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_DISABLE_MKL'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from dat_cnn_lstm_model import DaTCNNLSTMModel

print("=" * 80)
print("DaT SCAN MODEL TRAINING - NTUA DATASET (66 SUBJECTS)")
print("=" * 80)


class NTUADaTModelTrainer:
    """Trainer for NTUA DaT dataset"""
    
    def __init__(self, 
                 preprocessed_dir: str = "ml_models/dat_preprocessed_ntua",
                 model_output_dir: str = "models/dat_scan",
                 batch_size: int = 4,
                 epochs: int = 50,
                 augmentation_factor: int = 2):
        """
        Initialize NTUA trainer
        
        Args:
            preprocessed_dir: Directory with NTUA preprocessed .npy files
            model_output_dir: Directory to save trained models
            batch_size: Batch size for training (default: 4 for 6GB GPU)
            epochs: Maximum training epochs
            augmentation_factor: How many augmented versions per original sample
        """
        self.preprocessed_dir = Path(preprocessed_dir)
        self.model_output_dir = Path(model_output_dir)
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        self.augmentation_factor = augmentation_factor
        self.use_augmentation = augmentation_factor > 0
        
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
        
    def augment_data(self, X, y):
        """
        Apply data augmentation to training data
        
        Args:
            X: Input data (samples, slices, height, width, channels)
            y: Labels
            
        Returns:
            Augmented data and labels
        """
        if not self.use_augmentation:
            return X, y
            
        print(f"\nApplying data augmentation (factor: {self.augmentation_factor})...")
        
        augmented_X = [X]
        augmented_y = [y]
        
        # Create augmented versions
        for aug_idx in range(self.augmentation_factor):
            print(f"  Creating augmentation variant {aug_idx + 1}/{self.augmentation_factor}...")
            
            aug_data = []
            for i in range(len(X)):
                sample = X[i]  # (16, 128, 128, 1)
                
                # Apply random augmentations to each slice
                augmented_sample = []
                for slice_idx in range(sample.shape[0]):
                    slice_img = sample[slice_idx, :, :, 0]
                    
                    # Random rotation (-15 to +15 degrees)
                    if np.random.random() > 0.5:
                        angle = np.random.uniform(-15, 15)
                        k = int(angle / 90)
                        slice_img = np.rot90(slice_img, k)
                    
                    # Random horizontal flip
                    if np.random.random() > 0.5:
                        slice_img = np.fliplr(slice_img)
                    
                    # Random zoom (0.9 to 1.1)
                    if np.random.random() > 0.5:
                        zoom_factor = np.random.uniform(0.95, 1.05)
                        h, w = slice_img.shape
                        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
                        
                        if zoom_factor > 1.0:
                            # Crop center
                            start_h = (new_h - h) // 2
                            start_w = (new_w - w) // 2
                            from scipy.ndimage import zoom
                            zoomed = zoom(slice_img, zoom_factor)
                            slice_img = zoomed[start_h:start_h+h, start_w:start_w+w]
                        else:
                            # Pad edges
                            from scipy.ndimage import zoom
                            zoomed = zoom(slice_img, zoom_factor)
                            pad_h = (h - zoomed.shape[0]) // 2
                            pad_w = (w - zoomed.shape[1]) // 2
                            slice_img = np.pad(zoomed, 
                                             ((pad_h, h-zoomed.shape[0]-pad_h),
                                              (pad_w, w-zoomed.shape[1]-pad_w)),
                                             mode='constant')
                    
                    # Random brightness adjustment (0.9 to 1.1)
                    if np.random.random() > 0.5:
                        brightness = np.random.uniform(0.9, 1.1)
                        slice_img = np.clip(slice_img * brightness, 0, 1)
                    
                    # Random Gaussian noise
                    if np.random.random() > 0.5:
                        noise = np.random.normal(0, 0.02, slice_img.shape)
                        slice_img = np.clip(slice_img + noise, 0, 1)
                    
                    augmented_sample.append(slice_img[..., np.newaxis])
                
                aug_data.append(np.array(augmented_sample))
            
            augmented_X.append(np.array(aug_data))
            augmented_y.append(y.copy())
        
        # Concatenate all versions
        X_augmented = np.concatenate(augmented_X, axis=0)
        y_augmented = np.concatenate(augmented_y, axis=0)
        
        print(f"✅ Augmentation complete!")
        print(f"   Original size: {X.shape}")
        print(f"   Augmented size: {X_augmented.shape}")
        
        return X_augmented, y_augmented
    
    def train(self):
        """Train the model"""
        print("\nLoading NTUA preprocessed data...")
        
        # Load data
        X_train = np.load(self.preprocessed_dir / "train_X.npy")
        y_train = np.load(self.preprocessed_dir / "train_y.npy")
        X_val = np.load(self.preprocessed_dir / "val_X.npy")
        y_val = np.load(self.preprocessed_dir / "val_y.npy")
        X_test = np.load(self.preprocessed_dir / "test_X.npy")
        y_test = np.load(self.preprocessed_dir / "test_y.npy")
        
        print(f"Original - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Apply augmentation to training data only
        X_train, y_train = self.augment_data(X_train, y_train)
        
        print(f"\n✅ Data loaded successfully!")
        print(f"Final - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Compute class weights
        class_weights_array = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weights = {i: class_weights_array[i] for i in range(len(class_weights_array))}
        print(f"\nClass weights: {class_weights}")
        
        # Build model
        print("\nBuilding model...")
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
        
        print("\n" + "=" * 80)
        print("MODEL ARCHITECTURE")
        print("=" * 80)
        self.model.summary()
        
        # Callbacks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.model_output_dir / f'dat_model_ntua_{timestamp}.keras'
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_auc',
                patience=self.config['patience'],
                restore_best_weights=True,
                mode='max',
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=str(model_path),
                monitor='val_auc',
                save_best_only=True,
                mode='max',
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
        print("\n" + "=" * 80)
        print("TRAINING START")
        print("=" * 80)
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            class_weight=class_weights,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate on test set
        print("\n" + "=" * 80)
        print("FINAL EVALUATION ON TEST SET")
        print("=" * 80)
        
        test_results = self.model.evaluate(X_test, y_test, verbose=1)
        test_metrics = {
            'test_loss': test_results[0],
            'test_accuracy': test_results[1],
            'test_auc': test_results[2],
            'test_precision': test_results[3],
            'test_recall': test_results[4]
        }
        
        print("\nTest Metrics:")
        for metric, value in test_metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        # Calculate F1 score
        precision = test_metrics['test_precision']
        recall = test_metrics['test_recall']
        f1_score = 2 * (precision * recall) / (precision + recall + 1e-7)
        test_metrics['test_f1_score'] = f1_score
        print(f"  test_f1_score: {f1_score:.4f}")
        
        # Save final model
        final_model_path = self.model_output_dir / f'dat_model_ntua_final_{timestamp}.keras'
        self.model.save(final_model_path)
        print(f"\n✅ Final model saved to: {final_model_path}")
        
        # Plot training history
        self.plot_training_history(timestamp)
        
        # Save training summary
        summary = {
            'timestamp': timestamp,
            'dataset': 'NTUA',
            'total_subjects': 66,
            'train_subjects': X_train.shape[0],
            'val_subjects': X_val.shape[0],
            'test_subjects': X_test.shape[0],
            'augmentation_factor': self.augmentation_factor,
            'epochs_trained': len(self.history.history['loss']),
            'config': self.config,
            'test_metrics': test_metrics,
            'model_path': str(final_model_path)
        }
        
        summary_path = self.model_output_dir / f'training_summary_ntua_{timestamp}.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Training summary saved to: {summary_path}")
        
        return test_metrics
    
    def plot_training_history(self, timestamp):
        """Plot and save training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Loss
        axes[0, 0].plot(self.history.history['loss'], label='Train Loss', linewidth=2)
        axes[0, 0].plot(self.history.history['val_loss'], label='Val Loss', linewidth=2)
        axes[0, 0].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy
        axes[0, 1].plot(self.history.history['accuracy'], label='Train Accuracy', linewidth=2)
        axes[0, 1].plot(self.history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
        axes[0, 1].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # AUC
        axes[1, 0].plot(self.history.history['auc'], label='Train AUC', linewidth=2)
        axes[1, 0].plot(self.history.history['val_auc'], label='Val AUC', linewidth=2)
        axes[1, 0].set_title('Model AUC', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('AUC')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Precision & Recall
        axes[1, 1].plot(self.history.history['precision'], label='Train Precision', linewidth=2)
        axes[1, 1].plot(self.history.history['val_precision'], label='Val Precision', linewidth=2)
        axes[1, 1].plot(self.history.history['recall'], label='Train Recall', linewidth=2)
        axes[1, 1].plot(self.history.history['val_recall'], label='Val Recall', linewidth=2)
        axes[1, 1].set_title('Precision & Recall', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        plot_path = self.model_output_dir / f'training_history_ntua_{timestamp}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✅ Training plots saved to: {plot_path}")
        
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
        print("\n⚠️  No GPU detected, using CPU")
    
    # Get absolute paths
    script_dir = Path(__file__).parent
    preprocessed_dir = script_dir / "dat_preprocessed_ntua"
    model_output_dir = script_dir.parent / "models" / "dat_scan"
    
    print(f"\n📁 NTUA preprocessed data: {preprocessed_dir}")
    print(f"📁 Model output directory: {model_output_dir}")
    
    # Initialize trainer
    trainer = NTUADaTModelTrainer(
        preprocessed_dir=str(preprocessed_dir),
        model_output_dir=str(model_output_dir),
        batch_size=4,
        epochs=50,
        augmentation_factor=2  # 46 train subjects → 138 samples
    )
    
    # Train
    metrics = trainer.train()
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\nFinal Test Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    print("\n✅ NTUA model training finished successfully!")
    print("\n📊 Dataset Comparison:")
    print("  Previous: 37 subjects → AUC 0.25")
    print("  NTUA:     66 subjects → Check test_auc above")
    print(f"  Improvement: +29 subjects (+78%)")


if __name__ == "__main__":
    main()
