#!/bin/bash

# Enterprise Risk Quantification & Analytics Engine - Run Script

set -e

echo "🎯 Enterprise Risk Quantification & Analytics Engine"
echo "======================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.9 or higher and try again."
    exit 1
fi

echo "✓ Python 3 detected: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Run tests (optional)
if [ "$1" == "--test" ]; then
    echo ""
    echo "🧪 Running tests..."
    pytest tests/ -v
    echo ""
fi

# Run the application
echo ""
echo "🚀 Starting the application..."
echo ""
echo "======================================================"
echo "The dashboard will open in your browser at:"
echo "http://localhost:8501"
echo "======================================================"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run src/dashboard.py

# Deactivate virtual environment on exit
deactivate
