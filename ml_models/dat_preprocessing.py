"""
DaT Scan Dataset Preprocessing Module
Handles loading, preprocessing, and preparation of DaT scan images for training
"""

import os
import numpy as np
import cv2
from pathlib import Path
from typing import Tuple, List, Dict
import json
import argparse
from sklearn.model_selection import train_test_split
from tqdm import tqdm

class DaTDatasetPreprocessor:
    """
    Preprocessor for DaT scan images
    Converts multi-slice scans into sequences ready for CNN+LSTM training
    """
    
    def __init__(
        self,
        data_dir: str,
        target_size: Tuple[int, int] = (128, 128),
        max_slices: int = 16,
        seed: int = 42
    ):
        """
        Initialize the preprocessor
        
        Args:
            data_dir: Path to DAT folder containing Healthy and PD subfolders
            target_size: Target image size (width, height)
            max_slices: Maximum number of slices per subject (pad or truncate)
            seed: Random seed for reproducibility
        """
        self.data_dir = Path(data_dir)
        self.target_size = target_size
        self.max_slices = max_slices
        self.seed = seed
        
        # Check for different directory naming conventions
        if (self.data_dir / "Non PD Patients").exists():
            # NTUA dataset structure
            self.healthy_dir = self.data_dir / "Non PD Patients"
            self.pd_dir = self.data_dir / "PD Patients"
        else:
            # Default structure
            self.healthy_dir = self.data_dir / "Healthy"
            self.pd_dir = self.data_dir / "PD"
        
        # Verify directories exist
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {data_dir}")
        if not self.healthy_dir.exists():
            raise ValueError(f"Healthy directory not found: {self.healthy_dir}")
        if not self.pd_dir.exists():
            raise ValueError(f"PD directory not found: {self.pd_dir}")
    
    def preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Preprocess a single image slice
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image array (128x128x1)
        """
        # Read image in grayscale
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Resize to target size
        img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)
        
        # Normalize pixel values to [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # Add channel dimension (H, W) -> (H, W, 1)
        img = np.expand_dims(img, axis=-1)
        
        return img
    
    def load_subject_scans(self, subject_dir: Path, label: int) -> Tuple[np.ndarray, int]:
        """
        Load all slices for a single subject
        
        Args:
            subject_dir: Directory containing subject's scan slices
            label: Class label (0=Healthy, 1=PD)
            
        Returns:
            Tuple of (scan_sequence, label)
            scan_sequence shape: (max_slices, H, W, 1)
        """
        # Try to find PNG files in nested structure (NTUA dataset)
        # Structure: Subject*/0.DAT/s1/*.png or Subject*/0.DAT/s2/*.png
        dat_dir = subject_dir / "0.DAT"
        slice_files = []
        
        if dat_dir.exists():
            # Look in s1 and s2 subfolders
            for subfolder in ["s1", "s2"]:
                subfolder_path = dat_dir / subfolder
                if subfolder_path.exists():
                    slice_files.extend(sorted(subfolder_path.glob("*.png")))
                    break  # Use first available subfolder
        
        # Fallback: Look for PNG files directly in subject directory
        if len(slice_files) == 0:
            slice_files = sorted(subject_dir.glob("*.png"))
        
        if len(slice_files) == 0:
            raise ValueError(f"No PNG files found in {subject_dir}")
        
        # Load and preprocess all slices
        slices = []
        for slice_file in slice_files:
            try:
                img = self.preprocess_image(slice_file)
                slices.append(img)
            except Exception as e:
                print(f"Warning: Failed to load {slice_file}: {e}")
                continue
        
        if len(slices) == 0:
            raise ValueError(f"No valid slices loaded from {subject_dir}")
        
        # Convert to numpy array
        slices = np.array(slices)
        
        # Pad or truncate to max_slices
        if len(slices) < self.max_slices:
            # Pad with zeros
            padding = np.zeros(
                (self.max_slices - len(slices), *self.target_size, 1),
                dtype=np.float32
            )
            slices = np.concatenate([slices, padding], axis=0)
        elif len(slices) > self.max_slices:
            # Take evenly spaced slices
            indices = np.linspace(0, len(slices) - 1, self.max_slices, dtype=int)
            slices = slices[indices]
        
        return slices, label
    
    def load_dataset(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Load entire dataset from Healthy and PD directories
        
        Returns:
            Tuple of (X, y, subject_ids)
            X shape: (num_subjects, max_slices, H, W, 1)
            y shape: (num_subjects,)
        """
        X_list = []
        y_list = []
        subject_ids = []
        
        print("Loading Healthy subjects...")
        healthy_subjects = sorted([d for d in self.healthy_dir.iterdir() if d.is_dir()])
        for subject_dir in tqdm(healthy_subjects, desc="Healthy"):
            try:
                scans, label = self.load_subject_scans(subject_dir, label=0)
                X_list.append(scans)
                y_list.append(label)
                subject_ids.append(f"Healthy_{subject_dir.name}")
            except Exception as e:
                print(f"Error loading {subject_dir}: {e}")
        
        print("Loading PD subjects...")
        pd_subjects = sorted([d for d in self.pd_dir.iterdir() if d.is_dir()])
        for subject_dir in tqdm(pd_subjects, desc="PD"):
            try:
                scans, label = self.load_subject_scans(subject_dir, label=1)
                X_list.append(scans)
                y_list.append(label)
                subject_ids.append(f"PD_{subject_dir.name}")
            except Exception as e:
                print(f"Error loading {subject_dir}: {e}")
        
        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        
        print(f"\nDataset loaded successfully!")
        print(f"Total subjects: {len(X)}")
        print(f"Healthy: {np.sum(y == 0)}, PD: {np.sum(y == 1)}")
        print(f"Shape: {X.shape}")
        
        return X, y, subject_ids
    
    def split_dataset(
        self,
        X: np.ndarray,
        y: np.ndarray,
        subject_ids: List[str],
        train_ratio: float = 0.7,
        val_ratio: float = 0.2,
        test_ratio: float = 0.1
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray, List[str]]]:
        """
        Split dataset into train, validation, and test sets
        
        Args:
            X: Feature array
            y: Label array
            subject_ids: List of subject identifiers
            train_ratio: Proportion for training set
            val_ratio: Proportion for validation set
            test_ratio: Proportion for test set
            
        Returns:
            Dictionary with 'train', 'val', 'test' keys containing (X, y, ids) tuples
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
            "Ratios must sum to 1.0"
        
        # First split: train vs (val + test)
        X_train, X_temp, y_train, y_temp, ids_train, ids_temp = train_test_split(
            X, y, subject_ids,
            test_size=(val_ratio + test_ratio),
            random_state=self.seed,
            stratify=y
        )
        
        # Second split: val vs test
        val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
        X_val, X_test, y_val, y_test, ids_val, ids_test = train_test_split(
            X_temp, y_temp, ids_temp,
            test_size=(1 - val_ratio_adjusted),
            random_state=self.seed,
            stratify=y_temp
        )
        
        print(f"\nDataset split:")
        print(f"Train: {len(X_train)} samples (Healthy: {np.sum(y_train == 0)}, PD: {np.sum(y_train == 1)})")
        print(f"Val:   {len(X_val)} samples (Healthy: {np.sum(y_val == 0)}, PD: {np.sum(y_val == 1)})")
        print(f"Test:  {len(X_test)} samples (Healthy: {np.sum(y_test == 0)}, PD: {np.sum(y_test == 1)})")
        
        return {
            'train': (X_train, y_train, ids_train),
            'val': (X_val, y_val, ids_val),
            'test': (X_test, y_test, ids_test)
        }
    
    def save_preprocessed_data(
        self,
        data_splits: Dict[str, Tuple[np.ndarray, np.ndarray, List[str]]],
        output_dir: str
    ):
        """
        Save preprocessed data to disk
        
        Args:
            data_splits: Dictionary with train/val/test splits
            output_dir: Directory to save preprocessed data
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for split_name, (X, y, ids) in data_splits.items():
            np.save(output_path / f"{split_name}_X.npy", X)
            np.save(output_path / f"{split_name}_y.npy", y)
            
            with open(output_path / f"{split_name}_ids.json", 'w') as f:
                json.dump(ids, f, indent=2)
        
        # Save metadata
        metadata = {
            'target_size': self.target_size,
            'max_slices': self.max_slices,
            'num_classes': 2,
            'class_names': ['Healthy', 'Parkinson'],
            'seed': self.seed
        }
        
        with open(output_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nPreprocessed data saved to: {output_path}")


def main():
    """Main preprocessing script"""
    parser = argparse.ArgumentParser(description='Preprocess DaT scan dataset for training')
    parser.add_argument('--input_dir', type=str, 
                       default='/home/hari/Downloads/parkinson/ntua-parkinson-dataset',
                       help='Input directory containing PD Patients and Non PD Patients folders')
    parser.add_argument('--output_dir', type=str,
                       default='/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed_ntua',
                       help='Output directory for preprocessed data')
    parser.add_argument('--target_size', type=int, nargs=2, default=[128, 128],
                       help='Target size for images (height width)')
    parser.add_argument('--max_slices', type=int, default=16,
                       help='Maximum number of slices per scan')
    
    args = parser.parse_args()
    
    # Configuration
    DATA_DIR = args.input_dir
    OUTPUT_DIR = args.output_dir
    TARGET_SIZE = tuple(args.target_size)
    MAX_SLICES = args.max_slices
    
    print(f"Input directory: {DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Initialize preprocessor
    print("\nInitializing DaT dataset preprocessor...")
    preprocessor = DaTDatasetPreprocessor(
        data_dir=DATA_DIR,
        target_size=TARGET_SIZE,
        max_slices=MAX_SLICES
    )
    
    # Load dataset
    print("\nLoading dataset...")
    X, y, subject_ids = preprocessor.load_dataset()
    
    # Split dataset
    print("\nSplitting dataset...")
    data_splits = preprocessor.split_dataset(
        X, y, subject_ids,
        train_ratio=0.7,
        val_ratio=0.2,
        test_ratio=0.1
    )
    
    # Save preprocessed data
    print("\nSaving preprocessed data...")
    preprocessor.save_preprocessed_data(data_splits, OUTPUT_DIR)
    
    print("\n✅ Preprocessing complete!")


if __name__ == "__main__":
    main()
