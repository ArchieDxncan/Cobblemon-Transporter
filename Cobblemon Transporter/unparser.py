import nbtlib
import json
import os
import tkinter as tk
import random
from tkinter import filedialog, messagebox
import copy

# Directory for JSON files
JSON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cobblemon')

def select_json_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    response = messagebox.askyesno("Export to Cobblemon?", "Ensure you have a Pokemon in your party/boxes.")
    if not response:
        print("Export canceled.")
        return None
    
    file_paths = filedialog.askopenfilenames(title="Select Cobblemon JSON file", filetypes=[("JSON Files", "*.json")], initialdir=JSON_DIR)
    if not file_paths:
        print("No files selected. Exiting.")
        return None
    
    return file_paths

def select_dat_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(title="Select Cobblemon .dat file", filetypes=[("DAT Files", "*.dat")])
    if not file_path:
        print("No file selected. Exiting.")
        return None
    
    return file_path

def load_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def generate_uuid():
    """Generate a UUID as a list of 4 random integers that can be positive or negative"""
    # Using the same range as Java's random.nextInt() which can generate 32-bit signed integers
    return [random.randint(-2147483648, 2147483647) for _ in range(4)]

def detect_dat_type(nbt_data):
    """Detect whether the .dat file is for party or boxes"""
    # Check for Box0, Box1, etc.
    if any(key.startswith('Box') for key in nbt_data.keys()):
        return 'boxes'
    # Check for Slot0, Slot1, etc.
    elif any(key.startswith('Slot') for key in nbt_data.keys()):
        return 'party'
    else:
        return 'unknown'

def find_existing_pokemon_and_free_slots_party(nbt_data, num_needed):
    """Find an existing Pokémon and multiple free slots in party data"""
    existing_slot_index = None
    free_slot_indices = []
    
    for i in range(6):  # Check slots 0-5
        slot_key = f'Slot{i}'
        slot_data = nbt_data.get(slot_key)
        
        if slot_data and 'Species' in slot_data and existing_slot_index is None:
            existing_slot_index = i
        elif not slot_data:
            free_slot_indices.append(i)
            
        if existing_slot_index is not None and len(free_slot_indices) >= num_needed:
            break
    
    return existing_slot_index, free_slot_indices[:num_needed]

def find_existing_pokemon_and_free_slots_boxes(nbt_data, num_needed):
    """Find an existing Pokémon and multiple free slots in box data"""
    existing_location = None  # (box_index, slot_index)
    free_locations = []  # [(box_index, slot_index), ...]
    
    box_index = 0
    while True:
        box_key = f'Box{box_index}'
        if box_key not in nbt_data:
            break
            
        box_data = nbt_data[box_key]
        for slot_index in range(30):  # Assuming 30 slots per box
            slot_key = f'Slot{slot_index}'
            slot_data = box_data.get(slot_key)
            
            if slot_data and 'Species' in slot_data and existing_location is None:
                existing_location = (box_index, slot_index)
            elif not slot_data or len(slot_data) == 0:
                free_locations.append((box_index, slot_index))
                
            if existing_location is not None and len(free_locations) >= num_needed:
                return existing_location, free_locations[:num_needed]
        
        box_index += 1
    
    return existing_location, free_locations[:num_needed]

