import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import subprocess
import hashlib
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import tkinterdnd2
import re
import sys
import time

# Constants
GRID_ROWS = 5
GRID_COLS = 6
BOX_SIZE = GRID_ROWS * GRID_COLS  # 30 slots per box
TOTAL_BOXES = 40  # Number of boxes per grid
COBBLEMON_FOLDER = "cobblemon"  # Path to the folder where Cobblemon JSON files are stored
SPRITES_FOLDER = "sprites/regular"  # Path to the folder where Pokémon sprites are stored
SHINY_SPRITES_FOLDER = "sprites/shiny"  # Path to the folder where Shiny Pokémon sprites are stored

# Color scheme
COLORS = {
    "primary": "#4F6F8F",         # Soft blue
    "secondary": "#C6D8E7",       # Light blue
    "accent": "#FFC857",          # Gold/yellow
    "background": "#F5F9FC",      # Very light blue
    "text": "#2B3A4A",            # Dark blue/grey
    "empty_slot": "#E8EFF5",      # Very light grey-blue
    "filled_slot": "#A9CCE8",     # Light blue for filled slots
    "shiny_slot": "#FFE6B3",      # Light gold for shiny Pokémon
    "button_hover": "#3A5573",    # Darker blue for hover
    "separator": "#D1DEE9",        # Light grey for separators
    "dropdown_hover": "#EAF0F6"   # Light blue for dropdown hover
}

def run_windows_exe(exe_path, args, *, check=True, capture_output=False, text=True):
    """
    Run a Windows .exe on Linux/macOS via wine, or directly on Windows.
    args: list of arguments (NOT including exe_path)
    """
    cmd = [exe_path] + list(args)

    # If we're on Linux/macOS, run via wine.
    if not sys.platform.startswith("win"):
        cmd = [
            "env",
            "WINEPREFIX=" + os.path.expanduser("~/.winepkhex"),
            "DOTNET_BUNDLE_EXTRACT_BASE_DIR=",
            "wine",
            exe_path,
        ] + list(args)

    # Use subprocess.run; caller decides whether to capture output.
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture_output,
        text=text
    )

def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return self.create_polygon(points, smooth=True, **kwargs)

# Add the method to the Canvas class
tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

class PokemonHomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cobblemon Transporter")
        self.root.geometry("1000x650")  # Set a better default window size
        self.root.configure(bg=COLORS["background"])
        
        # Apply a theme for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Using 'clam' as base theme
        
        # Configure ttk styles
        self.configure_styles()
        
        # Local storage for Pokémon data
        self.local_storage = [[None] * BOX_SIZE for _ in range(TOTAL_BOXES)]  # Multiple boxes
        
        # Current box indices
        self.current_local_box = 0
        
        # Track the currently selected Pokémon
        self.selected_pokemon = None
        
        # Create main container frame
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a header frame with logo
        self.create_header()
        
        # Create content frame that will hold the grids and panels
        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # UI Layout
        self.create_grids()
        self.create_navigation_buttons()

        # Detailed info panel
        self.create_details_panel()

        # Status bar at the bottom
        self.create_status_bar()

        # Menu Bar
        self.create_menu()

        # Load Pokémon data from JSON files in the "cobblemon" folder
        self.load_pokemon_data()

        # Set up drag-and-drop
        self.setup_drag_and_drop()
        self.setup_drag_drop_for_boxes()

    def configure_styles(self):
        """Configure ttk styles for the application."""
        # Configure the notebook style
        self.style.configure('TNotebook', background=COLORS["background"], borderwidth=0)
        self.style.configure('TNotebook.Tab', background=COLORS["secondary"], foreground=COLORS["text"],
                             padding=[10, 5], font=('Roboto', 9, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', COLORS["primary"])],
                       foreground=[('selected', 'white')])
        
        # Configure the frame style
        self.style.configure('TFrame', background=COLORS["background"])
        
        # Configure the label style
        self.style.configure('TLabel', background=COLORS["background"], foreground=COLORS["text"], font=('Roboto', 10))
        self.style.configure('Header.TLabel', font=('Roboto', 16, 'bold'), background=COLORS["background"])
        self.style.configure('BoxTitle.TLabel', font=('Roboto', 12, 'bold'), background=COLORS["background"])
        
        # Configure the button style
        self.style.configure('TButton', background=COLORS["primary"], foreground='white', font=('Roboto', 10, 'bold'),
                            padding=5, borderwidth=0)
        self.style.map('TButton', background=[('active', COLORS["button_hover"])])
        
        # Configure navigation button style
        self.style.configure('Nav.TButton', background=COLORS["secondary"], foreground=COLORS["text"], 
                            padding=5, width=3, font=('Roboto', 10, 'bold'))
        
        # Configure Pokemon button style - RED with white text
        self.style.configure('Pokemon.TButton', background="#E74C3C", foreground="white",
                            padding=8, font=('Roboto', 10, 'bold'))
        self.style.map('Pokemon.TButton', background=[('active', "#C0392B")])  # Darker red on hover
        
        # Configure showdown button style
        self.style.configure('Showdown.TButton', background="#4C6EF5", foreground="white",
                            padding=8, font=('Roboto', 10, 'bold'))
                            
        # Configure Cobblemon button style
        self.style.configure('Cobblemon.TButton', background="#66BB6A", foreground="white",
                            padding=8, font=('Roboto', 10, 'bold'))

    def create_header(self):
        """Create a header with logo and title."""
        header_frame = tk.Frame(self.main_frame, bg=COLORS["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Try to load a logo if available
        try:
            logo_path = "logo.png"  # Create a logo.png file and place it in your project directory
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((50, 50), Image.Resampling.NEAREST)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=logo_photo, bg=COLORS["background"])
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Application title
        title_label = ttk.Label(header_frame, text="Cobblemon Transporter", style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Version info
        version_label = ttk.Label(header_frame, text="GitHub - ArchieDxncan", foreground="#888888", background=COLORS["background"])
        version_label.pack(side=tk.RIGHT, padx=10)

    def setup_drag_and_drop(self):
        """Set up drag-and-drop functionality for .pk9 files."""
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Also set up drag and drop for the grid itself
        self.setup_drag_drop_for_grid()
        
    def setup_drag_drop_for_grid(self):
        """Set up drag and drop for JSON files directly onto the grid."""
        # Each button in the grid should accept drops
        for i, button in enumerate(self.local_buttons):
            button.drop_target_register(DND_FILES)
            button.dnd_bind('<<Drop>>', lambda e, idx=i: self.on_grid_drop(e, idx))
            
            # Get the canvas that contains the button
            canvas = button.master
            canvas.drop_target_register(DND_FILES)
            canvas.dnd_bind('<<Drop>>', lambda e, idx=i: self.on_grid_drop(e, idx))
    
    def on_grid_drop(self, event, slot_index):
        """Handle files dropped directly onto a specific slot in the box."""
        try:
            # Use regex to properly extract file paths including those with spaces
            file_paths = re.findall(r'\{.*?\}|\S+', event.data)
            
            # Remove surrounding braces from paths
            file_paths = [path.strip("{}") for path in file_paths]
            
            # Supported file extensions
            supported_extensions = {
                '.pk9', '.cb9', '.pa9', '.pb8', '.pk8', '.pk7', '.pb7', '.pk6', '.pk5', '.pk4', '.pk3', '.dat', '.json', '.pkm'
            }
            
            for file_path in file_paths:
                file_ext = os.path.splitext(file_path.lower())[1]
                
                if not os.path.exists(file_path):
                    messagebox.showwarning("File Not Found", f"Cannot find file: {file_path}")
                    continue
                
                # If it's a JSON file, handle it directly
                if file_ext == '.json':
                    self.place_json_in_slot(file_path, self.current_local_box, slot_index)
                # Otherwise convert it first
                elif file_ext in supported_extensions:
                    # Convert the file to JSON
                    if file_ext == '.dat':
                        self.process_dat_file(file_path)
                    else:
                        self.convert_file_to_json_at_slot(file_path, slot_index)
                else:
                    messagebox.showwarning(
                        "Unsupported File", 
                        f"{os.path.basename(file_path)} is not a supported file type."
                    )
            
            # Reload the Pokémon data to display changes
            self.load_pokemon_data()
            
        except Exception as e:
            error_msg = f"Error handling dropped files onto grid: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.update_status(f"Error: {error_msg}")
            print(f"Exception details: {e}")
    
    def place_json_in_slot(self, json_path, box_index, slot_index):
        """Place a JSON file directly into a specific slot."""
        try:
            # Check if the slot is already occupied
            if self.local_storage[box_index][slot_index] is not None:
                # Ask if the user wants to replace the Pokémon
                pokemon_name = self.local_storage[box_index][slot_index]['species'].capitalize()
                replace = messagebox.askyesno(
                    "Replace Pokémon", 
                    f"Slot {slot_index + 1} is already occupied by {pokemon_name}. Replace it?"
                )
                if not replace:
                    return False
            
            # Load the JSON data
            with open(json_path, 'r') as f:
                pokemon_data = json.load(f)
            
            # Update the box and slot information
            pokemon_data['box_number'] = box_index + 1  # 1-indexed for user clarity
            pokemon_data['slot_number'] = slot_index + 1  # 1-indexed for user clarity
            
            # If the JSON is not in the current folder, copy it there
            if not json_path.startswith(self.current_folder):
                # Create a new filename based on the Pokémon species and a timestamp
                species = pokemon_data.get('species', 'pokemon').lower()
                timestamp = int(time.time())
                new_filename = f"{species}_{timestamp}.json"
                new_path = os.path.join(self.current_folder, new_filename)
                
                # Copy the file to the current folder
                with open(new_path, 'w') as f:
                    json.dump(pokemon_data, f, indent=4)
                
                # Update the file path for future reference
                json_path = new_path
            else:
                # Save changes to the existing file
                with open(json_path, 'w') as f:
                    json.dump(pokemon_data, f, indent=4)
            
            # Update the local storage
            pokemon_data['file_path'] = json_path
            self.local_storage[box_index][slot_index] = pokemon_data
            
            self.update_status(f"Placed {pokemon_data['species']} in Box {box_index + 1}, Slot {slot_index + 1}")
            return True
            
        except Exception as e:
            error_msg = f"Error placing JSON in slot: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.update_status(f"Error: {error_msg}")
            print(f"Exception details: {e}")
            return False
    
    def convert_file_to_json_at_slot(self, file_path, slot_index):
        """Convert a file to JSON and place it in a specific slot."""
        # Get the current script directory
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Locate PB8ToJson.exe in the same directory as this script
        pb8_to_json_directory = os.path.join(current_directory, 'modules', 'PokemonImporter')
        pb8_to_json_exe = os.path.join(pb8_to_json_directory, 'PB8ToJson.exe')

        # Ensure the executable exists
        if not os.path.isfile(pb8_to_json_exe):
            self.update_status(f"Error: {pb8_to_json_exe} not found.")
            return
        
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.current_folder):
            os.makedirs(self.current_folder)
        
        # Run the executable with file path and output directory
        run_windows_exe(pb8_to_json_exe, [file_path, "--output", self.current_folder], check=False)
        
        # Find the newly created JSON file
        try:
            # Get the base name of the original file without extension
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Look for the corresponding JSON file
            json_file_path = None
            for file in os.listdir(self.current_folder):
                if file.startswith(base_name) and file.endswith(".json"):
                    json_file_path = os.path.join(self.current_folder, file)
                    break
            
            # If found, place it in the specified slot
            if json_file_path and os.path.exists(json_file_path):
                self.place_json_in_slot(json_file_path, self.current_local_box, slot_index)
        except Exception as e:
            print(f"Error finding converted JSON file: {e}")
            # Continue without placing if there's an error

    def on_drop(self, event):
        """Handle dropped files."""
        try:
            # Use regex to properly extract file paths including those with spaces.
            file_paths = re.findall(r'\{.*?\}|\S+', event.data)

            # Remove surrounding braces from paths like {C:\Some Folder\file.pk9}
            file_paths = [path.strip("{}") for path in file_paths]

            # Supported file extensions
            supported_extensions = {
                # Gen 9
                '.pk9', '.cb9', '.pa9',
                # Gen 8
                '.pb8', '.pk8', 
                # Gen 7
                '.pk7', '.pb7',
                # Gen 6
                '.pk6',
                # Gen 5
                '.pk5',
                # Gen 4
                '.pk4',
                # Gen 3
                '.pk3',
                # Other
                '.dat',
                '.pkm'
            }
            processed_count = 0
            error_count = 0

            for file_path in file_paths:
                file_ext = os.path.splitext(file_path.lower())[1]
                
                if not os.path.exists(file_path):
                    messagebox.showwarning("File Not Found", f"Cannot find file: {file_path}")
                    self.update_status(f"Error: File not found - {os.path.basename(file_path)}")
                    error_count += 1
                    continue
                    
                if file_ext == '.dat':
                    self.update_status(f"Processing DAT file: {os.path.basename(file_path)}")
                    self.process_dat_file(file_path)
                    processed_count += 1
                elif file_ext in supported_extensions:
                    self.update_status(f"Converting file: {os.path.basename(file_path)}")
                    self.convert_file_to_json(file_path)
                    processed_count += 1
                else:
                    messagebox.showwarning(
                        "Unsupported File", 
                        f"{os.path.basename(file_path)} is not a supported file type (.pk9, .cb9, .pa9, .pb8, .pk8, .dat, .pkm)."
                    )
                    self.update_status(f"Import failed: Unsupported file type - {os.path.basename(file_path)}")
                    error_count += 1

            # Final status update
            if processed_count > 0 and error_count == 0:
                self.update_status(f"Successfully processed {processed_count} file(s)")
            elif processed_count > 0 and error_count > 0:
                self.update_status(f"Processed {processed_count} file(s) with {error_count} error(s)")
            elif error_count > 0:
                self.update_status(f"Failed to process any files: {error_count} error(s)")
                
            # Reload the Pokémon data to display newly converted Pokémon
            self.load_pokemon_data()
                
        except Exception as e:
            error_msg = f"Error handling dropped files: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.update_status(f"Error: {error_msg}")
            print(f"Exception details: {e}")

    def process_dat_file(self, file_path):
        """Run CobblemonImporter.py on a dropped .dat file."""
        try:
            self.update_status(f"Processing DAT file: {os.path.basename(file_path)}")
            
            # Get the current script directory
            current_directory = os.path.dirname(os.path.abspath(__file__))
            parser_script = os.path.join(current_directory, "modules", "CobblemonImporter.py")
            
            # Check if CobblemonImporter.py exists
            if not os.path.exists(parser_script):
                messagebox.showerror("Error", f"Parser script not found at: {parser_script}")
                self.update_status("Error: Parser script not found")
                return
                
            # Run CobblemonImporter.py with the DAT file path as an argument
            # Add the --output argument to specify the current folder
            process = subprocess.run(
                [sys.executable, parser_script, "--cli", "--files", file_path, "--output", self.current_folder], 
                check=False,
                capture_output=True,
                text=True
            )
            
            # Check if the process executed successfully
            if process.returncode != 0:
                error_msg = f"Parser script returned error code {process.returncode}:\n{process.stderr}"
                messagebox.showerror("Error", error_msg)
                self.update_status(f"Error processing DAT file: {os.path.basename(file_path)}")
                print(f"Error output: {process.stderr}")
                return
                
            # Show output in console for debugging
            print(f"Parser output: {process.stdout}")
            
            # Get the list of newly created JSON files and update their box/slot
            self.update_json_files_box_slot()
            
            # Reload the Pokémon data to display the newly converted Pokémon
            self.load_pokemon_data()
            self.update_status(f"Successfully processed {os.path.basename(file_path)}")
        except Exception as e:
            error_msg = f"Failed to process DAT file: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.update_status(f"Error: {error_msg}")
            print(f"Exception details: {e}")
            
    def update_json_files_box_slot(self):
        """Update all JSON files in the current folder to use the current box if they don't have box info yet."""
        try:
            if not os.path.exists(self.current_folder):
                return
                
            # Get all existing Pokémon loaded in the storage to avoid duplicates
            used_slots = set()
            for box_idx in range(TOTAL_BOXES):
                for slot_idx in range(BOX_SIZE):
                    if self.local_storage[box_idx][slot_idx] is not None:
                        used_slots.add((box_idx + 1, slot_idx + 1))  # 1-indexed for consistency with JSON files
            
            # Get list of JSON files in the folder
            json_files = [f for f in os.listdir(self.current_folder) if f.endswith('.json')]
            files_updated = 0
            
            # Start from the current box for placement
            current_box = self.current_local_box
            current_slot = 0
            
            for json_file in json_files:
                json_path = os.path.join(self.current_folder, json_file)
                
                # Load the JSON data
                with open(json_path, 'r') as f:
                    pokemon_data = json.load(f)
                
                # Skip if this Pokémon already has box and slot assigned
                if 'box_number' in pokemon_data and 'slot_number' in pokemon_data:
                    box_slot = (pokemon_data['box_number'], pokemon_data['slot_number'])
                    if box_slot in used_slots:
                        continue
                
                # Find the next available slot
                while True:
                    if (current_box + 1, current_slot + 1) not in used_slots:
                        # Found an empty slot
                        pokemon_data['box_number'] = current_box + 1
                        pokemon_data['slot_number'] = current_slot + 1
                        
                        # Add this slot to used slots
                        used_slots.add((current_box + 1, current_slot + 1))
                        
                        # Save the updated JSON
                        with open(json_path, 'w') as f:
                            json.dump(pokemon_data, f, indent=4)
                            
                        files_updated += 1
                        break
                    
                    # Move to the next slot
                    current_slot += 1
                    if current_slot >= BOX_SIZE:
                        current_slot = 0
                        current_box = (current_box + 1) % TOTAL_BOXES
            
            if files_updated > 0:
                self.update_status(f"Updated {files_updated} Pokémon to be in the current box and folder")
        except Exception as e:
            print(f"Error updating JSON files box/slot: {e}")

    def convert_pk9_to_json(self, file_path):
        """Convert a .pk9 file to JSON using the PB8ToJson.py script."""
        try:
            subprocess.run(["python", "PokemonImporter.py", file_path], check=True)
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
    
    def convert_file_to_json(self, file_path):
        """Convert a file to JSON using the PB8ToJson.exe tool."""
        # Get the current script directory
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Locate PB8ToJson.exe in the same directory as this script
        pb8_to_json_directory = os.path.join(current_directory, 'modules', 'PokemonImporter')
        pb8_to_json_exe = os.path.join(pb8_to_json_directory, 'PB8ToJson.exe')

        # Ensure the executable exists
        if not os.path.isfile(pb8_to_json_exe):
            self.update_status(f"Error: {pb8_to_json_exe} not found.")
            return
        
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.current_folder):
            os.makedirs(self.current_folder)
        
        # Run the executable with file path and output directory
        run_windows_exe(pb8_to_json_exe, [file_path, "--output", self.current_folder], check=False)
        
        # Find the newly created JSON file and modify its box/slot information
        try:
            # Get the base name of the original file without extension
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Look for the corresponding JSON file
            json_file_path = None
            for file in os.listdir(self.current_folder):
                if file.startswith(base_name) and file.endswith(".json"):
                    json_file_path = os.path.join(self.current_folder, file)
                    break
                    
            # If found, update the box and slot information
            if json_file_path and os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    pokemon_data = json.load(f)
                
                # Find the first empty slot in the current box
                empty_slot = None
                for slot_idx in range(BOX_SIZE):
                    if self.local_storage[self.current_local_box][slot_idx] is None:
                        empty_slot = slot_idx
                        break
                
                # If empty slot found, update box and slot
                if empty_slot is not None:
                    pokemon_data['box_number'] = self.current_local_box + 1  # 1-indexed for user clarity
                    pokemon_data['slot_number'] = empty_slot + 1  # 1-indexed for user clarity
                    
                    # Save the updated JSON
                    with open(json_file_path, 'w') as f:
                        json.dump(pokemon_data, f, indent=4)
                    
                    self.update_status(f"Placed {os.path.basename(json_file_path)} in Box {self.current_local_box + 1}, Slot {empty_slot + 1}")
        except Exception as e:
            print(f"Error updating box/slot for converted file: {e}")
            # Continue without updating box/slot if there's an error
        
        self.load_pokemon_data()
        self.update_status("Conversion completed successfully")

    def create_grids(self):
        """Create a grid for local storage."""
        left_frame = tk.Frame(self.content_frame, bg=COLORS["background"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Box title with decorative elements and folder selector
        title_frame = tk.Frame(left_frame, bg=COLORS["background"])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Pokémon Storage", style="BoxTitle.TLabel").pack(side=tk.LEFT)
        
        # Add a folder selector dropdown
        self.current_folder = COBBLEMON_FOLDER
        self.folder_var = tk.StringVar(value=COBBLEMON_FOLDER)
        
        # Style the combobox
        self.style.configure("Folder.TCombobox", 
                           padding=5,
                           background=COLORS["secondary"],
                           fieldbackground=COLORS["background"])
        
        # Create and position the dropdown
        self.folder_dropdown = ttk.Combobox(title_frame, 
                                          textvariable=self.folder_var,
                                          style="Folder.TCombobox",
                                          state="readonly",
                                          width=15)
        self.folder_dropdown.pack(side=tk.RIGHT)
        
        # Populate the dropdown with available folders
        self.update_folder_dropdown()
        
        # Bind the dropdown selection event
        self.folder_dropdown.bind("<<ComboboxSelected>>", self.on_folder_selected)
        
        # Horizontal separator under the title
        separator = ttk.Separator(left_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Create a frame for the grid with a subtle border
        grid_frame = tk.Frame(left_frame, bg=COLORS["secondary"], padx=2, pady=2)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner frame for the grid buttons
        inner_grid_frame = tk.Frame(grid_frame, bg=COLORS["background"], padx=10, pady=10)
        inner_grid_frame.pack(fill=tk.BOTH, expand=True)
        
        self.local_buttons = []
        for i in range(BOX_SIZE):
            row = i // GRID_COLS
            col = i % GRID_COLS
            
            # Create a frame for each button to add padding and rounded corners
            btn_frame = tk.Frame(inner_grid_frame, bg=COLORS["background"], padx=1, pady=1)
            btn_frame.grid(row=row, column=col, padx=2, pady=2)
            
            # Create a canvas for rounded corners - make it larger to allow sprite overflow
            canvas = tk.Canvas(btn_frame, width=70, height=70, bg=COLORS["background"], 
                             highlightthickness=0, bd=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Draw rounded rectangle - will be updated when Pokémon is added
            canvas.create_rounded_rectangle(0, 0, 70, 70, radius=8, 
                                         fill=COLORS["empty_slot"], outline="")
            
            button = tk.Button(canvas, bg=COLORS["empty_slot"], relief=tk.FLAT, 
                             width=60, height=60, bd=0, highlightthickness=0)
            button.place(x=5, y=5, width=60, height=60)  # Center the button in the larger canvas
            button.bind("<Button-1>", lambda e, idx=i: self.show_pokemon_info(e, "local", idx))
            
            # Add hover effect
            button.bind("<Enter>", lambda e, btn=button, c=canvas: self.on_button_enter(e, btn, c))
            button.bind("<Leave>", lambda e, btn=button, c=canvas, idx=i: 
                      self.on_button_leave(e, btn, c, idx))
            
            self.local_buttons.append(button)

    def create_navigation_buttons(self):
        """Create navigation buttons for cycling between boxes."""
        # Find the left frame (parent of the grid)
        left_frame = self.local_buttons[0].master.master.master.master
        
        # Create a frame for navigation with background
        nav_bg_frame = tk.Frame(left_frame, bg=COLORS["secondary"], padx=2, pady=2, bd=1, relief=tk.SOLID)
        nav_bg_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Inner frame for nav buttons
        self.local_nav_frame = tk.Frame(nav_bg_frame, bg=COLORS["background"], padx=10, pady=8)
        self.local_nav_frame.pack(fill=tk.X)
        
        # Left navigation button
        prev_btn = ttk.Button(self.local_nav_frame, text="←", style="Nav.TButton", 
                            command=lambda: self.cycle_box("local", -1))
        prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Box title frame with fancy border
        box_title_frame = tk.Frame(self.local_nav_frame, bg=COLORS["primary"], bd=0, relief=tk.FLAT)
        box_title_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Box label with better styling
        self.local_box_label = tk.Label(box_title_frame, text="Box 1", bg=COLORS["primary"], 
                                      fg="white", font=("Roboto", 11, "bold"), padx=15, pady=2)
        self.local_box_label.pack(fill=tk.X, expand=True)
        
        # Right navigation button
        next_btn = ttk.Button(self.local_nav_frame, text="→", style="Nav.TButton", 
                            command=lambda: self.cycle_box("local", 1))
        next_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def cycle_box(self, grid_type, direction):
        """Cycle between boxes."""
        if grid_type == "local":
            self.current_local_box = (self.current_local_box + direction) % TOTAL_BOXES
            self.local_box_label.config(text=f"Box {self.current_local_box + 1}")
        self.update_grid_buttons()
        self.update_status(f"Viewing Box {self.current_local_box + 1}")

    def update_grid_buttons(self):  
        """Update the button colors based on current box contents."""
        for i, button in enumerate(self.local_buttons):
            pokemon = self.local_storage[self.current_local_box][i]
            if pokemon is not None:
                # Determine the sprite folder based on whether the Pokémon is shiny
                sprite_folder = SHINY_SPRITES_FOLDER if pokemon['shiny'] else SPRITES_FOLDER
            
                # Check for form_id and append the appropriate suffix
                species_name = pokemon['species'].lower()
                if 'form_id' in pokemon:
                    if pokemon['form_id'].lower() in ['galar', 'alola', 'hisui', 'dusk', 'midnight', 'dawn']:
                        species_name += f"-{pokemon['form_id'].lower()}"
            
                sprite_path = os.path.join(sprite_folder, f"{species_name}.png")
        
                if os.path.exists(sprite_path):
                    img = Image.open(sprite_path)
                    # Keep original sprite size (68x56) for pixel-perfect display
                    img = img.resize((85, 70), Image.Resampling.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                    
                    # Set background color based on whether the Pokémon is shiny
                    bg_color = COLORS["shiny_slot"] if pokemon['shiny'] else COLORS["filled_slot"]
                    
                    # Update the canvas background with larger rounded rectangle
                    canvas = button.master
                    canvas.delete(0)  # Remove the old rectangle
                    canvas.create_rounded_rectangle(0, 0, 70, 70, radius=8, 
                                                 fill=bg_color, outline="")
                    
                    # Configure button to display sprite
                    button.config(image=img, text="", compound=tk.CENTER, 
                                 width=60, height=60, bg=bg_color)
                    button.image = img  # Keep a reference to avoid garbage collection
                else:
                    # Use a gradient background for Pokémon without sprites
                    # Capitalize the species name for display
                    display_name = pokemon['species'].capitalize()
                    canvas = button.master
                    canvas.delete(0)  # Remove the old rectangle
                    canvas.create_rounded_rectangle(0, 0, 70, 70, radius=8, 
                                                 fill=COLORS["filled_slot"], outline="")
                    button.config(bg=COLORS["filled_slot"], text=display_name,
                                font=("Roboto", 8, "bold"), fg=COLORS["text"])
            else:
                # Reset the button completely
                canvas = button.master
                canvas.delete(0)  # Remove the old rectangle
                canvas.create_rounded_rectangle(0, 0, 70, 70, radius=8, 
                                             fill=COLORS["empty_slot"], outline="")
                button.config(image="", text="", compound=tk.NONE,
                            width=60, height=60, bg=COLORS["empty_slot"])
                button.image = None  # Clear the reference

    def create_details_panel(self):
        """Create a panel to display Pokémon details with tabs."""
        # Create a frame for the details panel
        self.details_frame = tk.Frame(self.content_frame, bg=COLORS["background"], bd=1, 
                                    relief=tk.SOLID, padx=2, pady=2)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Add buttons frame at the bottom first to ensure it's always visible
        buttons_frame = tk.Frame(self.details_frame, bg=COLORS["background"], pady=10, height=50)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)
        # Force the buttons frame to maintain its size
        buttons_frame.pack_propagate(False)
        
        # Create an inner frame to center the buttons
        buttons_inner_frame = tk.Frame(buttons_frame, bg=COLORS["background"])
        buttons_inner_frame.pack(side=tk.TOP, fill=tk.X)
        buttons_inner_frame.columnconfigure(0, weight=1)  # Left padding
        buttons_inner_frame.columnconfigure(1, weight=0)  # First button
        buttons_inner_frame.columnconfigure(2, weight=0)  # Second button
        buttons_inner_frame.columnconfigure(3, weight=0)  # Third button
        buttons_inner_frame.columnconfigure(4, weight=1)  # Right padding

        # "Showdown" button with blue styling
        self.showdown_button = ttk.Button(buttons_inner_frame, text="Showdown", style="Showdown.TButton",
                                      command=self.export_to_showdown)
        self.showdown_button.grid(row=0, column=1, padx=5)
        
        # "Cobblemon" button with green styling
        self.cobblemon_button = ttk.Button(buttons_inner_frame, text="Cobblemon", style="Cobblemon.TButton",
                                      command=self.export_to_cobblemon)
        self.cobblemon_button.grid(row=0, column=2, padx=5)
        
        # "Pokémon" button (renamed from "Convert to .cb9")
        self.convert_button = ttk.Button(buttons_inner_frame, text="Pokémon", style="Pokemon.TButton", 
                                      command=self.export_to_pokemon)
        self.convert_button.grid(row=0, column=3, padx=5)
        
        # Initially hide the buttons
        self.showdown_button.grid_remove()
        self.cobblemon_button.grid_remove()
        self.convert_button.grid_remove()
        
        # Inner frame with padding
        inner_details = tk.Frame(self.details_frame, bg=COLORS["background"], padx=15, pady=15)
        inner_details.pack(fill=tk.BOTH, expand=True)
        
        # Title for details panel
        ttk.Label(inner_details, text="Pokémon Details", style="BoxTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Create a Notebook (tabbed interface) with styled tabs
        self.notebook = ttk.Notebook(inner_details)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs with consistent styling
        self.overview_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.moves_tab = ttk.Frame(self.notebook)
        self.origin_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.stats_tab, text="Stats")
        self.notebook.add(self.moves_tab, text="Moves")
        self.notebook.add(self.origin_tab, text="Origin")
        
        # Create a scrollable frame for overview
        canvas = tk.Canvas(self.overview_tab, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overview_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add a default message when no Pokémon is selected
        self.default_message = ttk.Label(scrollable_frame, text="Select a Pokémon to view details", 
                                      font=("Roboto", 11), foreground="#888888")
        self.default_message.pack(pady=50)

    def create_status_bar(self):
        """Create a status bar at the bottom of the application."""
        self.status_frame = tk.Frame(self.root, bg=COLORS["primary"], height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", bg=COLORS["primary"], 
                                   fg="white", font=("Roboto", 9), anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.X)

    def update_status(self, message):
        """Update the status bar with a message."""
        self.status_label.config(text=message)
        self.root.update_idletasks()  # Force update

    def export_to_showdown(self):
        """Export the selected Pokémon's data to Pokémon Showdown format."""
        if self.selected_pokemon is None:
            messagebox.showerror("Error", "No Pokémon selected!")
            self.update_status("Error: No Pokémon selected")
            return
        
        # Convert Pokémon data to Showdown format
        showdown_data = self.convert_to_showdown_format(self.selected_pokemon)
        
        # Create a popup window to display the showdown format
        showdown_window = tk.Toplevel(self.root)
        showdown_window.title("Export to Showdown")
        showdown_window.geometry("500x400")
        showdown_window.configure(bg=COLORS["background"])
        showdown_window.transient(self.root)  # Set to be on top of the main window
        showdown_window.grab_set()  # Modal
        
        # Center the window
        showdown_window.update_idletasks()
        width = showdown_window.winfo_width()
        height = showdown_window.winfo_height()
        x = (showdown_window.winfo_screenwidth() // 2) - (width // 2)
        y = (showdown_window.winfo_screenheight() // 2) - (height // 2)
        showdown_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create content frame with padding
        content_frame = tk.Frame(showdown_window, bg=COLORS["background"], padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = f"Showdown Format: {self.selected_pokemon['species'].capitalize()}"
        title_label = tk.Label(content_frame, text=title_text, font=("Roboto", 14, "bold"),
                            bg=COLORS["background"], fg=COLORS["text"])
        title_label.pack(pady=(0, 15))
        
        # Text area for showdown format with syntax highlighting styling
        text_frame = tk.Frame(content_frame, bg=COLORS["secondary"], padx=2, pady=2, bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, bg="#F8F8F8", fg="#333333",
                          padx=10, pady=10, font=("Consolas", 11))
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, showdown_data)
        text_area.config(state=tk.DISABLED)  # Make read-only
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg=COLORS["background"], pady=15)
        button_frame.pack(fill=tk.X)
        
        # Copy to clipboard button
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(showdown_data)
            self.update_status(f"Copied {self.selected_pokemon['species'].capitalize()} Showdown format to clipboard")
            
        copy_button = ttk.Button(button_frame, text="Copy to Clipboard", 
                               command=copy_to_clipboard, style="Showdown.TButton")
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=showdown_window.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # Update status
        self.update_status(f"Exported {self.selected_pokemon['species'].capitalize()} to Showdown format")

    def convert_to_showdown_format(self, pokemon):
        """Convert a Pokémon's data to Showdown format."""
        output_lines = []
        
        # Add nickname and species
        if pokemon.get("nickname") and pokemon.get("nickname").lower() != pokemon.get("species").lower():
            output_lines.append(f"{pokemon['nickname']} ({pokemon['species'].capitalize()})")
        else:
            output_lines.append(f"{pokemon['species'].capitalize()}")
        
        # Add gender if available
        if pokemon.get("gender"):
            gender_symbol = "M" if pokemon["gender"] == "MALE" else "F" if pokemon["gender"] == "FEMALE" else ""
            if gender_symbol:
                output_lines[0] += f" ({gender_symbol})"
        
        # Add item if available (not in this JSON, but adding for completeness)
        item = pokemon.get("held_item", "")
        if item:
            output_lines.append(f"@ {item}")
        
        # Add ability
        ability = pokemon.get("ability", "").replace("-", " ").title()
        output_lines.append(f"Ability: {ability}")
        
        # Add level
        output_lines.append(f"Level: {pokemon.get('level', 100)}")
        
        # Add shiny status if shiny
        if pokemon.get("shiny"):
            output_lines.append("Shiny: Yes")
        
        # Add EVs if any are non-zero
        evs = pokemon.get("evs", {})
        ev_list = []
        for stat, value in evs.items():
            if value > 0:
                # Convert snake_case to typical Pokemon stat names
                stat_name = stat.replace("_", " ").replace("defence", "defense").title()
                if stat_name == "Hp":
                    stat_name = "HP"
                elif stat_name == "Special Attack":
                    stat_name = "SpA"
                elif stat_name == "Special Defense":
                    stat_name = "SpD"
                elif stat_name == "Speed":
                    stat_name = "Spe"
                elif stat_name == "Attack":
                    stat_name = "Atk"
                elif stat_name == "Defense":
                    stat_name = "Def"
                ev_list.append(f"{value} {stat_name}")
        
        if ev_list:
            output_lines.append(f"EVs: {' / '.join(ev_list)}")
        
        # Add nature
        if pokemon.get("nature"):
            output_lines.append(f"{pokemon['nature']} Nature")
        
        # Add IVs if any are not perfect (31)
        ivs = pokemon.get("ivs", {})
        iv_list = []
        for stat, value in ivs.items():
            if value < 31:  # Only add if not perfect IV
                # Convert snake_case to typical Pokemon stat names
                stat_name = stat.replace("_", " ").replace("defence", "defense").title()
                if stat_name == "Hp":
                    stat_name = "HP"
                elif stat_name == "Special Attack":
                    stat_name = "SpA"
                elif stat_name == "Special Defense":
                    stat_name = "SpD"
                elif stat_name == "Speed":
                    stat_name = "Spe"
                elif stat_name == "Attack":
                    stat_name = "Atk"
                elif stat_name == "Defense":
                    stat_name = "Def"
                iv_list.append(f"{value} {stat_name}")
        
        if iv_list:
            output_lines.append(f"IVs: {' / '.join(iv_list)}")
        
        # Add moves
        moves = pokemon.get('moves', [])
        for move in moves:
            # Format move name (replace hyphens with spaces and capitalize each word)
            formatted_move = " ".join(word.capitalize() for word in move.split("-"))
            output_lines.append(f"- {formatted_move}")
        
        # Join all lines with newlines and return
        return "\n".join(output_lines)

    def show_pokemon_info(self, event, grid_type, index):
        """Show the Pokémon's info in a tabbed interface."""
        if grid_type == "local":
            box = self.local_storage[self.current_local_box]
    
        if box[index] is not None:
            self.selected_pokemon = box[index]  # Update the selected Pokémon
            pokemon = self.selected_pokemon

            # Clear previous content in tabs
            for widget in self.overview_tab.winfo_children():
                widget.destroy()
            for widget in self.stats_tab.winfo_children():
                widget.destroy()
            for widget in self.moves_tab.winfo_children():
                widget.destroy()
            for widget in self.origin_tab.winfo_children():
                widget.destroy()

            # Overview Tab
            self.create_overview_tab(pokemon)

            # Stats Tab
            self.create_stats_tab(pokemon)

            # Moves Tab
            self.create_moves_tab(pokemon)
            
            # Origin Tab
            self.create_origin_tab(pokemon)
            
            # Show the buttons
            self.showdown_button.grid(row=0, column=1, padx=5)
            self.cobblemon_button.grid(row=0, column=2, padx=5)
            self.convert_button.grid(row=0, column=3, padx=5)
            
            # Update status
            self.update_status(f"Selected: {pokemon['species']} (Level {pokemon['level']})")
            
            # Force update the window
            self.root.update_idletasks()
        else:
            # Clear previous content in tabs
            for widget in self.overview_tab.winfo_children():
                widget.destroy()
            for widget in self.stats_tab.winfo_children():
                widget.destroy()
            for widget in self.moves_tab.winfo_children():
                widget.destroy()
            for widget in self.origin_tab.winfo_children():
                widget.destroy()
            
            # Create a scrollable frame for overview
            canvas = tk.Canvas(self.overview_tab, bg=COLORS["background"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.overview_tab, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add a default message
            self.default_message = ttk.Label(scrollable_frame, text="Select a Pokémon to view details", 
                                          font=("Roboto", 11), foreground="#888888")
            self.default_message.pack(pady=50)
            
            # Hide the buttons
            self.showdown_button.grid_remove()
            self.cobblemon_button.grid_remove()
            self.convert_button.grid_remove()
            
            # Update status
            self.update_status("No Pokémon selected")
            
            # Force update the window
            self.root.update_idletasks()

    def create_overview_tab(self, pokemon):
        """Populate the Overview tab with Pokémon details."""
        # Create a scrollable frame for overview
        canvas = tk.Canvas(self.overview_tab, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overview_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container with padding
        main_frame = ttk.Frame(scrollable_frame, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section with sprite and name
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Try to load the sprite
        sprite_folder = SHINY_SPRITES_FOLDER if pokemon['shiny'] else SPRITES_FOLDER
        species_name = pokemon['species'].lower()
        if 'form_id' in pokemon and pokemon['form_id'].lower() in ['galar', 'alola', 'hisui', 'dusk', 'midnight', 'dawn']:
            species_name += f"-{pokemon['form_id'].lower()}"
        
        sprite_path = os.path.join(sprite_folder, f"{species_name}.png")
        
        if os.path.exists(sprite_path):
            sprite_img = Image.open(sprite_path)
            sprite_img = sprite_img.resize((136, 112), Image.Resampling.NEAREST)  # Reverted to original size
            sprite_photo = ImageTk.PhotoImage(sprite_img)
            sprite_label = tk.Label(header_frame, image=sprite_photo, bg=COLORS["background"])
            sprite_label.image = sprite_photo  # Keep a reference
            sprite_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Name and species info
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.Y, pady=5)
        
        # Show species name in bold (capitalize first letter)
        formatted_species = pokemon['species'].capitalize()
        species_label = ttk.Label(name_frame, text=formatted_species, 
                              font=("Roboto", 16, "bold"), foreground=COLORS["text"])
        species_label.pack(anchor=tk.W)
        
        # Show nickname in quotes if it's different from species (preserve original capitalization)
        nickname = pokemon.get('nickname', '')
        if nickname and nickname.lower() != pokemon['species'].lower():
            # Show the nickname in quotes on the same line as species
            nickname_label = ttk.Label(name_frame, text=f'{nickname}', 
                           font=("Roboto", 12), foreground="#666666")
            nickname_label.pack(anchor=tk.W)
        
        # Level display in a box - now on the left under nickname
        level_box = tk.Frame(name_frame, bg="#6F8BAA", 
                          padx=6, pady=2, bd=0, relief=tk.FLAT)
        level_box.pack(anchor=tk.W, pady=(5, 0))
        
        tk.Label(level_box, text=f"Lv.{pokemon['level']}", 
               font=("Roboto", 10, "bold"), bg="#6F8BAA", 
               fg="white").pack()
        
        # Shiny indicator in a box if applicable - after level
        if pokemon['shiny']:
            shiny_box = tk.Frame(name_frame, bg=COLORS["accent"], 
                              padx=8, pady=3, bd=1, relief=tk.RAISED)
            shiny_box.pack(anchor=tk.W, pady=(5, 0))
            
            tk.Label(shiny_box, text="✨ SHINY", font=("Roboto", 9, "bold"), 
                   fg=COLORS["text"], bg=COLORS["accent"]).pack()
        
        # Information bars - one for each attribute
        info_container = tk.Frame(main_frame, bg=COLORS["background"])
        info_container.pack(fill=tk.X, expand=True, pady=(10, 0))
        
        # Individual bars for each attribute
        gender_text = self.format_gender_text(pokemon['gender'])
        self.create_info_bar(info_container, [("Gender", gender_text)])
        self.create_info_bar(info_container, [("Nature", pokemon['nature'].capitalize())])
        self.create_info_bar(info_container, [("Ability", self.format_ability(pokemon['ability']))])
        self.create_info_bar(info_container, [("Trainer", pokemon['original_trainer'])])
        self.create_info_bar(info_container, [("Experience", f"{pokemon['experience']:,}")])
        self.create_info_bar(info_container, [("Caught In", self.format_ball_name(pokemon['caught_ball']))])
    
    def create_info_bar(self, parent, items):
        """Create a horizontal info bar with multiple items."""
        # Create a bar with subtle styling
        bar = tk.Frame(parent, bg=COLORS["secondary"], bd=0, relief=tk.FLAT)
        bar.pack(fill=tk.X, pady=5)
        
        # Inner frame with padding
        inner_frame = tk.Frame(bar, bg=COLORS["secondary"], padx=12, pady=8)
        inner_frame.pack(fill=tk.X)
        
        # Divide space evenly among items
        for i, (label, value) in enumerate(items):
            item_frame = tk.Frame(inner_frame, bg=COLORS["secondary"])
            item_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0 if i == 0 else 15, 0))
            
            # Label
            tk.Label(item_frame, text=f"{label}:", font=("Roboto", 10, "bold"),
                   bg=COLORS["secondary"], fg=COLORS["text"]).pack(side=tk.LEFT)
            
            # Value - check if it's a tuple (for preformatted values with custom widgets)
            if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], tk.Widget):
                value[0].configure(bg=COLORS["secondary"])
                value[0].pack(side=tk.LEFT, padx=(8, 0))
            else:
                # Regular text value
                tk.Label(item_frame, text=value, font=("Roboto", 10),
                      bg=COLORS["secondary"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=(8, 0))
    
    def format_gender_text(self, gender):
        """Format gender as text with proper capitalization."""
        gender = gender.upper()
        if gender == "MALE":
            return "Male"
        elif gender == "FEMALE":
            return "Female"
        else:  # GENDERLESS
            return "Genderless"

    def format_gender(self, gender):
        """Format gender with appropriate icon and color."""
        gender_frame = tk.Frame()
        
        gender = gender.upper()
        if gender == "MALE":
            gender_icon = "♂"
            gender_color = "#3A7FD5"  # Blue for male
        elif gender == "FEMALE":
            gender_icon = "♀"
            gender_color = "#FC5D68"  # Pink for female
        else:  # GENDERLESS
            gender_icon = "⚪"
            gender_color = "#888888"  # Grey for genderless
            
        gender_label = tk.Label(gender_frame, text=gender_icon, font=("Roboto", 12, "bold"), 
                             fg=gender_color)
        gender_label.pack(side=tk.LEFT)
        
        # Add the gender text
        gender_text = tk.Label(gender_frame, text=f" {gender.capitalize()}", font=("Roboto", 10))
        gender_text.pack(side=tk.LEFT)
        
        return (gender_frame, None)

    def format_ability(self, ability_name):
        """Format ability name - capitalize each word."""
        return " ".join(word.capitalize() for word in ability_name.split())

    def format_ball_name(self, ball_name):
        """Format ball name - remove 'cobblemon:' prefix, replace underscores with spaces, capitalize each word."""
        if "cobblemon:" in ball_name.lower():
            ball_name = ball_name[ball_name.lower().index("cobblemon:") + 10:]  # Remove "cobblemon:" prefix
        ball_name = ball_name.replace("_", " ")
        return " ".join(word.capitalize() for word in ball_name.split())

    def create_stats_tab(self, pokemon):
        """Populate the Stats tab with IVs and EVs."""
        # Create a frame with padding
        main_frame = ttk.Frame(self.stats_tab, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # IVs section with a decorative header
        iv_header_frame = tk.Frame(main_frame, bg=COLORS["primary"], padx=10, pady=5)
        iv_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(iv_header_frame, text="Individual Values (IVs)", 
               font=("Roboto", 11, "bold"), bg=COLORS["primary"], fg="white").pack(anchor=tk.W)
        
        # IV bars with visual representation
        ivs_frame = ttk.Frame(main_frame)
        ivs_frame.pack(fill=tk.X, pady=(0, 20))
        
        iv_stats = {
            "HP": pokemon['ivs']['hp'], 
            "Attack": pokemon['ivs']['attack'],
            "Defence": pokemon['ivs']['defence'], 
            "Sp. Attack": pokemon['ivs']['special_attack'],
            "Sp. Defence": pokemon['ivs']['special_defence'], 
            "Speed": pokemon['ivs']['speed']
        }
        
        # Create IV stat bars
        self.create_stat_bars(ivs_frame, iv_stats, max_value=31)
        
        # EVs section
        ev_header_frame = tk.Frame(main_frame, bg=COLORS["accent"], padx=10, pady=5)
        ev_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(ev_header_frame, text="Effort Values (EVs)", 
               font=("Roboto", 11, "bold"), bg=COLORS["accent"], fg=COLORS["text"]).pack(anchor=tk.W)
        
        # EV bars with visual representation
        evs_frame = ttk.Frame(main_frame)
        evs_frame.pack(fill=tk.X)
        
        ev_stats = {
            "HP": pokemon['evs']['hp'], 
            "Attack": pokemon['evs']['attack'],
            "Defence": pokemon['evs']['defence'], 
            "Sp. Attack": pokemon['evs']['special_attack'],
            "Sp. Defence": pokemon['evs']['special_defence'], 
            "Speed": pokemon['evs']['speed']
        }
        
        # Create EV stat bars
        self.create_stat_bars(evs_frame, ev_stats, max_value=252, color=COLORS["accent"])

    def create_stat_bars(self, parent, stats, max_value=31, color=COLORS["primary"]):
        """Create visual stat bars for IVs or EVs."""
        row = 0
        for stat_name, stat_value in stats.items():
            # Stat name
            ttk.Label(parent, text=stat_name, font=("Roboto", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=3)
            
            # Stat value
            ttk.Label(parent, text=str(stat_value)).grid(row=row, column=1, padx=10, sticky=tk.W, pady=3)
            
            # Bar background
            bar_bg = tk.Frame(parent, width=200, height=15, bg=COLORS["secondary"])
            bar_bg.grid(row=row, column=2, sticky=tk.W, pady=3)
            bar_bg.grid_propagate(False)  # Prevent frame from shrinking
            
            # Calculate bar width based on stat value
            bar_width = int((stat_value / max_value) * 200)
            
            # Bar fill
            bar_fill = tk.Frame(bar_bg, width=bar_width, height=15, bg=color)
            bar_fill.place(x=0, y=0)
            
            row += 1

    def create_moves_tab(self, pokemon):
        """Populate the Moves tab with the Pokémon's moves."""
        # Create a frame with padding
        main_frame = ttk.Frame(self.moves_tab, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Moves header
        header_frame = tk.Frame(main_frame, bg=COLORS["primary"], padx=10, pady=5)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="Moves", font=("Roboto", 11, "bold"), 
               bg=COLORS["primary"], fg="white").pack(anchor=tk.W)
        
        # Get the moves
        moves = pokemon.get('moves', [])
        
        # Create a grid frame for the moves
        moves_grid = ttk.Frame(main_frame)
        moves_grid.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Configure the grid columns
        moves_grid.columnconfigure(0, weight=1)
        moves_grid.columnconfigure(1, weight=1)
        
        # If no moves, display a message
        if not moves or all(move is None for move in moves):
            no_moves_label = ttk.Label(moves_grid, text="No moves found", 
                                    font=("Roboto", 10), foreground="#888888")
            no_moves_label.grid(row=0, column=0, columnspan=2, pady=20)
        else:
            # Create a move card for each move in a 2x2 grid
            for i, move in enumerate(moves):
                if move is None:  # Skip None values
                    continue
                    
                # Calculate row and column for 2x2 grid
                row = i // 2
                col = i % 2
                
                # Create a frame for the move with nice styling
                move_frame = tk.Frame(moves_grid, bg=COLORS["background"], padx=10, pady=10,
                                    bd=1, relief=tk.SOLID)
                move_frame.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                
                # Format move name - replace hyphens with spaces and capitalize each word
                formatted_move = " ".join(word.capitalize() for word in move.split("-"))
                
                # Move name with larger font
                move_name = tk.Label(move_frame, text=formatted_move, 
                                   font=("Roboto", 11, "bold"), bg=COLORS["background"],
                                   fg=COLORS["text"])
                move_name.pack(anchor=tk.CENTER, pady=(0, 5))
                
                # Add a subtle separator
                separator = ttk.Separator(move_frame, orient='horizontal')
                separator.pack(fill=tk.X, pady=5)

    def export_to_pokemon(self):
        """Convert the selected Pokémon's JSON file to .cb9 using the external .exe."""
        if self.selected_pokemon is None:
            messagebox.showerror("Error", "No Pokémon selected!")
            self.update_status("Error: No Pokémon selected")
            return

        # Use the file_path directly from the selected_pokemon data
        if 'file_path' not in self.selected_pokemon or not os.path.exists(self.selected_pokemon['file_path']):
            messagebox.showerror("Error", f"JSON file for {self.selected_pokemon['species']} not found!")
            self.update_status(f"Error: JSON file not found for {self.selected_pokemon['species']}")
            return
        
        json_file_path = self.selected_pokemon['file_path']

        # Get the absolute path to the converter executable
        current_dir = os.path.dirname(os.path.abspath(__file__))
        converter_exe = os.path.join(current_dir, "modules", "PokemonExporter", "JsonToPB8.exe")
        
        # Debug information
        print(f"Current directory: {current_dir}")
        print(f"Looking for converter at: {converter_exe}")
        print(f"File exists: {os.path.exists(converter_exe)}")
        
        if not os.path.exists(converter_exe):
            messagebox.showerror("Error", f"Converter executable not found at: {converter_exe}\n\nCurrent directory: {current_dir}")
            self.update_status("Error: Converter executable not found")
            return

        try:
            # Update status before conversion
            self.update_status(f"Converting {self.selected_pokemon['species']} to .cb9...")
            
            # Run the converter .exe with the JSON file as an argument
            run_windows_exe(converter_exe, [json_file_path], check=True)
            
            # Show success message
            messagebox.showinfo("Success", f"Conversion successful: {os.path.basename(json_file_path)}.cb9 created!")
            self.update_status(f"Successfully converted {self.selected_pokemon['species']} to .cb9")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
            self.update_status("Error: Conversion failed")

    def get_selected_pokemon(self):
        """Get the currently selected Pokémon."""
        return self.selected_pokemon

    def load_pokemon_data(self):
        """Load all Pokémon data from JSON files in the selected folder."""
        try:
            # Ensure the selected directory exists
            if not os.path.exists(self.current_folder):
                os.makedirs(self.current_folder)
                self.update_status(f"Created directory: {self.current_folder}")
                return
                
            # Get all JSON files in the directory
            files = [f for f in os.listdir(self.current_folder) if f.endswith(".json")]
            
            if not files:
                self.update_status(f"No Pokémon data found in {self.current_folder}. Try importing some files.")
                return
                
            # Sort files by modification date (oldest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.current_folder, x)))
            
            # Clear existing storage first
            self.local_storage = [[None] * BOX_SIZE for _ in range(TOTAL_BOXES)]
            
            # Keep track of used slots to avoid duplicates
            used_slots = set()
            
            # Load Pokémon data
            pokemon_data = []
            for file in files:
                file_path = os.path.join(self.current_folder, file)
                with open(file_path, "r") as f:
                    pokemon = json.load(f)
                    # Store the file path with the Pokémon data (but don't save to JSON)
                    pokemon['file_path'] = file_path
                    
                    # Check if this Pokémon has box and slot info
                    if 'box_number' in pokemon and 'slot_number' in pokemon:
                        box_num = pokemon['box_number'] - 1  # Convert from 1-indexed to 0-indexed
                        slot_num = pokemon['slot_number'] - 1
                        
                        # Ensure the box and slot are valid
                        if 0 <= box_num < TOTAL_BOXES and 0 <= slot_num < BOX_SIZE:
                            # Create a unique identifier for this slot
                            slot_id = (box_num, slot_num)
                            
                            # Check if this slot is already used
                            if slot_id in used_slots:
                                # Slot conflict - add to the end instead
                                pokemon_data.append(pokemon)
                            else:
                                # Place directly in the right slot
                                self.local_storage[box_num][slot_num] = pokemon
                                used_slots.add(slot_id)
                        else:
                            # Invalid box/slot - add to the end
                            pokemon_data.append(pokemon)
                    else:
                        # No box/slot info - add to the end
                        pokemon_data.append(pokemon)
            
            # Place remaining Pokémon in empty slots, starting with the current box
            for pokemon in pokemon_data:
                placed = False
                
                # Start with the current box, then try other boxes
                box_order = list(range(TOTAL_BOXES))
                box_order.remove(self.current_local_box)
                box_order.insert(0, self.current_local_box)
                
                for box_index in box_order:
                    if placed:
                        break
                    for slot_index in range(BOX_SIZE):
                        if self.local_storage[box_index][slot_index] is None:
                            self.local_storage[box_index][slot_index] = pokemon
                            
                            # Update the Pokémon's box and slot info
                            pokemon['box_number'] = box_index + 1
                            pokemon['slot_number'] = slot_index + 1
                            
                            # Save the updated info to the file
                            with open(pokemon['file_path'], 'w') as f:
                                # Create a copy without the file_path
                                pokemon_save = {k: v for k, v in pokemon.items() if k != 'file_path'}
                                json.dump(pokemon_save, f, indent=4)
                                
                            placed = True
                            break
            
            self.update_grid_buttons()
            
            # Count total Pokémon
            total_loaded = sum(1 for box in self.local_storage for slot in box if slot is not None)
            self.update_status(f"Loaded {total_loaded} Pokémon from {self.current_folder} across {min(total_loaded // BOX_SIZE + 1, TOTAL_BOXES)} boxes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Pokémon data: {e}")
            self.update_status(f"Error loading Pokémon data: {str(e)}")

    def run_parser_script(self):
        """Run the CobblemonImporter.py script."""
        try:
            self.update_status("Running CobblemonImporter.py...")
            subprocess.run(["python", os.path.join("modules", "CobblemonImporter.py")], check=True)
            self.update_status("CobblemonImporter.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute CobblemonImporter.py: {e}")
            self.update_status(f"Error: Failed to execute CobblemonImporter.py: {str(e)}")

    def run_pb8_to_json_script(self):
        """Run the PokemonImporter.py script."""
        try:
            self.update_status("Running PokemonImporter.py...")
            subprocess.run(["python", os.path.join("modules", "PokemonImporter.py")], check=True)
            self.update_status("PokemonImporter.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute PokemonImporter.py: {e}")
            self.update_status(f"Error: Failed to execute PokemonImporter.py: {str(e)}")

    def run_export_script(self):
        """Run the CobblemonExporter.py script."""
        try:
            self.update_status("Running CobblemonExporter.py...")
            subprocess.run(["python", os.path.join("modules", "CobblemonExporter.py")], check=True)
            self.update_status("CobblemonExporter.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute CobblemonExporter.py: {e}")
            self.update_status(f"Error: Failed to execute CobblemonExporter.py: {str(e)}")

    def mass_convert_to_pb8(self):
        """Convert selected JSON files to .pb8 using an external .exe."""
        
        # Open a file dialog to select the JSON files
        json_file_paths = filedialog.askopenfilenames(
            title="Select JSON files to convert",
            filetypes=[("JSON files", "*.json")],
            initialdir=COBBLEMON_FOLDER
        )
        
        if not json_file_paths:
            # User canceled the file selection
            return

        # Assuming the .exe is named "converter.exe" and is in the same directory as the script
        converter_exe = "modules/PokemonExporter/JsonToPB8.exe"
        if not os.path.exists(converter_exe):
            messagebox.showerror("Error", "Converter executable not found!")
            self.update_status("Error: Converter executable not found")
            return

        # Track conversion stats
        successful = 0
        failed = 0
        
        for json_file_path in json_file_paths:
            if not os.path.exists(json_file_path):
                failed += 1
                continue

            try:
                # Run the converter .exe with the JSON file as an argument
                self.update_status(f"Converting {os.path.basename(json_file_path)}...")
                run_windows_exe(converter_exe, [json_file_path], check=True)
                successful += 1
            except subprocess.CalledProcessError:
                failed += 1
            except Exception:
                failed += 1
        
        # Show summary message
        if successful > 0 and failed == 0:
            messagebox.showinfo("Conversion Complete", f"Successfully converted {successful} files!")
        elif successful > 0 and failed > 0:
            messagebox.showwarning("Conversion Partial", f"Converted {successful} files successfully, {failed} files failed.")
        else:
            messagebox.showerror("Conversion Failed", "Failed to convert any files.")
            
        self.update_status(f"Conversion complete: {successful} successful, {failed} failed")

    def create_menu(self):
        """Create a menu bar with save and load options."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu with icons (if available)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Load Pokémon Data", command=self.load_pokemon_data, 
                            accelerator="Ctrl+R")
        file_menu.add_command(label="Create New Folder", command=self.create_new_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Cobblemon", command=self.run_export_script)
        file_menu.add_command(label="Export to Pokémon", command=self.mass_convert_to_pb8)
        file_menu.add_separator()
        file_menu.add_command(label="Import .dat", command=self.run_parser_script)
        file_menu.add_command(label="Import .pk9", command=self.run_pb8_to_json_script)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add keyboard shortcuts
        self.root.bind("<Control-r>", lambda event: self.load_pokemon_data())
        self.root.bind("<F1>", lambda event: self.show_help())

    def show_help(self):
        """Show the help/instructions dialog."""
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Use Cobblemon Transporter")
        help_window.geometry("650x500")
        help_window.resizable(True, True)
        help_window.configure(bg=COLORS["background"])
        help_window.transient(self.root)  # Set to be on top of the main window
        help_window.grab_set()  # Modal
        
        # Center the window
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create a frame with scrollbar
        main_frame = tk.Frame(help_window, bg=COLORS["background"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a frame inside the canvas
        content_frame = tk.Frame(canvas, bg=COLORS["background"], padx=10, pady=10)
        
        # Add the new frame to a window in the canvas
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Title
        title_label = tk.Label(content_frame, text="Cobblemon Transporter - Instructions", 
                            font=("Roboto", 16, "bold"), bg=COLORS["background"], fg=COLORS["text"])
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Instructions sections
        sections = [
            {
                "title": "Overview",
                "content": "Cobblemon Transporter allows you to manage and convert Pokémon between Cobblemon and other Pokémon games. It provides a visual interface for organizing your Pokémon and converting between different file formats."
            },
            {
                "title": "Importing Pokémon",
                "content": "There are several ways to import your Pokémon:\n\n• Drag & Drop: Simply drag .pk9, .cb9, .pb8 or .pk8 files directly onto the application window.\n\n• Import Menu: Use File → Import .pk9 or File → Import .dat to import Pokémon from PK9 files or Cobblemon DAT files.\n\n• After importing, your Pokémon will appear in the storage boxes."
            },
            {
                "title": "Managing Boxes",
                "content": "• Navigation: Use the arrow buttons below the storage grid to navigate between boxes.\n\n• Moving Pokémon: Right-click and drag a Pokémon to move it between slots or boxes.\n\n• Viewing Details: Left-click on a Pokémon to view its details in the panel on the right."
            },
            {
                "title": "Pokémon Details",
                "content": "When you select a Pokémon, you can view:\n\n• Overview: Species, nickname, level, gender, ability, nature, and other basic information.\n\n• Stats: Individual Values (IVs) and Effort Values (EVs) with visual indicators.\n\n• Moves: A list of the Pokémon's current moves."
            },
            {
                "title": "Converting Pokémon",
                "content": "• Converting Individual Pokémon: Select a Pokémon and click the 'Convert to .cb9' button at the bottom of the details panel.\n\n• Export to Showdown: Select a Pokémon and click the 'Export to Showdown' button to get the Pokémon's data in Showdown format for competitive battling.\n\n• Mass Conversion: Use File → Export to Pokémon to convert multiple JSON files to .cb9 format at once.\n\n• Exporting to Cobblemon: Use File → Export to Cobblemon to prepare your Pokémon for use in Cobblemon."
            },
            {
                "title": "Tips & Shortcuts",
                "content": "• Ctrl+R: Refresh Pokémon data\n• F1: Open this help window\n• Shiny Pokémon are highlighted with a gold background\n• You can organize your Pokémon across 8 different boxes\n• The status bar at the bottom shows the result of your most recent action"
            }
        ]
        
        # Add each section
        for i, section in enumerate(sections):
            # Section header
            section_frame = tk.Frame(content_frame, bg=COLORS["primary"], padx=10, pady=5)
            section_frame.pack(fill=tk.X, anchor=tk.W, pady=(15, 5) if i > 0 else (0, 5))
            
            section_label = tk.Label(section_frame, text=section["title"], font=("Roboto", 12, "bold"), 
                                bg=COLORS["primary"], fg="white")
            section_label.pack(anchor=tk.W)
            
            # Section content
            content_label = tk.Label(content_frame, text=section["content"], font=("Roboto", 10), 
                                bg=COLORS["background"], fg=COLORS["text"], 
                                justify=tk.LEFT, wraplength=580)
            content_label.pack(anchor=tk.W, padx=5)
        
        # Add close button at bottom
        button_frame = tk.Frame(content_frame, bg=COLORS["background"])
        button_frame.pack(pady=(20, 0))
        
        close_button = ttk.Button(button_frame, text="Close", command=help_window.destroy)
        close_button.pack()
        
        # Configure canvas scrolling
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        content_frame.bind("<Configure>", configure_canvas)
        
        # Configure mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mousewheel event (different for various operating systems)
        if sys.platform.startswith("win"):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        elif sys.platform.startswith("darwin"):  # macOS
            canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * event.delta), "units"))
        else:  # Linux
            canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

    def show_about(self):
        """Show the about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Cobblemon Transporter")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.configure(bg=COLORS["background"])
        about_window.transient(self.root)  # Set to be on top of the main window
        about_window.grab_set()  # Modal
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Content frame with padding
        content_frame = tk.Frame(about_window, bg=COLORS["background"], padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        tk.Label(content_frame, text="Cobblemon Transporter", font=("Roboto", 16, "bold"),
               bg=COLORS["background"], fg=COLORS["text"]).pack(pady=(0, 10))
        
        # Version info
        tk.Label(content_frame, text="by ArchieDxncan", font=("Roboto", 10),
               bg=COLORS["background"], fg=COLORS["text"]).pack(pady=(0, 20))
        
        # Description
        description = "A tool for managing and converting Pokémon between Cobblemon and other Pokémon games."
        tk.Label(content_frame, text=description, font=("Roboto", 9), wraplength=350,
               bg=COLORS["background"], fg=COLORS["text"]).pack(pady=(0, 20))
        
        # Close button
        ttk.Button(content_frame, text="Close", command=about_window.destroy).pack(pady=10)

    def setup_drag_drop_for_boxes(self):
        """Set up drag and drop functionality for box slots using right mouse button."""
        for i, button in enumerate(self.local_buttons):
            # Bind right-click events for drag and drop
            button.bind("<ButtonPress-3>", lambda e, idx=i: self.start_drag(e, idx))
            button.bind("<B3-Motion>", lambda e, idx=i: self.drag_motion(e, idx))
            button.bind("<ButtonRelease-3>", lambda e, idx=i: self.end_drag(e, idx))
            
            # We'll also need to keep track of the original appearance
            canvas = button.master  # Get the canvas that contains the button
            button.bind("<Enter>", lambda e, btn=button, c=canvas: self.on_button_enter(e, btn, c))
            button.bind("<Leave>", lambda e, btn=button, c=canvas, idx=i: 
                      self.on_button_leave(e, btn, c, idx))

    def start_drag(self, event, idx):
        """Start dragging a Pokémon with right-click."""
        # Only start drag if there's a Pokémon in the slot
        if self.local_storage[self.current_local_box][idx] is None:
            return
        
        # Store source information
        self.drag_source_box = self.current_local_box
        self.drag_source_idx = idx
        self.is_dragging = True
        
        # Visual feedback - change cursor and highlight
        event.widget.config(relief=tk.SUNKEN)
        self.root.config(cursor="fleur")  # Change cursor to indicate dragging
        
        # Create a semi-transparent drag image (optional, more advanced)
        # This would require additional work with a Canvas overlay

    def drag_motion(self, event, idx):
        """Handle the motion during drag."""
        if not hasattr(self, 'is_dragging') or not self.is_dragging:
            return
        
        # Find which button we're currently over
        x, y = event.widget.winfo_pointerxy()
        target_widget = self.root.winfo_containing(x, y)
        
        # Reset all buttons to their normal state
        for button in self.local_buttons:
            if button != self.local_buttons[self.drag_source_idx] or not self.is_dragging:
                pokemon = self.local_storage[self.current_local_box][self.local_buttons.index(button)]
                if pokemon is None:
                    button.config(bg=COLORS["empty_slot"], relief=tk.FLAT)
                else:
                    bg_color = COLORS["shiny_slot"] if pokemon['shiny'] else COLORS["filled_slot"]
                    button.config(bg=bg_color, relief=tk.FLAT)
        
        # Highlight the button we're over if it's a valid drop target
        if target_widget in self.local_buttons:
            target_idx = self.local_buttons.index(target_widget)
            # Don't highlight if it's the source
            if not (self.current_local_box == self.drag_source_box and target_idx == self.drag_source_idx):
                target_widget.config(bg=COLORS["accent"], relief=tk.GROOVE)

    def end_drag(self, event, idx):
        """End dragging and handle the drop."""
        if not hasattr(self, 'is_dragging') or not self.is_dragging:
            return
        
        # Reset cursor
        self.root.config(cursor="")
        
        # Find which button we're over for the drop
        x, y = event.widget.winfo_pointerxy()
        target_widget = self.root.winfo_containing(x, y)
        
        if target_widget in self.local_buttons:
            target_idx = self.local_buttons.index(target_widget)
            
            # Only process if dropping onto a different slot
            if not (self.current_local_box == self.drag_source_box and target_idx == self.drag_source_idx):
                # Perform the swap or move
                self.swap_pokemon(self.drag_source_box, self.drag_source_idx, 
                                self.current_local_box, target_idx)
        
        # Reset all buttons to normal state
        self.update_grid_buttons()
        
        # Reset dragging state
        self.is_dragging = False

    def swap_pokemon(self, source_box, source_idx, target_box, target_idx):
        """Swap or move Pokémon between slots."""
        # Get the Pokémon from the source and target slots
        source_pokemon = self.local_storage[source_box][source_idx]
        target_pokemon = self.local_storage[target_box][target_idx]
        
        if source_pokemon is None:
            return  # No Pokémon to move
        
        if target_pokemon is not None:
            # Swap Pokémon
            self.local_storage[source_box][source_idx] = target_pokemon
            self.local_storage[target_box][target_idx] = source_pokemon
            
            # Update box and slot data for both Pokémon
            self.update_pokemon_box_slot(source_pokemon, target_box, target_idx)
            self.update_pokemon_box_slot(target_pokemon, source_box, source_idx)
            
            self.update_status(f"Swapped {source_pokemon['species']} with {target_pokemon['species']}")
        else:
            # Move Pokémon to empty slot
            self.local_storage[target_box][target_idx] = source_pokemon
            self.local_storage[source_box][source_idx] = None
            
            # Update box and slot data
            self.update_pokemon_box_slot(source_pokemon, target_box, target_idx)
            
            self.update_status(f"Moved {source_pokemon['species']} to Box {target_box + 1}, Slot {target_idx + 1}")
        
        # Update the UI
        self.update_grid_buttons()

    def on_button_enter(self, event, button, c):
        """Handle mouse enter event for box buttons."""
        # Skip if we're currently dragging
        if hasattr(self, 'is_dragging') and self.is_dragging:
            return
        
        idx = self.local_buttons.index(button)
        if self.local_storage[self.current_local_box][idx] is None:
            c.itemconfig(0, fill=COLORS["secondary"])

    def on_button_leave(self, event, button, c, idx):
        """Handle mouse leave event for box buttons."""
        # Skip if we're currently dragging
        if hasattr(self, 'is_dragging') and self.is_dragging:
            return
            
        if self.local_storage[self.current_local_box][idx] is None:
            c.itemconfig(0, fill=COLORS["empty_slot"])

    def update_pokemon_box_slot(self, pokemon, box_num, slot_num):
        """Update a Pokémon's box and slot data in its JSON file."""
        try:
            # Add box and slot info to the Pokémon data
            pokemon['box_number'] = box_num + 1  # Convert to 1-indexed for user clarity
            pokemon['slot_number'] = slot_num + 1  # Convert to 1-indexed for user clarity
            
            # Use the file_path stored with the Pokémon data
            if 'file_path' in pokemon and os.path.exists(pokemon['file_path']):
                with open(pokemon['file_path'], 'w') as f:
                    # Create a copy of the pokemon dict without the file_path key
                    pokemon_save = {k: v for k, v in pokemon.items() if k != 'file_path'}
                    json.dump(pokemon_save, f, indent=4)
                self.update_status(f"Updated {pokemon['species']} box/slot info")
            else:
                self.update_status(f"Warning: Could not find JSON file for {pokemon['species']}")
            
            # Check for box/slot conflicts
            conflict_file = pokemon.get('file_path', "")
            self.resolve_box_slot_conflicts(box_num, slot_num, conflict_file)
            
        except Exception as e:
            self.update_status(f"Error updating Pokémon data: {str(e)}")

    def resolve_box_slot_conflicts(self, box_num, slot_num, excluded_file):
        """Check for and resolve box/slot conflicts among Pokémon JSON files."""
        try:
            files = [f for f in os.listdir(COBBLEMON_FOLDER) if f.endswith(".json") 
                    and os.path.join(COBBLEMON_FOLDER, f) != excluded_file]
            
            for file in files:
                file_path = os.path.join(COBBLEMON_FOLDER, file)
                with open(file_path, "r") as f:
                    pokemon_data = json.load(f)
                    
                # Check if this Pokémon has the same box and slot
                if ('box_number' in pokemon_data and 'slot_number' in pokemon_data and
                    pokemon_data['box_number'] == box_num + 1 and pokemon_data['slot_number'] == slot_num + 1):
                    
                    # Found a conflict, move this Pokémon to the first empty slot
                    for b in range(TOTAL_BOXES):
                        for s in range(BOX_SIZE):
                            if self.local_storage[b][s] is None:
                                # Update the conflicting Pokémon's data
                                pokemon_data['box_number'] = b + 1
                                pokemon_data['slot_number'] = s + 1
                                
                                # Save the updated data
                                with open(file_path, 'w') as f:
                                    json.dump(pokemon_data, f, indent=4)
                                
                                # If there's a Pokémon object in memory for this file, update its file_path
                                for box in self.local_storage:
                                    for slot in box:
                                        if slot is not None and slot.get('file_path') == file_path:
                                            slot['box_number'] = b + 1
                                            slot['slot_number'] = s + 1
                                
                                # Update local storage
                                pokemon_data['file_path'] = file_path  # Add file_path
                                self.local_storage[b][s] = pokemon_data
                                
                                # If we're viewing the affected box, update the UI
                                if b == self.current_local_box:
                                    self.update_grid_buttons()
                                    
                                self.update_status(f"Resolved box/slot conflict for {pokemon_data['species']}")
                                return
                    
                    # If no empty slots were found, just clear the box/slot data
                    pokemon_data.pop('box_number', None)
                    pokemon_data.pop('slot_number', None)
                    
                    # Save the updated data
                    with open(file_path, 'w') as f:
                        json.dump(pokemon_data, f, indent=4)
                        
        except Exception as e:
            self.update_status(f"Error resolving box/slot conflicts: {str(e)}")

    def create_origin_tab(self, pokemon):
        """Populate the Origin tab with Pokémon's origin data and other details."""
        # Create a scrollable frame for origin info
        canvas = tk.Canvas(self.origin_tab, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.origin_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Origin Information Section
        origin_header_frame = tk.Frame(scrollable_frame, bg=COLORS["primary"], padx=10, pady=5)
        origin_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(origin_header_frame, text="Origin Information", 
               font=("Roboto", 11, "bold"), bg=COLORS["primary"], fg="white").pack(anchor=tk.W)
        
        # Create info grid for origin data
        origin_frame = ttk.Frame(scrollable_frame)
        origin_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        # Determine origin game display name (convert abbreviation to full name)
        game_names = {
            # Gen 1
            "RD": "Pokémon Red",
            "BU": "Pokémon Blue",
            "GN": "Pokémon Green",
            "YW": "Pokémon Yellow",
            
            # Gen 2
            "GD": "Pokémon Gold",
            "SI": "Pokémon Silver",
            "C": "Pokémon Crystal",
            
            # Gen 3
            "R": "Pokémon Ruby",
            "S": "Pokémon Sapphire",
            "E": "Pokémon Emerald",
            "FR": "Pokémon FireRed",
            "LG": "Pokémon LeafGreen",
            "CXD": "Pokémon Colosseum/XD",
            
            # Gen 4
            "D": "Pokémon Diamond",
            "P": "Pokémon Pearl",
            "Pt": "Pokémon Platinum",
            "HG": "Pokémon HeartGold",
            "SS": "Pokémon SoulSilver",
            
            # Gen 5
            "B": "Pokémon Black",
            "W": "Pokémon White",
            "B2": "Pokémon Black 2",
            "W2": "Pokémon White 2",
            
            # Gen 6
            "X": "Pokémon X",
            "Y": "Pokémon Y",
            "OR": "Pokémon Omega Ruby",
            "AS": "Pokémon Alpha Sapphire",
            
            # Gen 7
            "SN": "Pokémon Sun",
            "MN": "Pokémon Moon",
            "US": "Pokémon Ultra Sun",
            "UM": "Pokémon Ultra Moon",
            "GP": "Pokémon Let's Go Pikachu",
            "GE": "Pokémon Let's Go Eevee",
            "GO": "Pokémon GO",
            
            # Gen 8
            "SW": "Pokémon Sword",
            "SH": "Pokémon Shield",
            "BD": "Pokémon Brilliant Diamond",
            "SP": "Pokémon Shining Pearl",
            "PLA": "Pokémon Legends: Arceus",
            
            # Gen 9
            "SL": "Pokémon Scarlet",
            "VL": "Pokémon Violet",
            "ZA": "Pokémon Legends ZA"
        }
        
        origin_game = pokemon.get('origin_game', "Unknown")
        game_display = game_names.get(origin_game, origin_game)
        
        # Row 1 - Origin Game
        ttk.Label(origin_frame, text="Origin Game:", font=("Roboto", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(origin_frame, text=game_display).grid(row=0, column=1, sticky=tk.W, padx=(10, 30))
        
        # Row 2 - Met Info
        ttk.Label(origin_frame, text="Met Location:", font=("Roboto", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        # Note: We only have the location ID, not the location name
        ttk.Label(origin_frame, text=f"Location {pokemon.get('met_location', 'Unknown')}").grid(row=1, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(origin_frame, text="Met Date:", font=("Roboto", 10, "bold")).grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # Format date to DD/MM/YY if it exists and has the expected format
        met_date = pokemon.get('met_date', 'Unknown')
        if met_date != 'Unknown' and '-' in met_date:
            try:
                # Parse the date string (assuming YYYY-MM-DD format)
                date_parts = met_date.split('-')
                if len(date_parts) == 3:
                    year, month, day = date_parts
                    # Format as DD/MM/YYYY
                    formatted_date = f"{day}/{month}/{year}"
                    ttk.Label(origin_frame, text=formatted_date).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
                else:
                    ttk.Label(origin_frame, text=met_date).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
            except:
                ttk.Label(origin_frame, text=met_date).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        else:
            ttk.Label(origin_frame, text=met_date).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 3 - Met Level
        ttk.Label(origin_frame, text="Met Level:", font=("Roboto", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(origin_frame, text=str(pokemon.get('met_level', 'Unknown'))).grid(row=2, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(origin_frame, text="Language:", font=("Roboto", 10, "bold")).grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Map language codes to names
        language_names = {
            1: "Japanese",
            2: "English",
            3: "French",
            4: "Italian",
            5: "German",
            7: "Spanish",
            8: "Korean",
            9: "Chinese (Simplified)",
            10: "Chinese (Traditional)"
        }
        
        language_code = pokemon.get('language', 0)
        language_name = language_names.get(language_code, f"Unknown ({language_code})")
        ttk.Label(origin_frame, text=language_name).grid(row=2, column=3, sticky=tk.W, padx=(10, 0))
        
        # Physical Characteristics Section
        physical_header_frame = tk.Frame(scrollable_frame, bg=COLORS["accent"], padx=10, pady=5)
        physical_header_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(physical_header_frame, text="Physical Characteristics", 
               font=("Roboto", 11, "bold"), bg=COLORS["accent"], fg=COLORS["text"]).pack(anchor=tk.W)
        
        # Create info grid for physical data
        physical_frame = ttk.Frame(scrollable_frame)
        physical_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        # Row 1 - Height & Weight
        ttk.Label(physical_frame, text="Height:", font=("Roboto", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(physical_frame, text=f"{pokemon.get('height', 'Unknown')}").grid(row=0, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(physical_frame, text="Weight:", font=("Roboto", 10, "bold")).grid(row=0, column=2, sticky=tk.W, pady=5)
        ttk.Label(physical_frame, text=f"{pokemon.get('weight', 'Unknown')}").grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 2 - Scale
        ttk.Label(physical_frame, text="Scale:", font=("Roboto", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(physical_frame, text=f"{pokemon.get('scale', 'Unknown')}").grid(row=1, column=1, sticky=tk.W, padx=(10, 30))
        
        # Row 3 - Friendship & Tera Type
        ttk.Label(physical_frame, text="Friendship:", font=("Roboto", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Create a visual indicator for friendship level
        friendship_value = pokemon.get('friendship', 0)
        friendship_frame = tk.Frame(physical_frame, bg=COLORS["background"])
        friendship_frame.grid(row=2, column=1, sticky=tk.W, padx=(10, 30))
        
        # Display numeric value
        ttk.Label(friendship_frame, text=str(friendship_value)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Add a visual indicator (hearts) based on friendship level
        hearts_frame = tk.Frame(friendship_frame, bg=COLORS["background"])
        hearts_frame.pack(side=tk.LEFT)
        
        # Display hearts based on friendship level (max 5 hearts)
        heart_levels = [0, 50, 100, 150, 200, 255]
        heart_colors = ["#CCCCCC", "#FF9999", "#FF6666", "#FF3333", "#FF0000", "#FF0066"]
        
        for i in range(5):
            if friendship_value >= heart_levels[i+1]:
                color = heart_colors[i+1]
            elif friendship_value >= heart_levels[i]:
                color = heart_colors[i]
            else:
                color = "#CCCCCC"  # Gray for empty hearts
                
            heart = tk.Label(hearts_frame, text="♥", font=("Roboto", 10), fg=color, bg=COLORS["background"])
            heart.pack(side=tk.LEFT, padx=1)
        
        ttk.Label(physical_frame, text="Tera Type:", font=("Roboto", 10, "bold")).grid(row=2, column=2, sticky=tk.W, pady=5)
        
        tera_type = pokemon.get('tera_type', 'Unknown')
        ttk.Label(physical_frame, text=tera_type).grid(row=2, column=3, sticky=tk.W, padx=(10, 0))
        
        # Additional Data Section (if ribbons are present)
        if 'ribbons' in pokemon and pokemon['ribbons']:
            ribbons_header_frame = tk.Frame(scrollable_frame, bg=COLORS["primary"], padx=10, pady=5)
            ribbons_header_frame.pack(fill=tk.X, pady=(10, 10))
            
            tk.Label(ribbons_header_frame, text="Ribbons & Marks", 
                   font=("Roboto", 11, "bold"), bg=COLORS["primary"], fg="white").pack(anchor=tk.W)
            
            # Create info grid for ribbons
            ribbons_frame = ttk.Frame(scrollable_frame)
            ribbons_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
            
            # Note: The ribbons are stored as integers that would need to be mapped to actual ribbon names
            # For now, just display the ribbon IDs
            ribbon_list = pokemon.get('ribbons', [])
            if ribbon_list:
                ttk.Label(ribbons_frame, text="Ribbons:", font=("Roboto", 10, "bold")).grid(row=0, column=0, sticky=tk.NW, pady=5)
                
                ribbons_text = ", ".join([f"Ribbon #{r}" for r in ribbon_list])
                ttk.Label(ribbons_frame, text=ribbons_text, wraplength=400).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Technical Details Section (trainer IDs only)
        has_technical_data = any(k in pokemon for k in ['tid', 'sid'])
        
        if has_technical_data:
            technical_header_frame = tk.Frame(scrollable_frame, bg="#666666", padx=10, pady=5)  # Darker color for technical section
            technical_header_frame.pack(fill=tk.X, pady=(10, 10))
            
            tk.Label(technical_header_frame, text="Technical Data", 
                   font=("Roboto", 11, "bold"), bg="#666666", fg="white").pack(anchor=tk.W)
            
            # Create info grid for technical data
            technical_frame = ttk.Frame(scrollable_frame)
            technical_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
            
            row = 0
            if 'tid' in pokemon:
                ttk.Label(technical_frame, text="Trainer ID:", font=("Roboto", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=3)
                ttk.Label(technical_frame, text=str(pokemon['tid'])).grid(row=row, column=1, sticky=tk.W, padx=(10, 30))
                row += 1
                
            if 'sid' in pokemon:
                ttk.Label(technical_frame, text="Secret ID:", font=("Roboto", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=3)
                ttk.Label(technical_frame, text=str(pokemon['sid'])).grid(row=row, column=1, sticky=tk.W, padx=(10, 30))
                row += 1

    def export_to_cobblemon(self):
        """Export the selected Pokémon to Cobblemon format using unparser.py."""
        if self.selected_pokemon is None:
            messagebox.showerror("Error", "No Pokémon selected!")
            self.update_status("Error: No Pokémon selected")
            return

        try:
            # Check if the file exists
            if 'file_path' not in self.selected_pokemon or not os.path.exists(self.selected_pokemon['file_path']):
                messagebox.showerror("Error", f"JSON file for {self.selected_pokemon['species']} not found!")
                self.update_status(f"Error: JSON file not found for {self.selected_pokemon['species']}")
                return

            # Get directory of the current script
            current_directory = os.path.dirname(os.path.abspath(__file__))
            unparser_script = os.path.join(current_directory, "modules", "CobblemonExporter.py")
            
            # Check if CobblemonExporter.py exists
            if not os.path.exists(unparser_script):
                messagebox.showerror("Error", f"Unparser script not found at: {unparser_script}")
                self.update_status("Error: Unparser script not found")
                return
            
            # Update status before execution
            self.update_status(f"Exporting {self.selected_pokemon['species']} to Cobblemon...")
            
            # Set up a proper environment for the subprocess with UTF-8 encoding
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            # Run CobblemonExporter.py with the CLI argument for the JSON file
            process = subprocess.run(
                [sys.executable, unparser_script, "--json", self.selected_pokemon['file_path']],
                check=False,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='backslashreplace',
                env=env
            )
            
            # Output the result to console for debugging
            print(f"Unparser output: {process.stdout}")
            print(f"Unparser errors: {process.stderr}")
            
            # Check process return code first
            if process.returncode != 0:
                if process.stderr and "UnicodeEncodeError" in process.stderr:
                    # Specific error handling for encoding issues
                    messagebox.showerror("Error", 
                        "Encoding error occurred. The file path or Pokémon data contains special characters that "
                        "cannot be processed correctly by the terminal.\n\n"
                        "Please rename your Pokémon or move files to a path without special characters.")
                    self.update_status(f"Error exporting: Encoding issue with special characters")
                else:
                    # General error handling
                    messagebox.showerror("Error", f"Export failed with error:\n{process.stderr}")
                    self.update_status("Error during Cobblemon export")
                return
            
            # Check for success message in the output
            if "Successfully processed" in process.stdout:
                messagebox.showinfo("Success", f"Successfully exported {self.selected_pokemon['species']} to Cobblemon!")
                self.update_status(f"Successfully exported {self.selected_pokemon['species']} to Cobblemon")
            else:
                # If no explicit success message but process completed, show info
                messagebox.showinfo("Information", f"Export process completed with message:\n{process.stdout.strip()}")
                self.update_status("Cobblemon export process completed")
            
        except Exception as e:
            error_msg = f"Failed to export to Cobblemon: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.update_status(f"Error: {error_msg}")
            print(f"Exception details: {e}")

    def update_folder_dropdown(self):
        """Update the folder dropdown with available subfolders."""
        folders = [COBBLEMON_FOLDER]  # Always include the main folder
        
        # Check if the main COBBLEMON_FOLDER exists
        if os.path.exists(COBBLEMON_FOLDER):
            # Get all subdirectories
            for item in os.listdir(COBBLEMON_FOLDER):
                full_path = os.path.join(COBBLEMON_FOLDER, item)
                if os.path.isdir(full_path):
                    folders.append(os.path.join(COBBLEMON_FOLDER, item))
        
        # Update the dropdown values
        self.folder_dropdown['values'] = folders
        
        # If the current folder isn't in the list, reset to the main folder
        if self.current_folder not in folders:
            self.folder_var.set(COBBLEMON_FOLDER)
            self.current_folder = COBBLEMON_FOLDER

    def on_folder_selected(self, event):
        """Handle folder selection from the dropdown."""
        selected_folder = self.folder_var.get()
        if selected_folder and selected_folder != self.current_folder:
            self.current_folder = selected_folder
            self.update_status(f"Loading Pokémon from folder: {selected_folder}")
            self.load_pokemon_data()

    def create_new_folder(self):
        """Create a new subfolder in the Cobblemon folder."""
        # Prompt the user for a folder name
        folder_name = simpledialog.askstring("Create Folder", "Enter new folder name:")
        
        # Validate folder name
        if not folder_name:
            return
            
        # Remove any invalid characters for file paths
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in [' ', '_', '-'])
        
        if not folder_name:
            messagebox.showerror("Error", "Invalid folder name. Please use alphanumeric characters, spaces, underscores, or hyphens.")
            return
            
        # Create the full path
        new_folder_path = os.path.join(COBBLEMON_FOLDER, folder_name)
        
        # Check if the folder already exists
        if os.path.exists(new_folder_path):
            messagebox.showwarning("Warning", f"Folder '{folder_name}' already exists.")
            return
            
        # Create the folder
        try:
            os.makedirs(new_folder_path)
            self.update_status(f"Created new folder: {new_folder_path}")
            
            # Update the dropdown and select the new folder
            self.update_folder_dropdown()
            self.folder_var.set(new_folder_path)
            self.current_folder = new_folder_path
            
            # Load (empty) data from the new folder
            self.load_pokemon_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder: {str(e)}")




if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD's Tk instead of tk.Tk
    app = PokemonHomeApp(root)
    root.mainloop()