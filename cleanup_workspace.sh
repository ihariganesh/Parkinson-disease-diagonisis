#!/bin/bash

echo "🧹 Cleaning up workspace for GitHub push..."
echo "============================================"

cd /home/hari/Downloads/parkinson/parkinson-app

# Remove Python cache files
echo "📦 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type f -name "*.log" -delete 2>/dev/null

# Remove Node modules (will be reinstalled)
echo "📦 Removing node_modules..."
rm -rf frontend/node_modules 2>/dev/null

# Remove virtual environment
echo "🐍 Removing virtual environment..."
rm -rf ml_env 2>/dev/null

# Remove uploads
echo "📁 Removing uploads directory..."
rm -rf uploads 2>/dev/null

# Remove temporary files
echo "🗑️  Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null
find . -type f -name "*~" -delete 2>/dev/null
find . -type f -name ".DS_Store" -delete 2>/dev/null

# Remove training output logs
echo "📝 Removing training logs..."
rm -f training_*.log 2>/dev/null

# Remove large dataset directories (keep structure, remove data)
echo "📊 Cleaning dataset directories..."
# Note: Keeping the structure but removing large files

# Remove preprocessed data files (too large for GitHub)
echo "💾 Removing preprocessed data files..."
rm -f ml_models/dat_preprocessed/*.npy 2>/dev/null
rm -f ml_models/dat_preprocessed_ntua/*.npy 2>/dev/null

# Remove large model files (users will train their own)
echo "🤖 Removing trained model files..."
rm -f models/dat_scan/*.keras 2>/dev/null
rm -f models/dat_scan/*.h5 2>/dev/null

# Remove audio/image test files
echo "🎵 Removing test audio/image files..."
find . -type f \( -name "*.wav" -o -name "*.mp3" \) -delete 2>/dev/null
find . -path "*/uploads/*" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -delete 2>/dev/null

# Clean up NTUA dataset clone (too large)
echo "📚 Removing NTUA dataset (users can clone separately)..."
rm -rf ntua-parkinson-dataset 2>/dev/null

# Remove DAT scan images
echo "🧠 Removing DAT scan images..."
rm -rf DAT 2>/dev/null

# Remove handwriting images
echo "✍️  Removing handwriting samples..."
rm -rf Healthy 2>/dev/null
rm -rf Parkinson 2>/dev/null
rm -rf handwritings 2>/dev/null

# Remove database files
echo "🗄️  Removing database files..."
rm -f backend/*.db 2>/dev/null
rm -f backend/*.sqlite 2>/dev/null

# Create empty placeholder files for important directories
echo "📝 Creating placeholder files..."
mkdir -p uploads/handwriting uploads/dat_scans uploads/voice
echo "# Upload directory for handwriting samples" > uploads/handwriting/.gitkeep
echo "# Upload directory for DaT scans" > uploads/dat_scans/.gitkeep
echo "# Upload directory for voice recordings" > uploads/voice/.gitkeep

mkdir -p models/dat_scan models/speech
echo "# Trained DaT scan models will be saved here" > models/dat_scan/README.md
echo "# Trained speech analysis models will be saved here" > models/speech/README.md

mkdir -p ml_models/dat_preprocessed ml_models/dat_preprocessed_ntua
echo "# Preprocessed DaT scan data" > ml_models/dat_preprocessed/README.md
echo "# Preprocessed NTUA dataset" > ml_models/dat_preprocessed_ntua/README.md

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Repository size after cleanup:"
du -sh .
echo ""
echo "📝 Files remaining:"
find . -type f | wc -l
echo ""
