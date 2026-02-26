#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

print("Testing all imports...")

try:
    # Basic imports
    import tensorflow as tf
    print(f" TensorFlow {tf.__version__}")
    
    import numpy as np
    print(f" NumPy {np.__version__}")
    
    import cv2
    print(f" OpenCV {cv2.__version__}")
    
    import pandas as pd
    print(f" Pandas {pd.__version__}")
    
    import matplotlib.pyplot as plt
    print(" Matplotlib")
    
    import seaborn as sns
    print(" Seaborn")
    
    from sklearn.metrics import classification_report
    print(" Scikit-learn")
    
    # TensorFlow components
    layers = tf.keras.layers
    GlobalAveragePooling2D = tf.keras.layers.GlobalAveragePooling2D
    Dropout = tf.keras.layers.Dropout
    Dense = tf.keras.layers.Dense
    BatchNormalization = tf.keras.layers.BatchNormalization
    ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator
    ResNet50 = tf.keras.applications.ResNet50
    EfficientNetB0 = tf.keras.applications.EfficientNetB0
    EarlyStopping = tf.keras.callbacks.EarlyStopping
    ReduceLROnPlateau = tf.keras.callbacks.ReduceLROnPlateau
    ModelCheckpoint = tf.keras.callbacks.ModelCheckpoint
    Adam = tf.keras.optimizers.Adam
    
    print(" All TensorFlow components imported")
    
    # Test creating a simple model
    model = tf.keras.Sequential([
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    
    print(" Model creation test passed")
    print("\n All imports working correctly!")
    
except ImportError as e:
    print(f" Import error: {e}")
except Exception as e:
    print(f" Unexpected error: {e}")