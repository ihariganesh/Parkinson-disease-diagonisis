"""
Speech Analysis Model for Parkinson's Disease Detection
Train CNN+LSTM model using the provided speech features dataset
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Model, Sequential
from keras.layers import Dense, LSTM, Conv1D, MaxPooling1D, Dropout, Flatten, Input, Reshape
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import os
from datetime import datetime

class SpeechPDModel:
    def __init__(self, model_save_dir="models/speech"):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model_save_dir = model_save_dir
        self.feature_names = None
        
        # Create model directory if it doesn't exist
        os.makedirs(model_save_dir, exist_ok=True)
        
    def load_data(self, csv_path):
        """Load and preprocess the speech features dataset"""
        print("Loading speech features dataset...")
        
        # Load the CSV file
        df = pd.read_csv(csv_path)
        print(f"Dataset shape: {df.shape}")
        
        # Separate features and target
        X = df.drop(['class'], axis=1)
        y = df['class']
        
        # Store feature names for later use
        self.feature_names = X.columns.tolist()
        print(f"Number of features: {len(self.feature_names)}")
        print(f"Class distribution:\n{y.value_counts()}")
        
        return X.values, y.values
        
    def preprocess_data(self, X, y):
        """Preprocess features and labels"""
        print("Preprocessing data...")
        
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
        
        print(f"Training set shape: {X_train_scaled.shape}")
        print(f"Test set shape: {X_test_scaled.shape}")
        print(f"Training labels distribution: {np.bincount(y_train)}")
        print(f"Test labels distribution: {np.bincount(y_test)}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
        
    def create_cnn_lstm_model(self, input_shape):
        """Create CNN+LSTM model for speech feature classification"""
        print(f"Creating CNN+LSTM model with input shape: {input_shape}")
        
        model = Sequential([
            # Reshape for CNN (add channel dimension)
            Reshape((input_shape[0], 1)),
            
            # First CNN block
            Conv1D(64, 3, activation='relu', padding='same'),
            Conv1D(64, 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # Second CNN block
            Conv1D(128, 3, activation='relu', padding='same'),
            Conv1D(128, 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # Third CNN block
            Conv1D(256, 3, activation='relu', padding='same'),
            Conv1D(256, 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Dropout(0.25),
            
            # LSTM layers
            LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.3),
            LSTM(64, dropout=0.3, recurrent_dropout=0.3),
            
            # Dense layers
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
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
        print("Training CNN+LSTM model...")
        
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
                filepath=os.path.join(self.model_save_dir, 'best_speech_model.h5'),
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
        print("Evaluating model...")
        
        # Make predictions
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Test Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Healthy', 'Parkinson\'s']))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        return accuracy, y_pred_proba
        
    def save_model_components(self):
        """Save model, scaler, and label encoder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save the trained model
        model_path = os.path.join(self.model_save_dir, f'speech_cnn_lstm_model_{timestamp}.h5')
        self.model.save(model_path)
        print(f"Model saved to: {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(self.model_save_dir, f'speech_scaler_{timestamp}.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"Scaler saved to: {scaler_path}")
        
        # Save label encoder
        encoder_path = os.path.join(self.model_save_dir, f'speech_label_encoder_{timestamp}.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        print(f"Label encoder saved to: {encoder_path}")
        
        # Save feature names
        features_path = os.path.join(self.model_save_dir, f'speech_feature_names_{timestamp}.pkl')
        with open(features_path, 'wb') as f:
            pickle.dump(self.feature_names, f)
        print(f"Feature names saved to: {features_path}")
        
        return model_path, scaler_path, encoder_path, features_path

def main():
    """Main training function"""
    print("=== Speech Analysis Model Training ===")
    
    # Initialize the model
    speech_model = SpeechPDModel()
    
    # Load the data
    csv_path = "pd_speech_features.csv"
    X, y = speech_model.load_data(csv_path)
    
    # Preprocess the data
    X_train, X_test, y_train, y_test = speech_model.preprocess_data(X, y)
    
    # Train the model
    history = speech_model.train_model(X_train, y_train, X_test, y_test)
    
    # Evaluate the model
    accuracy, predictions = speech_model.evaluate_model(X_test, y_test)
    
    # Save model components
    model_path, scaler_path, encoder_path, features_path = speech_model.save_model_components()
    
    print(f"\n=== Training Complete ===")
    print(f"Final Test Accuracy: {accuracy:.4f}")
    print(f"Model saved successfully!")

if __name__ == "__main__":
    main()