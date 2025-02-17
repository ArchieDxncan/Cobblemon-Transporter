@echo off
echo Installing required Python packages...

:: Install nbtlib
pip install nbtlib

:: Install requests
pip install requests

:: Install Pillow (for image handling in pokemonpc.py)
pip install pillow

:: Install tkinter (usually comes with Python, but just in case)
pip install tk

echo All dependencies installed successfully.
pause