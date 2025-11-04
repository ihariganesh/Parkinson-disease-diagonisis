#!/usr/bin/env python3
"""
📊 MRI Training Progress Monitor

This script monitors the training progress and provides real-time updates
on the focused ensemble training process.
"""

import os
import time
import json
from pathlib import Path
import subprocess

def check_training_progress():
    """Check training progress and display status"""
    
    print("🧠 MRI Ensemble Training Monitor")
    print("=" * 50)
    
    # Check if training process is running
    result = subprocess.run(['pgrep', '-f', 'train_focused_ensemble.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Training process is running (PID: {})".format(result.stdout.strip()))
    else:
        print("⚠️  Training process not detected")
    
    # Check for model files being created
    models_dir = Path("models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*.h5"))
        weights_files = list(models_dir.glob("*weights*"))
        results_files = list(models_dir.glob("*results*.json"))
        
        print(f"\n📁 Models Directory Status:")
        print(f"   Model files (.h5): {len(model_files)}")
        print(f"   Weight files: {len(weights_files)}")
        print(f"   Results files: {len(results_files)}")
        
        if model_files:
            print(f"\n🎯 Model Files Found:")
            for model_file in sorted(model_files):
                size_mb = model_file.stat().st_size / (1024 * 1024)
                print(f"   • {model_file.name} ({size_mb:.1f} MB)")
        
        # Check for results file
        results_file = models_dir / "focused_training_results.json"
        if results_file.exists():
            print(f"\n📊 Training Results Available!")
            try:
                with open(results_file, 'r') as f:
                    results = json.load(f)
                
                print("🏆 Final Results Summary:")
                for model_name, data in results.items():
                    if model_name != 'ensemble' and 'error' not in data:
                        accuracy = data.get('accuracy', 0)
                        print(f"   • {model_name}: {accuracy:.1%} accuracy")
                
                if 'ensemble' in results:
                    ens_data = results['ensemble']
                    print(f"   🎯 Ensemble: {ens_data.get('accuracy', 0):.1%} accuracy")
                        
            except Exception as e:
                print(f"   Error reading results: {e}")
    else:
        print("\n📁 Models directory not found yet")
    
    # Check GPU usage if nvidia-smi is available
    try:
        gpu_result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
        if gpu_result.returncode == 0:
            lines = gpu_result.stdout.strip().split('\n')
            print(f"\n🖥️  GPU Status:")
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) >= 3:
                    util, mem_used, mem_total = parts
                    print(f"   GPU {i}: {util}% utilization, {mem_used}/{mem_total} MB memory")
    except:
        print("\n💻 GPU monitoring not available (using CPU)")
    
    return model_files, results_files

def main():
    """Main monitoring function"""
    
    print("🚀 Starting MRI Training Monitor...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            model_files, results_files = check_training_progress()
            
            # If training is complete (results file exists), show final status
            if results_files:
                print("\n🎉 Training appears to be complete!")
                print("Check the detailed results above.")
                break
            
            print(f"\n⏱️  Next check in 30 seconds... (Training in progress)")
            print("-" * 50)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

if __name__ == "__main__":
    main()