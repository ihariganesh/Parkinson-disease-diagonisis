#!/bin/bash
# Setup and train the speech analysis model for Parkinson's disease detection

echo "=== Speech Analysis Model Setup ==="
echo "Setting up the environment and training the CNN+LSTM model"
echo

# Navigate to ml-models directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo

# Check if the CSV file exists
if [ ! -f "pd_speech_features.csv" ]; then
    echo "Error: pd_speech_features.csv not found in current directory"
    echo "Please ensure the speech features dataset is in the ml-models directory"
    exit 1
fi

echo "Found speech features dataset: pd_speech_features.csv"
echo "Dataset info:"
echo "  Rows: $(tail -n +2 pd_speech_features.csv | wc -l)"
echo "  Columns: $(head -1 pd_speech_features.csv | tr ',' '\n' | wc -l)"
echo

# Install dependencies
echo "Installing Python dependencies..."
echo

if [ -f "requirements_speech.txt" ]; then
    python3 -m pip install -r requirements_speech.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
else
    echo "Installing core dependencies manually..."
    python3 -m pip install tensorflow==2.13.0 numpy==1.24.3 pandas==2.0.3 scikit-learn==1.3.0 scipy==1.11.1 librosa==0.10.1 soundfile==0.12.1 praat-parselmouth==0.4.3
fi

echo "Dependencies installed successfully!"
echo

# Create models directory
mkdir -p models/speech
echo "Created models/speech directory"
echo

# Train the model
echo "Starting model training..."
echo "This may take 15-30 minutes depending on your hardware..."
echo

python3 train_speech_model.py --csv-path pd_speech_features.csv --epochs 50 --models-dir models/speech

if [ $? -eq 0 ]; then
    echo
    echo "=== Training Complete! ==="
    echo
    echo "Speech analysis model has been trained successfully!"
    echo "Model files are saved in: models/speech/"
    echo
    echo "Next steps:"
    echo "1. Start the backend server: cd ../backend && python -m uvicorn app.main:app --reload"
    echo "2. Test the speech analysis API endpoint: /api/v1/analysis/speech/analyze"
    echo "3. Use the frontend speech analysis page: http://localhost:5173/speech"
    echo
    echo "The speech analysis service is now ready for use!"
else
    echo
    echo "=== Training Failed ==="
    echo "Please check the error messages above and try again."
    echo "Common issues:"
    echo "1. Insufficient memory (requires ~4GB RAM)"
    echo "2. Missing dependencies"
    echo "3. Corrupted CSV file"
    exit 1
fi