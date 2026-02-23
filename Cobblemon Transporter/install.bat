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
if errorlevel 1 (
    echo Error: Failed to install nbtlib.
    pause
    exit /b 1
)

:: Install requests
python -m pip install requests
if errorlevel 1 (
    echo Error: Failed to install requests.
    pause
    exit /b 1
)

:: Install Pillow (for image handling in pokemonpc.py)
python -m pip install pillow
if errorlevel 1 (
    echo Error: Failed to install Pillow.
    pause
    exit /b 1
)

:: Install tkinterdnd2
python -m pip install tkinterdnd2
if errorlevel 1 (
    echo Error: Failed to install tkinterdnd2.
    pause
    exit /b 1
)

:: Verify installations
echo Verifying installations...
python -c "import nbtlib; print('nbtlib installed successfully')"
if errorlevel 1 (
    echo Error: nbtlib verification failed.
    pause
    exit /b 1
)

python -c "import requests; print('requests installed successfully')"
if errorlevel 1 (
    echo Error: requests verification failed.
    pause
    exit /b 1
)

python -c "import PIL; print('Pillow installed successfully')"
if errorlevel 1 (
    echo Error: Pillow verification failed.
    pause
    exit /b 1
)

python -c "import tkinterdnd2; print('tkinterdnd2 installed successfully')"
if errorlevel 1 (
    echo Error: tkinterdnd2 verification failed.
    pause
    exit /b 1
)

echo All dependencies installed successfully!
pause



