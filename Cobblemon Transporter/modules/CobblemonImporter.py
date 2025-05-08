import nbtlib
import random
import json
import hashlib
import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
from datetime import date
import argparse
import sys
import threading
from nbtlib import nbt
from nbtlib.tag import Compound, List, String, Int, Float, Byte, Short, Long, Double, ByteArray, IntArray, LongArray
import time
import logging

# Define colors directly in code
THEME_PRIMARY = "#3f51b5"  # Primary blue
THEME_SECONDARY = "#303f9f"  # Darker blue
THEME_ACCENT = "#ff4081"  # Pink accent
THEME_BACKGROUND = "#f5f5f6"  # Light gray background
THEME_SURFACE = "#ffffff"  # White surface
THEME_ERROR = "#f44336"  # Red for errors
THEME_SUCCESS = "#4caf50"  # Green for success
THEME_TEXT_PRIMARY = "#212121"  # Dark text
THEME_TEXT_SECONDARY = "#757575"  # Gray text

# Cache for UUID-to-username mappings
uuid_cache = {}

# Directory for cache
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'uuid_cache.json')

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cobblemon')

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Parse Cobblemon .dat files')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode without GUI dialogs')
    parser.add_argument('--files', type=str, help='Path to the .dat file to process')
    parser.add_argument('--output', type=str, help='Output directory for the parsed files (default: "cobblemon" folder in script directory)')
    return parser.parse_args()

def select_file():
    file_path = filedialog.askopenfilename(title="Select Cobblemon .dat file", filetypes=[("DAT Files", "*.dat")])
    return file_path

def load_nbt(file_path):
    # Load the NBT file
    try:
        nbt_file = nbt.load(file_path)
        # Debug: Print the structure of the NBT file to understand it better
        print("NBT File Structure:")
        print(f"Type of nbt_file: {type(nbt_file)}")
        print(f"Top-level keys: {list(nbt_file.keys())}")
        
        # Check if there are party slots (Slot0-Slot5)
        party_slots = [key for key in nbt_file.keys() if key.startswith('Slot') and key[4:].isdigit()]
        if party_slots:
            print(f"Found party slots: {party_slots}")
            # Print structure of a party Pokémon as example
            if party_slots:
                first_slot = party_slots[0]
                print(f"Party Pokémon structure ({first_slot}):")
                if first_slot in nbt_file:
                    print(f"Keys in {first_slot}: {list(nbt_file[first_slot].keys()) if hasattr(nbt_file[first_slot], 'keys') else 'Not a dictionary'}")
        
        # Check if there are box structures directly in the top level
        box_keys = [key for key in nbt_file.keys() if key.startswith('Box') and key[3:].isdigit()]
        if box_keys:
            print(f"Found box keys at top level: {box_keys}")
            # Print structure of the first box as example
            if box_keys:
                first_box = box_keys[0]
                print(f"First box structure ({first_box}):")
                if hasattr(nbt_file[first_box], 'keys'):
                    print(f"Keys in {first_box}: {list(nbt_file[first_box].keys())}")
                    # Print a sample slot from this box
                    slot_keys = [key for key in nbt_file[first_box].keys() if key.startswith('Slot') and key[4:].isdigit()]
                    if slot_keys:
                        sample_slot = slot_keys[0]
                        print(f"Sample slot in {first_box}: {sample_slot}")
                        print(f"Keys in {first_box}.{sample_slot}: {list(nbt_file[first_box][sample_slot].keys()) if hasattr(nbt_file[first_box][sample_slot], 'keys') else 'Not a dictionary'}")
                else:
                    print(f"{first_box} is not a dictionary-like object, it's a {type(nbt_file[first_box])}")
        
        # Check more detailed PC structure
        if 'pc' in nbt_file:
            print("\nFound 'pc' key in top level")
            if hasattr(nbt_file['pc'], 'keys'):
                print(f"Keys in 'pc': {list(nbt_file['pc'].keys())}")
                
                # Check if the PC has a boxes list/array
                if 'boxes' in nbt_file['pc']:
                    print(f"'pc.boxes' type: {type(nbt_file['pc']['boxes'])}")
                    if isinstance(nbt_file['pc']['boxes'], list):
                        print(f"Number of boxes in pc.boxes: {len(nbt_file['pc']['boxes'])}")
                        if len(nbt_file['pc']['boxes']) > 0:
                            first_box = nbt_file['pc']['boxes'][0]
                            print(f"First box in pc.boxes type: {type(first_box)}")
                            if hasattr(first_box, 'keys'):
                                print(f"Keys in first box: {list(first_box.keys())}")
                                
                                # Check if there's a 'pokemon' list in the box
                                if 'pokemon' in first_box and isinstance(first_box['pokemon'], list):
                                    print(f"Number of Pokémon in first box: {len(first_box['pokemon'])}")
                                    if len(first_box['pokemon']) > 0:
                                        print(f"First Pokémon in box type: {type(first_box['pokemon'][0])}")
                                        if hasattr(first_box['pokemon'][0], 'keys'):
                                            print(f"Keys in first Pokémon: {list(first_box['pokemon'][0].keys())}")
                                            # Particularly interested in slot_number for our use case
                                            if 'slot_number' in first_box['pokemon'][0]:
                                                print(f"slot_number value: {first_box['pokemon'][0]['slot_number']}")
                
                # Check if PC has direct Box0, Box1, etc. structure
                pc_box_keys = [key for key in nbt_file['pc'].keys() if key.startswith('Box') and key[3:].isdigit()]
                if pc_box_keys:
                    print(f"Found box keys inside 'pc': {pc_box_keys}")
                    # Print structure of the first box as example
                    first_pc_box = pc_box_keys[0]
                    print(f"First PC box structure ({first_pc_box}):")
                    if hasattr(nbt_file['pc'][first_pc_box], 'keys'):
                        print(f"Keys in pc.{first_pc_box}: {list(nbt_file['pc'][first_pc_box].keys())}")
            else:
                print(f"'pc' is not a dictionary-like object, it's a {type(nbt_file['pc'])}")
        
        return nbt_file
    except Exception as e:
        print(f"Error loading NBT file: {str(e)}")
        return None, str(e)

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
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'PokemonPC/1.0'
    }
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                username = data.get('name', 'Unknown')
                # Cache the result
                uuid_cache[uuid] = username
                return username
            elif response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            return 'Unknown'
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            return 'Unknown'
    return 'Unknown'

