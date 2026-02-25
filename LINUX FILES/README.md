# Cobblemon Transporter - Linux Setup

This folder contains Linux-specific files to run the Cobblemon Transporter application on Linux.

## Prerequisites

- Linux distribution (Ubuntu 20.04+, Fedora 30+, etc.)
- Python 3.8 or higher (install via package manager: `sudo apt install python3 python3-venv` on Ubuntu)
- .NET 9.0 runtime (install via Microsoft repository or package manager)

## Setup Instructions

1. Copy the contents of this `LINUX FILES` folder into the main project directory (where `pokemonpc.py` is located).

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

## .NET Installation on Linux

For Ubuntu/Debian:
```bash
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-runtime-9.0
```

For other distributions, see: https://learn.microsoft.com/en-us/dotnet/core/install/linux

## Troubleshooting

- If you get permission errors, make the scripts executable: `chmod +x install.sh start.sh`
- If tkinter doesn't work, install python3-tk: `sudo apt install python3-tk` (Ubuntu/Debian)
- The application uses .NET DLLs for data conversion, so .NET 9.0 runtime is required.
- For GUI issues, ensure you have a desktop environment with X11 support.

## Notes

- This application is a Pokémon data management tool for the Cobblemon Minecraft mod.
- The Linux version uses native .NET DLLs instead of Windows executables.
- All features should work identically to the Windows version.</content>