def merge_pokemon_data(existing_slot, new_data):
    """
    Merge new Pokémon data into the existing slot data.
    Only updates fields that are present in the new data.
    """
    if 'species' in new_data:
        clean_species = new_data['species'].replace('-', '').lower()
        existing_slot['Species'] = nbtlib.String(f"cobblemon:{clean_species}")
    if 'level' in new_data:
        existing_slot['Level'] = nbtlib.Int(new_data['level'])
    if 'ability' in new_data:
        clean_ability = new_data['ability'].replace('-', '').lower()
        clean_ability = clean_ability.capitalize()
        existing_slot['Ability'] = nbtlib.Compound({'AbilityName': nbtlib.String(clean_ability)})
    
    # Merge IVs
    if 'ivs' in new_data:
        ivs = existing_slot.get('IVs', nbtlib.Compound())
        for stat, value in new_data['ivs'].items():
            ivs[f'cobblemon:{stat}'] = nbtlib.Int(value)
        existing_slot['IVs'] = ivs

    # Merge EVs
    if 'evs' in new_data:
        evs = existing_slot.get('EVs', nbtlib.Compound())
        for stat, value in new_data['evs'].items():
            evs[f'cobblemon:{stat}'] = nbtlib.Int(value)
        existing_slot['EVs'] = evs

    # Merge other fields if they exist
    if 'nature' in new_data:
        clean_nature = new_data['nature'].replace('-', '').lower()
        existing_slot['Nature'] = nbtlib.String(f"cobblemon:{clean_nature}")
    if 'health' in new_data:
        existing_slot['Health'] = nbtlib.Int(new_data['health'])
    if 'experience' in new_data:
        existing_slot['Experience'] = nbtlib.Int(new_data['experience'])
    if 'shiny' in new_data:
        existing_slot['Shiny'] = nbtlib.Byte(new_data['shiny'])
    if 'caught_ball' in new_data:
        existing_slot['CaughtBall'] = nbtlib.String(new_data['caught_ball'].lower())
    if 'gender' in new_data:
        existing_slot['Gender'] = nbtlib.String(new_data['gender'])
    if 'friendship' in new_data:
        existing_slot['Friendship'] = nbtlib.Int(new_data['friendship'])
    if 'healing_timer' in new_data:
        existing_slot['HealingTimer'] = nbtlib.Int(new_data['healing_timer'])
    if 'gmax_factor' in new_data:
        existing_slot['GmaxFactor'] = nbtlib.Byte(new_data['gmax_factor'])
    if 'gmax_level' in new_data:
        existing_slot['DmaxLevel'] = nbtlib.Int(new_data['gmax_level'])
    if 'tera_type' in new_data:
        tera_type_value = new_data['tera_type'].lower()
        if not tera_type_value.startswith("cobblemon:"):
            tera_type_value = "cobblemon:" + tera_type_value
        existing_slot['TeraType'] = nbtlib.String(tera_type_value)
    if 'form_id' in new_data:
        existing_slot['FormId'] = nbtlib.String(new_data['form_id'])
    if 'uuid' in new_data:
        new_uuid = generate_uuid()
        existing_slot['UUID'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(u) for u in new_uuid])
    if 'scale_modifier' in new_data:
        existing_slot['ScaleModifier'] = nbtlib.Float(new_data['scale_modifier'])
    if 'nickname' in new_data:
        existing_slot['Nickname'] = nbtlib.String(new_data['nickname'])

    # Handle PersistentData/CobbleExtraData
    persistent_data = existing_slot.get('PersistentData', nbtlib.Compound())
    
    if 'met_location' in new_data:
        persistent_data['MetLocation'] = nbtlib.String(new_data['met_location'])
    if 'met_level' in new_data:
        persistent_data['MetLevel'] = nbtlib.Int(new_data['met_level'])
    if 'met_date' in new_data:
        persistent_data['MetDate'] = nbtlib.String(new_data['met_date'])
    if 'tid' in new_data:
        persistent_data['TID'] = nbtlib.Long(new_data['tid'])
    if 'pid' in new_data:
        persistent_data['PID'] = nbtlib.Long(new_data['pid'])
    if 'sid' in new_data:
        persistent_data['SID'] = nbtlib.Long(new_data['sid'])
    if 'language' in new_data:
        persistent_data['Language'] = nbtlib.Int(new_data['language'])
    if 'origin_game' in new_data:
        persistent_data['OriginGame'] = nbtlib.String(new_data['origin_game'])
    if 'original_trainer' in new_data:
        persistent_data['OriginalTrainer'] = nbtlib.String(new_data['original_trainer'])

    # Restore Home Tracker, Encryption Constant, Height, Weight, Scale, Ribbons, and Relearn Move Flags
    if 'home_tracker' in new_data:
        persistent_data['HomeTracker'] = nbtlib.Long(new_data['home_tracker'])
    if 'encryption_constant' in new_data:
        persistent_data['EncryptionConstant'] = nbtlib.Long(new_data['encryption_constant'])
    if 'height' in new_data:
        persistent_data['Height'] = nbtlib.Int(new_data['height'])
    if 'weight' in new_data:
        persistent_data['Weight'] = nbtlib.Int(new_data['weight'])
    if 'scale' in new_data:
        persistent_data['Scale'] = nbtlib.Int(new_data['scale'])
    if 'ribbons' in new_data:
        persistent_data['Ribbons'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(r) for r in new_data['ribbons']])
    if 'relearn_flags' in new_data:
        persistent_data['RelearnFlags'] = nbtlib.List[nbtlib.Byte]([nbtlib.Byte(f) for f in new_data['relearn_flags']])
    if 'fateful_encounter' in new_data:
        persistent_data['FatefulEncounter'] = nbtlib.Byte(new_data['fateful_encounter'])

    # Handle memory data
    if 'memories' in new_data:
        memory_data = new_data['memories']
        persistent_data = existing_slot.get('PersistentData', nbtlib.Compound())
        memories = nbtlib.Compound({
            'MemoryType': nbtlib.Int(memory_data.get('memory_type', 0)),
            'MemoryIntensity': nbtlib.Int(memory_data.get('memory_intensity', 0)),
            'MemoryFeeling': nbtlib.Int(memory_data.get('memory_feeling', 0)),
            'MemoryVariable': nbtlib.Int(memory_data.get('memory_variable', 0)),
        })
        persistent_data['Memories'] = memories

    existing_slot['PersistentData'] = persistent_data

    return existing_slot

