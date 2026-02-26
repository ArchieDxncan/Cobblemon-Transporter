#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run './install.sh' first to set up the environment."
    exit 1
fi

VENV_PYTHON="venv/bin/python"

# Ensure venv python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python not found inside virtual environment."
    echo "Please delete 'venv' and run './install.sh' again."
    exit 1
fi

# Verify Tk version (macOS safety check)
TK_VERSION=$($VENV_PYTHON -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)

if [ -z "$TK_VERSION" ]; then
    echo "Error: Tkinter not available in this environment."
    echo "Re-run './install.sh'."
    exit 1
fi

if [[ "$TK_VERSION" < "8.6" ]]; then
    echo "Error: Tk version is too old ($TK_VERSION)."
    echo "Python was not installed from python.org."
    echo "Please reinstall properly and run './install.sh' again."
    exit 1
fi

# Check if pokemonpc.py exists
if [ ! -f "pokemonpc.py" ]; then
    echo "Error: pokemonpc.py not found in current directory."
    exit 1
fi

echo "Starting Cobblemon Transporter..."
echo "Using Python: $($VENV_PYTHON --version)"
echo "Tk Version: $TK_VERSION"
echo ""

# Run the application using venv interpreter directly
"$VENV_PYTHON" pokemonpc.py