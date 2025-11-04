#!/usr/bin/env python3
"""
Advanced Transfer Learning System for Parkinson's Disease Detection
Using ResNet50 and EfficientNet with proper preprocessing and evaluation
"""

import os
import sys
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from pathlib import Path
import cv2  # type: ignore
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
import json
from datetime import datetime

# TensorFlow imports
try:
    import tensorflow as tf  # type: ignore
    from tensorflow import keras  # type: ignore
    # Import through tf.keras to avoid resolution issues
    layers = tf.keras.layers  # type: ignore
    GlobalAveragePooling2D = tf.keras.layers.GlobalAveragePooling2D  # type: ignore
    Dropout = tf.keras.layers.Dropout  # type: ignore
    Dense = tf.keras.layers.Dense  # type: ignore
    BatchNormalization = tf.keras.layers.BatchNormalization  # type: ignore
    ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator  # type: ignore
    ResNet50 = tf.keras.applications.ResNet50  # type: ignore
    EfficientNetB0 = tf.keras.applications.EfficientNetB0  # type: ignore
    EarlyStopping = tf.keras.callbacks.EarlyStopping  # type: ignore
    ReduceLROnPlateau = tf.keras.callbacks.ReduceLROnPlateau  # type: ignore
    ModelCheckpoint = tf.keras.callbacks.ModelCheckpoint  # type: ignore
    Adam = tf.keras.optimizers.Adam  # type: ignore
    print("✅ TensorFlow imported successfully")
except ImportError as e:
    print(f"❌ TensorFlow import failed: {e}")
    print("Install with: pip install tensorflow>=2.8.0")
    sys.exit(1)

