#!/usr/bin/env python3
"""
🧠 Focused MRI Ensemble Training for Parkinson's Disease Detection

This script trains three optimized deep learning models:
- ResNet50: Deep residual networks for feature extraction
- EfficientNetB0: Efficient compound scaling network
- EfficientNetB3: Advanced efficient compound scaling network

Memory-optimized approach for stable training with comprehensive accuracy improvements.
"""

import os
import sys
import warnings
import time
import json
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Add the ml-models directory to Python path
ml_models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ml-models"))
if ml_models_path not in sys.path:
    sys.path.insert(0, ml_models_path)

def main():
    """
    Main training function for the focused MRI ensemble system
    """
    
    print("🧠 Focused MRI Ensemble Training for Parkinson's Disease Detection")
    print("=" * 70)
    print("🎯 Training Three Optimized Models:")
    print("   • ResNet50 - Deep residual networks")
    print("   • EfficientNetB0 - Efficient compound scaling")
    print("   • EfficientNetB3 - Advanced efficient compound scaling")
    print("⚡ Memory-optimized for stable training")
    print("=" * 70)
    
    try:
        # Import the focused ensemble service
        print("📦 Importing focused MRI ensemble service...")
        from mri_focused_ensemble import FocusedMRIEnsemble
        print("✓ Successfully imported focused ensemble service")
        
        # Check dataset
        data_dir = "/home/hari/Downloads/parkinson/MRI"
        if not os.path.exists(data_dir):
            print(f"❌ Dataset directory not found: {data_dir}")
            print("Please ensure the MRI dataset is available with structure:")
            print("  MRI/")
            print("  ├── Healthy/")
            print("  └── PD/")
            return False
        
        # Check subdirectories
        healthy_dir = os.path.join(data_dir, "Healthy")
        pd_dir = os.path.join(data_dir, "PD")
        
        if not os.path.exists(healthy_dir):
            print(f"❌ Healthy images directory not found: {healthy_dir}")
            return False
        
        if not os.path.exists(pd_dir):
            print(f"❌ PD images directory not found: {pd_dir}")
            return False
        
        # Count images
        healthy_count = len([f for f in os.listdir(healthy_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        pd_count = len([f for f in os.listdir(pd_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        print(f"📊 Dataset Summary:")
        print(f"   Healthy images: {healthy_count}")
        print(f"   PD images: {pd_count}")
        print(f"   Total images: {healthy_count + pd_count}")
        
        if healthy_count == 0 or pd_count == 0:
            print("❌ Insufficient data for training")
            return False
        
        # Initialize the focused ensemble service
        print("\n🚀 Initializing Focused MRI Ensemble Service...")
        ensemble_service = FocusedMRIEnsemble(
            img_size=(224, 224),
            batch_size=8  # Optimized batch size for three models
        )
        print("✓ Service initialized with 3-model focused ensemble")
        
        # Focused training configuration
        training_config = {
            'epochs': 15,              # Comprehensive training epochs
            'validation_split': 0.2,   # 20% for validation
            'use_augmentation': True,  # Enable data augmentation
            'enable_fine_tuning': True,# Enable fine-tuning for better accuracy
            'max_samples_per_class': 3000  # Memory-safe sample limit
        }
        
        print(f"\n🎯 Focused Training Configuration:")
        for key, value in training_config.items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*70)
        print("🚀 STARTING FOCUSED ENSEMBLE TRAINING")
        print("="*70)
        
        # Start training with memory-optimized approach
        start_time = time.time()
        
        training_results = ensemble_service.train_focused_ensemble(
            data_dir=data_dir,
            **training_config
        )
        
        training_time = time.time() - start_time
        
        print("\n" + "="*70)
        print("🎉 FOCUSED TRAINING COMPLETED!")
        print("="*70)
        print(f"⏱️  Total training time: {training_time:.1f} seconds ({training_time/60:.1f} minutes)")
        
        # Analyze and display results
        print("\n📊 FOCUSED TRAINING RESULTS:")
        print("-" * 50)
        
        successful_models = 0
        total_accuracy = 0
        best_model = None
        best_accuracy = 0
        
        for model_name, results in training_results.items():
            if model_name == 'ensemble':
                continue
                
            if 'error' in results:
                print(f"❌ {model_name}: Training failed - {results['error']}")
            else:
                successful_models += 1
                accuracy = results.get('accuracy', 0)
                fine_tune_acc = results.get('fine_tune_accuracy')
                improvement = results.get('improvement', 0)
                auc = results.get('auc', 0)
                
                print(f"✓ {model_name}:")
                print(f"   📈 Base Accuracy: {accuracy:.1%}")
                if fine_tune_acc is not None:
                    print(f"   🎯 Fine-tuned Accuracy: {fine_tune_acc:.1%} (Δ{improvement:+.1%})")
                    accuracy = fine_tune_acc  # Use fine-tuned accuracy for comparison
                print(f"   📊 AUC Score: {auc:.3f}")
                
                total_accuracy += accuracy
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model = model_name
        
        # Ensemble results
        if 'ensemble' in training_results and 'error' not in training_results['ensemble']:
            ensemble_results = training_results['ensemble']
            print(f"\n🏆 FOCUSED ENSEMBLE PERFORMANCE:")
            print(f"   📈 Accuracy: {ensemble_results['accuracy']:.1%}")
            print(f"   📊 Precision: {ensemble_results['precision']:.3f}")
            print(f"   📊 Recall: {ensemble_results['recall']:.3f}")
            print(f"   📊 F1-Score: {ensemble_results['f1_score']:.3f}")
            print(f"   📊 AUC: {ensemble_results['auc']:.3f}")
            print(f"   🎯 Models Used: {ensemble_results['models_used']}/3")
        
        # Performance summary
        if successful_models > 0:
            avg_accuracy = total_accuracy / successful_models
            print(f"✓ Successfully trained models: {successful_models}/3")
            print(f"📊 Average model accuracy: {avg_accuracy:.1%}")
            print(f"🏆 Best performing model: {best_model} ({best_accuracy:.1%})")
        else:
            print("❌ No models trained successfully")
            print("🔧 Troubleshooting recommendations:")
            print("   • Check GPU memory availability")
            print("   • Reduce batch size further")
            print("   • Verify data format and structure")
        
        # Save focused results
        results_dir = "/home/hari/Downloads/parkinson/parkinson-app/models"
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = os.path.join(results_dir, "focused_training_results.json")
        with open(results_file, 'w') as f:
            json.dump(training_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        print("\n" + "="*70)
        print("🎯 FOCUSED ENSEMBLE TRAINING COMPLETE")
        print("📈 Memory-optimized three-model approach:")
        print("   ✓ ResNet50 - Deep residual learning")
        print("   ✓ EfficientNetB0 - Efficient compound scaling")
        print("   ✓ EfficientNetB3 - Advanced efficiency")
        print("   ✓ Data augmentation with comprehensive transformations")
        print("   ✓ Fine-tuning with domain adaptation")
        print("   ✓ Memory-safe progressive training")
        print("="*70)
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing focused ensemble service: {e}")
        print(f"Make sure mri_focused_ensemble.py exists in {ml_models_path}")
        return False
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Focused ensemble training completed successfully!")
        print("🚀 Start the backend to use the new focused ensemble models")
    else:
        print("\n💥 Training failed. Please check the errors above.")
        sys.exit(1)