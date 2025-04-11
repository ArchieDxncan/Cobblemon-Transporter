@echo off
echo Installing required Python packages...

:: Install nbtlib
python -m pip install nbtlib

:: Install requests
python -m pip install requests

:: Install Pillow (for image handling in pokemonpc.py)
python -m pip install pillow

:: Install tkinter (usually comes with Python, but just in case)
python -m pip install tk

python -m pip install tkinterdnd2

echo All dependencies installed successfully.
pause