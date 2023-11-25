import json
from typing import Dict
import pickle

# Function to load text from a JSON file
def load_text(file_name: str) -> Dict:
    path = f'data/dialog/{file_name}.json'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {file_name}.json was not found.")
    except json.JSONDecodeError:
        print(f"The file {file_name}.json contains invalid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return {} 

# Function to save game state
def save_game(state, filename='savegame.pkl'):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
        print(f"Game saved successfully as {filename}.")
    except Exception as e:
        print(f"An error occurred while saving the game: {e}")

# Function to load game state
def load_game(filename='savegame.pkl'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Save file not found.")
    except Exception as e:
        print(f"An error occurred while loading the game: {e}")
    return None