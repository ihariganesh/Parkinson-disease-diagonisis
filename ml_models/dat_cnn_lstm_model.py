"""
DaT Scan CNN+LSTM Model Architecture
2D CNN for feature extraction + LSTM for sequence learning + Classification head
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.utils import register_keras_serializable
from typing import Tuple, Optional
import numpy as np


@register_keras_serializable(package="Custom", name="GrayscaleToRGBLayer")
class GrayscaleToRGBLayer(layers.Layer):
    """Custom layer to convert grayscale to RGB by repeating channels"""
    
    def call(self, inputs):
        return tf.repeat(inputs, 3, axis=-1)
    
    def compute_output_shape(self, input_shape):
        # Change last dimension from 1 to 3
        return input_shape[:-1] + (3,)
    
    def get_config(self):
        config = super().get_config()
        return config


class DaTCNNLSTMModel:
    """
    Hybrid CNN-LSTM model for DaT scan classification
    
    Architecture:
        1. TimeDistributed CNN (EfficientNetB0) - extracts features from each slice
        2. Bidirectional LSTM - learns temporal/spatial patterns across slices
        3. Dense layers - classification head
    """
    
    def __init__(
        self,
        input_shape: Tuple[int, int, int, int] = (16, 128, 128, 1),
        num_classes: int = 2,
        lstm_units: int = 128,
        dropout_rate: float = 0.5,
        learning_rate: float = 0.0001
    ):
        """
        Initialize model architecture
        
        Args:
            input_shape: (num_slices, height, width, channels)
            num_classes: Number of output classes (2 for binary)
            lstm_units: Number of LSTM units
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        
        self.model = None
        self.history = None
    
    def build_model(self) -> Model:
        """
        Build the CNN-LSTM model
        
        Returns:
            Compiled Keras model
        """
        num_slices, height, width, channels = self.input_shape
        
        # Input layer: (batch, num_slices, H, W, C)
        inputs = keras.Input(shape=self.input_shape, name='input_scans')
        
        # Convert grayscale to RGB for CNN (repeat channels)
        if channels == 1:
            x = layers.TimeDistributed(
                GrayscaleToRGBLayer(),
                name='grayscale_to_rgb'
            )(inputs)
        else:
            x = inputs
        
        # Custom CNN Feature Extractor (more GPU-efficient than EfficientNet)
        # Build a custom CNN that works well with our data
        def create_custom_cnn():
            """Create a custom CNN for feature extraction"""
            cnn_input = keras.Input(shape=(height, width, 3))
            
            # Block 1
            x = layers.Conv2D(32, (3, 3), activation='relu', padding='same', name='block1_conv1')(cnn_input)
            x = layers.BatchNormalization(name='block1_bn1')(x)
            x = layers.Conv2D(32, (3, 3), activation='relu', padding='same', name='block1_conv2')(x)
            x = layers.BatchNormalization(name='block1_bn2')(x)
            x = layers.MaxPooling2D((2, 2), name='block1_pool')(x)
            x = layers.Dropout(0.25, name='block1_dropout')(x)
            
            # Block 2
            x = layers.Conv2D(64, (3, 3), activation='relu', padding='same', name='block2_conv1')(x)
            x = layers.BatchNormalization(name='block2_bn1')(x)
            x = layers.Conv2D(64, (3, 3), activation='relu', padding='same', name='block2_conv2')(x)
            x = layers.BatchNormalization(name='block2_bn2')(x)
            x = layers.MaxPooling2D((2, 2), name='block2_pool')(x)
            x = layers.Dropout(0.25, name='block2_dropout')(x)
            
            # Block 3
            x = layers.Conv2D(128, (3, 3), activation='relu', padding='same', name='block3_conv1')(x)
            x = layers.BatchNormalization(name='block3_bn1')(x)
            x = layers.Conv2D(128, (3, 3), activation='relu', padding='same', name='block3_conv2')(x)
            x = layers.BatchNormalization(name='block3_bn2')(x)
            x = layers.MaxPooling2D((2, 2), name='block3_pool')(x)
            x = layers.Dropout(0.25, name='block3_dropout')(x)
            
            # Block 4
            x = layers.Conv2D(256, (3, 3), activation='relu', padding='same', name='block4_conv1')(x)
            x = layers.BatchNormalization(name='block4_bn1')(x)
            x = layers.Conv2D(256, (3, 3), activation='relu', padding='same', name='block4_conv2')(x)
            x = layers.BatchNormalization(name='block4_bn2')(x)
            x = layers.GlobalAveragePooling2D(name='block4_gap')(x)
            
            cnn_model = Model(inputs=cnn_input, outputs=x, name='custom_cnn')
            return cnn_model
        
        cnn_base = create_custom_cnn()
        
        # Apply CNN to each time step (slice)
        x = layers.TimeDistributed(cnn_base, name='cnn_feature_extractor')(x)
        
        # Add batch normalization
        x = layers.BatchNormalization(name='bn_after_cnn')(x)
        
        # Bidirectional LSTM for sequence learning
        # Forward LSTM learns patterns from slice 1 → N
        # Backward LSTM learns patterns from slice N → 1
        x = layers.Bidirectional(
            layers.LSTM(
                self.lstm_units,
                return_sequences=True,
                dropout=self.dropout_rate,
                recurrent_dropout=0.2,
                name='lstm_1'
            ),
            name='bidirectional_lstm_1'
        )(x)
        
        # Second LSTM layer (optional, for deeper learning)
        x = layers.Bidirectional(
            layers.LSTM(
                self.lstm_units // 2,
                return_sequences=False,  # Only return final output
                dropout=self.dropout_rate,
                recurrent_dropout=0.2,
                name='lstm_2'
            ),
            name='bidirectional_lstm_2'
        )(x)
        
        # Dense classification head
        x = layers.Dense(256, activation='relu', name='fc1')(x)
        x = layers.BatchNormalization(name='bn_fc1')(x)
        x = layers.Dropout(self.dropout_rate, name='dropout_fc1')(x)
        
        x = layers.Dense(128, activation='relu', name='fc2')(x)
        x = layers.BatchNormalization(name='bn_fc2')(x)
        x = layers.Dropout(self.dropout_rate / 2, name='dropout_fc2')(x)
        
        # Output layer
        if self.num_classes == 2:
            # Binary classification
            outputs = layers.Dense(1, activation='sigmoid', name='output')(x)
            loss = 'binary_crossentropy'
            metrics = [
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        else:
            # Multi-class classification
            outputs = layers.Dense(self.num_classes, activation='softmax', name='output')(x)
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']
        
        # Create model
        model = Model(inputs=inputs, outputs=outputs, name='DaT_CNN_LSTM')
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )
        
        self.model = model
        return model
    
    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            self.build_model()
        
        # Capture summary as string
        summary_lines = []
        self.model.summary(print_fn=lambda x: summary_lines.append(x))
        return '\n'.join(summary_lines)
    
    def count_parameters(self) -> dict:
        """Count trainable and non-trainable parameters"""
        if self.model is None:
            self.build_model()
        
        trainable_count = sum([tf.size(w).numpy() for w in self.model.trainable_weights])
        non_trainable_count = sum([tf.size(w).numpy() for w in self.model.non_trainable_weights])
        
        return {
            'trainable': trainable_count,
            'non_trainable': non_trainable_count,
            'total': trainable_count + non_trainable_count
        }
    
    def save_model(self, filepath: str):
        """Save model to disk"""
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        self.model.save(filepath)
        print(f"Model saved to: {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from disk"""
        self.model = keras.models.load_model(filepath)
        print(f"Model loaded from: {filepath}")
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data
        
        Args:
            X: Input data (batch, num_slices, H, W, C)
            threshold: Classification threshold for binary classification
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model() or load_model() first.")
        
        # Get prediction probabilities
        probabilities = self.model.predict(X, verbose=0)
        
        # Convert to class predictions
        if self.num_classes == 2:
            predictions = (probabilities > threshold).astype(int).flatten()
        else:
            predictions = np.argmax(probabilities, axis=1)
        
        return predictions, probabilities


class DaTModelBuilder:
    """Factory class for building different model variants"""
    
    @staticmethod
    def build_lightweight_model(input_shape: Tuple[int, int, int, int]) -> DaTCNNLSTMModel:
        """Build a lightweight model for faster training (RTX 3050 friendly)"""
        return DaTCNNLSTMModel(
            input_shape=input_shape,
            num_classes=2,
            lstm_units=64,
            dropout_rate=0.4,
            learning_rate=0.001
        )
    
    @staticmethod
    def build_standard_model(input_shape: Tuple[int, int, int, int]) -> DaTCNNLSTMModel:
        """Build standard model (balanced performance and accuracy)"""
        return DaTCNNLSTMModel(
            input_shape=input_shape,
            num_classes=2,
            lstm_units=128,
            dropout_rate=0.5,
            learning_rate=0.0001
        )
    
    @staticmethod
    def build_deep_model(input_shape: Tuple[int, int, int, int]) -> DaTCNNLSTMModel:
        """Build deep model for maximum accuracy (requires more GPU memory)"""
        return DaTCNNLSTMModel(
            input_shape=input_shape,
            num_classes=2,
            lstm_units=256,
            dropout_rate=0.6,
            learning_rate=0.00005
        )


def main():
    """Test model building"""
    print("Building DaT CNN-LSTM model...")
    
    # Build model
    model_builder = DaTCNNLSTMModel(
        input_shape=(16, 128, 128, 1),
        num_classes=2,
        lstm_units=128,
        dropout_rate=0.5
    )
    
    model = model_builder.build_model()
    
    # Print summary
    print("\n" + "="*80)
    print("MODEL ARCHITECTURE")
    print("="*80)
    print(model_builder.get_model_summary())
    
    # Print parameter counts
    params = model_builder.count_parameters()
    print("\n" + "="*80)
    print("MODEL PARAMETERS")
    print("="*80)
    print(f"Trainable parameters:     {params['trainable']:,}")
    print(f"Non-trainable parameters: {params['non_trainable']:,}")
    print(f"Total parameters:         {params['total']:,}")
    
    print("\n✅ Model built successfully!")


if __name__ == "__main__":
    main()
