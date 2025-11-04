#!/usr/bin/env python3
"""
Script to train handwriting analysis models using the provided dataset
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ml_models.handwriting_analyzer import HandwritingAnalyzer, train_models_from_dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Dataset path
    dataset_path = "archive"
    
    # Check if dataset exists
    if not Path(dataset_path).exists():
        print(f"Error: Dataset not found at {dataset_path}")
        return 1
    
    print("Starting model training...")
    print(f"Dataset path: {dataset_path}")
    
    # Create models directory
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    try:
        # Train models for both spiral and wave
        train_models_from_dataset(dataset_path)
        print("Model training completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())