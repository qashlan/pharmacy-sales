#!/bin/bash
# Clear Python cache files to ensure code changes are loaded

echo "🧹 Clearing Python cache files..."

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null

echo "✅ Cache cleared successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Restart the Streamlit app if it's running"
echo "2. Run: streamlit run dashboard.py"
echo ""