def extract_pokemon_data(nbt_data, slot):
    if not nbt_data:
        return None, "Invalid NBT data"
    
    try:
        # Parse the slot parameter to get the actual data
        pokemon_data = None
        box_number = None
        slot_number = None
        
        # Check if the slot parameter is a direct key (e.g., 'Slot0' for party)
        if slot in nbt_data:
            pokemon_data = nbt_data[slot]
            # This is a party Pokémon - assign to box 0 (party)
            if slot.startswith('Slot') and slot[4:].isdigit():
                try:
                    box_number = 0  # Party Pokémon (box 0)
                    slot_number = int(slot[4:]) + 1  # Convert from 0-indexed to 1-indexed
                except ValueError:
                    pass
        # Check if the slot parameter is a compound key (e.g., 'Box0 -> Slot1')
        elif '->' in slot:
            parts = slot.split(' -> ')
            if len(parts) == 2 and parts[0].startswith('Box') and parts[1].startswith('Slot'):
                box_key = parts[0]
                slot_key = parts[1]
                
                # Get box and slot indices
                try:
                    box_idx = int(box_key[3:])
                    slot_idx = int(slot_key[4:])
                    
                    # Track if we found the data
                    found = False
                    
                    # Try strategy 1: Direct Box0/Slot0 access at top level
                    if box_key in nbt_data and slot_key in nbt_data[box_key]:
                        pokemon_data = nbt_data[box_key][slot_key]
                        box_number = box_idx + 1  # Convert from 0-indexed to 1-indexed
                        slot_number = slot_idx + 1  # Convert from 0-indexed to 1-indexed
                        found = True
                    
                    # Try strategy 2: pc.boxes[box_idx].pokemon array with slot_number
                    if not found and 'pc' in nbt_data and 'boxes' in nbt_data['pc'] and isinstance(nbt_data['pc']['boxes'], list):
                        # Check if the box index is valid
                        if 0 <= box_idx < len(nbt_data['pc']['boxes']):
                            box = nbt_data['pc']['boxes'][box_idx]
                            
                            # Check if the Pokemon list exists in this box
                            if 'pokemon' in box and isinstance(box['pokemon'], list):
                                # Find the Pokemon with matching slot in this box
                                for poke in box['pokemon']:
                                    if 'slot_number' in poke and poke['slot_number'] == slot_idx:
                                        pokemon_data = poke
                                        box_number = box_idx + 1  # Convert from 0-indexed to 1-indexed
                                        slot_number = slot_idx + 1  # Convert from 0-indexed to 1-indexed
                                        found = True
                                        break
                    
                    # Try strategy 3: Direct pc.Box0/Slot0 access
                    if not found and 'pc' in nbt_data:
                        if box_key in nbt_data['pc'] and slot_key in nbt_data['pc'][box_key]:
                            pokemon_data = nbt_data['pc'][box_key][slot_key]
                            box_number = box_idx + 1
                            slot_number = slot_idx + 1
                            found = True
                    
                    # Try strategy 4: Maybe box_idx.slot_idx format in pc
                    if not found and 'pc' in nbt_data:
                        pc_data = nbt_data['pc']
                        # Convert string box/slot index to actual keys
                        str_box_idx = str(box_idx)
                        str_slot_idx = str(slot_idx)
                        
                        if str_box_idx in pc_data and isinstance(pc_data[str_box_idx], dict):
                            if str_slot_idx in pc_data[str_box_idx]:
                                pokemon_data = pc_data[str_box_idx][str_slot_idx]
                                box_number = box_idx + 1
                                slot_number = slot_idx + 1
                                found = True
                    
                    # Try strategy 5: Maybe just a single pc.pokemon array with indices
                    if not found and 'pc' in nbt_data and 'pokemon' in nbt_data['pc'] and isinstance(nbt_data['pc']['pokemon'], list):
                        for poke in nbt_data['pc']['pokemon']:
                            if ('box_number' in poke and poke['box_number'] == box_idx and
                                'slot_number' in poke and poke['slot_number'] == slot_idx):
                                pokemon_data = poke
                                box_number = box_idx + 1
                                slot_number = slot_idx + 1
                                found = True
                                break
                    
                    if not found:
                        return None, f"Could not find Pokémon data for {slot} in any NBT structure"
                
                except (ValueError, IndexError, KeyError) as e:
                    return None, f"Error parsing slot format '{slot}': {str(e)}"
        
        # If we couldn't get the Pokémon data, return an error
        if pokemon_data is None:
            return None, f"Could not extract Pokémon data from slot: {slot}"
        
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
        
        # Extract egg data
        egg_location = persistent_data.get('EggLocation', '0')
        egg_date = persistent_data.get('EggDate', '')
        is_egg = bool(persistent_data.get('IsEgg', False))
        
        # Extract Pokérus data
        pokerus_strain = int(persistent_data.get('PokerusStrain', 0))
        pokerus_days = int(persistent_data.get('PokerusDays', 0))
        
        # Extract handler data
        current_handler = int(persistent_data.get('CurrentHandler', 0))
        handling_trainer_name = persistent_data.get('HandlingTrainerName', '')
        handling_trainer_gender = int(persistent_data.get('HandlingTrainerGender', 0))
        handling_trainer_friendship = int(persistent_data.get('HandlingTrainerFriendship', 0))
        original_trainer_gender = int(persistent_data.get('OriginalTrainerGender', 0))
        
        # Extract ability and nature data
        ability_number = int(persistent_data.get('AbilityNumber', 1))
        stat_nature = persistent_data.get('StatNature', '')
        
        # Extract stats and type data
        characteristic = int(persistent_data.get('Characteristic', -1))
        tsv = int(persistent_data.get('TSV', 0))
        psv = int(persistent_data.get('PSV', 0))
        hp_type = int(persistent_data.get('HPType', 0))
        hp_power = int(persistent_data.get('HPPower', 0))
        iv_total = int(persistent_data.get('IVTotal', 0))
        potential_rating = int(persistent_data.get('PotentialRating', 0))
        
        # Extract relearn moves
        relearn_move1 = int(persistent_data.get('RelearnMove1', 0))
        relearn_move2 = int(persistent_data.get('RelearnMove2', 0))
        relearn_move3 = int(persistent_data.get('RelearnMove3', 0))
        relearn_move4 = int(persistent_data.get('RelearnMove4', 0))
        
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
            "memories": memories,
            "egg_location": egg_location,
            "egg_date": egg_date,
            "is_egg": is_egg,
            "pokerus_strain": pokerus_strain,
            "pokerus_days": pokerus_days,
            "current_handler": current_handler,
            "handling_trainer_name": handling_trainer_name,
            "handling_trainer_gender": handling_trainer_gender,
            "handling_trainer_friendship": handling_trainer_friendship,
            "original_trainer_gender": original_trainer_gender,
            "ability_number": ability_number,
            "stat_nature": stat_nature,
            "characteristic": characteristic,
            "tsv": tsv,
            "psv": psv,
            "hp_type": hp_type,
            "hp_power": hp_power,
            "iv_total": iv_total,
            "potential_rating": potential_rating,
            "relearn_move1": relearn_move1,
            "relearn_move2": relearn_move2,
            "relearn_move3": relearn_move3,
            "relearn_move4": relearn_move4
        }
        
        # Add box and slot information if available
        if box_number is not None and slot_number is not None:
            pokemon_info['box_number'] = box_number
            pokemon_info['slot_number'] = slot_number
        
        return pokemon_info, None
    except Exception as e:
        import traceback
        error_msg = f"Error extracting pokemon data: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Print for debugging
        return None, error_msg

