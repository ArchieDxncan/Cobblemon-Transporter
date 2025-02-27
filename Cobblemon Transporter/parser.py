import nbtlib
import random
import json
import hashlib
import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import date

# Cache for UUID-to-username mappings
uuid_cache = {}

# Directory for cache
CACHE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'uuid_cache.json')

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    response = messagebox.askyesno("Import Cobblemon?", "Do you want to import a Cobblemon .dat file?")
    if not response:
        print("Import canceled.")
        return None
    
    file_path = filedialog.askopenfilename(title="Select Cobblemon .dat file", filetypes=[("DAT Files", "*.dat")])
    if not file_path:
        print("No file selected. Exiting.")
        return None
    
    return file_path

def load_nbt(file_path):
    # Load the NBT file
    try:
        nbt_file = nbtlib.load(file_path)
        return nbt_file
    except Exception as e:
        print(f"Error loading NBT file: {e}")
        return None

def generate_unique_filename(pokemon_data):
    # Use species, level, and a hash of the stats to generate a unique filename
    name = pokemon_data['species'].lower()
    stats_string = str(pokemon_data['ivs']) + str(pokemon_data['evs'])  # Example of stats-based uniqueness
    unique_number = int(hashlib.md5(stats_string.encode('utf-8')).hexdigest(), 16) % 10000
    filename = f"{name}_{unique_number}.json"
    return filename

def fetch_username_from_uuid(uuid):
    # Check if the UUID is already in the cache
    if uuid in uuid_cache:
        return uuid_cache[uuid]

    # Mojang API endpoint to get username from UUID
    url = f"https://api.mojang.com/user/profile/{uuid}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            username = data.get('name', 'Unknown')
            # Cache the result
            uuid_cache[uuid] = username
            return username
        else:
            print(f"Failed to fetch username for UUID {uuid}. Status code: {response.status_code}")
            return 'Unknown'
    except Exception as e:
        print(f"Error fetching username from UUID: {e}")
        return 'Unknown'

def extract_pokemon_data(nbt_data, slot):
    if not nbt_data:
        return None
    
    try:
        # Extract the Pokémon's main data
        pokemon_data = nbt_data[slot]  # Use the slot parameter to get the specific Pokémon

        # Extract species and remove 'cobblemon:' prefix if it exists
        species = pokemon_data['Species']
        if species.startswith('cobblemon:'):
            species = species[len('cobblemon:'):]
            
        level = int(pokemon_data['Level'])  # Convert to int

        moves = []
        hyphen_moves = load_hyphen_moves()
        
        # Check and apply hyphenation to ability
        ability = pokemon_data['Ability']['AbilityName']
        if ability in hyphen_moves:
            ability = hyphen_moves[ability].capitalize()

        if species in hyphen_moves:
            species = hyphen_moves[species].capitalize()

        for move_data in pokemon_data['MoveSet']:  # Loop through the list of Compound objects
            move_name = move_data.get('MoveName', 'Unknown')  # Access MoveName from each Compound
            
            # Check if move_name needs hyphenation
            if move_name in hyphen_moves:
                move_name = hyphen_moves[move_name]
            
            moves.append(move_name)  # Append the (potentially hyphenated) move name
    

        # Convert IVs and EVs to integers and ensure they are lists
        ivs = {stat: int(pokemon_data['IVs'].get(f'cobblemon:{stat}', 0)) for stat in ['attack', 'defence', 'hp', 'special_attack', 'special_defence', 'speed']}
        evs = {stat: int(pokemon_data['EVs'].get(f'cobblemon:{stat}', 0)) for stat in ['attack', 'defence', 'hp', 'special_attack', 'special_defence', 'speed']}
        
        # Convert Nature, Original Trainer, Health, and Experience
        nature = pokemon_data['Nature'].split(":")[-1].capitalize()
        original_trainer_uuid = pokemon_data['PokemonOriginalTrainer']
        original_trainer = fetch_username_from_uuid(original_trainer_uuid)
        health = int(pokemon_data['Health'])  # Convert to int
        experience = int(pokemon_data['Experience'])  # Convert to int

        # Get shiny status (assuming shiny is indicated by 'Shiny' key)
        shiny = int(pokemon_data.get('Shiny', 0))

        # Get the ball type (assuming 'CaughtBall' stores the ball type)
        caught_ball = pokemon_data.get('CaughtBall', 'Unknown')

        # Get the gender (assuming 'Gender' key exists and stores 'MALE' or 'FEMALE')
        gender = pokemon_data.get('Gender', 'Unknown')

        # Extract other fields
        friendship = int(pokemon_data.get('Friendship', 0))
        healing_timer = int(pokemon_data.get('HealingTimer', 0))
        gmax_factor = int(pokemon_data.get('GmaxFactor', 0))
        gmax_level = int(pokemon_data.get('DmaxLevel', 0))
        tera_type = pokemon_data.get('TeraType', 'Unknown')
        form_id = pokemon_data.get('FormId', 'normal')
        uuid = list(pokemon_data.get('UUID', []))  # Convert UUID to a list
        scale_modifier = float(pokemon_data.get('ScaleModifier', 1.0))
        nickname = pokemon_data.get('Nickname', species.capitalize())

        # Extract MetDate, MetLevel, and MetLocation from PersistentData
        persistent_data = pokemon_data.get('PersistentData', {})

        date_today = date.today().strftime('%Y-%m-%d')  # Format the date as YYYY-MM-DD
        met_date = persistent_data.get('MetDate', date_today)
        met_level = persistent_data.get('MetLevel', level)
        met_location = persistent_data.get('MetLocation', 'a lovely place')

        origin_game = persistent_data.get('OriginGame', 'Cobblemon')
        original_trainer = persistent_data.get('OriginalTrainer', fetch_username_from_uuid(original_trainer_uuid))
        language = persistent_data.get('Language', 2)
        tid = persistent_data.get('TID', )
        pid = persistent_data.get('PID', )
        sid = persistent_data.get('SID', )

        # Extract Home Tracker, Encryption Constant, Height, Weight, Scale, Ribbons, and Relearn Move Flags
        home_tracker = int(persistent_data.get('HomeTracker', 0))
        encryption_constant = int(persistent_data.get('EncryptionConstant', 0))
        height = int(persistent_data.get('Height', 0))
        weight = int(persistent_data.get('Weight', 0))
        scale = int(persistent_data.get('Scale', 0))
        ribbons = list(persistent_data.get('Ribbons', []))
        # Convert relearn flags to boolean values (true/false)
        relearn_flags = [bool(flag) for flag in persistent_data.get('RelearnFlags', [])]
        fateful_encounter = bool(persistent_data.get('FatefulEncounter', False))

        memory_data = persistent_data.get('Memories', {})
        memories = {
            "memory_type": memory_data.get('MemoryType', 0),
            "memory_intensity": memory_data.get('MemoryIntensity', 0),
            "memory_feeling": memory_data.get('MemoryFeeling', 0),
            "memory_variable": memory_data.get('MemoryVariable', 0),
        }

        # Create a simple dictionary with extracted data
        pokemon_info = {
            "species": species,
            "nickname": nickname,
            "level": level,
            "ability": ability,
            "moves": moves,  # Now this holds the move names instead of IDs
            "ivs": ivs,
            "evs": evs,
            "nature": nature,
            "original_trainer": original_trainer,
            "health": health,
            "experience": experience,
            "shiny": shiny,
            "caught_ball": caught_ball,
            "gender": gender,
            "friendship": friendship,
            "healing_timer": healing_timer,
            "gmax_factor": gmax_factor,
            "gmax_level": gmax_level,
            "tera_type": tera_type,
            "form_id": form_id,
            "uuid": uuid,
            "scale_modifier": scale_modifier,
            "met_date": met_date,
            "met_level": met_level,
            "met_location": met_location,
            "origin_game": origin_game,
            "language": language,
            "tid": tid,
            "pid": pid,
            "sid": sid,
            "home_tracker": home_tracker,
            "encryption_constant": encryption_constant,
            "height": height,
            "weight": weight,
            "scale": scale,
            "ribbons": ribbons,
            "relearn_flags": relearn_flags,
            "fateful_encounter": fateful_encounter,
            "memories": memories
        }

        return pokemon_info

    except KeyError as e:
        print(f"Missing key in NBT data: {e}")
        return None

