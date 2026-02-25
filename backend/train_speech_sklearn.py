import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import os

print("Loading data...")
try:
    df = pd.read_csv('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/ml-models/pd_speech_features.csv', header=1)
    if 'class' not in df.columns:
        df = pd.read_csv('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/ml-models/pd_speech_features.csv')
except Exception as e:
    df = pd.read_csv('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/ml-models/pd_speech_features.csv')

print(f"Dataset shape: {df.shape}")

# Features and target
y = df['class'].values
X = df.drop(['id', 'class'], axis=1, errors='ignore').values

print(f"X shape: {X.shape}, expected around 753-754 features")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_scaled, y)
print(f"Accuracy: {rf.score(X_scaled, y):.4f}")

out_dir = Path('/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/models/speech')
out_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(rf, out_dir / 'speech_rf_model.pkl')
joblib.dump(scaler, out_dir / 'speech_rf_scaler.pkl')

print("Models saved successfully to models/speech/")
