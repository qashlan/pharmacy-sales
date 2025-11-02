#!/bin/bash

# Pharmacy Sales Analytics - Startup Script

echo "🚀 Starting Pharmacy Sales Analytics Dashboard..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p data output reports charts

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting dashboard..."
echo "   Access the dashboard at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the dashboard
streamlit run dashboard.py

