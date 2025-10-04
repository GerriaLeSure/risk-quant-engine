#!/bin/bash

# Run Streamlit Dashboard for Risk MC Engine

echo "🚀 Starting Enterprise Risk Quantification Dashboard..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed"
    echo "   Install with: pip install streamlit"
    exit 1
fi

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Check if dashboard file exists
if [ ! -f "src/risk_mc_dashboard.py" ]; then
    echo "❌ Dashboard file not found: src/risk_mc_dashboard.py"
    exit 1
fi

echo "✓ Dashboard found"
echo "✓ Launching on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Run Streamlit
streamlit run src/risk_mc_dashboard.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false

