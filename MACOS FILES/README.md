# Cobblemon Transporter - macOS Setup

This folder contains macOS-specific files to run the Cobblemon Transporter application on macOS.

## Prerequisites

- macOS (tested on macOS 12+)
- Python 3.8 or higher (install via Homebrew: `brew install python`)
- .NET 9.0 runtime (install via Homebrew: `brew install --cask dotnet-sdk`)

## Setup Instructions

1. Copy the contents of this `MACOS FILES` folder into the main project directory (where `pokemonpc.py` is located).

2. Open Terminal and navigate to the project directory.

3. Run the installation script:
   ```bash
   ./install.sh
   ```

4. After installation completes, run the application:
   ```bash
   ./start.sh
   ```

## What the Scripts Do

- `install.sh`: Creates a Python virtual environment and installs all required dependencies from `requirements.txt`.
- `start.sh`: Activates the virtual environment and launches the Cobblemon Transporter GUI application.

## Troubleshooting

- If you get permission errors, make the scripts executable: `chmod +x install.sh start.sh`
- If tkinter doesn't work, ensure Python was installed with tkinter support (Homebrew's python includes it).
- The application uses .NET DLLs for data conversion, so .NET 9.0 runtime is required.
- If you encounter issues with the GUI, try running from a different terminal or check that XQuartz is installed for GUI apps.

## Notes

- This application is a Pokémon data management tool for the Cobblemon Minecraft mod.
- The macOS version uses native .NET DLLs instead of Windows executables.
- All features should work identically to the Windows version.</content>