def load_hyphen_moves():
    hyphen_moves_file = os.path.join(CACHE_DIR, 'hyphens.json')
    if os.path.exists(hyphen_moves_file):
        with open(hyphen_moves_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_pokemon_to_json(pokemon_info):
    if pokemon_info:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Define the cobblemon directory
        cobblemon_dir = os.path.join(script_dir, 'cobblemon')

        # Ensure the cobblemon directory exists
        os.makedirs(cobblemon_dir, exist_ok=True)

        filename = generate_unique_filename(pokemon_info)
        file_path = os.path.join(cobblemon_dir, filename)

        # Save the Pokémon data to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(pokemon_info, json_file, indent=4)
        print(f"Saved Pokémon data to {file_path}")
    else:
        print("No Pokémon data to save.")

def save_cache():
    # Ensure the cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    # Save the cache to the cache file
    with open(CACHE_FILE, 'w') as cache_file:
        json.dump(uuid_cache, cache_file)

def load_cache():
    # Load the cache from the cache file if it exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as cache_file:
            return json.load(cache_file)
    return {}

def main():
    # Load the cache at the start of the script
    global uuid_cache
    uuid_cache = load_cache()

    file_path =  select_file()
    nbt_data = load_nbt(file_path)

    if nbt_data:
        # Loop through all possible slots (assuming slots are named Slot0, Slot1, etc.)
        for i in range(6):  # Assuming there are up to 6 slots
            slot = f'Slot{i}'
            if slot in nbt_data:
                pokemon_info = extract_pokemon_data(nbt_data, slot)
                if pokemon_info:
                    print(f"Extracted Pokémon Data for {slot}:")
                    for key, value in pokemon_info.items():
                        print(f"{key}: {value}")
                    save_pokemon_to_json(pokemon_info)  # Save the Pokémon data to a JSON file
                else:
                    print(f"Failed to extract Pokémon data for {slot}.")
            else:
                print(f"No Pokémon found in {slot}.")

        # Check for boxed Pokémon (Box0 to Box29, each containing Slot0 to Slot29)
        for box in range(30):  
            box_key = f'Box{box}'
            if box_key in nbt_data:
                for slot in range(30):  
                    slot_key = f'Slot{slot}'
                    if slot_key in nbt_data[box_key]:  # Ensure the slot exists in the box
                        pokemon_info = extract_pokemon_data(nbt_data[box_key], slot_key)
                        if pokemon_info:
                            print(f"Extracted Pokémon Data for {box_key} -> {slot_key}:")
                            for key, value in pokemon_info.items():
                                print(f"{key}: {value}")
                            save_pokemon_to_json(pokemon_info)
                        else:
                            print(f"Failed to extract Pokémon data for {box_key} -> {slot_key}.")
    else:
        print("Failed to load NBT file.")

    # Save the cache at the end of the script
    save_cache()

if __name__ == "__main__":
    main()