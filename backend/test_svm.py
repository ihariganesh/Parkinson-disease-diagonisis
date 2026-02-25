import joblib

try:
    spiral_svm = joblib.load('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/models/spiral_svm_model_svm.pkl')
    spiral_scaler = joblib.load('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/models/spiral_svm_model_scaler.pkl')
    print("Spiral SVM loaded:", spiral_svm)
    print("Scaler extracted features assumed:", spiral_scaler.n_features_in_)
except Exception as e:
    print("Error loading:", e)
