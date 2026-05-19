@echo off
setlocal enabledelayedexpansion
echo --- Starting Audio/OBD Environment Installation (Windows) ---

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install it from python.org before continuing.
    pause
    exit /b 1
)

:: 2. Check if requirements.txt exists
if not exist "..\requirements.txt" (
    echo ERROR: requirements.txt not found in parent directory.
    pause
    exit /b 1
)

:: 3. Create virtual environment
if not exist "..\.venv" (
    echo Creating virtual environment ..\.venv...
    python -m venv ..\.venv
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

:: 4. Activate and install dependencies
echo Activating virtual environment and installing dependencies...
call ..\.venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo ERROR: Failed to upgrade pip.
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r ..\requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo --- Installation completed successfully! ---
echo To activate the environment later, run: ..\.venv\Scripts\activate
echo.
pause