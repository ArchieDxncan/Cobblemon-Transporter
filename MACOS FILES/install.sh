#!/bin/bash

echo "Setting up Python virtual environment and installing dependencies for macOS..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 using Homebrew: brew install python"
    echo "Or download from: https://www.python.org/downloads/"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Check if .NET is available
if ! command -v dotnet &> /dev/null; then
    echo "Warning: .NET runtime not found."
    echo "Please install .NET 9.0 SDK using Homebrew: brew install --cask dotnet-sdk"
    echo "Or download from: https://dotnet.microsoft.com/download"
    echo "Continuing anyway, but the app may not work without .NET..."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
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