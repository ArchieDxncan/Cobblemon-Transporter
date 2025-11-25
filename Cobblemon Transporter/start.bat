@echo off
:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Run the application
python pokemonpc.py

:: Keep window open if there's an error
if errorlevel 1 (
    pause
)