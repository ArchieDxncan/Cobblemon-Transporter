import nbtlib
import json
import os
import tkinter as tk
import random
from tkinter import filedialog, messagebox
import copy
import sys
import argparse
import io

# Set up the console to handle Unicode properly
if sys.platform.startswith('win'):
    # On Windows, try to set the console to use UTF-8
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # 65001 is the code page for UTF-8
    except Exception:
        # If setting the console code page fails, redirect stdout to handle Unicode safely
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')

# Directory for JSON files
JSON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cobblemon')

# Mapping from PKHeX ribbon names to Cobblemon mark/ribbon identifiers
MARK_NAME_MAP = {
    # Ribbons
    "ChampionKalos": "cobblemon:ribbon_champion_kalos",
    "ChampionG3": "cobblemon:ribbon_champion",
    "ChampionSinnoh": "cobblemon:ribbon_champion_sinnoh",
    "BestFriends": "cobblemon:ribbon_best_friends",
    "Training": "cobblemon:ribbon_training",
    "BattlerSkillful": "cobblemon:ribbon_battler_skillful",
    "BattlerExpert": "cobblemon:ribbon_battler_expert",
    "Effort": "cobblemon:ribbon_effort",
    "Alert": "cobblemon:ribbon_day_alert",
    "Shock": "cobblemon:ribbon_day_shock",
    "Downcast": "cobblemon:ribbon_day_downcast",
    "Careless": "cobblemon:ribbon_day_careless",
    "Relax": "cobblemon:ribbon_day_relax",
    "Snooze": "cobblemon:ribbon_day_snooze",
    "Smile": "cobblemon:ribbon_day_smile",
    "Gorgeous": "cobblemon:ribbon_syndicate_gorgeous",
    "Royal": "cobblemon:ribbon_syndicate_royal",
    "GorgeousRoyal": "cobblemon:ribbon_syndicate_gorgeous_royal",
    "Artist": "cobblemon:ribbon_artist",
    "Footprint": "cobblemon:ribbon_footprint",
    "Record": "cobblemon:ribbon_record",
    "Legend": "cobblemon:ribbon_legend",
    "Country": "cobblemon:ribbon_event_country",
    "National": "cobblemon:ribbon_event_national",
    "Earth": "cobblemon:ribbon_event_earth",
    "World": "cobblemon:ribbon_event_world",
    "Classic": "cobblemon:ribbon_event_classic",
    "Premier": "cobblemon:ribbon_event_premier",
    "Event": "cobblemon:ribbon_event",
    "Birthday": "cobblemon:ribbon_event_birthday",
    "Special": "cobblemon:ribbon_event_special",
    "Souvenir": "cobblemon:ribbon_event_souvenir",
    "Wishing": "cobblemon:ribbon_event_wishing",
    "ChampionBattle": "cobblemon:ribbon_event_champion_battle",
    "ChampionRegional": "cobblemon:ribbon_event_champion_regional",
    "ChampionNational": "cobblemon:ribbon_event_champion_national",
    "ChampionWorld": "cobblemon:ribbon_event_champion_world",
    "CountMemoryContest": "cobblemon:ribbon_memory_contest",
    "CountMemoryBattle": "cobblemon:ribbon_memory_battle",
    "ChampionG6Hoenn": "cobblemon:ribbon_champion_hoenn",
    "ContestStar": "cobblemon:ribbon_contest_super_star",
    "MasterCoolness": "cobblemon:ribbon_contest_super_master_coolness",
    "MasterBeauty": "cobblemon:ribbon_contest_super_master_beauty",
    "MasterCuteness": "cobblemon:ribbon_contest_super_master_cuteness",
    "MasterCleverness": "cobblemon:ribbon_contest_super_master_cleverness",
    "MasterToughness": "cobblemon:ribbon_contest_super_master_toughness",
    "ChampionAlola": "cobblemon:ribbon_champion_alola",
    "BattleRoyale": "cobblemon:ribbon_battle_royal_master",
    "BattleTreeGreat": "cobblemon:ribbon_battle_tree_great",
    "BattleTreeMaster": "cobblemon:ribbon_battle_tree_master",
    "ChampionGalar": "cobblemon:ribbon_champion_galar",
    "TowerMaster": "cobblemon:ribbon_battle_tower_master",
    "MasterRank": "cobblemon:ribbon_master_rank",
    "Hisui": "cobblemon:ribbon_hisui",
    "TwinklingStar": "cobblemon:ribbon_contest_super_star_twinkling",
    "ChampionPaldea": "cobblemon:ribbon_champion_paldea",
    "OnceInALifetime": "cobblemon:ribbon_once-in-a-lifetime",
    "Partner": "cobblemon:ribbon_partner",
    # Marks
    "MarkLunchtime": "cobblemon:mark_time_lunchtime",
    "MarkSleepyTime": "cobblemon:mark_time_sleepy-time",
    "MarkDusk": "cobblemon:mark_time_dusk",
    "MarkDawn": "cobblemon:mark_time_dawn",
    "MarkCloudy": "cobblemon:mark_weather_cloudy",
    "MarkRainy": "cobblemon:mark_weather_rainy",
    "MarkStormy": "cobblemon:mark_weather_stormy",
    "MarkSnowy": "cobblemon:mark_weather_snowy",
    "MarkBlizzard": "cobblemon:mark_weather_blizzard",
    "MarkDry": "cobblemon:mark_weather_dry",
    "MarkSandstorm": "cobblemon:mark_weather_sandstorm",
    "MarkMisty": "cobblemon:mark_weather_misty",
    "MarkDestiny": "cobblemon:mark_destiny",
    "MarkFishing": "cobblemon:mark_fishing",
    "MarkCurry": "cobblemon:mark_curry",
    "MarkUncommon": "cobblemon:mark_uncommon",
    "MarkRare": "cobblemon:mark_rare",
    "MarkRowdy": "cobblemon:mark_personality_rowdy",
    "MarkAbsentMinded": "cobblemon:mark_personality_absent-minded",
    "MarkJittery": "cobblemon:mark_personality_jittery",
    "MarkExcited": "cobblemon:mark_personality_excited",
    "MarkCharismatic": "cobblemon:mark_personality_charismatic",
    "MarkCalmness": "cobblemon:mark_personality_calmness",
    "MarkIntense": "cobblemon:mark_personality_intense",
    "MarkZonedOut": "cobblemon:mark_personality_zoned-out",
    "MarkJoyful": "cobblemon:mark_personality_joyful",
    "MarkAngry": "cobblemon:mark_personality_angry",
    "MarkSmiley": "cobblemon:mark_personality_smiley",
    "MarkTeary": "cobblemon:mark_personality_teary",
    "MarkUpbeat": "cobblemon:mark_personality_upbeat",
    "MarkPeeved": "cobblemon:mark_personality_peeved",
    "MarkIntellectual": "cobblemon:mark_personality_intellectual",
    "MarkFerocious": "cobblemon:mark_personality_ferocious",
    "MarkCrafty": "cobblemon:mark_personality_crafty",
    "MarkScowling": "cobblemon:mark_personality_scowling",
    "MarkKindly": "cobblemon:mark_personality_kindly",
    "MarkFlustered": "cobblemon:mark_personality_flustered",
    "MarkPumpedUp": "cobblemon:mark_personality_pumped-up",
    "MarkZeroEnergy": "cobblemon:mark_personality_zero_energy",
    "MarkPrideful": "cobblemon:mark_personality_prideful",
    "MarkUnsure": "cobblemon:mark_personality_unsure",
    "MarkHumble": "cobblemon:mark_personality_humble",
    "MarkThorny": "cobblemon:mark_personality_thorny",
    "MarkVigor": "cobblemon:mark_personality_vigor",
    "MarkSlump": "cobblemon:mark_personality_slump",
    "MarkJumbo": "cobblemon:mark_jumbo",
    "MarkMini": "cobblemon:mark_mini",
    "MarkItemfinder": "cobblemon:mark_itemfinder",
    "MarkPartner": "cobblemon:mark_partner",
    "MarkGourmand": "cobblemon:mark_gourmand",
    "MarkAlpha": "cobblemon:mark_alpha",
    "MarkMightiest": "cobblemon:mark_mightiest",
    "MarkTitan": "cobblemon:mark_titan",
    "MarkRevival": "cobblemon:mark_revival",
}

