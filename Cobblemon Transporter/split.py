import os
import shutil
import requests

# Define Pokedex number ranges for each generation
generation_ranges = {
    1: (1, 151),    # Gen 1: Bulbasaur to Mew
    2: (152, 251),  # Gen 2: Chikorita to Celebi
    3: (252, 386),  # Gen 3: Treecko to Deoxys
    4: (387, 493),  # Gen 4: Turtwig to Arceus
    5: (494, 649),  # Gen 5: Victini to Genesect
    6: (650, 721),  # Gen 6: Chespin to Volcanion
    7: (722, 809),  # Gen 7: Rowlet to Melmetal
    8: (810, 905),  # Gen 8: Grookey to Enamorus
    9: (906, 1010), # Gen 9: Sprigatito to ??? (as of current knowledge)
}

# Define the folder containing your .cb9 files
input_folder = "cobblemon"
output_base_folder = "output"

# Create output folders for each generation
for gen in range(1, 10):  # Generations 1 to 9
    os.makedirs(os.path.join(output_base_folder, f"Gen{gen}"), exist_ok=True)

# Function to get Pokémon ID (Pokedex number) from PokeAPI
def get_pokemon_id(species_name):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{species_name.lower()}/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["id"]  # Pokedex number
    else:
        print(f"Error fetching data for {species_name}: {response.status_code}")
        return None

# Process each .cb9 file
for filename in os.listdir(input_folder):
    if filename.endswith(".cb9"):
        # Extract species name from the filename (e.g., "gloom_6972.cb9" -> "gloom")
        species_name = filename.split("_")[0]

        # Get Pokémon ID from PokeAPI
        pokemon_id = get_pokemon_id(species_name)
        if pokemon_id is None:
            print(f"Skipping {filename}: Could not fetch Pokémon ID")
            continue

        # Determine the generation based on Pokedex number ranges
        generation = None
        for gen, (start, end) in generation_ranges.items():
            if start <= pokemon_id <= end:
                generation = gen
                break

        if generation:
            # Move the file to the corresponding generation folder
            output_folder = os.path.join(output_base_folder, f"Gen{generation}")
            shutil.move(
                os.path.join(input_folder, filename),
                os.path.join(output_folder, filename)
            )
            print(f"Moved {filename} to {output_folder} (ID: {pokemon_id}, Gen: {generation})")
        else:
            print(f"Could not determine generation for {filename} (ID: {pokemon_id})")