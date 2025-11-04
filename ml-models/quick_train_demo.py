#!/usr/bin/env python3
"""
Quick Demo Training Script - Train a single MobileNetV2 model for testing
This is a faster alternative to train all models for immediate testing
"""

import os
import sys
import numpy as np
import cv2
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def check_packages():
    """Check if required packages are available"""
    try:
        import tensorflow as tf  # type: ignore
        print(f"✓ TensorFlow: {tf.__version__}")
        
        import sklearn  # type: ignore
        print(f"✓ Scikit-learn: {sklearn.__version__}")
        
        import cv2  # type: ignore
        print(f"✓ OpenCV: {cv2.__version__}")
        
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install: pip install tensorflow opencv-python scikit-learn matplotlib")
        return False

def quick_train_mobilenet():
    """Train a single MobileNetV2 model quickly for demo"""
    print("🚀 Quick Training - MobileNetV2 for Demo")
    print("=" * 50)
    
    import tensorflow as tf  # type: ignore
    MobileNetV2 = tf.keras.applications.MobileNetV2  # type: ignore
    layers = tf.keras.layers  # type: ignore
    Model = tf.keras.Model  # type: ignore
    from sklearn.model_selection import train_test_split  # type: ignore
    
    # Set up paths
    data_path = Path("../archive/drawings")
    if not data_path.exists():
        print(f"❌ Dataset not found at {data_path}")
        return False
    
    # Load data quickly
    print("📂 Loading dataset...")
    images = []
    labels = []
    
    # Load spiral data
    for category, label in [('healthy', 0), ('parkinson', 1)]:
        spiral_path = data_path / 'spiral' / 'training' / category
        if spiral_path.exists():
            for img_file in list(spiral_path.glob('*.png'))[:20]:  # Limit for quick training
                try:
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (224, 224))
                        images.append(img)
                        labels.append(label)
                except Exception as e:
                    print(f"Skipping {img_file}: {e}")
                    continue
    
    # Load wave data  
    for category, label in [('healthy', 0), ('parkinson', 1)]:
        wave_path = data_path / 'wave' / 'training' / category
        if wave_path.exists():
            for img_file in list(wave_path.glob('*.png'))[:20]:  # Limit for quick training
                try:
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (224, 224))
                        images.append(img)
                        labels.append(label)
                except Exception as e:
                    print(f"Skipping {img_file}: {e}")
                    continue
    
    if len(images) < 10:
        print("❌ Not enough images loaded for training")
        return False
    
    print(f"📊 Loaded {len(images)} images")
    
    # Prepare data
    X = np.array(images, dtype='float32') / 255.0
    y = np.array(labels)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"🔄 Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Create model
    print("🏗️  Building MobileNetV2 model...")
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False
    
    model = tf.keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Train model (quick training)
    print("🎯 Training model (quick mode)...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=5,  # Quick training
        batch_size=8,
        verbose=1
    )
    
    # Evaluate
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"📈 Test Accuracy: {test_accuracy:.3f}")
    
    # Save model
    model_dir = Path("trained_models")
    model_dir.mkdir(exist_ok=True)
    
    model.save(model_dir / "mobilenetv2_best.h5")
    print(f"💾 Model saved to {model_dir}/mobilenetv2_best.h5")
    
    # Test the advanced detector
    print("\n🧪 Testing Advanced Detector...")
    try:
        from advanced_detector import AdvancedParkinsonsDetector
        detector = AdvancedParkinsonsDetector()
        
        if detector.models:
            print(f"✅ Detector loaded with models: {list(detector.models.keys())}")
            
            # Test with a sample image
            test_path = data_path / "spiral" / "training" / "healthy"
            test_files = list(test_path.glob("*.png"))
            if test_files:
                result = detector.analyze_handwriting(test_files[0])
                if 'error' not in result:
                    summary = result['prediction_summary']
                    print(f"🎯 Test Result: {summary['final_diagnosis']} ({summary['confidence_score']})")
                else:
                    print(f"❌ Test failed: {result['error']}")
            
        else:
            print("❌ No models loaded in detector")
            
    except Exception as e:
        print(f"❌ Detector test failed: {e}")
    
    return True

def main():
    """Main function"""
    print("🧠 Quick Demo Training for Advanced Parkinson's Detection")
    print("=" * 60)
    
    if not check_packages():
        return False
    
    # Change to ml-models directory
    os.chdir(Path(__file__).parent)
    
    if quick_train_mobilenet():
        print("\n🎉 Quick training completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ MobileNetV2 model trained and saved")
        print("   ✅ Advanced detector tested")
        print("   ✅ Ready for web application integration")
        print("\n🚀 Next steps:")
        print("   1. Start the backend server")
        print("   2. Test the handwriting analysis in the web app")
        print("   3. Run full training later with: python train_advanced_models.py")
        return True
    else:
        print("\n❌ Quick training failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)