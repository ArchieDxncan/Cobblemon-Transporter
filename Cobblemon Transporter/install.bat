@echo off
echo Setting up Python virtual environment and installing dependencies...

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required packages
echo Installing required Python packages...

:: Install nbtlib
python -m pip install nbtlib

:: Install requests
python -m pip install requests

:: Install Pillow (for image handling in pokemonpc.py)
python -m pip install pillow

:: Install tkinter (usually comes with Python, but just in case)
python -m pip install tk

:: Install tkinterdnd2
python -m pip install tkinterdnd2
pause



