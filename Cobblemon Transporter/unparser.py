import nbtlib
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Directory for JSON files
JSON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cobblemon')

def select_json_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    response = messagebox.askyesno("Export to Cobblemon?", "This will overwrite a Pokémon slot.")
    if not response:
        print("Export canceled.")
        return None, None
    
    file_paths = filedialog.askopenfilenames(title="Select Cobblemon JSON file", filetypes=[("JSON Files", "*.json")], initialdir=JSON_DIR)
    if not file_paths:
        print("No files selected. Exiting.")
        return None, None
    
    slot = simpledialog.askinteger("Select Slot", "Enter the slot number to overwrite (0-5):", minvalue=0, maxvalue=5)
    if slot is None:
        print("Slot selection canceled. Exiting.")
        return None, None
    
    return file_paths, slot

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
        existing_slot['Ability'] = nbtlib.Compound({'AbilityName': nbtlib.String(clean_ability)})
    
    # Merge moves
    #if 'moves' in new_data:
    #    move_set = nbtlib.List[nbtlib.Compound]()
    #    for move in new_data['moves']:
    #        move_set.append(nbtlib.Compound({'MoveName': nbtlib.String(move)}))
    #    existing_slot['MoveSet'] = move_set

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
    #if 'original_trainer' in new_data:
    #    existing_slot['PokemonOriginalTrainer'] = nbtlib.String(new_data['original_trainer'])
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
    #if 'uuid' in new_data:
    #    existing_slot['UUID'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(u) for u in new_data['uuid']])
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
    json_files, slot = select_json_files()
    if not json_files or slot is None:
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

    for json_file in json_files:
        pokemon_info = load_json(json_file)
        if pokemon_info:
            # Load the existing slot data
            slot_key = f'Slot{slot}'
            existing_slot = nbt_data.get(slot_key, nbtlib.Compound())
            # Merge the new data into the existing slot data
            nbt_data[slot_key] = merge_pokemon_data(existing_slot, pokemon_info)
            print(f"Merged Pokémon data into {slot_key} from {json_file}")
        else:
            print(f"Skipping invalid JSON file: {json_file}")

    if nbt_data:
        save_nbt_to_dat(nbt_data, dat_file)
    else:
        print("No valid Pokémon data to save.")

if __name__ == "__main__":
    main()