import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import hashlib
from PIL import Image, ImageTk

# Constants
GRID_ROWS = 5
GRID_COLS = 6
BOX_SIZE = GRID_ROWS * GRID_COLS  # 30 slots per box
TOTAL_BOXES = 8  # Number of boxes per grid
COBBLEMON_FOLDER = "cobblemon"  # Path to the folder where Cobblemon JSON files are stored
SPRITES_FOLDER = "sprites/regular"  # Path to the folder where Pokémon sprites are stored
SHINY_SPRITES_FOLDER = "sprites/shiny"  # Path to the folder where Shiny Pokémon sprites are stored

class PokemonHomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon PC")
        
        # Local storage for Pokémon data
        self.local_storage = [[None] * BOX_SIZE for _ in range(TOTAL_BOXES)]  # Multiple boxes
        
        # Current box indices
        self.current_local_box = 0
        
        # Track the currently selected Pokémon
        self.selected_pokemon = None
        
        # UI Layout
        self.create_grids()
        self.create_navigation_buttons()

        # Detailed info panel
        self.create_details_panel()

        # Menu Bar
        self.create_menu()

        # Load Pokémon data from JSON files in the "cobblemon" folder
        self.load_pokemon_data()

    def create_grids(self):
        """Create a grid for local storage."""
        tk.Label(self.root, text="Local Storage", font=("Arial", 14)).grid(row=0, column=0, pady=10)
        self.local_buttons = self.create_grid(1, 0, self.local_storage, "local")

    def create_grid(self, row, col, data, grid_type):
        """Create a grid of buttons for Pokémon storage."""
        frame = tk.Frame(self.root)
        frame.grid(row=row, column=col, padx=20, pady=10)
        
        buttons = []
        for i in range(BOX_SIZE):
            button = tk.Button(frame, bg="lightgrey", relief="raised", width=6, height=3)
            button.grid(row=i // GRID_COLS, column=i % GRID_COLS, padx=2, pady=2)
            button.bind("<Button-1>", lambda e, idx=i, grid=grid_type: self.show_pokemon_info(e, grid, idx))
            buttons.append(button)
        return buttons

    def create_navigation_buttons(self):
        """Create navigation buttons for cycling between boxes."""
        # Local Storage Navigation
        self.local_nav_frame = tk.Frame(self.root)
        self.local_nav_frame.grid(row=2, column=0, pady=10)
        tk.Button(self.local_nav_frame, text="<<", command=lambda: self.cycle_box("local", -1)).pack(side="left")
        self.local_box_label = tk.Label(self.local_nav_frame, text="Box 1")
        self.local_box_label.pack(side="left", padx=10)
        tk.Button(self.local_nav_frame, text=">>", command=lambda: self.cycle_box("local", 1)).pack(side="left")

    def cycle_box(self, grid_type, direction):
        """Cycle between boxes."""
        if grid_type == "local":
            self.current_local_box = (self.current_local_box + direction) % TOTAL_BOXES
            self.local_box_label.config(text=f"Box {self.current_local_box + 1}")
        self.update_grid_buttons()

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
                    if pokemon['form_id'].lower() in ['galar', 'alola', 'hisui']:
                        species_name += f"-{pokemon['form_id'].lower()}"
            
                sprite_path = os.path.join(sprite_folder, f"{species_name}.png")
        
                if os.path.exists(sprite_path):
                    img = Image.open(sprite_path)
                    img = img.resize((68, 56), Image.Resampling.BICUBIC)  # Resize the sprite to fit the button
                    img = ImageTk.PhotoImage(img)
                    button.config(image=img, text="", compound=tk.BOTTOM, width=46, height=50, anchor='s')  # Adjust padding
                    button.image = img  # Keep a reference to avoid garbage collection
                else:
                    button.config(bg="green", text=pokemon['species'])
            else:
                button.config(bg="lightgrey", text="", image=None)

    def create_details_panel(self):
        """Create a panel to display Pokémon details with tabs."""
        self.details_frame = ttk.Frame(self.root)
        self.details_frame.grid(row=1, column=1, padx=20, pady=10)

        # Create a Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.details_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.overview_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.moves_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.stats_tab, text="Stats")
        self.notebook.add(self.moves_tab, text="Moves")

        # Add "Convert to .pb8" button
        self.convert_button = ttk.Button(self.details_frame, text="Convert to .cb9", command=self.convert_to_pb8)
        self.convert_button.pack(pady=10)

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

    def create_overview_tab(self, pokemon):
        """Populate the Overview tab with Pokémon details."""
        ttk.Label(self.overview_tab, text=f"{pokemon['species']} ({pokemon['nickname']})", font=("Arial", 12)).pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Level: {pokemon['level']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Gender: {pokemon['gender']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Shiny: {'Yes' if pokemon['shiny'] else 'No'}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Ability: {pokemon['ability']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Caught in: {pokemon['caught_ball']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Nature: {pokemon['nature']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Original Trainer: {pokemon['original_trainer']}").pack(pady=5)
        ttk.Label(self.overview_tab, text=f"Experience: {pokemon['experience']}").pack(pady=5)

    def create_stats_tab(self, pokemon):
        """Populate the Stats tab with IVs and EVs."""
        # IVs
        ttk.Label(self.stats_tab, text="IVs", font=("Arial", 12)).pack(pady=5)
        ivs_frame = ttk.Frame(self.stats_tab)
        ivs_frame.pack(pady=5)
        ttk.Label(ivs_frame, text=f"Attack: {pokemon['ivs']['attack']}").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(ivs_frame, text=f"Defence: {pokemon['ivs']['defence']}").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(ivs_frame, text=f"HP: {pokemon['ivs']['hp']}").grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(ivs_frame, text=f"Special Attack: {pokemon['ivs']['special_attack']}").grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(ivs_frame, text=f"Special Defence: {pokemon['ivs']['special_defence']}").grid(row=2, column=0, padx=5, pady=2)
        ttk.Label(ivs_frame, text=f"Speed: {pokemon['ivs']['speed']}").grid(row=2, column=1, padx=5, pady=2)

        # EVs
        ttk.Label(self.stats_tab, text="EVs", font=("Arial", 12)).pack(pady=5)
        evs_frame = ttk.Frame(self.stats_tab)
        evs_frame.pack(pady=5)
        ttk.Label(evs_frame, text=f"Attack: {pokemon['evs']['attack']}").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(evs_frame, text=f"Defence: {pokemon['evs']['defence']}").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(evs_frame, text=f"HP: {pokemon['evs']['hp']}").grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(evs_frame, text=f"Special Attack: {pokemon['evs']['special_attack']}").grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(evs_frame, text=f"Special Defence: {pokemon['evs']['special_defence']}").grid(row=2, column=0, padx=5, pady=2)
        ttk.Label(evs_frame, text=f"Speed: {pokemon['evs']['speed']}").grid(row=2, column=1, padx=5, pady=2)

    def create_moves_tab(self, pokemon):
        """Populate the Moves tab with the Pokémon's moves."""
        ttk.Label(self.moves_tab, text="Moves", font=("Arial", 12)).pack(pady=5)
        moves_frame = ttk.Frame(self.moves_tab)
        moves_frame.pack(pady=5)
        for i, move in enumerate(pokemon['moves']):
            ttk.Label(moves_frame, text=move).grid(row=i, column=0, padx=5, pady=2, sticky="w")

    def convert_to_pb8(self):
        """Convert the selected Pokémon's JSON file to .pb8 using the external .exe."""
        if self.selected_pokemon is None:
            messagebox.showerror("Error", "No Pokémon selected!")
            return

         # Generate the unique filename based on the Pokémon's species, IVs, and EVs
        name = self.selected_pokemon['species'].lower()
        stats_string = str(self.selected_pokemon['ivs']) + str(self.selected_pokemon['evs'])
        unique_number = int(hashlib.md5(stats_string.encode('utf-8')).hexdigest(), 16) % 10000
        json_file_path = os.path.join(COBBLEMON_FOLDER, f"{name}_{unique_number}.json")

        if not os.path.exists(json_file_path):
            messagebox.showerror("Error", f"JSON file for {self.selected_pokemon['species']} not found!")
            return

        # Assuming the .exe is named "converter.exe" and is in the same directory as the script
        converter_exe = "JsonToPB8/JsonToPB8.exe"
        if not os.path.exists(converter_exe):
            messagebox.showerror("Error", "Converter executable not found!")
            return

        try:
            # Run the converter .exe with the JSON file as an argument
            subprocess.run([converter_exe, json_file_path], check=True)
            messagebox.showinfo("Success", f"Conversion successful: {json_file_path}.cb9 created!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")

    def get_selected_pokemon(self):
        """Get the currently selected Pokémon."""
        return self.selected_pokemon

    def load_pokemon_data(self):
        """Load all Pokémon data from JSON files in the 'cobblemon' folder."""
        try:
            files = [f for f in os.listdir(COBBLEMON_FOLDER) if f.endswith(".json")]
            # Sort files by modification date (oldest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(COBBLEMON_FOLDER, x)))
            
            pokemon_data = []
            for file in files:
                file_path = os.path.join(COBBLEMON_FOLDER, file)
                with open(file_path, "r") as f:
                    pokemon = json.load(f)
                    pokemon_data.append(pokemon)
            
            # Add the Pokémon data to the local storage
            for i, pokemon in enumerate(pokemon_data):
                box_index = i // BOX_SIZE
                slot_index = i % BOX_SIZE
                self.local_storage[box_index][slot_index] = pokemon
            
            self.update_grid_buttons()
            print("Success", "Pokémon data loaded successfully!")
        except Exception as e:
            print("Error", f"Failed to load Pokémon data: {e}")

    def run_parser_script(self):
        """Run the parser.py script."""
        try:
            subprocess.run(["python", "parser.py"], check=True)
            print("Success", "parser.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            print("Error", f"Failed to execute parser.py: {e}")

            self.load_pokemon_data()

    def run_pb8_to_json_script(self):
        """Run the PB8ToJson.py script."""
        try:
            subprocess.run(["python", "PB8ToJson.py"], check=True)
            print("Success", "PB8ToJson.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute PB8ToJson.py: {e}")

    def run_export_script(self):
        """Run the PB8ToJson.py script."""
        try:
            subprocess.run(["python", "unparser.py"], check=True)
            print("Success", "unparser.py executed successfully!")
            self.load_pokemon_data()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute PB8ToJson.py: {e}")

    def mass_convert_to_pb8(self):
        """Convert selected JSON files to .pb8 using an external .exe."""
        
        # Open a file dialog to select the JSON files
        json_file_paths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        
        if not json_file_paths:
            # User canceled the file selection
            return

        # Assuming the .exe is named "converter.exe" and is in the same directory as the script
        converter_exe = "JsonToPB8/JsonToPB8.exe"
        if not os.path.exists(converter_exe):
            messagebox.showerror("Error", "Converter executable not found!")
            return

        for json_file_path in json_file_paths:
            if not os.path.exists(json_file_path):
                messagebox.showerror("Error", f"File not found: {json_file_path}")
                continue

            try:
                # Run the converter .exe with the JSON file as an argument
                subprocess.run([converter_exe, json_file_path], check=True)
                messagebox.showinfo("Success", f"Conversion successful: {json_file_path}.cb9 created!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Conversion failed for {json_file_path}: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred for {json_file_path}: {e}")

    def create_menu(self):
        """Create a menu bar with save and load options."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Load Pokémon Data", command=self.load_pokemon_data)  # New option
        file_menu.add_command(label="Export to Cobblemon", command=self.run_export_script)  # New option
        file_menu.add_command(label="Export to Pokémon", command=self.mass_convert_to_pb8)  # New option
        file_menu.add_command(label="Import .dat", command=self.run_parser_script)  # New option
        file_menu.add_command(label="Import .pk9", command=self.run_pb8_to_json_script)  # New option
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)


if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonHomeApp(root)
    root.mainloop()