import json
from typing import Dict

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