def load_hyphen_moves():
    hyphen_moves_file = os.path.join(CACHE_DIR, 'hyphens.json')
    if os.path.exists(hyphen_moves_file):
        with open(hyphen_moves_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def find_available_box_slot():
    """Find an available box slot for a Pokémon by checking existing JSON files"""
    try:
        # Use the global output directory
        global OUTPUT_DIR
        
        # Ensure the directory exists
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            # If directory was just created, first slot in first box is available
            return 1, 1
        
        # Maximum box and slot numbers
        MAX_BOXES = 30
        MAX_SLOTS_PER_BOX = 30
        
        # Keep track of occupied slots
        occupied_slots = set()
        
        # Parse all existing JSON files to find occupied slots
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(OUTPUT_DIR, filename), 'r') as f:
                        pokemon_data = json.load(f)
                        if 'box_number' in pokemon_data and 'slot_number' in pokemon_data:
                            box_num = pokemon_data['box_number']
                            slot_num = pokemon_data['slot_number']
                            occupied_slots.add((box_num, slot_num))
                except:
                    # Skip files that can't be parsed
                    continue
        
        # Find first available slot
        for box in range(1, MAX_BOXES + 1):
            for slot in range(1, MAX_SLOTS_PER_BOX + 1):
                if (box, slot) not in occupied_slots:
                    return box, slot
        
        # If all slots are occupied, default to box 1, slot 1 (will overwrite)
        return 1, 1
    except Exception as e:
        # In case of any error, default to box 1, slot 1
        return 1, 1

