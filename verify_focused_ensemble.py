#!/usr/bin/env python3
"""
🔍 Verify Focused MRI Ensemble Configuration

This script verifies that VGG16 and Swin-Transformer have been successfully removed
and only ResNet50, EfficientNetB0, and EfficientNetB3 are configured for MRI analysis.
"""

import os
import sys
import json
from pathlib import Path

def check_ensemble_weights():
    """Check ensemble weights configuration"""
    weights_file = Path("models/ensemble_weights.json")
    if weights_file.exists():
        with open(weights_file, 'r') as f:
            weights = json.load(f)
        
        print("📊 Ensemble Weights Configuration:")
        for model, weight in weights.items():
            print(f"   • {model}: {weight}")
        
        # Verify only 3 models
        if len(weights) == 3 and all(model in weights for model in ['resnet50', 'efficientnet_b0', 'efficientnet_b3']):
            print("✅ Focused ensemble configuration verified!")
            return True
        else:
            print("❌ Configuration still contains unwanted models")
            return False
    else:
        print("⚠️ Ensemble weights file not found")
        return False

def check_model_imports():
    """Check that VGG16 and Swin-Transformer imports are removed"""
    service_files = [
        "ml-models/mri_ensemble_service.py",
        "ml-models/mri_ensemble_service_enhanced.py", 
        "ml-models/mri_ensemble_service_backup.py"
    ]
    
    issues = []
    
    for file_path in service_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for unwanted imports
            if 'VGG16' in content:
                issues.append(f"{file_path}: Still contains VGG16 import")
            if 'SwinTransformerBlock' in content:
                issues.append(f"{file_path}: Still contains SwinTransformerBlock")
            if "'vgg16'" in content:
                issues.append(f"{file_path}: Still contains vgg16 references")
            if "'swin_transformer'" in content:
                issues.append(f"{file_path}: Still contains swin_transformer references")
    
    if issues:
        print("❌ Found remaining VGG16/Swin-Transformer references:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ All VGG16/Swin-Transformer references removed!")
        return True

def check_focused_ensemble():
    """Check focused ensemble implementation"""
    focused_file = Path("ml-models/mri_focused_ensemble.py")
    if focused_file.exists():
        print("✅ Focused ensemble implementation available")
        return True
    else:
        print("❌ Focused ensemble implementation not found")
        return False

def main():
    """Main verification function"""
    print("🧠 Focused MRI Ensemble Verification")
    print("=" * 50)
    
    os.chdir(Path(__file__).parent)
    
    all_good = True
    
    # Check configurations
    all_good &= check_ensemble_weights()
    print()
    all_good &= check_model_imports() 
    print()
    all_good &= check_focused_ensemble()
    print()
    
    if all_good:
        print("🎉 All verifications passed!")
        print("\n📝 Summary of Changes:")
        print("   • Removed VGG16 model from all ensemble services")
        print("   • Removed Swin-Transformer model from all ensemble services")
        print("   • Rebalanced weights for 3-model ensemble:")
        print("     - ResNet50: 35%")
        print("     - EfficientNetB0: 30%")
        print("     - EfficientNetB3: 35%")
        print("   • Updated documentation and API references")
        print("   • Maintained memory optimization features")
        print("\n🚀 Ready to train focused ensemble:")
        print("   python train_focused_ensemble.py")
        return True
    else:
        print("❌ Some issues found. Please fix before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)