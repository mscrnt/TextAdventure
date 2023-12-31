# utilities.py

import json
from typing import Dict
import pickle
import os
from icecream import ic
import glob
import re

def normalize_name(name):
    ic(f"Normalizing name: {name}")
    normalized_name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
    normalized_name = re.sub(r'\s+', ' ', normalized_name).strip().lower()
    ic(f"Normalized name: {normalized_name}")
    return normalized_name

# Function to load text from a JSON file
def load_text(file_name: str) -> Dict:
    path = f'data/dialog/{file_name}.json'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        ic(f"The file {file_name}.json was not found.")
    except json.JSONDecodeError:
        ic(f"The file {file_name}.json contains invalid JSON.")
    except Exception as e:
        ic(f"An error occurred: {e}")

    return {} 

# Function to load json data from a file
def load_json(file_name: str, key) -> Dict:
    path = f'data/{file_name}.json'
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return data.get(key, []) 
    except FileNotFoundError:
        ic(f"The file {file_name}.json was not found.")
    except json.JSONDecodeError as e:
        ic(f"The file {file_name}.json contains invalid JSON: {e}")
    except Exception as e:
        ic(f"An error occurred: {e}")
    return []

def save_game_data(state, filename='savegame.pkl'):
    save_directory = "save_data"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    file_path = os.path.join(save_directory, filename)
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(state, f)
        print(f"Game saved successfully as {file_path}.")
    except Exception as e:
        print(f"An error occurred while saving the game: {e}")

    # Ensure the location is a dictionary with the 'world' key
    if isinstance(state['player_sheet'].location, dict) and 'world' in state['player_sheet'].location:
        world_name = state['player_sheet'].location['world']
        print(f"Saving world data for: {world_name}")
        working_world_path = f'data/worlds/working_{world_name}.json'
        try:
            with open(working_world_path, 'w') as f:
                json.dump(state['world_data'], f, indent=4)
            print(f"Working world data saved successfully as {working_world_path}.")
        except Exception as e:
            print(f"An error occurred while saving the working world data: {e}")
    else:
        print(f'Player location: {state["player_sheet"].location}')
        print("The player's location is not in the correct format. Cannot save world data.")


# Function to load game state
def load_game_data(filename='savegame.pkl'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        ic("Save file not found.")
    except Exception as e:
        ic(f"An error occurred while loading the game: {e}")
    return None

def create_working_world_data(world_name):
    # Construct the file paths for base and working world data
    base_world_path = f'data/worlds/{world_name}.json'
    working_world_path = f'data/worlds/working_{world_name}.json'
    
    # Load the base world data
    with open(base_world_path, 'r') as f:
        base_world_data = json.load(f)
    
    # Create a working copy for this game session
    with open(working_world_path, 'w') as f:
        json.dump(base_world_data, f)

def load_working_world_data(world_name):
    # Directly use the provided world name to construct file paths
    working_world_path = f'data/worlds/working_{world_name}.json'
    saved_game_path = f'save_data/working_{world_name}_savegame.pkl'
    print(f"Loading working world data for {world_name}.")


    # Check if there's a saved game specific to this world
    if os.path.exists(saved_game_path):
        print(f"Found saved game state for {world_name}.")
        # Load the saved game state
        try:
            with open(saved_game_path, 'rb') as f:
                saved_state = pickle.load(f)
                print(f"Loaded saved game state for {world_name}.")
                return saved_state['world_data']
        except Exception as e:
            print(f"Error loading saved game state for {world_name}: {e}")

    # If no specific saved game state, create a new working copy
    if not os.path.exists(working_world_path):
        # If the working world file does not exist, create it from the base file
        create_working_world_data(world_name)

    # Load the working world data into memory and return it
    with open(working_world_path, 'r') as f:
        return json.load(f)
    
def load_all_worlds():
    world_directory = 'data/worlds'
    world_data = {}
    ic("Loading world data...")

    try:
        for filename in os.listdir(world_directory):
            ic(filename)
            if filename.endswith('.json') and not filename.startswith('working_'):
                world_name = filename[:-5]  # Remove .json extension
                ic(world_name)
                with open(os.path.join(world_directory, filename), 'r') as file:
                    data = json.load(file)
                    world_display_name = data.get("name", "Unknown World")
                    world_data[world_name] = world_display_name
    except Exception as e:
        ic(f"An error occurred while loading world data: {e}")

    return world_data

def convert_text_to_display(text):
    # Convert newlines in the text to HTML paragraph tags
    paragraphs = text.split('\n')
    html_paragraphs = ['<p>{}</p>'.format(p.strip()) for p in paragraphs if p.strip()]

    # Assemble the HTML content
    html_content = "<html><body>{}</body></html>".format(''.join(html_paragraphs))

    return html_content

def delete_working_files():
    # Delete all working files "working_*.json"
    working_world_path = f'data/worlds/working_*.json'
    working_world_files = glob.glob(working_world_path)
    for file in working_world_files:
        os.remove(file)
    ic(f"Deleted {len(working_world_files)} working world files.")

