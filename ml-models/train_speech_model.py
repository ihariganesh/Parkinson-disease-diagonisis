#!/usr/bin/env python3
"""
Train Speech Analysis Model for Parkinson's Disease Detection
This script trains the CNN+LSTM model using the provided speech features dataset
"""

import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from speech_model_trainer import SpeechPDModel

def main():
    parser = argparse.ArgumentParser(description='Train Speech Analysis Model for Parkinson\'s Disease Detection')
    parser.add_argument('--csv-path', type=str, default='pd_speech_features.csv',
                       help='Path to the speech features CSV file')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--models-dir', type=str, default='models/speech',
                       help='Directory to save trained models')
    
    args = parser.parse_args()
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_path):
        print(f"Error: CSV file not found at {args.csv_path}")
        print("Please ensure the pd_speech_features.csv file is in the current directory")
        return 1
    
    print("=== Speech Analysis Model Training ===")
    print(f"CSV file: {args.csv_path}")
    print(f"Training epochs: {args.epochs}")
    print(f"Models directory: {args.models_dir}")
    print()
    
    try:
        # Initialize the model trainer
        speech_model = SpeechPDModel(model_save_dir=args.models_dir)
        
        # Load the data
        print("Loading speech features dataset...")
        X, y = speech_model.load_data(args.csv_path)
        
        # Preprocess the data
        print("Preprocessing data...")
        X_train, X_test, y_train, y_test = speech_model.preprocess_data(X, y)
        
        # Train the model
        print("Starting model training...")
        history = speech_model.train_model(X_train, y_train, X_test, y_test, epochs=args.epochs)
        
        # Evaluate the model
        print("Evaluating model...")
        accuracy, predictions = speech_model.evaluate_model(X_test, y_test)
        
        # Save model components
        print("Saving model...")
        model_path, scaler_path, encoder_path, features_path = speech_model.save_model_components()
        
        print(f"\n=== Training Complete ===")
        print(f"Final Test Accuracy: {accuracy:.4f}")
        print(f"Model saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")
        print(f"Label encoder saved to: {encoder_path}")
        print(f"Feature names saved to: {features_path}")
        print()
        print("The speech analysis model is now ready for use!")
        print("You can now use the speech analysis API endpoints.")
        
        return 0
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)