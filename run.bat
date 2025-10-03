@echo off
REM Enterprise Risk Quantification & Analytics Engine - Run Script (Windows)

echo.
echo 🎯 Enterprise Risk Quantification ^& Analytics Engine
echo ======================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python 3 is not installed.
    echo Please install Python 3.9 or higher and try again.
    exit /b 1
)

echo ✓ Python detected
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo ✓ Dependencies installed

REM Run tests (optional)
if "%1"=="--test" (
    echo.
    echo 🧪 Running tests...
    pytest tests/ -v
    echo.
)

REM Run the application
echo.
echo 🚀 Starting the application...
echo.
echo ======================================================
echo The dashboard will open in your browser at:
echo http://localhost:8501
echo ======================================================
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run src/dashboard.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
