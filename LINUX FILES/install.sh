#!/bin/bash
echo "Setting up Python virtual environment and installing dependencies..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH."
    echo "Please install Python3 and try again."
    exit 1
fi

# Check if .NET is available
if ! command -v dotnet &> /dev/null; then
    echo "Warning: .NET runtime not found."
    echo "Please install .NET 9.0 runtime:"
    echo "  Ubuntu/Debian: Follow https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu"
    echo "  Fedora: sudo dnf install dotnet-runtime-9.0"
    echo "  Or download from: https://dotnet.microsoft.com/download"
    echo "Continuing anyway, but the app may not work without .NET..."
fi

# Install python3-tk if not available (for tkinter)
if ! dpkg -l | grep -q python3-tk; then
    echo "Installing python3-tk..."
    sudo apt update && sudo apt install python3-tk -y
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install python3-tk."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages
echo "Installing required Python packages..."

# Install nbtlib
python -m pip install nbtlib
if [ $? -ne 0 ]; then
    echo "Error: Failed to install nbtlib."
    exit 1
fi

# Install requests
python -m pip install requests
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requests."
    exit 1
fi

# Install Pillow (for image handling in pokemonpc.py)
python -m pip install pillow
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Pillow."
    exit 1
fi

# Install tkinterdnd2
python -m pip install tkinterdnd2
if [ $? -ne 0 ]; then
    echo "Error: Failed to install tkinterdnd2."
    exit 1
fi

# Verify installations
echo "Verifying installations..."
python -c "import nbtlib; print('nbtlib installed successfully')"
if [ $? -ne 0 ]; then
    echo "Error: nbtlib verification failed."
    exit 1
fi

python -c "import requests; print('requests installed successfully')"
if [ $? -ne 0 ]; then
    echo "Error: requests verification failed."
    exit 1
fi

python -c "import PIL; print('Pillow installed successfully')"
if [ $? -ne 0 ]; then
    echo "Error: Pillow verification failed."
    exit 1
fi

python -c "import tkinterdnd2; print('tkinterdnd2 installed successfully')"
if [ $? -ne 0 ]; then
    echo "Error: tkinterdnd2 verification failed."
    exit 1
fi

echo "All dependencies installed successfully!"