def save_pokemon_to_json(pokemon_info):
    if pokemon_info:
        # Get the output directory (use the global variable that may have been set via command line)
        global OUTPUT_DIR
        
        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Use existing box and slot if available, otherwise find available ones
        if 'box_number' in pokemon_info and 'slot_number' in pokemon_info:
            box_num = pokemon_info['box_number']
            slot_num = pokemon_info['slot_number']
        else:
            box_num, slot_num = find_available_box_slot()
            # Add box and slot information to the Pokémon data
            pokemon_info['box_number'] = box_num
            pokemon_info['slot_number'] = slot_num

        filename = generate_unique_filename(pokemon_info)
        file_path = os.path.join(OUTPUT_DIR, filename)

        # Save the Pokémon data to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(pokemon_info, json_file, indent=4)
        return f"Saved to {filename} (Box {box_num}, Slot {slot_num})"
    else:
        return "No Pokémon data to save."

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

def process_file(file_path, output_text, progress_var=None, status_label=None):
    """Process a .dat file and display results in the output text widget"""
    if not file_path:
        output_text.insert(tk.END, "No file selected.\n")
        return

    # Update status label if provided
    if status_label:
        status_label.config(text=f"Processing: {os.path.basename(file_path)}")
    
    output_text.insert(tk.END, f"Processing file: {file_path}\n", "heading")
    output_text.see(tk.END)
    
    nbt_data = load_nbt(file_path)
    
    if isinstance(nbt_data, tuple):  # Error occurred
        nbt_data, error = None, nbt_data[1]
        output_text.insert(tk.END, f"❌ Error loading NBT file: {error}\n", "error")
        output_text.see(tk.END)
        if status_label:
            status_label.config(text="Error loading file")
        return
    
    pokemon_count = 0
    error_count = 0
    total_possible = 0  # For progress calculation
    
    # Count total possible Pokémon slots for progress bar
    # Party slots
    total_possible += sum(1 for i in range(6) if f'Slot{i}' in nbt_data)
    
    # Check for different PC box structures
    box_structure = "unknown"
    if any(f'Box{i}' in nbt_data for i in range(30)):
        # Traditional Box0, Box1, etc. structure
        box_structure = "direct"
        for box in range(30):
            box_key = f'Box{box}'
            if box_key in nbt_data:
                total_possible += sum(1 for slot in range(30) if f'Slot{slot}' in nbt_data[box_key])
    elif 'pc' in nbt_data:
        if 'boxes' in nbt_data['pc'] and isinstance(nbt_data['pc']['boxes'], list):
            # Structure with pc.boxes array
            box_structure = "pc_boxes_array"
            for box_idx, box in enumerate(nbt_data['pc']['boxes']):
                if 'pokemon' in box and isinstance(box['pokemon'], list):
                    total_possible += len(box['pokemon'])
        elif any(f'Box{i}' in nbt_data['pc'] for i in range(30)):
            # Structure with pc.Box0, pc.Box1, etc.
            box_structure = "pc_boxes_direct"
            for box in range(30):
                box_key = f'Box{box}'
                if box_key in nbt_data['pc']:
                    total_possible += sum(1 for slot in range(30) if f'Slot{slot}' in nbt_data['pc'][box_key])
    
    output_text.insert(tk.END, f"Detected box structure: {box_structure}\n", "heading")
    processed_count = 0

    # Process party Pokémon
    for i in range(6):
        slot = f'Slot{i}'
        if slot in nbt_data:
            pokemon_info, error = extract_pokemon_data(nbt_data, slot)
            processed_count += 1
            if pokemon_info:
                pokemon_count += 1
                save_result = save_pokemon_to_json(pokemon_info)
                shiny_star = "⭐ " if pokemon_info['shiny'] else ""
                output_text.insert(tk.END, f"✅ Party {slot}: {shiny_star}{pokemon_info['species']} (Lv. {pokemon_info['level']}) - {save_result}\n", 
                                   "success")
            else:
                error_count += 1
                output_text.insert(tk.END, f"❌ Error in Party {slot}: {error}\n", "error")
            output_text.see(tk.END)
            
            # Update progress bar if provided
            if progress_var and total_possible > 0:
                progress_var.set((processed_count / total_possible) * 100)

    # Process PC boxes based on detected structure
    if box_structure == "direct":
        # Process traditional Box0, Box1, etc. structure
        for box in range(30):
            box_key = f'Box{box}'
            if box_key in nbt_data:
                for slot in range(30):
                    slot_key = f'Slot{slot}'
                    # Only process if the slot actually exists in the box
                    if slot_key in nbt_data[box_key]:
                        # Create a compound slot key in the format "Box{box} -> Slot{slot}"
                        compound_slot_key = f"{box_key} -> {slot_key}"
                        pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                        processed_count += 1
                        if pokemon_info:
                            pokemon_count += 1
                            save_result = save_pokemon_to_json(pokemon_info)
                            shiny_star = "⭐ " if pokemon_info['shiny'] else ""
                            output_text.insert(tk.END, f"✅ {box_key} {slot_key}: {shiny_star}{pokemon_info['species']} (Lv. {pokemon_info['level']}) - {save_result}\n", 
                                              "success")
                        else:
                            error_count += 1
                            output_text.insert(tk.END, f"❌ Error in {box_key} {slot_key}: {error}\n", "error")
                        output_text.see(tk.END)
                        
                        # Update progress bar if provided
                        if progress_var and total_possible > 0:
                            progress_var.set((processed_count / total_possible) * 100)
    
    elif box_structure == "pc_boxes_array":
        # Process pc.boxes array structure
        for box_idx, box in enumerate(nbt_data['pc']['boxes']):
            box_key = f'Box{box_idx}'
            if 'pokemon' in box and isinstance(box['pokemon'], list):
                for poke in box['pokemon']:
                    if 'slot_number' in poke:
                        slot_idx = poke['slot_number']
                        slot_key = f'Slot{slot_idx}'
                        compound_slot_key = f"{box_key} -> {slot_key}"
                        pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                        processed_count += 1
                        if pokemon_info:
                            pokemon_count += 1
                            save_result = save_pokemon_to_json(pokemon_info)
                            shiny_star = "⭐ " if pokemon_info['shiny'] else ""
                            output_text.insert(tk.END, f"✅ {box_key} {slot_key}: {shiny_star}{pokemon_info['species']} (Lv. {pokemon_info['level']}) - {save_result}\n", 
                                              "success")
                        else:
                            error_count += 1
                            output_text.insert(tk.END, f"❌ Error in {box_key} {slot_key}: {error}\n", "error")
                        output_text.see(tk.END)
                        
                        # Update progress bar if provided
                        if progress_var and total_possible > 0:
                            progress_var.set((processed_count / total_possible) * 100)
    
    elif box_structure == "pc_boxes_direct":
        # Process pc.Box0, pc.Box1, etc. structure
        for box in range(30):
            box_key = f'Box{box}'
            if box_key in nbt_data['pc']:
                for slot in range(30):
                    slot_key = f'Slot{slot}'
                    # Only process if the slot actually exists in the box
                    if slot_key in nbt_data['pc'][box_key]:
                        # Create a compound slot key in the format "Box{box} -> Slot{slot}"
                        compound_slot_key = f"{box_key} -> {slot_key}"
                        pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                        processed_count += 1
                        if pokemon_info:
                            pokemon_count += 1
                            save_result = save_pokemon_to_json(pokemon_info)
                            shiny_star = "⭐ " if pokemon_info['shiny'] else ""
                            output_text.insert(tk.END, f"✅ {box_key} {slot_key}: {shiny_star}{pokemon_info['species']} (Lv. {pokemon_info['level']}) - {save_result}\n", 
                                              "success")
                        else:
                            error_count += 1
                            output_text.insert(tk.END, f"❌ Error in {box_key} {slot_key}: {error}\n", "error")
                        output_text.see(tk.END)
                        
                        # Update progress bar if provided
                        if progress_var and total_possible > 0:
                            progress_var.set((processed_count / total_possible) * 100)
    else:
        # Unknown structure, try all possibilities for each box
        for box in range(30):
            box_key = f'Box{box}'
            for slot in range(30):
                slot_key = f'Slot{slot}'
                compound_slot_key = f"{box_key} -> {slot_key}"
                
                # Try to extract data with our flexible function
                pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                if pokemon_info:
                    pokemon_count += 1
                    save_result = save_pokemon_to_json(pokemon_info)
                    shiny_star = "⭐ " if pokemon_info['shiny'] else ""
                    output_text.insert(tk.END, f"✅ {box_key} {slot_key}: {shiny_star}{pokemon_info['species']} (Lv. {pokemon_info['level']}) - {save_result}\n", 
                                      "success")
                    output_text.see(tk.END)
                    processed_count += 1
                    
                    # Update progress bar if provided
                    if progress_var:
                        progress_var.set((processed_count / (30 * 30)) * 100)  # Approximate progress
    
    output_text.insert(tk.END, f"\n📊 Summary for {os.path.basename(file_path)}:\n", "heading")
    output_text.insert(tk.END, f"✅ Successfully processed {pokemon_count} Pokémon\n", "success")
    if error_count > 0:
        output_text.insert(tk.END, f"❌ Encountered {error_count} errors\n", "error")
    output_text.insert(tk.END, "──────────────────────────────────────\n\n")
    output_text.see(tk.END)
    
    # Update status label if provided
    if status_label:
        status_label.config(text=f"Completed: {os.path.basename(file_path)}")
    
    # Reset progress bar to 100%
    if progress_var:
        progress_var.set(100)

