import cv2
import numpy as np

def fix_image_preprocessing(image_path):
    # This simulates what we should do to user photos
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None: return None
    
    # Apply Otsu's thresholding to remove shadows/grey background
    # Background usually becomes white, ink becomes black
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Back to RGB so ResNet accepts it
    thresh_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    
    # Resize to 224x224
    resized = cv2.resize(thresh_rgb, (224, 224))
    
    # Normalize
    normalized = resized.astype(np.float32) / 255.0
    return np.expand_dims(normalized, axis=0)

