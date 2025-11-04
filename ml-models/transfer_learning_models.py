"""
Advanced Transfer Learning Models for Parkinson's Disease Detection
Using ResNet, EfficientNet, MobileNetV2, and Vision Transformers
"""

import os
import numpy as np  # type: ignore
import cv2  # type: ignore
import tensorflow as tf  # type: ignore
from tensorflow import keras  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.metrics import classification_report, confusion_matrix  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from pathlib import Path
import joblib  # type: ignore
import warnings
warnings.filterwarnings('ignore')

# Import TensorFlow components through tf.keras to avoid resolution issues
layers = tf.keras.layers  # type: ignore
Model = tf.keras.Model  # type: ignore
ResNet50 = tf.keras.applications.ResNet50  # type: ignore
EfficientNetB0 = tf.keras.applications.EfficientNetB0  # type: ignore
MobileNetV2 = tf.keras.applications.MobileNetV2  # type: ignore
DenseNet121 = tf.keras.applications.DenseNet121  # type: ignore
ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator  # type: ignore

class ParkinsonsTransferLearningModels:
    def __init__(self, data_path, img_size=(224, 224), batch_size=32):
        """
        Initialize the transfer learning models for Parkinson's detection
        
        Args:
            data_path: Path to the drawings dataset
            img_size: Input image size for the models
            batch_size: Batch size for training
        """
        self.data_path = Path(data_path)
        self.img_size = img_size
        self.batch_size = batch_size
        self.models = {}
        self.histories = {}
        
        # Create model directory
        self.model_dir = Path("trained_models")
        self.model_dir.mkdir(exist_ok=True)
        
        print(f"Dataset path: {self.data_path}")
        print(f"Image size: {self.img_size}")
        print(f"Batch size: {self.batch_size}")
    
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print("Loading and preprocessing data...")
        
        spiral_data = []
        wave_data = []
        
        # Load spiral data
        for category in ['healthy', 'parkinson']:
            spiral_path = self.data_path / 'spiral' / 'training' / category
            if spiral_path.exists():
                for img_file in spiral_path.glob('*.png'):
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.img_size)
                        spiral_data.append({
                            'image': img,
                            'label': 0 if category == 'healthy' else 1,
                            'type': 'spiral'
                        })
        
        # Load wave data
        for category in ['healthy', 'parkinson']:
            wave_path = self.data_path / 'wave' / 'training' / category
            if wave_path.exists():
                for img_file in wave_path.glob('*.png'):
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.img_size)
                        wave_data.append({
                            'image': img,
                            'label': 0 if category == 'healthy' else 1,
                            'type': 'wave'
                        })
        
        print(f"Loaded {len(spiral_data)} spiral images")
        print(f"Loaded {len(wave_data)} wave images")
        
        # Combine all data
        all_data = spiral_data + wave_data
        np.random.shuffle(all_data)
        
        # Separate images and labels
        images = np.array([item['image'] for item in all_data])
        labels = np.array([item['label'] for item in all_data])
        types = np.array([item['type'] for item in all_data])
        
        # Normalize images
        images = images.astype('float32') / 255.0
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            images, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        print(f"Training set: {len(X_train)} images")
        print(f"Test set: {len(X_test)} images")
        print(f"Healthy samples: {np.sum(labels == 0)}")
        print(f"Parkinson samples: {np.sum(labels == 1)}")
        
        return X_train, X_test, y_train, y_test
    
    def create_resnet_model(self):
        """Create ResNet50 based model"""
        print("Creating ResNet50 model...")
        
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid', name='predictions')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_efficientnet_model(self):
        """Create EfficientNetB0 based model"""
        print("Creating EfficientNetB0 model...")
        
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.4),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid', name='predictions')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_mobilenetv2_model(self):
        """Create MobileNetV2 based model"""
        print("Creating MobileNetV2 model...")
        
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.4),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid', name='predictions')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_vision_transformer(self):
        """Create a simple Vision Transformer model"""
        print("Creating Vision Transformer model...")
        
        # Patch extraction layer
        class Patches(layers.Layer):
            def __init__(self, patch_size):
                super(Patches, self).__init__()
                self.patch_size = patch_size
            
            def call(self, images):
                batch_size = tf.shape(images)[0]
                patches = tf.image.extract_patches(
                    images=images,
                    sizes=[1, self.patch_size, self.patch_size, 1],
                    strides=[1, self.patch_size, self.patch_size, 1],
                    rates=[1, 1, 1, 1],
                    padding="VALID",
                )
                patch_dims = patches.shape[-1]
                patches = tf.reshape(patches, [batch_size, -1, patch_dims])
                return patches
        
        # Patch encoding layer
        class PatchEncoder(layers.Layer):
            def __init__(self, num_patches, projection_dim):
                super(PatchEncoder, self).__init__()
                self.num_patches = num_patches
                self.projection = layers.Dense(units=projection_dim)
                self.position_embedding = layers.Embedding(
                    input_dim=num_patches, output_dim=projection_dim
                )
            
            def call(self, patch):
                positions = tf.range(start=0, limit=self.num_patches, delta=1)
                encoded = self.projection(patch) + self.position_embedding(positions)
                return encoded
        
        # Model parameters
        patch_size = 16
        num_patches = (224 // patch_size) ** 2
        projection_dim = 128
        num_heads = 8
        transformer_units = [projection_dim * 2, projection_dim]
        
        inputs = layers.Input(shape=(*self.img_size, 3))
        
        # Create patches
        patches = Patches(patch_size)(inputs)
        # Encode patches
        encoded_patches = PatchEncoder(num_patches, projection_dim)(patches)
        
        # Create multiple transformer blocks
        for _ in range(4):  # 4 transformer layers
            # Layer normalization 1
            x1 = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
            # Multi-head attention
            attention_output = layers.MultiHeadAttention(
                num_heads=num_heads, key_dim=projection_dim, dropout=0.1
            )(x1, x1)
            # Skip connection 1
            x2 = layers.Add()([attention_output, encoded_patches])
            # Layer normalization 2
            x3 = layers.LayerNormalization(epsilon=1e-6)(x2)
            # MLP
            x3 = layers.Dense(transformer_units[0], activation=tf.nn.gelu)(x3)
            x3 = layers.Dropout(0.1)(x3)
            x3 = layers.Dense(transformer_units[1], activation=tf.nn.gelu)(x3)
            x3 = layers.Dropout(0.1)(x3)
            # Skip connection 2
            encoded_patches = layers.Add()([x3, x2])
        
        # Final layers
        representation = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
        representation = layers.GlobalAveragePooling1D()(representation)
        representation = layers.Dropout(0.5)(representation)
        
        # Classification head
        features = layers.Dense(512, activation="relu")(representation)
        features = layers.Dropout(0.3)(features)
        features = layers.Dense(256, activation="relu")(features)
        features = layers.Dropout(0.2)(features)
        outputs = layers.Dense(1, activation="sigmoid")(features)
        
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_ensemble_model(self):
        """Create an ensemble of multiple models"""
        print("Creating ensemble model...")
        
        # Create base models
        resnet = self.create_resnet_model()
        efficientnet = self.create_efficientnet_model()
        mobilenet = self.create_mobilenetv2_model()
        
        # Remove the final classification layers
        resnet_features = Model(inputs=resnet.input, outputs=resnet.layers[-5].output)
        efficientnet_features = Model(inputs=efficientnet.input, outputs=efficientnet.layers[-5].output)
        mobilenet_features = Model(inputs=mobilenet.input, outputs=mobilenet.layers[-5].output)
        
        # Freeze feature extractors
        for model in [resnet_features, efficientnet_features, mobilenet_features]:
            model.trainable = False
        
        # Input layer
        input_layer = layers.Input(shape=(*self.img_size, 3))
        
        # Extract features from each model
        resnet_out = resnet_features(input_layer)
        efficientnet_out = efficientnet_features(input_layer)
        mobilenet_out = mobilenet_features(input_layer)
        
        # Concatenate features
        combined = layers.Concatenate()([resnet_out, efficientnet_out, mobilenet_out])
        
        # Final classification layers
        x = layers.Dense(512, activation='relu')(combined)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(1, activation='sigmoid')(x)
        
        ensemble_model = Model(inputs=input_layer, outputs=outputs)
        ensemble_model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0005),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return ensemble_model
    
    def train_model(self, model, model_name, epochs=50):
        """Train a model with data augmentation and callbacks"""
        print(f"\nTraining {model_name}...")
        
        # Data augmentation
        datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=self.model_dir / f'{model_name}_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train model
        history = model.fit(
            datagen.flow(self.X_train, self.y_train, batch_size=self.batch_size),
            validation_data=(self.X_test, self.y_test),
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        # Fine-tuning phase for transfer learning models
        if model_name in ['resnet50', 'efficientnet', 'mobilenetv2']:
            print(f"Fine-tuning {model_name}...")
            
            # Unfreeze the base model
            if hasattr(model.layers[0], 'trainable'):
                model.layers[0].trainable = True
            
            # Use lower learning rate for fine-tuning
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.0001),
                loss='binary_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            # Continue training with fine-tuning
            history_ft = model.fit(
                datagen.flow(self.X_train, self.y_train, batch_size=self.batch_size),
                validation_data=(self.X_test, self.y_test),
                epochs=20,
                callbacks=callbacks,
                verbose=1
            )
            
            # Combine histories
            for key in history.history.keys():
                history.history[key].extend(history_ft.history[key])
        
        self.models[model_name] = model
        self.histories[model_name] = history
        
        return model, history
    
    def evaluate_model(self, model, model_name):
        """Evaluate model performance"""
        print(f"\nEvaluating {model_name}...")
        
        # Make predictions
        y_pred_prob = model.predict(self.X_test)
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        # Print classification report
        print(f"\n{model_name} Classification Report:")
        print(classification_report(self.y_test, y_pred, 
                                    target_names=['Healthy', 'Parkinson']))
        
        # Calculate metrics
        accuracy = np.mean(y_pred == self.y_test)
        print(f"\nAccuracy: {accuracy:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Healthy', 'Parkinson'],
                    yticklabels=['Healthy', 'Parkinson'])
        plt.title(f'{model_name} - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(self.model_dir / f'{model_name}_confusion_matrix.png')
        plt.close()
        
        return accuracy, y_pred_prob
    
    def plot_training_history(self, model_name):
        """Plot training history"""
        if model_name not in self.histories:
            return
        
        history = self.histories[model_name]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Accuracy
        ax1.plot(history.history['accuracy'], label='Training Accuracy')
        ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
        ax1.set_title(f'{model_name} - Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        ax1.grid(True)
        
        # Loss
        ax2.plot(history.history['loss'], label='Training Loss')
        ax2.plot(history.history['val_loss'], label='Validation Loss')
        ax2.set_title(f'{model_name} - Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True)
        
        # Precision
        if 'precision' in history.history:
            ax3.plot(history.history['precision'], label='Training Precision')
            ax3.plot(history.history['val_precision'], label='Validation Precision')
            ax3.set_title(f'{model_name} - Precision')
            ax3.set_xlabel('Epoch')
            ax3.set_ylabel('Precision')
            ax3.legend()
            ax3.grid(True)
        
        # Recall
        if 'recall' in history.history:
            ax4.plot(history.history['recall'], label='Training Recall')
            ax4.plot(history.history['val_recall'], label='Validation Recall')
            ax4.set_title(f'{model_name} - Recall')
            ax4.set_xlabel('Epoch')
            ax4.set_ylabel('Recall')
            ax4.legend()
            ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.model_dir / f'{model_name}_training_history.png')
        plt.close()
    
    def save_models(self):
        """Save all trained models"""
        print("\nSaving models...")
        for name, model in self.models.items():
            model.save(self.model_dir / f'{name}_final.h5')
            print(f"Saved {name}")
    
    def train_all_models(self):
        """Train all models"""
        print("Starting comprehensive model training...")
        
        # Load data
        self.load_and_preprocess_data()
        
        model_configs = [
            (self.create_resnet_model, 'resnet50'),
            (self.create_efficientnet_model, 'efficientnet'),
            (self.create_mobilenetv2_model, 'mobilenetv2'),
            (self.create_vision_transformer, 'vision_transformer'),
            (self.create_ensemble_model, 'ensemble')
        ]
        
        results = {}
        
        for model_creator, model_name in model_configs:
            try:
                print(f"\n{'='*50}")
                print(f"Training {model_name.upper()}")
                print(f"{'='*50}")
                
                # Create and train model
                model = model_creator()
                model, history = self.train_model(model, model_name)
                
                # Evaluate model
                accuracy, predictions = self.evaluate_model(model, model_name)
                results[model_name] = accuracy
                
                # Plot training history
                self.plot_training_history(model_name)
                
                print(f"{model_name} training completed successfully!")
                
            except Exception as e:
                print(f"Error training {model_name}: {str(e)}")
                continue
        
        # Save all models
        self.save_models()
        
        # Print final results
        print(f"\n{'='*50}")
        print("FINAL RESULTS")
        print(f"{'='*50}")
        for model_name, accuracy in results.items():
            print(f"{model_name:20}: {accuracy:.4f}")
        
        # Find best model
        if results:
            best_model = max(results.items(), key=lambda x: x[1])
            print(f"\nBest Model: {best_model[0]} with accuracy: {best_model[1]:.4f}")
        
        return results

def main():
    """Main training function"""
    # Set up GPU if available
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Using GPU: {len(gpus)} GPU(s) available")
        except RuntimeError as e:
            print(f"GPU setup error: {e}")
    else:
        print("Using CPU for training")
    
    # Initialize trainer
    data_path = "/home/hari/Downloads/parkinson/parkinson-app/archive/drawings"
    trainer = ParkinsonsTransferLearningModels(data_path)
    
    # Train all models
    results = trainer.train_all_models()
    
    print("\nTraining completed!")
    return trainer, results

if __name__ == "__main__":
    trainer, results = main()