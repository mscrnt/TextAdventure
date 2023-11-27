# engine/world_builder.py

import json
from icecream import ic
import re

class WorldBuilder:
    def __init__(self, game_manager, world_data):
        self.game_manager = game_manager
        self.world_data = world_data

    def incoming_command(self, command):
        # Check if a container is open and restrict actions
        open_container_name = self.is_container_open()
        if open_container_name and not (command.startswith("close") or command.startswith("take") or command.startswith("help") or command.startswith("examine")):
            # Show a message and the contents of the open container
            container_contents = self.open_container(open_container_name)
            return "You must close the open container before doing anything else.\n\n" + container_contents

        # Process the command normally
        if command.startswith("take"):
            item_name = command[len("take"):].strip()
            return self.take_item(item_name)
        elif command.startswith("move to"):
            location_name = command[len("move to"):].strip()
            return self.move_player(location_name)
        elif command.startswith("examine"):
            item_name = command[len("examine"):].strip()
            return self.examine_item(item_name)
        elif command.startswith("whereami"):
            return self.where_am_i()
        elif command.startswith("look around"):
            return self.look_around()
        elif command.startswith("open"):
            container_name = command[len("open"):].strip()
            return self.open_container(container_name)
        elif command.startswith("close"):
            return self.close_container()
        elif command.startswith("help"):
            return self.display_help()
        else:
            return f"Unrecognized command: {command}"

    def find_location_data(self, location_name):
        # Handle the case where location_name is a dictionary
        if isinstance(location_name, dict):
            location_name = location_name.get("location/sublocation", "Unknown Location")

        for location in self.world_data.get('locations', []):
            if isinstance(location, dict) and 'name' in location:
                if location['name'].lower() == location_name.lower():
                    return location
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

        # Check if player_location is a dictionary and extract the location name
        if isinstance(player_location, dict):
            location_name = player_location.get("location/sublocation", "Unknown Location")
        else:
            # If it's already a string, use it directly
            location_name = player_location

        location_data = self.find_location_data(location_name)
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

    def normalize_name(self, name):
        return re.sub(r'\s+', ' ', name).strip().lower()

    def open_container(self, container_name):
        # Normalize the input for comparison
        container_name = self.normalize_name(container_name)

        # Get the current location data
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        # Check if the location data contains the specified container
        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if self.normalize_name(container['name']) == container_name:
                    container['isOpen'] = True  # Set the isOpen flag to true
                    ic(f"Container opened: {container_name}, isOpen: {container['isOpen']}")
                    return self.list_container_contents(container)

        return f"No container named '{container_name}' found here."

    def list_container_contents(self, container):
        contents_text = f"{container['name']} contains:\n"
        for item in container.get('contains', []):
            contents_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        return contents_text.strip()

    def list_containers(self, location_data):
        containers_text = "Containers:\n"
        for container in location_data.get('containers', []):
            containers_text += f"- {container['name']} - {container['description']}\n"
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
        # Normalize the item name for comparison
        normalized_item_name = self.normalize_name(item_name)

        # Check if the item is inside an open container
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if container['isOpen']:
                    for item in container.get('contains', []):
                        if self.normalize_name(item['name']) == normalized_item_name:
                            # Check if the item is collectable
                            if not item.get('collectable', True):  # Default to True if 'collectable' not specified
                                return f"{item['name']} cannot be taken."

                            # Remove the item from the container in location_data
                            container['contains'].remove(item)

                            # Update the container in world_data with the new container contents
                            self.update_world_data(current_location_str, {'containers': location_data['containers']})

                            # Add the item to the player's inventory
                            self.game_manager.player_sheet.add_item(item)
                            return f"You have taken {item['name']} from {container['name']}."

        return "You cannot take that item."

    
    def is_container_open(self):
        current_location = self.game_manager.player_sheet.location
        if isinstance(current_location, dict):
            current_location = current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location)

        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if container.get('isOpen', False):
                    ic(f"Container open: {container['name']}")
                    return container['name']  # Return the name of the open container
        return None  # Return None if no container is open
    
    def close_container(self):
        open_container_name = self.is_container_open()
        if open_container_name:
            current_location = self.game_manager.player_sheet.location
            location_data = self.find_location_data(current_location)
            
            if location_data and 'containers' in location_data:
                for container in location_data['containers']:
                    if container['name'] == open_container_name:
                        container['isOpen'] = False  # Close the container
                        ic(f"Container closed: {open_container_name}, isOpen: {container['isOpen']}")
                        return f"You have closed {open_container_name}."
        return "You are not in an open container."

    def move_player(self, location_name):
        # Get the current location data from the player's current location
        current_location = self.game_manager.player_sheet.location

        # We expect current_location to always be a dictionary now
        current_location_str = current_location.get("location/sublocation", "Unknown Location")

        current_location_data = self.find_location_data(current_location_str)

        # If current location is not found, return an error message
        if not current_location_data:
            return "You are in an unknown location and cannot move."

        # Normalize the location name for comparison
        sanitized_location_name = self.normalize_name(location_name)

        # Check if the desired location is a direct path from the current location
        if sanitized_location_name in (self.normalize_name(dest) for dest in current_location_data.get('paths', {}).values()):
            # Move to the new location
            destination = next((dest for dest in current_location_data['paths'].values() if self.normalize_name(dest) == sanitized_location_name), None)
            if destination:
                # Here we assume destination is just the location name, not a full dictionary
                # You would need to ensure this matches the expected dictionary structure
                new_location_dict = {
                    "world": current_location['world'],  # keep the current world
                    "location/sublocation": destination  # update sublocation
                }
                self.game_manager.player_sheet.location = new_location_dict
                return f"You moved to {destination}."
            else:
                return f"No path to '{location_name}' found from your current location."
        else:
            # If the location is not directly accessible, check if it's a sublocation
            sublocation = next((sub for sub in current_location_data.get('sublocations', []) if self.normalize_name(sub['name']) == sanitized_location_name), None)
            if sublocation:
                # Set the new sublocation
                new_location_dict = {
                    "world": current_location['world'],  # keep the current world
                    "location/sublocation": sublocation['name']  # update sublocation
                }
                self.game_manager.player_sheet.location = new_location_dict
                return f"You moved to {sublocation['name']}."
            else:
                return f"You cannot move to '{location_name}' from your current location."


    def examine_item(self, item_name):
        location_data = self.find_location_data(self.game_manager.player_sheet.location)
        item = self.find_item_in_location_or_inventory(item_name, location_data)
        if item:
            return f"{item['name']}: {item['description']}"
        return f"{item_name} not found."

    def where_am_i(self):
        # Extract location name from the player's location
        location = self.game_manager.player_sheet.location
        if isinstance(location, dict):
            location_str = location.get("location/sublocation", "Unknown Location")
        else:
            location_str = location

        # Use the extracted string to find location data
        location_data = self.find_location_data(location_str)
        if location_data:
            return f"You are at {location_str}. {location_data['description']}"
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
            "open <container> - Open a container in your current location to see its contents.\n\n"
            "help - Display this list of commands."
        )
        return help_text
    
    def update_world_data(self, location_name, update_dict):
        """
        Update the world_data based on the provided location and update dictionary.

        Args:
        location_name (str): The name of the location to update.
        update_dict (dict): A dictionary containing the keys (such as 'containers', 'items', etc.) 
                            and their new values to be updated in the world_data.
        """
        for location in self.world_data.get('locations', []):
            # Check both top-level locations and sublocations
            if location['name'].lower() == location_name.lower():
                self._apply_updates(location, update_dict)
            for sublocation in location.get('sublocations', []):
                if sublocation['name'].lower() == location_name.lower():
                    self._apply_updates(sublocation, update_dict)

    def _apply_updates(self, location_dict, update_dict):
        """
        Apply updates to the specified location dictionary based on the update dictionary.

        Args:
        location_dict (dict): The dictionary of the location to be updated.
        update_dict (dict): The updates to apply.
        """
        for key, value in update_dict.items():
            if key in location_dict:
                location_dict[key] = value

    def close_all_containers(self):
        """Close all open containers in the world."""
        for location in self.world_data.get('locations', []):
            self._close_containers_in_location(location)
            for sublocation in location.get('sublocations', []):
                self._close_containers_in_location(sublocation)

    def _close_containers_in_location(self, location):
        """Close all containers in a specific location."""
        for container in location.get('containers', []):
            container['isOpen'] = False