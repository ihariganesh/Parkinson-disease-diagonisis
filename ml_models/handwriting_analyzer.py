import os
import numpy as np  # type: ignore
import cv2  # type: ignore
from pathlib import Path
from typing import Tuple, Dict
import tensorflow as tf  # type: ignore
from tensorflow import keras  # type: ignore
layers = tf.keras.layers  # type: ignore
import joblib  # type: ignore
from sklearn.svm import SVC  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from skimage.feature import hog  # type: ignore
import logging

logger = logging.getLogger(__name__)

class HandwritingAnalyzer:
    """
    Handwriting analyzer for Parkinson's disease detection
    Supports both CNN and SVM+HOG approaches
    """
    
    def __init__(self, model_path: str = None, use_cnn: bool = True):
        self.use_cnn = use_cnn
        self.model = None
        self.scaler = None
        self.model_path = model_path
        self.image_size = (128, 128)
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.warning("No pre-trained model found. Training required.")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for analysis"""
        try:
            # Read image
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize image
            image = cv2.resize(image, self.image_size)
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Apply Gaussian blur to reduce noise
            image = cv2.GaussianBlur(image, (3, 3), 0)
            
            # Enhance contrast
            image = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(
                (image * 255).astype(np.uint8)
            ).astype(np.float32) / 255.0
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise
    
    def extract_hog_features(self, image: np.ndarray) -> np.ndarray:
        """Extract HOG features from image"""
        features, _ = hog(
            image,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm='L2-Hys',
            visualize=True,
            feature_vector=True
        )
        return features
    
    def create_cnn_model(self) -> keras.Model:
        """Create CNN model for handwriting analysis"""
        model = keras.Sequential([
            layers.Input(shape=(*self.image_size, 1)),
            
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third convolutional block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Global average pooling
            layers.GlobalAveragePooling2D(),
            
            # Dense layers
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Output layer (binary classification)
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def train_model(self, dataset_path: str, drawing_type: str = "spiral"):
        """Train the model on the provided dataset"""
        logger.info(f"Training model for {drawing_type} drawings...")
        
        # Load dataset
        X_train, y_train, X_test, y_test = self._load_dataset(dataset_path, drawing_type)
        
        if self.use_cnn:
            # Train CNN model
            self.model = self.create_cnn_model()
            
            # Data augmentation
            datagen = keras.preprocessing.image.ImageDataGenerator(
                rotation_range=10,
                width_shift_range=0.1,
                height_shift_range=0.1,
                zoom_range=0.1,
                horizontal_flip=False,
                vertical_flip=False
            )
            
            # Callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7
                )
            ]
            
            # Train model
            history = self.model.fit(
                datagen.flow(X_train, y_train, batch_size=32),
                epochs=100,
                validation_data=(X_test, y_test),
                callbacks=callbacks,
                verbose=1
            )
            
        else:
            # Train SVM with HOG features
            logger.info("Extracting HOG features...")
            X_train_hog = np.array([self.extract_hog_features(img) for img in X_train])
            X_test_hog = np.array([self.extract_hog_features(img) for img in X_test])
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train_hog)
            X_test_scaled = self.scaler.transform(X_test_hog)
            
            # Train SVM
            self.model = SVC(kernel='rbf', probability=True, random_state=42)
            self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        if self.use_cnn:
            test_loss, test_acc, test_precision, test_recall = self.model.evaluate(X_test, y_test, verbose=0)
            logger.info(f"Test accuracy: {test_acc:.4f}")
            logger.info(f"Test precision: {test_precision:.4f}")
            logger.info(f"Test recall: {test_recall:.4f}")
        else:
            test_acc = self.model.score(X_test_scaled, y_test)
            logger.info(f"Test accuracy: {test_acc:.4f}")
        
        # Save model
        self.save_model()
        
        return self.model
    
    def _load_dataset(self, dataset_path: str, drawing_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load and preprocess dataset"""
        dataset_dir = Path(dataset_path) / drawing_type
        
        # Load training data
        train_healthy_dir = dataset_dir / "training" / "healthy"
        train_parkinson_dir = dataset_dir / "training" / "parkinson"
        
        # Load test data
        test_healthy_dir = dataset_dir / "testing" / "healthy"
        test_parkinson_dir = dataset_dir / "testing" / "parkinson"
        
        # Load images and labels
        X_train, y_train = self._load_images_from_dirs([train_healthy_dir, train_parkinson_dir], [0, 1])
        X_test, y_test = self._load_images_from_dirs([test_healthy_dir, test_parkinson_dir], [0, 1])
        
        logger.info(f"Loaded {len(X_train)} training samples and {len(X_test)} test samples")
        
        return X_train, y_train, X_test, y_test
    
    def _load_images_from_dirs(self, directories: list, labels: list) -> Tuple[np.ndarray, np.ndarray]:
        """Load images from directories"""
        images = []
        image_labels = []
        
        for dir_path, label in zip(directories, labels):
            if not dir_path.exists():
                logger.warning(f"Directory does not exist: {dir_path}")
                continue
                
            for img_path in dir_path.glob("*.png"):
                try:
                    image = self.preprocess_image(str(img_path))
                    images.append(image)
                    image_labels.append(label)
                except Exception as e:
                    logger.warning(f"Failed to load image {img_path}: {str(e)}")
        
        X = np.array(images)
        y = np.array(image_labels)
        
        # Reshape for CNN if needed
        if self.use_cnn and len(X.shape) == 3:
            X = X.reshape(-1, *self.image_size, 1)
        
        return X, y
    
    def analyze_handwriting(self, image_path: str) -> Dict:
        """Analyze handwriting sample and return prediction"""
        if self.model is None:
            raise ValueError("No model loaded. Please train or load a model first.")
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_path)
            
            if self.use_cnn:
                # CNN prediction
                image_batch = image.reshape(1, *self.image_size, 1)
                prediction_prob = self.model.predict(image_batch, verbose=0)[0][0]
                prediction = "parkinson" if prediction_prob > 0.5 else "healthy"
                confidence = float(prediction_prob if prediction_prob > 0.5 else 1 - prediction_prob)
                
            else:
                # SVM prediction
                features = self.extract_hog_features(image).reshape(1, -1)
                features_scaled = self.scaler.transform(features)
                prediction_prob = self.model.predict_proba(features_scaled)[0]
                prediction = "parkinson" if prediction_prob[1] > 0.5 else "healthy"
                confidence = float(max(prediction_prob))
            
            # Extract additional features for detailed analysis
            details = self._analyze_features(image)
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "details": details,
                "model_type": "CNN" if self.use_cnn else "SVM+HOG"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing handwriting: {str(e)}")
            raise
    
    def _analyze_features(self, image: np.ndarray) -> Dict:
        """Extract detailed features from image"""
        try:
            # Calculate tremor features
            edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Largest contour (main drawing)
                main_contour = max(contours, key=cv2.contourArea)
                
                # Smoothness measure
                arc_length = cv2.arcLength(main_contour, closed=False)
                area = cv2.contourArea(main_contour)
                smoothness = area / (arc_length + 1e-6) if arc_length > 0 else 0
                
                # Tremor frequency (roughness of contour)
                hull = cv2.convexHull(main_contour)
                hull_area = cv2.contourArea(hull)
                tremor_ratio = (hull_area - area) / (hull_area + 1e-6) if hull_area > 0 else 0
                
            else:
                smoothness = 0
                tremor_ratio = 0
            
            # Pressure variation (pixel intensity variation)
            pressure_variation = float(np.std(image))
            
            return {
                "smoothness": float(smoothness),
                "tremor_ratio": float(tremor_ratio),
                "pressure_variation": pressure_variation,
                "contour_count": len(contours)
            }
            
        except Exception as e:
            logger.warning(f"Error extracting detailed features: {str(e)}")
            return {}
    
    def save_model(self, path: str = None):
        """Save trained model"""
        if path is None:
            path = self.model_path or "models/handwriting_model"
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if self.use_cnn:
            self.model.save(f"{path}.h5")
        else:
            joblib.dump(self.model, f"{path}_svm.pkl")
            if self.scaler:
                joblib.dump(self.scaler, f"{path}_scaler.pkl")
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load pre-trained model"""
        try:
            if self.use_cnn:
                if os.path.exists(f"{path}.h5"):
                    self.model = keras.models.load_model(f"{path}.h5")
                else:
                    raise FileNotFoundError(f"CNN model not found: {path}.h5")
            else:
                if os.path.exists(f"{path}_svm.pkl"):
                    self.model = joblib.load(f"{path}_svm.pkl")
                    if os.path.exists(f"{path}_scaler.pkl"):
                        self.scaler = joblib.load(f"{path}_scaler.pkl")
                else:
                    raise FileNotFoundError(f"SVM model not found: {path}_svm.pkl")
            
            logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

# Global analyzer instance
_analyzer = None

def get_analyzer() -> HandwritingAnalyzer:
    """Get or create handwriting analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = HandwritingAnalyzer(
            model_path="models/handwriting_model",
            use_cnn=True
        )
    return _analyzer

def train_models_from_dataset(dataset_path: str):
    """Train models for both spiral and wave drawings"""
    for drawing_type in ["spiral", "wave"]:
        logger.info(f"Training model for {drawing_type}...")
        
        # Train CNN model
        cnn_analyzer = HandwritingAnalyzer(
            model_path=f"models/{drawing_type}_cnn_model",
            use_cnn=True
        )
        cnn_analyzer.train_model(dataset_path, drawing_type)
        
        # Train SVM model
        svm_analyzer = HandwritingAnalyzer(
            model_path=f"models/{drawing_type}_svm_model",
            use_cnn=False
        )
        svm_analyzer.train_model(dataset_path, drawing_type)
        
        logger.info(f"Completed training for {drawing_type}")

if __name__ == "__main__":
    # Train models if run as script
    dataset_path = "archive"
    train_models_from_dataset(dataset_path)