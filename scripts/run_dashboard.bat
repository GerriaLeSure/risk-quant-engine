@echo off
REM Run Streamlit Dashboard for Risk MC Engine (Windows)

echo.
echo 🚀 Starting Enterprise Risk Quantification Dashboard...
echo.

REM Check if streamlit is installed
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit is not installed
    echo    Install with: pip install streamlit
    exit /b 1
)

REM Navigate to project root
cd /d %~dp0\..

REM Check if dashboard file exists
if not exist "src\risk_mc_dashboard.py" (
    echo ❌ Dashboard file not found: src\risk_mc_dashboard.py
    exit /b 1
)

echo ✓ Dashboard found
echo ✓ Launching on http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Run Streamlit
streamlit run src\risk_mc_dashboard.py ^
    --server.port=8501 ^
    --server.address=localhost ^
    --browser.gatherUsageStats=false
