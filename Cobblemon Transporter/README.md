## Cobblemon NBT Parser

### Setup (Windows)
- Create/install the venv + dependencies:
  - Run `install.bat`
- Start the app:
  - Run `start.bat`

### Fixing “wrong venv” in Cursor/VS Code
This repo ships a workspace setting that pins Python to the project venv:
- `.vscode/settings.json` -> `venv\Scripts\python.exe`

If you still see missing imports under `modules/`, reload the window and ensure the selected interpreter matches the above path.


