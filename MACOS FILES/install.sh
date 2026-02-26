#!/bin/bash

echo "Setting up Python virtual environment and installing dependencies for macOS..."

# Detect official python.org installation (required for proper Tk support)
PYTHON_FRAMEWORK_PATH="/Library/Frameworks/Python.framework/Versions"

if [ -d "$PYTHON_FRAMEWORK_PATH" ]; then
    PYTHON_BIN=$(ls -d $PYTHON_FRAMEWORK_PATH/3.* 2>/dev/null | sort -V | tail -n 1)/bin/python3
else
    PYTHON_BIN=""
fi

if [ -z "$PYTHON_BIN" ] || [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Official python.org Python not found."
    echo "Please install Python from: https://www.python.org/downloads/macos/"
    echo "Download the 'macOS 64-bit universal2 installer'."
    exit 1
fi

echo "Using Python from: $PYTHON_BIN"
echo "Python 3 found: $($PYTHON_BIN --version)"

# Verify Tk version
TK_VERSION=$($PYTHON_BIN -c "import tkinter; print(tkinter.TkVersion)")
echo "Detected Tk version: $TK_VERSION"

if [[ "$TK_VERSION" < "8.6" ]]; then
    echo "Error: Tk version is too old (must be 8.6+)."
    echo "Reinstall Python from python.org."
    exit 1
fi

# Check if .NET is available
if ! command -v dotnet &> /dev/null; then
    echo "Warning: .NET runtime not found."
    echo "Please install .NET 9.0 SDK using Homebrew: brew install --cask dotnet-sdk"
    echo "Or download from: https://dotnet.microsoft.com/download"
    echo "Continuing anyway, but importing and exporting to Pokémon will not work without .NET..."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_BIN" -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "Installation completed successfully!"
    echo "Run './start.sh' to launch the application."
else
    echo ""
    echo "Error: Failed to install dependencies."
    exit 1
fi</content>