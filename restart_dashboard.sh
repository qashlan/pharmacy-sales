#!/bin/bash
# Quick fix script to clear cache and restart dashboard

echo "🔄 Clearing Python cache..."
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales

# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove all .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "✓ Cache cleared!"
echo ""
echo "📊 Starting dashboard..."
echo "Note: Stop with Ctrl+C when needed"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run streamlit
streamlit run dashboard.py

