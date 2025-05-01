import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import hashlib
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import tkinterdnd2
import re
import sys

# Constants
GRID_ROWS = 5
GRID_COLS = 6
BOX_SIZE = GRID_ROWS * GRID_COLS  # 30 slots per box
TOTAL_BOXES = 8  # Number of boxes per grid
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
    "separator": "#D1DEE9"        # Light grey for separators
}

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
        
        # Configure convert button style
        self.style.configure('Convert.TButton', background=COLORS["accent"], foreground=COLORS["text"],
                            padding=8, font=('Roboto', 10, 'bold'))
        
        # Configure showdown button style
        self.style.configure('Showdown.TButton', background="#4C6EF5", foreground="white",
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

    def on_drop(self, event):
        """Handle dropped files."""
        # Use regex to properly extract file paths including those with spaces.
        file_paths = re.findall(r'\{.*?\}|\S+', event.data)

        # Remove surrounding braces from paths like {C:\Some Folder\file.pk9}
        file_paths = [path.strip("{}") for path in file_paths]

        # Supported file extensions
        supported_extensions = {'.pk9', '.cb9', '.pb8', '.pk8', '.dat'}

        # Then in the same method, add a condition to handle .dat files differently
        for file_path in file_paths:
            if file_path.lower().endswith('.dat'):
                self.process_dat_file(file_path)
                self.update_status(f"Processed: {os.path.basename(file_path)}")
            elif any(file_path.lower().endswith(ext) for ext in supported_extensions):
                self.convert_file_to_json(file_path)
                self.update_status(f"Imported: {os.path.basename(file_path)}")
            else:
                messagebox.showwarning("Unsupported File", f"{file_path} is not a supported file type (.pk9, .cb9, .pb8, .pk8, .dat).")
                self.update_status("Import failed: Unsupported file type")


    def process_dat_file(self, file_path):
        """Run parser.py on a dropped .dat file."""
        try:
            self.update_status(f"Processing DAT file: {os.path.basename(file_path)}")
            # Run parser.py with the DAT file path as an argument
            subprocess.run(["python", "parser.py", "--cli", "--files", file_path], check=True)
            
            # Reload the Pokémon data to display the newly converted Pokémon
            self.load_pokemon_data()
            self.update_status(f"Successfully processed {os.path.basename(file_path)}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to process DAT file: {e}")
            self.update_status(f"Error: Failed to process DAT file: {str(e)}")

    def convert_pk9_to_json(self, file_path):
        """Convert a .pk9 file to JSON using the PB8ToJson.py script."""
        try:
            subprocess.run(["python", "PB8ToJson.py", file_path], check=True)
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
    
    def convert_file_to_json(self, file_path):
        """Convert a file to JSON using the PB8ToJson.exe tool."""
        # Get the current script directory
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Locate PB8ToJson.exe in the same directory as this script
        pb8_to_json_directory = os.path.join(current_directory, 'PB8ToJson')
        pb8_to_json_exe = os.path.join(pb8_to_json_directory, 'PB8ToJson.exe')

        # Ensure the executable exists
        if not os.path.isfile(pb8_to_json_exe):
            self.update_status(f"Error: {pb8_to_json_exe} not found.")
            return
        
        subprocess.run([pb8_to_json_exe, file_path])
        self.load_pokemon_data()
        self.update_status("Conversion completed successfully")

    def create_grids(self):
        """Create a grid for local storage."""
        left_frame = tk.Frame(self.content_frame, bg=COLORS["background"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Box title with decorative elements
        title_frame = tk.Frame(left_frame, bg=COLORS["background"])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Pokémon Storage", style="BoxTitle.TLabel").pack(side=tk.LEFT)
        
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

        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.stats_tab, text="Stats")
        self.notebook.add(self.moves_tab, text="Moves")
        
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
        
        # Add buttons frame at the bottom
        buttons_frame = tk.Frame(self.details_frame, bg=COLORS["background"], pady=10)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # "Export to Showdown" button with blue styling
        self.showdown_button = ttk.Button(buttons_frame, text="Export to Showdown", style="Showdown.TButton",
                                      command=self.export_to_showdown)
        self.showdown_button.pack(side=tk.LEFT, padx=5)
        
        # "Convert to .cb9" button with improved styling
        self.convert_button = ttk.Button(buttons_frame, text="Convert to .cb9", style="Convert.TButton", 
                                      command=self.convert_to_pb8)
        self.convert_button.pack(side=tk.RIGHT, padx=5)
        
        # Initially hide the buttons
        self.showdown_button.pack_forget()
        self.convert_button.pack_forget()

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

            # Overview Tab
            self.create_overview_tab(pokemon)

            # Stats Tab
            self.create_stats_tab(pokemon)

            # Moves Tab
            self.create_moves_tab(pokemon)
            
            # Show the buttons
            self.showdown_button.pack(side=tk.LEFT, padx=5)
            self.convert_button.pack(side=tk.RIGHT, padx=5)
            
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
            self.showdown_button.pack_forget()
            self.convert_button.pack_forget()
            
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
        
        # Create a header with name and sprite
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Try to load the sprite
        sprite_folder = SHINY_SPRITES_FOLDER if pokemon['shiny'] else SPRITES_FOLDER
        species_name = pokemon['species'].lower()
        if 'form_id' in pokemon and pokemon['form_id'].lower() in ['galar', 'alola', 'hisui', 'dusk', 'midnight', 'dawn']:
            species_name += f"-{pokemon['form_id'].lower()}"
        
        sprite_path = os.path.join(sprite_folder, f"{species_name}.png")
        
        if os.path.exists(sprite_path):
            sprite_img = Image.open(sprite_path)
            sprite_img = sprite_img.resize((136, 112), Image.Resampling.NEAREST)
            sprite_photo = ImageTk.PhotoImage(sprite_img)
            sprite_label = tk.Label(header_frame, image=sprite_photo, bg=COLORS["background"])
            sprite_label.image = sprite_photo  # Keep a reference
            sprite_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Name and nickname
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.Y, pady=5)
        
        # Show species name in bold (capitalize first letter)
        formatted_species = pokemon['species'].capitalize()
        species_label = ttk.Label(name_frame, text=formatted_species, 
                              font=("Roboto", 14, "bold"), foreground=COLORS["text"])
        species_label.pack(anchor=tk.W)
        
        # Show nickname in quotes if it's different from species (capitalize first letter)
        formatted_nickname = pokemon['nickname'].capitalize()
        if formatted_nickname.lower() != formatted_species.lower():
            nickname_label = ttk.Label(name_frame, text=f"\"{pokemon['nickname']}\"", 
                           font=("Roboto", 12, "italic"), foreground="#666666")
            nickname_label.pack(anchor=tk.W)
        
        # Shiny indicator if applicable
        if pokemon['shiny']:
            shiny_frame = tk.Frame(name_frame, bg=COLORS["accent"], bd=0, relief=tk.FLAT, padx=5, pady=2)
            shiny_frame.pack(anchor=tk.W, pady=(5, 0))
            shiny_label = tk.Label(shiny_frame, text="✨ SHINY", font=("Roboto", 8, "bold"), 
                                 fg=COLORS["text"], bg=COLORS["accent"])
            shiny_label.pack()
        
        # Separator
        separator = ttk.Separator(scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10, padx=10)
        
        # Create info grid for better layout
        info_frame = ttk.Frame(scrollable_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Row 1
        ttk.Label(info_frame, text="Level:", font=("Roboto", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=str(pokemon['level'])).grid(row=0, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(info_frame, text="Gender:", font=("Roboto", 10, "bold")).grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Gender with icons instead of text
        gender_frame = tk.Frame(info_frame, bg=COLORS["background"])
        gender_frame.grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        gender = pokemon['gender'].upper()
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
                             fg=gender_color, bg=COLORS["background"])
        gender_label.pack(side=tk.LEFT)
        
        # Row 2
        ttk.Label(info_frame, text="Ability:", font=("Roboto", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Format ability name - capitalize each word
        ability_name = pokemon['ability']
        formatted_ability = " ".join(word.capitalize() for word in ability_name.split())
        ttk.Label(info_frame, text=formatted_ability).grid(row=1, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(info_frame, text="Nature:", font=("Roboto", 10, "bold")).grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # Format nature name - capitalize
        nature_name = pokemon['nature'].capitalize()
        ttk.Label(info_frame, text=nature_name).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 3
        ttk.Label(info_frame, text="Caught in:", font=("Roboto", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Format ball name - remove "cobblemon:" prefix, replace underscores with spaces, capitalize each word
        ball_name = pokemon['caught_ball']
        if "cobblemon:" in ball_name.lower():
            ball_name = ball_name[ball_name.lower().index("cobblemon:") + 10:]  # Remove "cobblemon:" prefix
        ball_name = ball_name.replace("_", " ")
        formatted_ball = " ".join(word.capitalize() for word in ball_name.split())
        
        ttk.Label(info_frame, text=formatted_ball).grid(row=2, column=1, sticky=tk.W, padx=(10, 30))
        
        ttk.Label(info_frame, text="Trainer:", font=("Roboto", 10, "bold")).grid(row=2, column=2, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=pokemon['original_trainer']).grid(row=2, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 4
        ttk.Label(info_frame, text="Experience:", font=("Roboto", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=str(pokemon['experience'])).grid(row=3, column=1, sticky=tk.W, padx=(10, 30), columnspan=3)

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
        
        # Moves list with improved styling
        moves_frame = ttk.Frame(main_frame)
        moves_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a table-like header
        ttk.Label(moves_frame, text="Move Name", font=("Roboto", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Label(moves_frame, text="Type", font=("Roboto", 10, "bold")).grid(row=0, column=1, sticky=tk.W, pady=(0, 10), padx=20)
        
        # Add separator under header
        separator = ttk.Separator(moves_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        # Display moves with alternating row colors
        moves = pokemon.get('moves', [])
        for i, move in enumerate(moves):
            if move is None:  # Skip None values
                continue
                
            # We don't have move types in the data, so just showing the move names
            bg_color = COLORS["background"] if i % 2 == 0 else "#F0F5FA"
            
            # Create frame for the row with background color
            row_frame = tk.Frame(moves_frame, bg=bg_color)
            row_frame.grid(row=i+2, column=0, columnspan=2, sticky=tk.EW)
            
            # Format move name - replace underscores with spaces and capitalize each word
            formatted_move = move.replace("_", " ")
            formatted_move = " ".join(word.capitalize() for word in formatted_move.split("-"))
            
            # Move name
            ttk.Label(row_frame, text=formatted_move, background=bg_color).grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)

    def convert_to_pb8(self):
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

        # Assuming the .exe is named JsonToPB8.exe and is in JsonToPB8 directory
        converter_exe = "JsonToPB8/JsonToPB8.exe"
        if not os.path.exists(converter_exe):
            messagebox.showerror("Error", "Converter executable not found!")
            self.update_status("Error: Converter executable not found")
            return

        try:
            # Update status before conversion
            self.update_status(f"Converting {self.selected_pokemon['species']} to .cb9...")
            
            # Run the converter .exe with the JSON file as an argument
            subprocess.run([converter_exe, json_file_path], check=True)
            
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
        """Load all Pokémon data from JSON files in the 'cobblemon' folder."""
        try:
            # Ensure the cobblemon directory exists
            if not os.path.exists(COBBLEMON_FOLDER):
                os.makedirs(COBBLEMON_FOLDER)
                self.update_status(f"Created directory: {COBBLEMON_FOLDER}")
                return
                
            # Get all JSON files in the directory
            files = [f for f in os.listdir(COBBLEMON_FOLDER) if f.endswith(".json")]
            
            if not files:
                self.update_status("No Pokémon data found. Try importing some files.")
                return
                
            # Sort files by modification date (oldest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(COBBLEMON_FOLDER, x)))
            
            # Clear existing storage first
            self.local_storage = [[None] * BOX_SIZE for _ in range(TOTAL_BOXES)]
            
            # Keep track of used slots to avoid duplicates
            used_slots = set()
            
            # Load Pokémon data
            pokemon_data = []
            for file in files:
                file_path = os.path.join(COBBLEMON_FOLDER, file)
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
            
            # Place remaining Pokémon in empty slots
            for pokemon in pokemon_data:
                placed = False
                for box_index in range(TOTAL_BOXES):
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
            self.update_status(f"Loaded {total_loaded} Pokémon across {min(total_loaded // BOX_SIZE + 1, TOTAL_BOXES)} boxes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Pokémon data: {e}")
            self.update_status(f"Error loading Pokémon data: {str(e)}")

    def run_parser_script(self):
        """Run the parser.py script."""
        try:
            self.update_status("Running parser.py...")
            subprocess.run(["python", "parser.py"], check=True)
            self.update_status("parser.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute parser.py: {e}")
            self.update_status(f"Error: Failed to execute parser.py: {str(e)}")

    def run_pb8_to_json_script(self):
        """Run the PB8ToJson.py script."""
        try:
            self.update_status("Running PB8ToJson.py...")
            subprocess.run(["python", "PB8ToJson.py"], check=True)
            self.update_status("PB8ToJson.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute PB8ToJson.py: {e}")
            self.update_status(f"Error: Failed to execute PB8ToJson.py: {str(e)}")

    def run_export_script(self):
        """Run the unparser.py script."""
        try:
            self.update_status("Running unparser.py...")
            subprocess.run(["python", "unparser.py"], check=True)
            self.update_status("unparser.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute unparser.py: {e}")
            self.update_status(f"Error: Failed to execute unparser.py: {str(e)}")

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
        converter_exe = "JsonToPB8/JsonToPB8.exe"
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
                subprocess.run([converter_exe, json_file_path], check=True)
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
            button.bind("<Leave>", lambda e, btn=button, c=canvas, idx=i: self.on_button_leave(e, btn, c, idx))

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


if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD's Tk instead of tk.Tk
    app = PokemonHomeApp(root)
    root.mainloop()