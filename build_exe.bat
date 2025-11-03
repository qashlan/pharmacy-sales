@echo off
REM Build script for Pharmacy Sales Analytics Windows Executable
REM This script must be run on Windows with Python installed

echo ========================================
echo  Pharmacy Sales Analytics - Build
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if exist build_venv (
    echo Removing existing build_venv...
    rmdir /s /q build_venv
)
python -m venv build_venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call build_venv\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing build dependencies...
pip install -r build_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 5: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 6: Building executable with PyInstaller...
pyinstaller pharmacy_app.spec --clean
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo The executable is located in: dist\PharmacySalesAnalytics\
echo.
echo To run the application:
echo 1. Copy the entire "PharmacySalesAnalytics" folder to any Windows PC
echo 2. Double-click PharmacySalesAnalytics.exe
echo.
echo The dashboard will automatically open in your browser.
echo.
echo Press any key to exit...
pause >nul