class ParkinsonDetectionModel:
    def __init__(self, model_type='resnet50', input_shape=(224, 224, 3)):
        self.model_type = model_type
        self.input_shape = input_shape
        self.model = None
        self.history = None
        self.dataset_path = "/home/hari/Downloads/parkinson/handwritings/drawings"
        
    def create_data_generators(self, batch_size=16):
        """Create data generators with proper augmentation"""
        print("🔄 Creating data generators...")
        
        # Training data augmentation (careful with medical images)
        train_datagen = ImageDataGenerator(
            rescale=1.0/255.0,
            rotation_range=15,          # ±15° rotation
            zoom_range=0.1,             # ±10% zoom
            brightness_range=[0.8, 1.2], # Brightness adjustment
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=False,       # Don't flip - direction matters for spirals
            vertical_flip=False,
            validation_split=0.2
        )
        
        # Test data - only rescaling
        test_datagen = ImageDataGenerator(rescale=1.0/255.0)
        
        generators = {}
        
        # Process spiral and wave separately
        for pattern_type in ['spiral', 'wave']:
            pattern_path = os.path.join(self.dataset_path, pattern_type)
            training_path = os.path.join(pattern_path, 'training')
            testing_path = os.path.join(pattern_path, 'testing')
            
            if os.path.exists(training_path) and os.path.exists(testing_path):
                # Training generator with validation split
                train_gen = train_datagen.flow_from_directory(
                    training_path,
                    target_size=self.input_shape[:2],
                    batch_size=batch_size,
                    class_mode='binary',
                    subset='training',
                    shuffle=True,
                    seed=42
                )
                
                # Validation generator
                val_gen = train_datagen.flow_from_directory(
                    training_path,
                    target_size=self.input_shape[:2],
                    batch_size=batch_size,
                    class_mode='binary',
                    subset='validation',
                    shuffle=False,
                    seed=42
                )
                
                # Test generator
                test_gen = test_datagen.flow_from_directory(
                    testing_path,
                    target_size=self.input_shape[:2],
                    batch_size=1,  # For individual predictions
                    class_mode='binary',
                    shuffle=False
                )
                
                generators[pattern_type] = {
                    'train': train_gen,
                    'validation': val_gen,
                    'test': test_gen
                }
                
                print(f"✅ {pattern_type.capitalize()} data loaded:")
                print(f"   Training: {train_gen.samples} samples")
                print(f"   Validation: {val_gen.samples} samples")
                print(f"   Testing: {test_gen.samples} samples")
                print(f"   Classes: {train_gen.class_indices}")
        
        return generators
    
    def build_model(self):
        """Build transfer learning model"""
        print(f"🏗️ Building {self.model_type} model...")
        
        # Choose base model
        if self.model_type.lower() == 'resnet50':
            base_model = ResNet50(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )
        elif self.model_type.lower() == 'efficientnet':
            base_model = EfficientNetB0(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Add custom classification head
        model = keras.Sequential([
            base_model,
            GlobalAveragePooling2D(),
            Dropout(0.3),
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.1),
            Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=1e-4),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        print(f"✅ Model built successfully")
        print(f"   Total parameters: {model.count_params():,}")
        
        return model
    
    def train_model(self, generators, pattern_type, epochs=30):
        """Train the model with early stopping"""
        print(f"🚀 Training {self.model_type} on {pattern_type} data...")
        
        train_gen = generators[pattern_type]['train']
        val_gen = generators[pattern_type]['validation']
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=7,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                f'models/{self.model_type}_{pattern_type}_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Train model
        history = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        self.history = history
        
        # Fine-tuning phase: unfreeze top layers
        print("🔧 Fine-tuning top layers...")
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze all layers except the top 20
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=Adam(learning_rate=1e-5),  # Lower learning rate
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Fine-tune for additional epochs
        fine_tune_epochs = 10
        total_epochs = epochs + fine_tune_epochs
        
        history_fine = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=total_epochs,
            initial_epoch=history.epoch[-1],
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        self.model.save(f'models/{self.model_type}_{pattern_type}_final.h5')
        
        print(f"✅ Training completed for {pattern_type}")
        return history, history_fine
    
    def evaluate_model(self, generators, pattern_type):
        """Comprehensive model evaluation"""
        print(f"📊 Evaluating {self.model_type} on {pattern_type} test data...")
        
        test_gen = generators[pattern_type]['test']
        
        # Predictions
        predictions = self.model.predict(test_gen, verbose=1)
        predicted_classes = (predictions > 0.5).astype(int).flatten()
        
        # True labels
        true_labels = test_gen.classes
        
        # Classification report
        report = classification_report(
            true_labels, 
            predicted_classes,
            target_names=['Healthy', 'Parkinson'],
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, predicted_classes)
        
        # ROC curve
        fpr, tpr, thresholds = roc_curve(true_labels, predictions)
        roc_auc = auc(fpr, tpr)
        
        # Calculate additional metrics
        accuracy = report['accuracy']
        precision = report['Parkinson']['precision']
        recall = report['Parkinson']['recall']
        f1_score = report['Parkinson']['f1-score']
        
        print(f"📈 Test Results for {pattern_type}:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall: {recall:.4f}")
        print(f"   F1-Score: {f1_score:.4f}")
        print(f"   ROC-AUC: {roc_auc:.4f}")
        
        # Save results
        results = {
            'model_type': self.model_type,
            'pattern_type': pattern_type,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'roc_auc': float(roc_auc),
            'confusion_matrix': cm.tolist(),
            'classification_report': report,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f'results/{self.model_type}_{pattern_type}_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def plot_training_history(self, pattern_type):
        """Plot training history"""
        if self.history is None:
            print("❌ No training history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Training')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Training')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Training')
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Training')
        axes[1, 1].plot(self.history.history['val_recall'], label='Validation')
        axes[1, 1].set_title('Model Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(f'plots/{self.model_type}_{pattern_type}_training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def predict_single_image(self, image_path, threshold=0.5):
        """Predict single image"""
        if self.model is None:
            raise ValueError("Model not loaded. Please train or load a model first.")
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self.input_shape[:2])
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        
        # Predict
        prediction = self.model.predict(image, verbose=0)[0][0]
        
        # Interpret results
        predicted_class = "Parkinson" if prediction > threshold else "Healthy"
        confidence = abs(prediction - 0.5) * 2  # Distance from decision boundary
        
        return {
            'prediction': predicted_class,
            'probability': float(prediction),
            'confidence': float(confidence),
            'raw_score': float(prediction)
        }

def main():
    """Main training pipeline"""
    print("🧠 Starting Parkinson's Disease Detection Training Pipeline")
    print("=" * 60)
    
    # Create output directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('plots', exist_ok=True)
    
    # Train models for both patterns and architectures
    models_to_train = [
        ('resnet50', 'spiral'),
        ('resnet50', 'wave'),
        ('efficientnet', 'spiral'),
        ('efficientnet', 'wave')
    ]
    
    results_summary = []
    
    for model_type, pattern_type in models_to_train:
        print(f"\n🎯 Training {model_type.upper()} for {pattern_type.upper()} detection")
        print("-" * 50)
        
        try:
            # Initialize model
            detector = ParkinsonDetectionModel(model_type=model_type)
            
            # Create data generators
            generators = detector.create_data_generators(batch_size=16)
            
            if pattern_type not in generators:
                print(f"❌ No data found for {pattern_type}")
                continue
            
            # Build model
            detector.build_model()
            
            # Train model
            history, history_fine = detector.train_model(generators, pattern_type, epochs=30)
            
            # Evaluate model
            results = detector.evaluate_model(generators, pattern_type)
            results_summary.append(results)
            
            # Plot training history
            detector.plot_training_history(pattern_type)
            
        except Exception as e:
            print(f"❌ Error training {model_type} on {pattern_type}: {e}")
            continue
    
    # Save summary results
    with open('results/training_summary.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print("\n🎉 Training pipeline completed!")
    print("📁 Check the following directories:")
    print("   - models/ : Trained model files")
    print("   - results/ : Evaluation results")
    print("   - plots/ : Training visualizations")

if __name__ == "__main__":
    main()