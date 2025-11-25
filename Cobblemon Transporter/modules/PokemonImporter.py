import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

# Get the current script directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the pokemon directory path (root cobblemon folder)
pokemon_directory = os.path.join(current_directory, '..', 'cobblemon')

# Function to show a confirmation popup
#def confirm_import():
    #root = tk.Tk()
    #root.withdraw()  # Hide the main window
    #return messagebox.askyesno("Confirmation", "Do you want to import a Pokemon .pk9 file?")

# If the user clicks "No", exit the script
#if not confirm_import():
#    print("Import canceled.")
#    exit(0)

# Locate PB8ToJson.exe in the modules directory
pb8_to_json_directory = os.path.join(current_directory, 'PokemonImporter')
pb8_to_json_exe = os.path.join(pb8_to_json_directory, 'PB8ToJson.exe')

# Ensure the executable exists
if not os.path.isfile(pb8_to_json_exe):
    print(f"Error: {pb8_to_json_exe} not found.")
    exit(1)

# Open a file dialog to select multiple .pb8 files
root = tk.Tk()
root.withdraw()  # Hide the main window
pb8_files = filedialog.askopenfilenames(
    initialdir=pokemon_directory,
    title="Select Pokemon files",
    filetypes=((".pk* files", "*.pk9"), (".pa9 files", "*.pa9"), (".pb8 files", "*.pb8"), ("All files", "*.*"))
)

# Check if any files were selected
if not pb8_files:
    print("No files selected.")
    exit(0)

# Ensure the output directory exists
if not os.path.exists(pokemon_directory):
    os.makedirs(pokemon_directory)

# Loop through the selected files and run PB8ToJson.exe on each
for pb8_file in pb8_files:
    # Run the converter
    subprocess.run([pb8_to_json_exe, pb8_file])

print("Conversion completed.")