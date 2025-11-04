"""
Enhanced DaT Scan Model Training with Data Augmentation
Improves model performance through augmentation and advanced techniques
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_DISABLE_MKL'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

# Import existing modules
from dat_cnn_lstm_model import DaTCNNLSTMModel

print("=" * 80)
print("DaT SCAN MODEL TRAINING - ENHANCED WITH DATA AUGMENTATION")
print("=" * 80)


class EnhancedDaTModelTrainer:
    """Enhanced trainer with data augmentation"""
    
    def __init__(self, 
                 preprocessed_dir: str = "ml_models/dat_preprocessed",
                 model_output_dir: str = "models/dat_scan",
                 batch_size: int = 4,
                 epochs: int = 50,
                 augmentation_factor: int = 3):
        """
        Initialize enhanced trainer
        
        Args:
            preprocessed_dir: Directory with preprocessed .npy files
            model_output_dir: Directory to save trained models
            batch_size: Batch size for training (default: 4 for 6GB GPU)
            epochs: Maximum training epochs
            augmentation_factor: How many augmented versions per original sample
        """
        self.preprocessed_dir = preprocessed_dir
        self.model_output_dir = Path(model_output_dir)
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        self.batch_size = batch_size
        self.epochs = epochs
        self.augmentation_factor = augmentation_factor
        self.use_augmentation = augmentation_factor > 0  # Enable augmentation if factor > 0
        
        # Training configuration
        self.config = {
            'input_shape': (16, 128, 128, 1),
            'num_classes': 1,
            'learning_rate': 0.0001,
            'patience': 10,
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
        
        augmented_X = []
        augmented_y = []
        
        # Keep original data
        augmented_X.append(X)
        augmented_y.append(y)
        
        # Create augmented versions
        for aug_idx in range(self.augmentation_factor):
            print(f"Creating augmentation variant {aug_idx + 1}/{self.augmentation_factor}...")
            
            aug_data = []
            for i in range(len(X)):
                sample = X[i]  # (16, 128, 128, 1)
                
                # Apply random augmentations to each slice in the sequence
                augmented_sample = []
                for slice_idx in range(sample.shape[0]):
                    slice_img = sample[slice_idx]  # (128, 128, 1)
                    
                    # Random rotation (-10 to 10 degrees)
                    if np.random.random() > 0.5:
                        angle = np.random.uniform(-10, 10)
                        slice_img = tf.keras.preprocessing.image.apply_affine_transform(
                            slice_img, theta=angle, fill_mode='nearest'
                        )
                    
                    # Random horizontal flip
                    if np.random.random() > 0.5:
                        slice_img = np.fliplr(slice_img)
                    
                    # Random vertical flip (less common for brain scans)
                    if np.random.random() > 0.7:
                        slice_img = np.flipud(slice_img)
                    
                    # Random zoom (90% to 110%)
                    if np.random.random() > 0.5:
                        zoom_factor = np.random.uniform(0.9, 1.1)
                        slice_img = tf.keras.preprocessing.image.apply_affine_transform(
                            slice_img, zx=zoom_factor, zy=zoom_factor, fill_mode='nearest'
                        )
                    
                    # Random brightness adjustment
                    if np.random.random() > 0.5:
                        brightness_factor = np.random.uniform(0.85, 1.15)
                        slice_img = np.clip(slice_img * brightness_factor, 0, 1)
                    
                    # Random Gaussian noise
                    if np.random.random() > 0.7:
                        noise = np.random.normal(0, 0.02, slice_img.shape)
                        slice_img = np.clip(slice_img + noise, 0, 1)
                    
                    augmented_sample.append(slice_img)
                
                aug_data.append(np.array(augmented_sample))
            
            augmented_X.append(np.array(aug_data))
            augmented_y.append(y)
        
        # Concatenate all augmented data
        X_augmented = np.concatenate(augmented_X, axis=0)
        y_augmented = np.concatenate(augmented_y, axis=0)
        
        print(f"✅ Augmentation complete!")
        print(f"   Original size: {X.shape}")
        print(f"   Augmented size: {X_augmented.shape}")
        
        # Shuffle augmented data
        indices = np.random.permutation(len(X_augmented))
        X_augmented = X_augmented[indices]
        y_augmented = y_augmented[indices]
        
        return X_augmented, y_augmented
    
    def train(self):
        """Train the enhanced model"""
        print("\nLoading preprocessed data...")
        
        # Load preprocessed data directly from .npy files
        data_dir = Path(self.preprocessed_dir)
        if not data_dir.exists():
            raise FileNotFoundError(f"Preprocessed data directory not found: {data_dir}")
        
        X_train = np.load(data_dir / "train_X.npy")
        y_train = np.load(data_dir / "train_y.npy")
        X_val = np.load(data_dir / "val_X.npy")
        y_val = np.load(data_dir / "val_y.npy")
        X_test = np.load(data_dir / "test_X.npy")
        y_test = np.load(data_dir / "test_y.npy")
        
        print(f"Original train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Apply data augmentation to training data only
        X_train, y_train = self.augment_data(X_train, y_train)
        
        print(f"\n✅ Data loaded successfully!")
        print(f"Final train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Calculate class weights
        class_weights_array = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weights = {i: class_weights_array[i] for i in range(len(class_weights_array))}
        
        print(f"\nClass weights: {class_weights}")
        
        # Build model
        print("\nBuilding enhanced model...")
        model_builder = DaTCNNLSTMModel(
            input_shape=self.config['input_shape'],
            num_classes=self.config['num_classes']
        )
        self.model = model_builder.build_model()
        
        # Compile with optimizer
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
        
        # Model summary
        print("\nModel architecture:")
        trainable_params = np.sum([np.prod(v.shape) for v in self.model.trainable_weights])
        print(f"Trainable parameters: {trainable_params:,}")
        
        # Callbacks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.model_output_dir / f"dat_model_enhanced_{timestamp}.keras"
        
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                filepath=str(model_path),
                monitor='val_auc',
                mode='max',
                save_best_only=True,
                verbose=1
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config['patience'],
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            keras.callbacks.CSVLogger(
                str(self.model_output_dir / f'training_log_{timestamp}.csv')
            )
        ]
        
        # Train
        print("\n" + "=" * 80)
        print("STARTING ENHANCED TRAINING")
        print("=" * 80)
        print(f"\nTraining for {self.config['epochs']} epochs with batch size {self.config['batch_size']}...")
        print(f"Training samples: {len(X_train)}, Validation samples: {len(X_val)}")
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            class_weight=class_weights,
            callbacks=callbacks,
            verbose=1
        )
        
        print(f"\n✅ Training complete!")
        print(f"Best model saved to: {model_path}")
        
        # Evaluate
        print("\n" + "=" * 80)
        print("EVALUATION ON TEST SET")
        print("=" * 80)
        
        test_results = self.model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {
            'test_loss': float(test_results[0]),
            'test_accuracy': float(test_results[1]),
            'test_auc': float(test_results[2]),
            'test_precision': float(test_results[3]),
            'test_recall': float(test_results[4])
        }
        
        print(f"\nTest Results:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        # Predictions
        y_pred_probs = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_probs > 0.5).astype(int).flatten()
        
        # Confusion matrix
        from sklearn.metrics import confusion_matrix, classification_report
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)
        
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Healthy', 'Parkinson']))
        
        # Save metrics
        metrics_file = self.model_output_dir / f'metrics_{timestamp}.json'
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Plot training history
        self.plot_training_history(timestamp)
        
        return metrics
    
    def plot_training_history(self, timestamp):
        """Plot and save training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Enhanced Training History', fontsize=16)
        
        # Loss
        axes[0, 0].plot(self.history.history['loss'], label='Train Loss')
        axes[0, 0].plot(self.history.history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy
        axes[0, 1].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0, 1].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0, 1].set_title('Model Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # AUC
        axes[1, 0].plot(self.history.history['auc'], label='Train AUC')
        axes[1, 0].plot(self.history.history['val_auc'], label='Val AUC')
        axes[1, 0].set_title('Model AUC')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('AUC')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Precision & Recall
        axes[1, 1].plot(self.history.history['precision'], label='Train Precision')
        axes[1, 1].plot(self.history.history['recall'], label='Train Recall')
        axes[1, 1].plot(self.history.history['val_precision'], label='Val Precision')
        axes[1, 1].plot(self.history.history['val_recall'], label='Val Recall')
        axes[1, 1].set_title('Precision & Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        plot_path = self.model_output_dir / f'training_history_{timestamp}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Training plots saved to: {plot_path}")
        
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
    preprocessed_dir = script_dir / "dat_preprocessed"
    model_output_dir = script_dir.parent / "models" / "dat_scan"
    
    print(f"\n📁 Preprocessed data directory: {preprocessed_dir}")
    print(f"📁 Model output directory: {model_output_dir}")
    
    # Initialize trainer with augmentation
    trainer = EnhancedDaTModelTrainer(
        preprocessed_dir=str(preprocessed_dir),
        model_output_dir=str(model_output_dir),
        batch_size=4,
        epochs=50,
        augmentation_factor=3  # Create 3 augmented versions per sample
    )
    
    # Train
    metrics = trainer.train()
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\nFinal Test Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    print("\n✅ Enhanced model training finished successfully!")


if __name__ == "__main__":
    main()
