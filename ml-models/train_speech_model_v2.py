#!/usr/bin/env python3
"""
Enhanced Speech Model Trainer for Parkinson's Disease Detection
Version 2.0 - Uses available features instead of pre-computed dataset

This script:
1. Uses the actual feature extractor to extract features from audio files
2. Trains a CNN+LSTM model with the features that can be reliably extracted
3. Ensures compatibility between training and inference
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, LSTM, Conv1D, MaxPooling1D, Dropout, Flatten, Reshape
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import logging
from datetime import datetime
from pathlib import Path
import soundfile as sf
import librosa

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from speech_feature_extractor import SpeechFeatureExtractor
from speech_analysis_service_v2 import SpeechAnalysisServiceV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechModelTrainerV2:
    def __init__(self, model_save_dir="models/speech"):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model_save_dir = model_save_dir
        self.feature_names = None
        self.feature_extractor = SpeechFeatureExtractor()
        
        # Create model directory if it doesn't exist
        os.makedirs(model_save_dir, exist_ok=True)
        
        # Get feature statistics
        self.feature_stats = self.feature_extractor.get_feature_statistics()
        if self.feature_stats:
            logger.info(f"✓ Feature extractor ready: {self.feature_stats['total_features']} features")
            logger.info(f"✓ Parselmouth available: {self.feature_stats['parselmouth_available']}")
        else:
            logger.error("❌ Failed to initialize feature extractor")
            raise RuntimeError("Feature extractor initialization failed")
    
    def check_feature_compatibility(self):
        """Check feature compatibility and return information"""
        if not self.feature_stats:
            return {
                'feature_count': 0,
                'recommendations': ['Feature extractor not initialized']
            }
        
        recommendations = []
        
        if not self.feature_stats['parselmouth_available']:
            recommendations.append("Install praat-parselmouth for enhanced feature extraction")
        
        if self.feature_stats['total_features'] < 100:
            recommendations.append("Low feature count - consider adding more feature types")
        
        return {
            'feature_count': self.feature_stats['total_features'],
            'parselmouth_available': self.feature_stats['parselmouth_available'],
            'feature_categories': self.feature_stats['feature_categories'],
            'recommendations': recommendations
        }
        
    def create_synthetic_dataset(self, num_samples=500):
        """Create a synthetic dataset for demonstration/testing purposes"""
        logger.info("Creating synthetic dataset for training...")
        
        # Create synthetic audio signals
        features_list = []
        labels = []
        
        sample_rate = 22050
        duration = 3  # seconds
        
        for i in range(num_samples):
            # Create synthetic signals with different characteristics
            # Simulate healthy vs Parkinson's speech patterns
            
            is_parkinsons = i < num_samples // 2
            
            if is_parkinsons:
                # Simulate Parkinson's characteristics
                # - More irregular fundamental frequency
                # - Higher jitter and shimmer
                # - Different spectral characteristics
                base_freq = np.random.uniform(80, 200)
                freq_variation = np.random.uniform(0.1, 0.3)  # Higher variation
                noise_level = np.random.uniform(0.1, 0.3)  # More noise
                tremor_freq = np.random.uniform(4, 8)  # Tremor simulation
            else:
                # Simulate healthy speech
                base_freq = np.random.uniform(100, 250)
                freq_variation = np.random.uniform(0.02, 0.1)  # Lower variation
                noise_level = np.random.uniform(0.05, 0.15)  # Less noise
                tremor_freq = 0  # No tremor
            
            # Generate time vector
            t = np.linspace(0, duration, sample_rate * duration)
            
            # Create fundamental frequency with variation
            f0_variation = np.sin(2 * np.pi * tremor_freq * t) * freq_variation * base_freq
            instantaneous_freq = base_freq + f0_variation
            
            # Generate signal with harmonics
            signal = np.zeros_like(t)
            for harmonic in range(1, 5):
                amplitude = 1.0 / harmonic
                signal += amplitude * np.sin(2 * np.pi * harmonic * instantaneous_freq * t)
            
            # Add noise
            signal += noise_level * np.random.randn(len(signal))
            
            # Normalize
            signal = signal / np.max(np.abs(signal))
            
            # Save as temporary file and extract features
            temp_filename = f"temp_synthetic_{i}.wav"
            try:
                sf.write(temp_filename, signal, sample_rate)
                features = self.feature_extractor.extract_all_features(temp_filename)
                
                if features and len(features) > 0:
                    features_list.append(features)
                    labels.append("1" if is_parkinsons else "0")  # 1 = Parkinson's, 0 = Healthy
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"Generated {i + 1}/{num_samples} samples...")
                        
            except Exception as e:
                logger.warning(f"Failed to generate sample {i}: {e}")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        
        if not features_list:
            raise RuntimeError("No valid features could be extracted from synthetic data")
            
        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        features_df['class'] = labels
        
        logger.info(f"✓ Created synthetic dataset: {len(features_df)} samples, {len(features_df.columns)-1} features")
        logger.info(f"✓ Class distribution: {pd.Series(labels).value_counts().to_dict()}")
        
        return features_df
        
    def load_data_from_csv(self, csv_path):
        """Load data from existing CSV file (legacy support)"""
        logger.info(f"Loading data from CSV: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
        df = pd.read_csv(csv_path)
        logger.info(f"✓ Loaded CSV: {df.shape[0]} samples, {df.shape[1]} columns")
        
        # Check if we can extract the same features from audio
        available_features = set(self.feature_stats['feature_names'])
        csv_features = set(df.columns) - {'class', 'gender', 'id'}  # Remove non-feature columns
        
        matching_features = available_features.intersection(csv_features)
        missing_features = csv_features - available_features
        
        logger.info(f"✓ Feature compatibility check:")
        logger.info(f"  - CSV features: {len(csv_features)}")
        logger.info(f"  - Available features: {len(available_features)}")
        logger.info(f"  - Matching features: {len(matching_features)}")
        logger.info(f"  - Missing features: {len(missing_features)}")
        
        if len(matching_features) < len(csv_features) * 0.5:
            logger.warning("⚠️  Less than 50% of CSV features are available from feature extractor")
            logger.warning("   Recommendation: Use synthetic dataset or retrain with available features")
            
        return df
        
    def prepare_data(self, data_source="synthetic", csv_path=None, num_synthetic_samples=500):
        """Prepare training data from specified source"""
        if data_source == "synthetic":
            df = self.create_synthetic_dataset(num_synthetic_samples)
        elif data_source == "csv" and csv_path:
            df = self.load_data_from_csv(csv_path)
        else:
            raise ValueError("Invalid data source. Use 'synthetic' or provide csv_path")
            
        # Separate features and target
        feature_columns = [col for col in df.columns if col not in ['class', 'gender', 'id']]
        X = df[feature_columns].values
        y = df['class'].values
        
        # Store feature names for later use
        self.feature_names = feature_columns
        logger.info(f"✓ Prepared data: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"✓ Class distribution: {pd.Series(y).value_counts().to_dict()}")
        
        return X, y
        
    def preprocess_data(self, X, y):
        """Preprocess features and labels"""
        logger.info("Preprocessing data...")
        
        # Handle any missing values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Encode labels (0: Healthy, 1: Parkinson's)
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"✓ Training set: {X_train_scaled.shape}")
        logger.info(f"✓ Test set: {X_test_scaled.shape}")
        logger.info(f"✓ Training labels: {np.bincount(y_train)}")
        logger.info(f"✓ Test labels: {np.bincount(y_test)}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
        
    def create_cnn_lstm_model(self, input_shape):
        """Create CNN+LSTM model optimized for available features"""
        logger.info(f"Creating CNN+LSTM model with input shape: {input_shape}")
        
        # Adjust architecture based on number of features
        num_features = input_shape[0]
        
        if num_features < 100:
            # Smaller architecture for fewer features
            conv_filters = [32, 64, 128]
            lstm_units = [64, 32]
            dense_units = [64, 32, 16]
        elif num_features < 300:
            # Medium architecture
            conv_filters = [64, 128, 256]
            lstm_units = [128, 64]
            dense_units = [128, 64, 32]
        else:
            # Full architecture for many features
            conv_filters = [64, 128, 256]
            lstm_units = [128, 64]
            dense_units = [128, 64, 32]
        
        model = Sequential([
            # Reshape for CNN (add channel dimension)
            Reshape((input_shape[0], 1)),
            
            # First CNN block
            Conv1D(conv_filters[0], 3, activation='relu', padding='same'),
            Conv1D(conv_filters[0], 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # Second CNN block
            Conv1D(conv_filters[1], 3, activation='relu', padding='same'),
            Conv1D(conv_filters[1], 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # Third CNN block
            Conv1D(conv_filters[2], 3, activation='relu', padding='same'),
            Conv1D(conv_filters[2], 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # LSTM layers
            LSTM(lstm_units[0], return_sequences=True, dropout=0.3, recurrent_dropout=0.3),
            LSTM(lstm_units[1], dropout=0.3, recurrent_dropout=0.3),
            
            # Dense layers
            Dense(dense_units[0], activation='relu'),
            Dropout(0.5),
            Dense(dense_units[1], activation='relu'),
            Dropout(0.3),
            Dense(dense_units[2], activation='relu'),
            Dropout(0.2),
            
            # Output layer (sigmoid for binary classification)
            Dense(1, activation='sigmoid')
        ])
        
        # Compile the model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
        
    def train_model(self, X_train, y_train, X_val, y_val, epochs=100):
        """Train the CNN+LSTM model"""
        logger.info("Training CNN+LSTM model...")
        
        # Create the model
        self.model = self.create_cnn_lstm_model(X_train.shape[1:])
        
        # Print model summary
        self.model.summary()
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=8,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=os.path.join(self.model_save_dir, 'best_speech_model_v2.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False,
                verbose=1
            )
        ]
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
        
    def evaluate_model(self, X_test, y_test):
        """Evaluate the trained model"""
        logger.info("Evaluating model...")
        
        # Make predictions
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"✓ Test Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Healthy', 'Parkinson\'s']))
        
        logger.info("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        return accuracy, y_pred_proba
        
    def save_model_components(self):
        """Save model, scaler, label encoder, and feature names"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save the trained model
        model_path = os.path.join(self.model_save_dir, f'speech_cnn_lstm_model_v2_{timestamp}.h5')
        self.model.save(model_path)
        logger.info(f"✓ Model saved to: {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(self.model_save_dir, f'speech_scaler_v2_{timestamp}.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        logger.info(f"✓ Scaler saved to: {scaler_path}")
        
        # Save label encoder
        encoder_path = os.path.join(self.model_save_dir, f'speech_label_encoder_v2_{timestamp}.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        logger.info(f"✓ Label encoder saved to: {encoder_path}")
        
        # Save feature names
        features_path = os.path.join(self.model_save_dir, f'speech_feature_names_v2_{timestamp}.pkl')
        with open(features_path, 'wb') as f:
            pickle.dump(self.feature_names, f)
        logger.info(f"✓ Feature names saved to: {features_path}")
        
        return model_path, scaler_path, encoder_path, features_path

def main():
    parser = argparse.ArgumentParser(description='Train Enhanced Speech Analysis Model for Parkinson\'s Detection V2')
    parser.add_argument('--data-source', type=str, default='synthetic', choices=['synthetic', 'csv'],
                       help='Data source: synthetic or csv')
    parser.add_argument('--csv-path', type=str, default='pd_speech_features.csv',
                       help='Path to the CSV file (if using csv data source)')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--models-dir', type=str, default='models/speech',
                       help='Directory to save trained models')
    parser.add_argument('--num-samples', type=int, default=500,
                       help='Number of synthetic samples to generate')
    
    args = parser.parse_args()
    
    logger.info("=== Enhanced Speech Analysis Model Training V2 ===")
    logger.info(f"Data source: {args.data_source}")
    logger.info(f"Training epochs: {args.epochs}")
    logger.info(f"Models directory: {args.models_dir}")
    
    if args.data_source == 'csv':
        if not os.path.exists(args.csv_path):
            logger.error(f"❌ CSV file not found: {args.csv_path}")
            return 1
        logger.info(f"CSV file: {args.csv_path}")
    else:
        logger.info(f"Synthetic samples: {args.num_samples}")
    
    try:
        # Initialize the model trainer
        trainer = SpeechModelTrainerV2(model_save_dir=args.models_dir)
        
        # Prepare the data
        logger.info("Preparing training data...")
        X, y = trainer.prepare_data(
            data_source=args.data_source,
            csv_path=args.csv_path if args.data_source == 'csv' else None,
            num_synthetic_samples=args.num_samples
        )
        
        # Preprocess the data
        logger.info("Preprocessing data...")
        X_train, X_test, y_train, y_test = trainer.preprocess_data(X, y)
        
        # Train the model
        logger.info("Starting model training...")
        history = trainer.train_model(X_train, y_train, X_test, y_test, epochs=args.epochs)
        
        # Evaluate the model
        logger.info("Evaluating model...")
        accuracy, predictions = trainer.evaluate_model(X_test, y_test)
        
        # Save model components
        logger.info("Saving model...")
        model_path, scaler_path, encoder_path, features_path = trainer.save_model_components()
        
        logger.info(f"\n=== Training Complete ===")
        logger.info(f"✓ Final Test Accuracy: {accuracy:.4f}")
        logger.info(f"✓ Model saved to: {model_path}")
        logger.info(f"✓ All components saved successfully!")
        
        # Test the trained model with the service
        logger.info("\n=== Testing with Service ===")
        service = SpeechAnalysisServiceV2(models_dir=args.models_dir)
        if service.load_models():
            info = service.get_system_info()
            logger.info(f"✓ Service compatibility: {info['compatibility']['status'] if info['compatibility'] else 'N/A'}")
            logger.info("✓ The speech analysis model is now ready for use!")
        else:
            logger.warning("⚠️  Service test failed, but model was saved successfully")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)