class CobblemonParserUI:
    def __init__(self, root):
        # Load the cache at the start
        global uuid_cache
        uuid_cache = load_cache()
        
        self.root = root
        self.root.title("Cobblemon Parser")
        self.root.geometry("900x700")
        self.root.configure(bg=THEME_BACKGROUND)
        self.root.minsize(800, 600)
        
        # Create custom fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.heading_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=10)
        
        # Configure styles
        self.style = ttk.Style()
        
        # Configure TButton style
        self.style.configure("TButton", 
                            font=self.text_font,
                            padding=10)
                            
        # Configure TFrame style
        self.style.configure("TFrame", background=THEME_BACKGROUND)
        
        # Configure TLabel style
        self.style.configure("TLabel", background=THEME_BACKGROUND, font=self.text_font)
        
        # Main layout
        self.create_main_layout()
        
    def create_main_layout(self):
        # Create main container frame
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add title
        self.title_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.title_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.title_label = tk.Label(self.title_frame, text="Cobblemon Parser", 
                                font=self.title_font, bg=THEME_BACKGROUND, fg=THEME_PRIMARY)
        self.title_label.pack(side=tk.LEFT)
        
        # Create input section
        self.input_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Input section title
        input_title = tk.Label(self.input_frame, text="Select Cobblemon .dat Files", 
                           font=self.heading_font, bg=THEME_BACKGROUND, fg=THEME_TEXT_PRIMARY)
        input_title.pack(anchor="w", pady=(0, 10))
        
        # File 1 selection frame
        self.file_frame1 = ttk.Frame(self.input_frame, style="TFrame")
        self.file_frame1.pack(fill=tk.X, pady=5)
        
        # File 1 label
        tk.Label(self.file_frame1, text=".dat 1:", bg=THEME_BACKGROUND).pack(side=tk.LEFT, padx=5)
        
        # File 1 entry
        self.file1_var = tk.StringVar()
        self.file1_entry = ttk.Entry(self.file_frame1, textvariable=self.file1_var, width=50)
        self.file1_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # File 1 browse button
        ttk.Button(self.file_frame1, text="Browse...", command=self.browse_file1).pack(side=tk.LEFT, padx=5)
        
        # File 2 selection frame
        self.file_frame2 = ttk.Frame(self.input_frame, style="TFrame")
        self.file_frame2.pack(fill=tk.X, pady=5)
        
        # File 2 label
        tk.Label(self.file_frame2, text=".dat 2:", bg=THEME_BACKGROUND).pack(side=tk.LEFT, padx=5)
        
        # File 2 entry
        self.file2_var = tk.StringVar()
        self.file2_entry = ttk.Entry(self.file_frame2, textvariable=self.file2_var, width=50)
        self.file2_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # File 2 browse button
        ttk.Button(self.file_frame2, text="Browse...", command=self.browse_file2).pack(side=tk.LEFT, padx=5)
        
        # Status and progress section
        self.status_frame = ttk.Frame(self.input_frame, style="TFrame")
        self.status_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Status label
        self.status_label = tk.Label(self.status_frame, text="Ready", bg=THEME_BACKGROUND)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, 
                                          length=100, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Process button frame
        self.button_frame = ttk.Frame(self.input_frame, style="TFrame")
        self.button_frame.pack(fill=tk.X, pady=(10, 15), anchor='e')
        
        # Process button
        self.process_btn = ttk.Button(self.button_frame, text="Process Files", command=self.process_files)
        self.process_btn.pack(side=tk.RIGHT)
        
        # Create output section title
        output_title = tk.Label(self.main_frame, text="Processing Results", 
                            font=self.heading_font, bg=THEME_BACKGROUND, fg=THEME_TEXT_PRIMARY)
        output_title.pack(anchor="w", pady=(10, 5))
        
        # Output text frame
        self.output_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Output text area
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, 
                                 bg=THEME_SURFACE, 
                                 fg=THEME_TEXT_PRIMARY,
                                 font=self.text_font)
        self.output_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add scrollbar to output text
        scrollbar = ttk.Scrollbar(self.output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Configure text tags for styling
        self.output_text.tag_configure("error", foreground=THEME_ERROR)
        self.output_text.tag_configure("success", foreground=THEME_SUCCESS)
        self.output_text.tag_configure("heading", font=self.heading_font, foreground=THEME_PRIMARY)
        
        # Welcome message
        self.output_text.insert(tk.END, "Welcome to Cobblemon Parser!\n", "heading")
        self.output_text.insert(tk.END, "Select one or two .dat files to process and click 'Process Files'.\n\n")
        
    def browse_file1(self):
        file_path = select_file()
        if file_path:
            self.file1_var.set(file_path)
            
    def browse_file2(self):
        file_path = select_file()
        if file_path:
            self.file2_var.set(file_path)
            
    def process_files(self):
        # Clear output text
        self.output_text.delete(1.0, tk.END)
        
        file1 = self.file1_var.get().strip()
        file2 = self.file2_var.get().strip()
        
        if not file1 and not file2:
            self.output_text.insert(tk.END, "Please select at least one .dat file to process.\n", "error")
            return
        
        self.output_text.insert(tk.END, "Processing started...\n\n", "heading")
        self.status_label.config(text="Processing...")
        self.progress_var.set(0)
        
        # Use threading to avoid UI freezing
        def process_thread():
            # Process first file if provided
            if file1:
                process_file(file1, self.output_text, self.progress_var, self.status_label)
            
            # Process second file if provided
            if file2:
                process_file(file2, self.output_text, self.progress_var, self.status_label)
                
            # Save the cache at the end
            save_cache()
            
            # Update UI on completion
            self.output_text.insert(tk.END, "Processing complete! Cache saved.\n", "heading")
            self.status_label.config(text="Ready")
            self.progress_var.set(100)
        
        # Start the processing thread
        threading.Thread(target=process_thread, daemon=True).start()

def safe_json_loads(response_text, max_size=32768):
    """Safely parse JSON response with size validation and chunked handling."""
    if not response_text or not response_text.strip():
        logging.error("Empty response received")
        return None
        
    if len(response_text) > max_size:
        logging.warning(f"Response size ({len(response_text)} bytes) exceeds maximum size ({max_size} bytes)")
        # Try to find a valid JSON boundary
        last_valid_pos = response_text.rfind('}', 0, max_size)
        if last_valid_pos != -1:
            response_text = response_text[:last_valid_pos + 1]
            logging.info(f"Truncated response to {len(response_text)} bytes at valid JSON boundary")
        else:
            logging.error("Could not find valid JSON boundary for truncation")
            return None
            
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        # Try to recover partial JSON
        if e.pos > 0:
            try:
                return json.loads(response_text[:e.pos])
            except:
                logging.error("Failed to recover partial JSON")
                pass
        return None

def fetch_pokemon_data(species):
    """Fetch Pokemon data with proper error handling and chunked response support."""
    # Use pokemon-species endpoint instead of pokemon
    url = f"https://pokeapi.co/api/v2/pokemon-species/{species.lower()}"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'PokemonPC/1.0'
    }
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            if response.status_code == 200:
                # Use chunked response handling
                chunks = []
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                    if chunk:
                        chunks.append(chunk)
                        total_size += len(chunk)
                        if total_size > 32768:
                            logging.warning(f"Response for {species} exceeds size limit, truncating")
                            break
                response_text = ''.join(chunks)
                
                # Check if response is empty
                if not response_text.strip():
                    logging.error(f"Empty response received for {species}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return None
                    
                return safe_json_loads(response_text)
            elif response.status_code == 429:  # Rate limit
                logging.warning(f"Rate limit hit for {species}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            else:
                logging.error(f"HTTP {response.status_code} error for {species}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {species}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            return None
    return None

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Set the output directory if specified
    global OUTPUT_DIR
    if args.output:
        OUTPUT_DIR = args.output
        print(f"Using output directory: {OUTPUT_DIR}")
    
    if args.cli and args.files:
        # CLI mode - use the provided file path
        file_path = args.files
        print(f"Processing file in CLI mode: {file_path}")
        
        # Load cache
        global uuid_cache
        uuid_cache = load_cache()
        
        nbt_data = load_nbt(file_path)
        
        if not isinstance(nbt_data, tuple):  # No error
            # Process party Pokémon
            for i in range(6):
                slot = f'Slot{i}'
                if slot in nbt_data:
                    pokemon_info, error = extract_pokemon_data(nbt_data, slot)
                    if pokemon_info:
                        print(f"Extracted Pokémon Data for {slot}:")
                        for key, value in pokemon_info.items():
                            print(f"{key}: {value}")
                        save_pokemon_to_json(pokemon_info)
                    else:
                        print(f"Failed to extract Pokémon data for {slot}: {error}")
            
            # Check for different PC box structures
            box_structure = "unknown"
            if any(f'Box{i}' in nbt_data for i in range(30)):
                # Traditional Box0, Box1, etc. structure
                box_structure = "direct"
            elif 'pc' in nbt_data:
                if 'boxes' in nbt_data['pc'] and isinstance(nbt_data['pc']['boxes'], list):
                    # Structure with pc.boxes array
                    box_structure = "pc_boxes_array"
                elif any(f'Box{i}' in nbt_data['pc'] for i in range(30)):
                    # Structure with pc.Box0, pc.Box1, etc.
                    box_structure = "pc_boxes_direct"
            
            print(f"Detected box structure: {box_structure}")
            
            # Process PC boxes based on detected structure
            if box_structure == "direct":
                # Process traditional Box0, Box1, etc. structure
                for box in range(30):
                    box_key = f'Box{box}'
                    if box_key in nbt_data:
                        for slot in range(30):
                            slot_key = f'Slot{slot}'
                            # Only process if the slot actually exists in the box
                            if slot_key in nbt_data[box_key]:
                                # Create a compound slot key in the format "Box{box} -> Slot{slot}"
                                compound_slot_key = f"{box_key} -> {slot_key}"
                                pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                                if pokemon_info:
                                    print(f"Extracted Pokémon Data for {box_key} -> {slot_key}:")
                                    for key, value in pokemon_info.items():
                                        print(f"{key}: {value}")
                                    save_pokemon_to_json(pokemon_info)
                                else:
                                    print(f"Failed to extract Pokémon data for {box_key} -> {slot_key}: {error}")
            
            elif box_structure == "pc_boxes_array":
                # Process pc.boxes array structure
                for box_idx, box in enumerate(nbt_data['pc']['boxes']):
                    box_key = f'Box{box_idx}'
                    if 'pokemon' in box and isinstance(box['pokemon'], list):
                        for poke in box['pokemon']:
                            if 'slot_number' in poke:
                                slot_idx = poke['slot_number']
                                slot_key = f'Slot{slot_idx}'
                                compound_slot_key = f"{box_key} -> {slot_key}"
                                pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                                if pokemon_info:
                                    print(f"Extracted Pokémon Data for {box_key} -> {slot_key}:")
                                    for key, value in pokemon_info.items():
                                        print(f"{key}: {value}")
                                    save_pokemon_to_json(pokemon_info)
                                else:
                                    print(f"Failed to extract Pokémon data for {box_key} -> {slot_key}: {error}")
            
            elif box_structure == "pc_boxes_direct":
                # Process pc.Box0, pc.Box1, etc. structure
                for box in range(30):
                    box_key = f'Box{box}'
                    if box_key in nbt_data['pc']:
                        for slot in range(30):
                            slot_key = f'Slot{slot}'
                            # Only process if the slot actually exists in the box
                            if slot_key in nbt_data['pc'][box_key]:
                                # Create a compound slot key in the format "Box{box} -> Slot{slot}"
                                compound_slot_key = f"{box_key} -> {slot_key}"
                                pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                                if pokemon_info:
                                    print(f"Extracted Pokémon Data for {box_key} -> {slot_key}:")
                                    for key, value in pokemon_info.items():
                                        print(f"{key}: {value}")
                                    save_pokemon_to_json(pokemon_info)
                                else:
                                    print(f"Failed to extract Pokémon data for {box_key} -> {slot_key}: {error}")
            else:
                # Unknown structure, try all possibilities for each box
                print("Unknown box structure, trying all possibilities...")
                for box in range(30):
                    box_key = f'Box{box}'
                    for slot in range(30):
                        slot_key = f'Slot{slot}'
                        compound_slot_key = f"{box_key} -> {slot_key}"
                        
                        # Try to extract data with our flexible function
                        pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                        if pokemon_info:
                            print(f"Extracted Pokémon Data for {box_key} -> {slot_key}:")
                            for key, value in pokemon_info.items():
                                print(f"{key}: {value}")
                            save_pokemon_to_json(pokemon_info)
        else:
            print(f"Failed to load NBT file: {nbt_data[1]}")
        
        # Save the cache at the end
        save_cache()
    else:
        # GUI mode - create and run the application
        try:
            # Set app theme
            root = tk.Tk()
            root.configure(bg=THEME_BACKGROUND)
            
            # Create and run app
            app = CobblemonParserUI(root)
            root.mainloop()
        except Exception as e:
            print(f"Error starting GUI mode: {e}")
            print("Falling back to simple file selection.")
            
            # Create a simple Tkinter dialog to select a file
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to start GUI mode: {e}\nFalling back to file selection dialog.")
            file_path = filedialog.askopenfilename(title="Select Cobblemon .dat file", filetypes=[("DAT Files", "*.dat")])
            
            if file_path:
                # Process the file using the simplified approach
                uuid_cache = load_cache()
                nbt_data = load_nbt(file_path)
                
                if not isinstance(nbt_data, tuple):
                    # Process party Pokémon
                    for i in range(6):
                        slot = f'Slot{i}'
                        if slot in nbt_data:
                            pokemon_info, error = extract_pokemon_data(nbt_data, slot)
                            if pokemon_info:
                                save_pokemon_to_json(pokemon_info)
                                print(f"Processed {pokemon_info['species']} (Level {pokemon_info['level']})")
                    
                    # Check for different PC box structures
                    box_structure = "unknown"
                    if any(f'Box{i}' in nbt_data for i in range(30)):
                        # Traditional Box0, Box1, etc. structure
                        box_structure = "direct"
                        for box in range(30):
                            box_key = f'Box{box}'
                            if box_key in nbt_data:
                                for slot in range(30):
                                    slot_key = f'Slot{slot}'
                                    # Only process if the slot actually exists in the box
                                    if slot_key in nbt_data[box_key]:
                                        # Create a compound slot key
                                        compound_slot_key = f"{box_key} -> {slot_key}"
                                        pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                                        if pokemon_info:
                                            save_pokemon_to_json(pokemon_info)
                                            print(f"Processed {pokemon_info['species']} (Level {pokemon_info['level']})")
                    elif 'pc' in nbt_data:
                        print(f"Detected PC structure, checking format...")
                        # Try other structures with the same approach as in CLI mode
                        if 'boxes' in nbt_data['pc'] and isinstance(nbt_data['pc']['boxes'], list):
                            box_structure = "pc_boxes_array"
                            # Process the same way as in CLI mode
                            for box_idx, box in enumerate(nbt_data['pc']['boxes']):
                                if 'pokemon' in box and isinstance(box['pokemon'], list):
                                    for poke in box['pokemon']:
                                        if 'slot_number' in poke:
                                            slot_idx = poke['slot_number']
                                            box_key = f'Box{box_idx}'
                                            slot_key = f'Slot{slot_idx}'
                                            compound_slot_key = f"{box_key} -> {slot_key}"
                                            pokemon_info, error = extract_pokemon_data(nbt_data, compound_slot_key)
                                            if pokemon_info:
                                                save_pokemon_to_json(pokemon_info)
                                                print(f"Processed {pokemon_info['species']} (Level {pokemon_info['level']})")
                    
                    # Save the cache
                    save_cache()
                    messagebox.showinfo("Success", "Processing complete! Check the console for details.")
                else:
                    messagebox.showerror("Error", f"Failed to load NBT file: {nbt_data[1]}")
            else:
                print("No file selected. Exiting.")

if __name__ == "__main__":
    main()