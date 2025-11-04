#!/usr/bin/env python3
"""
Cleanup script to remove temporary files, cache, and unnecessary files
before pushing to GitHub
"""

import os
import shutil
import glob
from pathlib import Path

def remove_patterns(base_path, patterns):
    """Remove files/directories matching patterns"""
    removed = []
    for pattern in patterns:
        for path in glob.glob(os.path.join(base_path, pattern), recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    removed.append(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    removed.append(path)
            except Exception as e:
                print(f"⚠️  Could not remove {path}: {e}")
    return removed

def cleanup_workspace():
    """Main cleanup function"""
    print("🧹 Starting workspace cleanup...")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Patterns to remove
    cleanup_patterns = [
        # Python cache
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        
        # Logs
        "**/*.log",
        "**/logs",
        
        # Temporary files
        "**/*.tmp",
        "**/*.temp",
        "**/*.swp",
        "**/*.swo",
        "**/temp",
        "**/tmp",
        
        # OS files
        "**/.DS_Store",
        "**/Thumbs.db",
        
        # IDE files
        "**/.vscode",
        "**/.idea",
        
        # Frontend build artifacts (keep source)
        "frontend/dist",
        "frontend/build",
        "frontend/.cache",
        
        # Test cache
        "**/.pytest_cache",
        "**/htmlcov",
        "**/.coverage",
        
        # Backup files
        "**/*.bak",
        "**/*.backup",
    ]
    
    print("\n📁 Cleaning patterns:")
    for pattern in cleanup_patterns:
        print(f"   - {pattern}")
    
    print("\n🔄 Removing files...")
    removed = remove_patterns(base_path, cleanup_patterns)
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Removed {len(removed)} items")
    
    if removed:
        print("\n📝 Removed items (first 20):")
        for item in removed[:20]:
            rel_path = os.path.relpath(item, base_path)
            print(f"   - {rel_path}")
        
        if len(removed) > 20:
            print(f"   ... and {len(removed) - 20} more items")
    
    print("\n" + "=" * 60)
    print("✨ Workspace is now clean and ready for git!")
    
    # Show disk space saved
    print("\n💾 Large directories to exclude (in .gitignore):")
    large_dirs = [
        "ml_env",
        "node_modules", 
        "uploads",
        "models",
        "ml_models/dat_preprocessed",
        "ml_models/dat_preprocessed_ntua",
        "DAT",
        "ntua-parkinson-dataset",
        "handwritings"
    ]
    
    for dir_name in large_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if os.path.exists(dir_path):
            size = get_dir_size(dir_path)
            print(f"   - {dir_name}: {format_size(size)}")

def get_dir_size(path):
    """Get total size of directory"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except:
        pass
    return total

def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

if __name__ == "__main__":
    cleanup_workspace()
