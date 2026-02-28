import sys
sys.path.append('backend')
from ml_enhanced_analyzer import get_analyzer
import cv2
import numpy as np

# Create transparent image (white/transparent bg, black ink)
# BGRA: transparent is (0,0,0,0). Let's make a solid black line.
img = np.zeros((200, 200, 4), dtype=np.uint8)
# black background, fully transparent
# ink: black, fully opaque
cv2.line(img, (50, 50), (150, 150), (0, 0, 0, 255), 3)

cv2.imwrite('test_transp.png', img)

analyzer = get_analyzer()
print("Analyzing transparent image with black ink:")
res = analyzer.analyze_handwriting('test_transp.png', 'spiral')
print(res.get('prediction_summary', {}).get('final_diagnosis'))
print(res.get('ensemble_prediction', {}).get('raw_prediction'))

# what if it's white ink on black background? (like a dark mode canvas)
img2 = np.zeros((200, 200, 3), dtype=np.uint8)
cv2.line(img2, (50, 50), (150, 150), (255, 255, 255), 3)
cv2.imwrite('test_dark.png', img2)
print("Analyzing dark mode image:")
res2 = analyzer.analyze_handwriting('test_dark.png', 'spiral')
print(res2.get('prediction_summary', {}).get('final_diagnosis'))
print(res2.get('ensemble_prediction', {}).get('raw_prediction'))