def safe_print(text):
    """Print text with safe encoding handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fall back to printing with escape characters if direct printing fails
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def select_json_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    response = messagebox.askyesno("Export to Cobblemon?", "Ensure you have a Pokemon in your party/boxes.")
    if not response:
        safe_print("Export canceled.")
        return None
    
    file_paths = filedialog.askopenfilenames(title="Select Cobblemon JSON file", filetypes=[("JSON Files", "*.json")], initialdir=JSON_DIR)
    if not file_paths:
        safe_print("No files selected. Exiting.")
        return None
    
    return file_paths

def select_dat_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(title="Select Cobblemon .dat file", filetypes=[("DAT Files", "*.dat")])
    if not file_path:
        safe_print("No file selected. Exiting.")
        return None
    
    return file_path

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except Exception as e:
        safe_print(f"Error loading JSON file {file_path}: {e}")
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

    # Handle moves
    if 'moves' in new_data:
        # First, check if an existing MoveSet is present to understand its structure
        if 'MoveSet' in existing_slot:
            #print(f"DEBUG: Found existing MoveSet structure: {type(existing_slot['MoveSet'])}")
            
            # Create an empty MoveSet with the same structure as the existing one
            move_list = type(existing_slot['MoveSet'])()
            
            # Clear the existing moves (since we're creating a new Pokémon)
            while len(move_list) > 0:
                move_list.pop()
        else:
            # No existing MoveSet, create a basic list
            move_list = nbtlib.List()
            #print(f"DEBUG: Created new MoveSet list: {type(move_list)}")
        
        # Add moves from the JSON
        for move_name in new_data['moves']:
            if move_name and isinstance(move_name, str):
                clean_move_name = move_name.replace('-', '').lower()
                
                # Create a move entry based on the structure we saw in screenshots
                # Use a Python dictionary first, then convert to nbtlib Compound
                move_dict = {
                    'RaisedPPStages': nbtlib.Int(0),
                    'MoveName': nbtlib.String(clean_move_name),
                    'MovePP': nbtlib.Int(5)  # Default PP value of 5
                }
                
                try:
                    # Try to append the move to the list
                    move_list.append(nbtlib.Compound(move_dict))
                    safe_print(f"Successfully added move {clean_move_name}")
                except Exception as e:
                    safe_print(f"Error adding move: {e}")
                    # Try fallback approach - add directly without wrapping in Compound
                    try:
                        move_list.append(move_dict)
                    except Exception as e2:
                        safe_print(f"Fallback also failed: {e2}")
        
        existing_slot['MoveSet'] = move_list

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
    # Set tera_type with a default value of "cobblemon:normal" if not present or empty
    if 'tera_type' in new_data and new_data['tera_type'].strip():
        tera_type_value = new_data['tera_type'].lower()
        if not tera_type_value.startswith("cobblemon:"):
            tera_type_value = "cobblemon:" + tera_type_value
        existing_slot['TeraType'] = nbtlib.String(tera_type_value)
    else:
        # Default to normal type if tera_type is missing or empty
        existing_slot['TeraType'] = nbtlib.String("cobblemon:normal")
    if 'form_id' in new_data:
        existing_slot['FormId'] = nbtlib.String(new_data['form_id'])
    if 'uuid' in new_data:
        new_uuid = generate_uuid()
        existing_slot['UUID'] = nbtlib.List[nbtlib.Int]([nbtlib.Int(u) for u in new_uuid])
    if 'scale_modifier' in new_data:
        existing_slot['ScaleModifier'] = nbtlib.Float(new_data['scale_modifier'])
    if 'nickname' in new_data:
        existing_slot['Nickname'] = nbtlib.String(new_data['nickname'])
    
    # Handle Marks (top level, not in PersistentData)
    if 'marks' in new_data and new_data['marks']:
        converted_marks = []
        for mark_name in new_data['marks']:
            mapped_name = MARK_NAME_MAP.get(mark_name)
            if mapped_name:
                converted_marks.append(nbtlib.String(mapped_name))
            else:
                safe_print(f"Warning: Unknown mark/ribbon '{mark_name}' - skipping.")
        if converted_marks:
            existing_slot['Marks'] = nbtlib.List[nbtlib.String](converted_marks)

    # Handle PersistentData/CobbleExtraData
    persistent_data = existing_slot.get('PersistentData', nbtlib.Compound())
    
    if 'met_location' in new_data:
        persistent_data['MetLocation'] = nbtlib.String(new_data['met_location'])
    if 'met_level' in new_data:
        persistent_data['MetLevel'] = nbtlib.Int(new_data['met_level'])
    if 'met_date' in new_data:
        persistent_data['MetDate'] = nbtlib.String(new_data['met_date'])
    if 'tid' in new_data and new_data['tid'] is not None:
        persistent_data['TID'] = nbtlib.Long(new_data['tid'])
    if 'pid' in new_data and new_data['pid'] is not None:
        persistent_data['PID'] = nbtlib.Long(new_data['pid'])
    if 'sid' in new_data and new_data['sid'] is not None:
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

    # Add egg data
    if 'egg_location' in new_data:
        persistent_data['EggLocation'] = nbtlib.String(new_data['egg_location'])
    if 'egg_date' in new_data:
        persistent_data['EggDate'] = nbtlib.String(new_data['egg_date'])
    if 'is_egg' in new_data:
        persistent_data['IsEgg'] = nbtlib.Byte(1 if new_data['is_egg'] else 0)

    # Add Pokérus data
    if 'pokerus_strain' in new_data:
        persistent_data['PokerusStrain'] = nbtlib.Int(new_data['pokerus_strain'])
    if 'pokerus_days' in new_data:
        persistent_data['PokerusDays'] = nbtlib.Int(new_data['pokerus_days'])

    # Add handler data
    if 'current_handler' in new_data:
        persistent_data['CurrentHandler'] = nbtlib.Int(new_data['current_handler'])
    if 'handling_trainer_name' in new_data:
        persistent_data['HandlingTrainerName'] = nbtlib.String(new_data['handling_trainer_name'])
    if 'handling_trainer_gender' in new_data:
        persistent_data['HandlingTrainerGender'] = nbtlib.Int(new_data['handling_trainer_gender'])
    if 'handling_trainer_friendship' in new_data:
        persistent_data['HandlingTrainerFriendship'] = nbtlib.Int(new_data['handling_trainer_friendship'])
    if 'original_trainer_gender' in new_data:
        persistent_data['OriginalTrainerGender'] = nbtlib.Int(new_data['original_trainer_gender'])

    # Add ability and nature data
    if 'ability_number' in new_data:
        persistent_data['AbilityNumber'] = nbtlib.Int(new_data['ability_number'])
    if 'stat_nature' in new_data:
        if new_data['stat_nature']:  # Only set if not empty
            persistent_data['StatNature'] = nbtlib.String(new_data['stat_nature'])

    # Add stats and type data
    if 'characteristic' in new_data:
        persistent_data['Characteristic'] = nbtlib.Int(new_data['characteristic'])
    if 'tsv' in new_data:
        persistent_data['TSV'] = nbtlib.Int(new_data['tsv'])
    if 'psv' in new_data:
        persistent_data['PSV'] = nbtlib.Int(new_data['psv'])
    if 'hp_type' in new_data:
        persistent_data['HPType'] = nbtlib.Int(new_data['hp_type'])
    if 'hp_power' in new_data:
        persistent_data['HPPower'] = nbtlib.Int(new_data['hp_power'])
    if 'iv_total' in new_data:
        persistent_data['IVTotal'] = nbtlib.Int(new_data['iv_total'])
    if 'potential_rating' in new_data:
        persistent_data['PotentialRating'] = nbtlib.Int(new_data['potential_rating'])

    # Add relearn moves
    if 'relearn_move1' in new_data:
        persistent_data['RelearnMove1'] = nbtlib.Int(new_data['relearn_move1'])
    if 'relearn_move2' in new_data:
        persistent_data['RelearnMove2'] = nbtlib.Int(new_data['relearn_move2'])
    if 'relearn_move3' in new_data:
        persistent_data['RelearnMove3'] = nbtlib.Int(new_data['relearn_move3'])
    if 'relearn_move4' in new_data:
        persistent_data['RelearnMove4'] = nbtlib.Int(new_data['relearn_move4'])

    existing_slot['PersistentData'] = persistent_data

    return existing_slot

def save_nbt_to_dat(nbt_data, file_path):
    try:
        existing_data = nbtlib.load(file_path) if os.path.exists(file_path) else nbtlib.File()
        existing_data.update(nbt_data)
        existing_data.save(file_path)
        safe_print(f"Saved NBT data to {file_path}")
    except Exception as e:
        safe_print(f"Error saving NBT file: {e}")

def process_files(json_files, dat_file):
    """Process the JSON and DAT files"""
    # Load the existing NBT file
    try:
        nbt_data = nbtlib.load(dat_file)
    except Exception as e:
        safe_print(f"Error loading NBT file: {e}")
        return False

    # Detect the type of .dat file
    dat_type = detect_dat_type(nbt_data)
    safe_print(f"Detected .dat type: {dat_type}")

    if dat_type == 'party':
        # Handle party data
        existing_slot_index, free_slot_indices = find_existing_pokemon_and_free_slots_party(nbt_data, len(json_files))
        
        if existing_slot_index is None:
            safe_print("No existing Pokémon found to duplicate in party.")
            return False
        
        if len(free_slot_indices) < len(json_files):
            safe_print(f"Only {len(free_slot_indices)} free slots available in party, but {len(json_files)} JSON files were selected.")
            return False
        
        safe_print(f"Found existing Pokémon in party slot {existing_slot_index}")
        safe_print(f"Will duplicate to {len(free_slot_indices)} free slots: {free_slot_indices}")

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
                safe_print(f"Processed Pokémon from {os.path.basename(json_file)} into party slot {free_slot_index}")
            else:
                safe_print(f"Skipping invalid JSON file: {json_file}")

    elif dat_type == 'boxes':
        # Handle box data
        existing_location, free_locations = find_existing_pokemon_and_free_slots_boxes(nbt_data, len(json_files))
        
        if existing_location is None:
            safe_print("No existing Pokémon found to duplicate in boxes.")
            return False
        
        if len(free_locations) < len(json_files):
            safe_print(f"Only {len(free_locations)} free slots available in boxes, but {len(json_files)} JSON files were selected.")
            return False
        
        existing_box, existing_slot = existing_location
        safe_print(f"Found existing Pokémon in box {existing_box}, slot {existing_slot}")
        safe_print(f"Will duplicate to {len(free_locations)} free locations")

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
                safe_print(f"Processed Pokémon from {os.path.basename(json_file)} into box {free_box}, slot {free_slot}")
            else:
                safe_print(f"Skipping invalid JSON file: {json_file}")

    else:
        safe_print("Unknown .dat file format. Cannot process.")
        return False

    # Save the modified NBT data
    save_nbt_to_dat(nbt_data, dat_file)
    safe_print(f"Successfully processed {len(json_files)} Pokémon")
    return True

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Export Pokémon from JSON to Cobblemon DAT file')
    parser.add_argument('--json', type=str, help='Path to a JSON file to export (CLI mode)')
    args = parser.parse_args()
    
    # CLI mode
    if args.json:
        # Verify JSON file exists
        if not os.path.exists(args.json):
            safe_print(f"Error: JSON file not found: {args.json}")
            return
            
        # Ask for DAT file
        safe_print("JSON file selected - Please select a Cobblemon .dat file to export to.")
        dat_file = select_dat_file()
        if not dat_file:
            return
            
        # Process the files
        json_files = [args.json]
        result = process_files(json_files, dat_file)
        if result:
            safe_print("Export completed successfully.")
        else:
            safe_print("Export failed.")
        return
    
    # GUI mode (original behavior)
    json_files = select_json_files()
    if not json_files:
        return

    dat_file = select_dat_file()
    if not dat_file:
        return
        
    process_files(json_files, dat_file)

if __name__ == "__main__":
    main()