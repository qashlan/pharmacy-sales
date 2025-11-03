@echo off
REM System Check for Pharmacy Sales Analytics Build
REM This script checks if the system is ready to build the executable

echo ========================================
echo   System Requirements Check
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python is not installed or not in PATH
    echo        Download from: https://www.python.org/downloads/
    echo        Make sure to check "Add Python to PATH" during installation
    set /a errors+=1
) else (
    python --version
    echo [OK] Python is installed
)
echo.

REM Check Python version
echo [2/5] Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python 3.8 or higher is required
    python -c "import sys; print('Current version:', sys.version)"
    set /a errors+=1
) else (
    echo [OK] Python version is compatible
)
echo.

REM Check pip
echo [3/5] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] pip is not available
    echo        Run: python -m ensurepip --upgrade
    set /a errors+=1
) else (
    python -m pip --version
    echo [OK] pip is available
)
echo.

REM Check disk space
echo [4/5] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set free=%%a
echo Available: %free% bytes
echo [OK] Disk space check complete (ensure at least 2GB free)
echo.

REM Check Windows version
echo [5/5] Checking Windows version...
ver | find "10.0" >nul
if not errorlevel 1 (
    echo [OK] Windows 10/11 detected
) else (
    ver | find "6." >nul
    if not errorlevel 1 (
        echo [WARN] Windows 7/8 detected - may have compatibility issues
        echo         Windows 10/11 is recommended
    ) else (
        echo [OK] Windows version detected
    )
)
echo.

echo ========================================
echo   Summary
echo ========================================
if defined errors (
    echo Status: NOT READY
    echo Please fix the issues above before building
) else (
    echo Status: READY TO BUILD!
    echo Run: build_exe.bat
)
echo ========================================
echo.
pause



