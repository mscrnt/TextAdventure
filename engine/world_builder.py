# engine/world_builder.py

import json
from icecream import ic
import re

class WorldBuilder:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.world_data = self.load_world_data()

    def find_location_data(self, location_name):
        # First, check if the location is a main location
        for location in self.world_data.get('locations', []):
            if location['name'].lower() == location_name.lower():
                return location
            # If not, check if it's a sublocation
            for sublocation in location.get('sublocations', []):
                if sublocation['name'].lower() == location_name.lower():
                    return sublocation
        return None


    def load_world_data(self):
        try:
            with open('data/worlds/avalonia.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            ic(f"Error loading world data: {e}")
            return {}

    def build_scene_text(self):
        player_location = self.game_manager.player_sheet.location
        location_data = self.find_location_data(player_location)
        scene_text = ""
        if location_data:
            scene_text += self.describe_location(location_data) + "\n"
            scene_text += self.list_items(location_data) + "\n" if location_data.get('items', []) else ""
            scene_text += self.list_interactables(location_data) + "\n" if location_data.get('interactables', []) else "\n"
            scene_text += self.list_containers(location_data) + "\n" if location_data.get('containers', []) else "\n"
            scene_text += self.show_paths(location_data) + "\n" if location_data.get('paths', {}) else "\n"
            scene_text += self.show_sublocations(location_data) + "\n" if location_data.get('sublocations', []) else "\n"
            scene_text += self.show_transport_options(location_data) if location_data.get('transport', []) else ""
        return scene_text.strip() 

    def describe_location(self, location_data):
        return f"You are at {location_data['name']}. {location_data['description']}"

    def list_items(self, location_data):
        items_text = "Items here:\n"
        for item in location_data.get('items', []):
            items_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        return items_text

    def list_interactables(self, location_data):
        interactables_text = "You can interact with:\n"
        for interactable in location_data.get('interactables', []):
            interactables_text += f"- {interactable['name']} - {interactable['description']}\n"
        return interactables_text

    def list_containers(self, location_data):
        containers_text = "Containers:\n"
        for container in location_data.get('containers', []):
            containers_text += f"- {container['name']} - {container['description']}\n"
            for contained_item in container.get('contains', []):
                containers_text += f"  - Contains: {contained_item['name']} ({contained_item['quantity']})\n"
        return containers_text

    def show_paths(self, location_data):
        paths_text = "Paths available:\n"
        for direction, destination in location_data.get('paths', {}).items():
            paths_text += f"- {direction.title()}: {destination}\n"
        return paths_text

    def show_transport_options(self, location_data):
        transport_text = "Transport options:\n"
        for transport in location_data.get('transport', []):
            transport_text += f"- {transport['type']} to {', '.join(transport['destinations'])}\n"
        return transport_text

    def take_item(self, item_name):
        location_data = self.find_location_data(self.game_manager.player_sheet.location)
        if location_data:
            return self.remove_item_from_location(item_name, location_data)
        return "You are in an unknown location."

    def move_player(self, location_name):
        # Get the current location data from the player's current location
        current_location_data = self.find_location_data(self.game_manager.player_sheet.location)

        # If current location is not found, return an error message
        if not current_location_data:
            return "You are in an unknown location and cannot move."

        # Get available paths and sublocations from current location data
        available_paths = current_location_data.get('paths', {})
        sublocations = current_location_data.get('sublocations', [])

        # Normalize the location name for comparison
        sanitized_location_name = re.sub(r'[^\w\s]', '', location_name).lower().strip()

        # Check if the desired location is a direct path from the current location
        if sanitized_location_name in (re.sub(r'[^\w\s]', '', dest).lower() for dest in available_paths.values()):
            # Move to the new location
            destination = next(dest for dest in available_paths.values() if re.sub(r'[^\w\s]', '', dest).lower() == sanitized_location_name)
            self.game_manager.player_sheet.location = destination
            return f"You moved to {destination}."

        # Check if the desired location is a sublocation of the current location
        sublocation = next((sub for sub in sublocations if re.sub(r'[^\w\s]', '', sub['name']).lower() == sanitized_location_name), None)
        if sublocation:
            # Move to the sublocation
            self.game_manager.player_sheet.location = sublocation['name']
            return f"You moved to {sublocation['name']}."

        # Check for 'exit' command from a sublocation
        if sanitized_location_name == 'exit' and 'exit' in available_paths:
            # Exit to the parent location
            self.game_manager.player_sheet.location = available_paths['exit']
            return f"You moved to {available_paths['exit']}."

        # If the location is not available, return an error message
        return f"You cannot move to '{location_name}' from your current location."



    def examine_item(self, item_name):
        location_data = self.find_location_data(self.game_manager.player_sheet.location)
        item = self.find_item_in_location_or_inventory(item_name, location_data)
        if item:
            return f"{item['name']}: {item['description']}"
        return f"{item_name} not found."

    def where_am_i(self):
        location = self.game_manager.player_sheet.location
        location_data = self.find_location_data(location)
        if location_data:
            return f"You are at {location}. {location_data['description']}"
        return "You are in an unknown location."

    def look_around(self):
        return self.build_scene_text()
    
    def show_sublocations(self, location_data):
        sublocations_text = "Sublocations here:\n"
        for sublocation in location_data.get('sublocations', []):
            sublocations_text += f"- {sublocation['name']}: {sublocation['description']}\n\n"
        return sublocations_text

    def display_help(self):
        help_text = (
            "Available commands:\n"
            "\n"
            "take <item> - Take an item from the current location and add it to your inventory.\n\n"
            "move <location> - Move to a different location.\n\n"
            "examine <item> - Examine an item in your current location or in your inventory for more details.\n\n"
            "whereami - Find out your current location.\n\n"
            "look around - Look around your current location to see items, interactables, and containers.\n\n"
            "help - Display this list of commands."
        )
        return help_text