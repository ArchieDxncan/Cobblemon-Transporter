#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run './install.sh' first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if pokemonpc.py exists
if [ ! -f "pokemonpc.py" ]; then
    echo "Error: pokemonpc.py not found in current directory."
    exit 1
fi

# Run the application
echo "Starting Cobblemon Transporter..."
python3 pokemonpc.py

# Deactivate virtual environment when done
deactivate</content>