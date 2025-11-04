#!/bin/bash
# Restart Streamlit with Session Fix Applied

echo "======================================"
echo "🔄 Restarting Dashboard with Session Fix"
echo "======================================"

cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales

# Kill all existing Streamlit processes
echo "1. Stopping all old Streamlit processes..."
pkill -9 -f "streamlit run dashboard.py"
sleep 2

# Verify all stopped
if ps aux | grep -v grep | grep streamlit > /dev/null; then
    echo "⚠️  Warning: Some Streamlit processes still running"
else
    echo "✅ All old processes stopped"
fi

# Clear Python cache
echo ""
echo "2. Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ Cache cleared"

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Start Streamlit
echo ""
echo "4. Starting Streamlit with updated code..."
echo ""
echo "======================================"
echo "🚀 Starting Dashboard..."
echo "======================================"
echo ""

streamlit run dashboard.py

# Note: This will run in foreground. Press Ctrl+C to stop.




