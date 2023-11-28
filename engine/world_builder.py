# engine/world_builder.py

import json
from icecream import ic
import re
from engine.ai_assist import AIAssist 

class WorldBuilder:
    def __init__(self, game_manager, world_data):
        self.game_manager = game_manager
        self.world_data = world_data

        self.use_ai_assist = True  
        if self.use_ai_assist:
            self.ai_assist = AIAssist(game_manager, self)

    def incoming_command(self, command):
        print(f"Received command: {command}")
        if self.use_ai_assist:
            print("Sending command to AI for processing.")
            response = self.ai_assist.handle_player_command(command)
            print(f"AI response: {response}")
            return response
        else:
            if command.startswith("take"):
                item_name = command[len("take"):].strip()
                return self.take_item(item_name)
            elif command.startswith("move to") or command.startswith("go to"):
                location_name = command[len("move to"):].strip() if command.startswith("move to") else command[len("go to"):].strip()
                return self.move_player(location_name)
            elif command.startswith("examine"):
                item_name = command[len("examine"):].strip()
                return self.examine_item(item_name)
            elif command.startswith("whereami") or command.startswith("where am i"):
                return self.where_am_i()
            elif command.startswith("look around") or command.startswith("look"):
                return self.look_around()
            elif command.startswith("open"):
                container_name = command[len("open"):].strip()
                return self.open_container(container_name)
            elif command.startswith("close"):
                return self.close_container()
            elif command.startswith("give"):
                item_name = command[len("give"):].strip()
                return self.give_item(item_name)
            elif command.startswith("help"):
                return self.display_help()
            else:
                return f"Unrecognized command: {command}"

    def find_location_data(self, location_name):
        if isinstance(location_name, dict):
            location_name = location_name.get("location/sublocation", "Unknown Location")

        for location in self.world_data.get('locations', []):
            if isinstance(location, dict) and 'name' in location:
                if location['name'].lower() == location_name.lower():
                    print(f"Found location: {location_name}")
                    return location
                for sublocation in location.get('sublocations', []):
                    if sublocation['name'].lower() == location_name.lower():
                        print(f"Found sublocation: {location_name}")
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
        print(f"Scene text: {scene_text}")
        return scene_text.strip() 

    def describe_location(self, location_data):
        print(f"Location data: {location_data}")
        print(f"Location name: {location_data['name']}")
        return f"You are at {location_data['name']}. {location_data['description']}"

    def list_items(self, location_data):
        items_text = "Items here:\n"
        for item in location_data.get('items', []):
            items_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        print(f"Items text: {items_text}")
        return items_text

    def list_interactables(self, location_data):
        interactables_text = "You can interact with:\n"
        for interactable in location_data.get('interactables', []):
            interactables_text += f"- {interactable['name']} - {interactable['description']}\n"
        print(f"Interactables text: {interactables_text}")
        return interactables_text

    def normalize_name(self, name):
        print(f"Normalizing name: {name}")
        # Remove 'The' if it's at the start of the name
        normalized_name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
        # Replace multiple spaces with a single space and trim leading/trailing spaces
        normalized_name = re.sub(r'\s+', ' ', normalized_name).strip().lower()
        print(f"Normalized name: {normalized_name}")
        return normalized_name


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
                    print(f"Container opened: {container_name}, isOpen: {container['isOpen']}")
                    return self.list_container_contents(container)

        return f"No container named '{container_name}' found here."

    def list_container_contents(self, container):
        contents_text = f"{container['name']} contains:\n"
        for item in container.get('contains', []):
            contents_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        print(f"Contents text: {contents_text}")
        return contents_text.strip()

    def list_containers(self, location_data):
        containers_text = "Containers:\n"
        for container in location_data.get('containers', []):
            containers_text += f"- {container['name']} - {container['description']}\n"
        print(f"Containers text: {containers_text}")
        return containers_text

    def show_paths(self, location_data):
        paths_text = "Paths available:\n"
        for direction, destination in location_data.get('paths', {}).items():
            paths_text += f"- {direction.title()}: {destination}\n"
        print(f"Paths text: {paths_text}")
        return paths_text

    def show_transport_options(self, location_data):
        transport_text = "Transport options:\n"
        for transport in location_data.get('transport', []):
            transport_text += f"- {transport['type']} to {', '.join(transport['destinations'])}\n"
        print(f"Transport text: {transport_text}")
        return transport_text

    def take_item(self, item_name):
        # Normalize the item name for comparison
        normalized_item_name = self.normalize_name(item_name)

        # Get the current location data
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        # Check if the item is in an open container
        item_taken = self._take_item_from_open_container(normalized_item_name, location_data)
        if item_taken:
            print(f"Item taken: {item_taken}")
            return item_taken

        # If not in a container, try taking directly from the location
        for item in location_data.get('items', []):
            if self.normalize_name(item['name']) == normalized_item_name:
                # Remove the item from the location
                location_data['items'].remove(item)
                self.update_world_data(current_location_str, {'items': location_data['items']})
                self.game_manager.player_sheet.add_item(item)
                print(f"Item taken: {item['name']}")
                return f"You have taken {item['name']}."

        print(f"Item not found: {item_name}")
        return "You cannot take that item."


    def _take_item_from_open_container(self, item_name, location_data):
        normalized_item_name = self.normalize_name(item_name)  # Normalize the item name
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == normalized_item_name:  # Use normalized name for comparison
                        if not item.get('collectable', True):
                            return f"{item['name']} cannot be taken."
                        container['contains'].remove(item)
                        self.update_world_data(location_data['name'], {'containers': location_data['containers']})
                        self.game_manager.player_sheet.add_item(item)
                        print(f"You have taken {item['name']} from {container['name']}.")
                        return f"You have taken {item['name']} from {container['name']}."

        print(f"Item not found: {normalized_item_name}")  # Use normalized name in the message
        return None


    
    def is_container_open(self):
        current_location = self.game_manager.player_sheet.location
        if isinstance(current_location, dict):
            current_location = current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location)

        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if container.get('isOpen', False):
                    ic(f"Container open: {container['name']}")
                    print(f"Container open: {container['name']}")
                    return container['name']  # Return the name of the open container
                
        print("No container open.")
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
                        print(f"Container closed: {open_container_name}, isOpen: {container['isOpen']}")
                        return f"You have closed {open_container_name}."
        
        print("No container open.")
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
        if any(self.normalize_name(dest) == sanitized_location_name for dest in current_location_data.get('paths', {}).values()):
            # Move to the new location
            destination = next((dest for dest in current_location_data['paths'].values() if self.normalize_name(dest) == sanitized_location_name), None)
            if destination:
                new_location_dict = {
                    "world": current_location['world'],  # keep the current world
                    "location/sublocation": destination  # update sublocation
                }
                self.game_manager.player_sheet.location = new_location_dict
                print(f"Player moved to {destination}.")
                return f"You moved to {destination}."
            else:
                return f"No path to '{location_name}' found from your current location."
        else:
            # If the location is not directly accessible, check if it's a sublocation
            if any(self.normalize_name(sub['name']) == sanitized_location_name for sub in current_location_data.get('sublocations', [])):
                # Find the sublocation
                sublocation = next((sub for sub in current_location_data.get('sublocations', []) if self.normalize_name(sub['name']) == sanitized_location_name), None)
                if sublocation:
                    # Set the new sublocation
                    new_location_dict = {
                        "world": current_location['world'],  # keep the current world
                        "location/sublocation": sublocation['name']  # update sublocation
                    }
                    self.game_manager.player_sheet.location = new_location_dict
                    print(f"Player moved to {sublocation['name']}.")
                    return f"You moved to {sublocation['name']}."
                else:
                    print(f"Cannot move to '{location_name}' from your current location.")
                    return f"You cannot move to '{location_name}' from your current location."

        # If the code reaches here, it means the location was neither a direct path nor a sublocation
        return f"Cannot determine how to move to '{location_name}'."

    def examine_item(self, item_name):
        # Normalize the item name for comparison
        normalized_item_name = self.normalize_name(item_name)

        # Get the current location data
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        # Check if the item is in an open container
        item_description = self._examine_item_in_open_container(item_name, location_data)
        if item_description:
            print(f"Item description: {item_description}")
            return item_description

        # If not in a container, try examining directly from the location
        for item in location_data.get('items', []):
            if self.normalize_name(item['name']) == normalized_item_name:
                print(f"Item description: {item['description']}")
                return f"{item['name']}: {item['description']}"

        return f"{item_name} not found."

    def _examine_item_in_open_container(self, item_name, location_data):
        normalized_item_name = self.normalize_name(item_name)  # Normalize the item name
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == normalized_item_name:  # Use normalized name for comparison
                        print(f"Item description: {item['description']}")
                        return f"{item['name']}: {item['description']}"

        return None


    def where_am_i(self):
        # Extract location name from the player's location
        location = self.game_manager.player_sheet.location
        location_str = location.get("location/sublocation", "Unknown Location") if isinstance(location, dict) else location

        # Use the extracted string to find location data
        location_data = self.find_location_data(location_str)
        location_description = location_data['description'] if location_data else "You are in an unknown location."

        # Initialize container_info
        container_info = ""

        # Check for any open container in the current location
        open_container_name = self.is_container_open()
        if open_container_name:
            container_info = f" Inside '{open_container_name}' container."

        print(f"Location: {location_str}, {location_description}. {container_info}")
        return f"You are at {location_str}. {location_description}.{container_info}"


    def look_around(self):
        # Check if the player is currently looking inside an open container
        open_container_name = self.is_container_open()
        if open_container_name:
            current_location = self.game_manager.player_sheet.location
            location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
            location_data = self.find_location_data(location_str)

            if location_data and 'containers' in location_data:
                for container in location_data['containers']:
                    if container['name'] == open_container_name:
                        # Display contents of the open container
                        print(f"Looking inside '{open_container_name}':\n\n{self.list_container_contents(container)}")
                        return f"You are looking into '{open_container_name}':\n\n{self.list_container_contents(container)}"

        # If no container is open, return the normal scene text
        return self.build_scene_text()
    
    def show_sublocations(self, location_data):
        sublocations_text = "Sublocations here:\n"
        for sublocation in location_data.get('sublocations', []):
            sublocations_text += f"- {sublocation['name']}: {sublocation['description']}\n\n"
        print(f"Sublocations text: {sublocations_text}")
        return sublocations_text

    def display_help(self):
        help_text = (
            "Available commands:\n\n"
            "take <item> - Take an item from the current location or an open container and add it to your inventory.\n Example: 'take potion'\n\n"
            "give <quantity> <item> - Give a specified quantity of an item from your inventory to an open container or NPC.\n Example: 'give 2 potions'\n\n"
            "move <location> - Move to a different location or sublocation.\n Example: 'move to the garden'\n\n"
            "examine <item> - Examine an item in your current location, an open container, or in your inventory for more details.\n Example: 'examine key'\n\n"
            "whereami - Find out your current location including any open container.\n Example: 'whereami'\n\n"
            "look around - Look around your current location to see items, interactables, containers, and sublocations. If inside an open container, it shows the contents of the container.\n Example: 'look around'\n\n"
            "open <container> - Open a container in your current location to interact with its contents.\n Example: 'open chest'\n\n"
            "close - Close the currently open container.\n Example: 'close'\n\n"
            "help - Display this list of commands.\n"
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

    def give_item(self, command):
        parts = command.split(maxsplit=1)  # Split command into at most three parts
        print(f"Parts: {parts}")
        if len(parts) < 2:
            return "Please specify an item and quantity to give. E.g., 'give 2 potions'."

        try:
            quantity = int(parts[0])
            item_name = parts[1].strip()
            print(f"Quantity: {quantity}, Item: {item_name}")
        except ValueError:
            # If the first part is not a number, consider the whole as an item name and quantity as 1
            quantity = 1
            item_name = command.strip()

        normalized_item_name = self.normalize_name(item_name)

        # Check if a container is open
        open_container_name = self.is_container_open()
        if open_container_name:
            # Give item to the open container
            return self._give_item_to_container(normalized_item_name, quantity, open_container_name)

        # Future implementation for NPCs can be added here

        return "You need to open a container or talk to an NPC to give items."

    def _give_item_to_container(self, normalized_item_name, quantity, container_name):
        player_inventory = self.game_manager.player_sheet.inventory
        current_location = self.game_manager.player_sheet.location
        location_str = current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(location_str)

        print(f"Looking for container '{container_name}' in location: {location_str}")

        for container in location_data.get('containers', []):
            normalized_container_name = self.normalize_name(container['name'])
            print(f"Checking container: {container['name']} (isOpen: {container.get('isOpen', False)})")

            if normalized_container_name == container_name.lower() and container.get('isOpen', False):
                for item in player_inventory:
                    normalized_player_item_name = self.normalize_name(item['name'])
                    print(f"Checking item in inventory: {item['name']} (Normalized: {normalized_player_item_name})")

                    if normalized_player_item_name == normalized_item_name:
                        if item.get('quantity', 1) >= quantity:
                            item['quantity'] = item.get('quantity', 1) - quantity
                            if item['quantity'] <= 0:
                                player_inventory.remove(item)

                            self._add_item_to_container(container, item, quantity)
                            print(f"Item '{item['name']}' given to container '{container['name']}'")
                            return f"You have given {quantity} {item['name']} to {container['name']}."
                        else:
                            return f"You don't have enough {item['name']} to give."
            else:
                print(f"Skipping container: {container['name']}, open: {container.get('isOpen', False)}, expected: {container_name}")

        print(f"No container named '{container_name}' found here or it is not open.")
        return f"No container named '{container_name}' found here or it is not open."


    def _add_item_to_container(self, container, item, quantity):
        for existing_item in container.get('contains', []):
            if self.normalize_name(existing_item['name']) == self.normalize_name(item['name']):
                existing_item['quantity'] = existing_item.get('quantity', 0) + quantity
                return

        new_item = {
            'name': item['name'],
            'description': item.get('description', ''),
            'quantity': quantity
        }
        container.setdefault('contains', []).append(new_item)