def save_nbt_to_dat(nbt_data, file_path):
    try:
        existing_data = nbtlib.load(file_path) if os.path.exists(file_path) else nbtlib.File()
        existing_data.update(nbt_data)
        existing_data.save(file_path)
        print(f"Saved NBT data to {file_path}")
    except Exception as e:
        print(f"Error saving NBT file: {e}")

def main():
    json_files = select_json_files()
    if not json_files:
        return

    dat_file = select_dat_file()
    if not dat_file:
        return

    # Load the existing NBT file
    try:
        nbt_data = nbtlib.load(dat_file)
    except Exception as e:
        print(f"Error loading NBT file: {e}")
        return

    # Detect the type of .dat file
    dat_type = detect_dat_type(nbt_data)
    print(f"Detected .dat type: {dat_type}")

    if dat_type == 'party':
        # Handle party data
        existing_slot_index, free_slot_indices = find_existing_pokemon_and_free_slots_party(nbt_data, len(json_files))
        
        if existing_slot_index is None:
            print("No existing Pokémon found to duplicate in party.")
            return
        
        if len(free_slot_indices) < len(json_files):
            print(f"Only {len(free_slot_indices)} free slots available in party, but {len(json_files)} JSON files were selected.")
            return
        
        print(f"Found existing Pokémon in party slot {existing_slot_index}")
        print(f"Will duplicate to {len(free_slot_indices)} free slots: {free_slot_indices}")

        # Get the existing slot data
        existing_slot_key = f'Slot{existing_slot_index}'
        existing_slot_data = nbt_data[existing_slot_key]

        # Process each JSON file to a separate slot
        for idx, json_file in enumerate(json_files):
            free_slot_index = free_slot_indices[idx]
            free_slot_key = f'Slot{free_slot_index}'
            
            # Deep copy the existing slot data
            duplicated_data = copy.deepcopy(existing_slot_data)
            
            # Generate a new UUID for the duplicated Pokémon
            new_uuid = generate_uuid()
            duplicated_data['UUID'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(u) for u in new_uuid])
            
            # Load and merge the JSON data
            pokemon_info = load_json(json_file)
            if pokemon_info:
                # Merge the new data into the duplicated slot
                duplicated_data = merge_pokemon_data(duplicated_data, pokemon_info)
                nbt_data[free_slot_key] = duplicated_data
                print(f"Processed Pokémon from {os.path.basename(json_file)} into party slot {free_slot_index}")
            else:
                print(f"Skipping invalid JSON file: {json_file}")

    elif dat_type == 'boxes':
        # Handle box data
        existing_location, free_locations = find_existing_pokemon_and_free_slots_boxes(nbt_data, len(json_files))
        
        if existing_location is None:
            print("No existing Pokémon found to duplicate in boxes.")
            return
        
        if len(free_locations) < len(json_files):
            print(f"Only {len(free_locations)} free slots available in boxes, but {len(json_files)} JSON files were selected.")
            return
        
        existing_box, existing_slot = existing_location
        print(f"Found existing Pokémon in box {existing_box}, slot {existing_slot}")
        print(f"Will duplicate to {len(free_locations)} free locations")

        # Get the existing slot data
        existing_box_key = f'Box{existing_box}'
        existing_slot_key = f'Slot{existing_slot}'
        existing_slot_data = nbt_data[existing_box_key][existing_slot_key]

        # Process each JSON file to a separate slot
        for idx, json_file in enumerate(json_files):
            free_box, free_slot = free_locations[idx]
            free_box_key = f'Box{free_box}'
            free_slot_key = f'Slot{free_slot}'
            
            # Ensure the box exists
            if free_box_key not in nbt_data:
                nbt_data[free_box_key] = nbtlib.Compound()
            
            # Deep copy the existing slot data
            duplicated_data = copy.deepcopy(existing_slot_data)
            
            # Generate a new UUID for the duplicated Pokémon
            new_uuid = generate_uuid()
            duplicated_data['UUID'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(u) for u in new_uuid])
            
            # Load and merge the JSON data
            pokemon_info = load_json(json_file)
            if pokemon_info:
                # Merge the new data into the duplicated slot
                duplicated_data = merge_pokemon_data(duplicated_data, pokemon_info)
                nbt_data[free_box_key][free_slot_key] = duplicated_data
                print(f"Processed Pokémon from {os.path.basename(json_file)} into box {free_box}, slot {free_slot}")
            else:
                print(f"Skipping invalid JSON file: {json_file}")

    else:
        print("Unknown .dat file format. Cannot process.")
        return

    # Save the modified NBT data
    save_nbt_to_dat(nbt_data, dat_file)
    print(f"Successfully processed {len(json_files)} Pokémon")

if __name__ == "__main__":
    main()