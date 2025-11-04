# Environment Configuration for Parkinson's Detection App

# Python Environment
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/ml-models:$(pwd)/backend"

# Virtual Environment Activation
source venv/bin/activate

# Optional: Disable TensorFlow warnings
export TF_CPP_MIN_LOG_LEVEL=2
export TF_ENABLE_ONEDNN_OPTS=0

echo "✅ Environment configured for Parkinson's Detection App"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python path: $PYTHONPATH"
echo "🧠 TensorFlow warnings suppressed"
