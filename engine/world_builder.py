# engine/world_builder.py

import json
from icecream import ic
import re
from engine.ai_assist import AIAssist 
from utilities import convert_text_to_display, load_working_world_data
from interfaces import IWorldBuilder, IGameManager
from PySide6.QtCore import QObject, Signal

class WorldBuilder(QObject, IWorldBuilder):
    display_text_signal = Signal(str)
    command_processed_signal = Signal() 
    last_spoken_npc = None

    def __init__(self, world_data, use_ai_assist=True):
        super().__init__()
        self.game_manager = None
        self.world_data = world_data
        ic(f'WorldBuilder initialized with world data')
        self.use_ai_assist = use_ai_assist
        if self.use_ai_assist:
            ic(f"AI assist enabled: {self.use_ai_assist}")
        else:
            ic("AI assist disabled")
        ic("WorldBuilder initialized, AI assist deferred")

    def set_world_data(self, world_data):
        self.world_data = world_data
        ic("World data set in WorldBuilder")

    def set_game_manager(self, game_manager: IGameManager):
        if not game_manager:
            raise ValueError("GameManager instance is required")
        self.game_manager = game_manager
        if self.use_ai_assist:
            self.initialize_ai_assist()

    def initialize_ai_assist(self):
        if not self.game_manager or not self.game_manager.player_sheet:
            raise ValueError("GameManager with PlayerSheet is required for AIAssist")
        ic("Initializing AI assist")
        self.ai_assist = AIAssist(self.game_manager.player_sheet, self)

    def incoming_command(self, command):
        ic(f"Received command: {command}")

        # Check if any container is open
        if self.is_container_open() and not any(cmd in command for cmd in ['open', 'close']):
            # Restrict commands to only container interactions
            allowed_commands = ['give', 'take', 'open', 'close', 'examine']
            if not any(cmd in command for cmd in allowed_commands):
                return convert_text_to_display("You must close the open container before doing that.")

        # Display the processing command message
        html_command = convert_text_to_display(f"Processing command: {command}")
        self.game_manager.display_text_signal.emit(html_command)

        # Initialize response variable
        response = ""

        try:
            # Check if AI assist is enabled and process the command
            if self.use_ai_assist:
                ic("Sending command to AI for processing.")
                response = self.ai_assist.handle_player_command(command)
                ic(f"AI responsed: {response}")
            else:
                ic("Processing command directly.")

                # Regular expressions for different command patterns
                patterns = {
                    r"^fast travel to (.+)$": self.fast_travel_to_world,
                    r"^(move to|go to) (.+)$": self.move_player,
                    r"^(give) (\d+) (.+)$": self.interact_with,  # for 'give 3 apples'
                    r"^(give) (.+)$": self.interact_with,        # for 'give sword'
                    r"^(take) (\d+) (.+)$": self.interact_with,  # for 'take 2 potions'
                    r"^(take) (.+)$": self.interact_with,        # for 'take key'
                    r"^(examine) (.+)$": self.examine_item,
                    r"^(talk to) (.+)$": self.interact_with,
                    r"^(open|close) (.+)$": self.interact_with,
                    r"^(look around|look|whereami|where am i|help)$": self.simple_command_handler
                }

                # Iterate through patterns to find a match
                for pattern, handler in patterns.items():
                    ic(f"Checking pattern: {pattern}")
                    ic(f"Checking handler: {handler}")
                    match = re.match(pattern, command, re.IGNORECASE)
                    ic(f"Match: {match}")
                    if match:
                        groups = match.groups()
                        if handler in [self.move_player, self.fast_travel_to_world]:
                            # For move_player and interact_with, pass only the required arguments
                            response = handler(groups[1])  # groups[1] will contain the target
                        else:
                            # For other commands, pass all captured groups
                            response = handler(*groups)
                        break
                else:
                    response = convert_text_to_display(f'Unknown command: {command}')


            # Emit the signal to indicate command processing is complete
            self.command_processed_signal.emit()
            return convert_text_to_display(response)

        except Exception as e:
            # Handle any exceptions that occur during command processing
            ic(f"Error processing command: {e}")
            response = convert_text_to_display(f"Error processing command: {e}")
            # Emit the signal even when an error occurs
            self.command_processed_signal.emit()
            return response

    def is_container_open(self):
        current_location = self.game_manager.player_sheet.location
        if isinstance(current_location, dict):
            current_location = current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location)

        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if container.get('isOpen', False):
                    ic(f"Container open: {container['name']}")
                    ic(f"Container open: {container['name']}")
                    return container['name']  
                
        ic("No container open.")
        return None # No container open

    def simple_command_handler(self, command):
        # Implement the logic for simple commands
        if command == "look" or command == "look around":
            return self.look_around()
        elif command == "whereami" or command == "where am i":
            return self.where_am_i()
        elif command == "help":
            return self.display_help()
        else:
            return f"Unknown simple command: {command}"

    def interact_with(self, *args):
        full_command = ' '.join(args)
        ic(f"Handling command: {full_command}")

        # Define regex patterns for interaction commands
        command_patterns = {
            r"^(talk to) (.+)$": self.handle_talk_to,
            r"^(give|take) (.+)$": self.handle_give_take,
            r"^(open) (.+)$": self.handle_open,
            r"^(close) (.+)$": self.handle_close
        }
        
        # Iterate through patterns to find a match
        for pattern, handler in command_patterns.items():
            ic(f"Checking pattern: {pattern}")
            match = re.match(pattern, full_command, re.IGNORECASE)
            if match:
                ic(f"Match found: {match}")
                # Pass only the necessary groups to the handler
                if handler in [self.handle_open, self.handle_close]:
                    return handler(match.group(2))  # Only pass the target name
                else:
                    return handler(*match.groups())

        return convert_text_to_display(f"Unknown interaction command: {full_command}")

    def handle_close(self, target_name=None):
        # Get the current location data
        current_location_data = self.get_current_location_data()

        if target_name:
            # Normalize the target name
            normalized_target_name = self.normalize_name(target_name)
            # Find the specific container by normalized name
            container = next((obj for obj in current_location_data.get('containers', [])
                            if self.normalize_name(obj['name']) == normalized_target_name), None)

            if not container:
                return convert_text_to_display(f"There is no '{target_name}' to close here.")
        else:
            # Find the first open container if no specific name is provided
            container = next((obj for obj in current_location_data.get('containers', [])
                            if obj.get('isOpen', False)), None)

            if not container:
                return convert_text_to_display("There are no open containers to close.")

        # Check if the container is already closed
        if not container.get('isOpen', True):
            return convert_text_to_display(f"The '{container['name']}' is already closed.")

        # Close the container
        container['isOpen'] = False

        return convert_text_to_display(f"You have closed the '{container['name']}'.")

    def handle_open(self, target_name):
        # Get the current location data
        current_location_data = self.get_current_location_data()

        # Normalize the target name
        normalized_target_name = self.normalize_name(target_name)
        # Find the container in the current location by normalized name
        container = next((obj for obj in current_location_data.get('containers', [])
                        if self.normalize_name(obj['name']) == normalized_target_name), None)

        if not container:
            return convert_text_to_display(f"There is no '{target_name}' to open here.")

        # Check if the container is already open
        if container.get('isOpen', False):
            contents = self.list_container_contents(container)
            return convert_text_to_display(f"The '{target_name}' is already open.\n{contents}")
        else:
            # Open the container
            container['isOpen'] = True
            contents = self.list_container_contents(container)
            return convert_text_to_display(f"You have opened the '{target_name}'.\n{contents}")

    def execute_interaction(self, interaction, target):
        if interaction['type'] == 'talk to':
            dialog = "\n".join(interaction.get('dialog', ["It has nothing to say."]))
            return f"{target['name']} says: \"{dialog}\""
        elif interaction['type'] == 'open':
            if target.get('isOpen', False):
                return f"{target['name']} is already open."
            else:
                target['isOpen'] = True
                return f"{target['name']} is now open."
        elif interaction['type'] == 'close':
            if not target.get('isOpen', False):
                return f"{target['name']} is already closed."
            else:
                target['isOpen'] = False
                return f"{target['name']} is now closed."

    def handle_talk_to(self, command, npc_name):
        ic(f"Handling 'talk to' command with NPC: {npc_name}")

        # Get the current location data
        location_data = self.get_current_location_data()

        # Find the NPC in the current location
        target_npc = self.find_interaction_target(npc_name, location_data)

        if target_npc:
            # Execute the 'talk to' interaction if the NPC is found
            interaction = {'type': 'talk to'}
            return self.execute_interaction(interaction, target_npc)
        else:
            # NPC not found in the current location
            return convert_text_to_display(f"Cannot find '{npc_name}' to talk to.")

    def handle_give_take(self, action, details):
        ic(f"Handling '{action}' command with details: {details}")

        # Split the details into parts
        target_name, quantity, item_name = self.parse_give_take_details(details.split())

        # Get the current location data
        location_data = self.get_current_location_data()

        if not target_name:
            # Find an open container if no target is specified
            open_containers = [c for c in location_data.get('containers', []) if c.get('isOpen', False)]
            target = open_containers[0] if open_containers else None
        else:
            # Find the specified target
            target = self.find_interaction_target(target_name, location_data)

        if not target:
            return convert_text_to_display(f"Cannot find '{target_name}' to {action}.")

        if action == "give":
            # Logic to handle the give command
            return self.process_give_command(target, item_name, quantity)
        elif action == "take":
            # Logic to handle the take command
            return self.process_take_command(target, item_name, quantity)

    def parse_give_take_details(self, parts):
        # Check if the last part is a digit (quantity), and adjust accordingly
        if parts[-1].isdigit():
            quantity = int(parts[-1])
            item = ' '.join(parts[:-1])  # All parts except the last one
            target = None  # No explicit target specified
        else:
            item = ' '.join(parts)
            quantity = 1  # Default quantity
            target = None  # No explicit target specified

        return target, quantity, item

    def find_interaction_target(self, target_name, location_data):
        normalized_target_name = self.normalize_name(target_name)

        # Check NPCs
        for npc in location_data.get('npcs', []):
            ic(f"Checking NPC: {npc['name']}")
            if self.normalize_name(npc['name']) == normalized_target_name:
                return npc

        # Check items
        for item in location_data.get('items', []):
            ic(f"Checking item: {item['name']}")
            if self.normalize_name(item['name']) == normalized_target_name:
                return item

        # Check containers
        for container in location_data.get('containers', []):
            ic(f"Checking container: {container['name']}")
            if self.normalize_name(container['name']) == normalized_target_name:
                return container

        return None

    def process_take_command(self, target, item_name, quantity):
        ic(f"Processing take command: taking {quantity} of {item_name} from {target['name']}")

        # Check if the target has the item and in sufficient quantity
        if not self.target_has_item(target, item_name, quantity):
            return convert_text_to_display(f"The {target['name']} does not have {quantity} of {item_name}.")

        # If the target is a container, check if it is open
        if target.get('type') == 'container':
            if not target.get('isOpen', False):
                return convert_text_to_display(f"The {target['name']} is closed. You cannot take items from it.")

        # Remove the item from the target's inventory and add it to the player's inventory
        self.remove_item_from_target(target, item_name, quantity)
        self.add_item_to_player_inventory(item_name, quantity)

        return convert_text_to_display(f"Took {quantity} of {item_name} from {target['name']}.")

    def add_item_to_player_inventory(self, item_name, quantity):
        # Access the player's inventory
        player_inventory = self.game_manager.player_sheet.inventory

        # Check if the player already has the item
        for item in player_inventory:
            if item['name'] == item_name:
                # If the item exists, update the quantity
                item['quantity'] += quantity
                return

        # If the item is not in the inventory, add it as a new entry
        new_item = {'name': item_name, 'quantity': quantity}
        player_inventory.append(new_item)


    def remove_item_from_target(self, target, item_name, quantity):
        # Access the target's inventory
        target_inventory = target.get('inventory', [])

        # Iterate through the inventory to find and remove the item
        for item in target_inventory:
            if item['name'] == item_name:
                if item['quantity'] > quantity:
                    # Reduce the quantity of the item
                    item['quantity'] -= quantity
                    return
                elif item['quantity'] == quantity:
                    # Remove the item completely if the quantity matches
                    target_inventory.remove(item)
                    return

    def target_has_item(self, target, item_name, quantity):
        # Access the target's inventory. This structure is an example.
        target_inventory = target.get('inventory', [])

        # Search for the item and check its quantity
        for item in target_inventory:
            if item['name'] == item_name and item['quantity'] >= quantity:
                return True

        # If the item is not found in the required quantity
        return False

    def process_give_command(self, target, item_name, quantity):
        ic(f"Processing give command: giving {quantity} of {item_name} to {target['name']}")

        # Validate if the player has the item and in sufficient quantity
        if not self.player_has_item(item_name, quantity):
            return convert_text_to_display(f"You do not have {quantity} of {item_name} to give.")

        # If the target is a container, check if it is open
        if target.get('type') == 'container':
            if not target.get('isOpen', False):
                return convert_text_to_display(f"The {target['name']} is closed. You cannot put items in it.")

        # Remove the item from the player's inventory and add it to the target's inventory
        self.remove_item_from_player(item_name, quantity)
        self.add_item_to_target_inventory(target, item_name, quantity)

        return convert_text_to_display(f"Gave {quantity} of {item_name} to {target['name']}.")

    def remove_item_from_player(self, item_name, quantity):
        # Access the player's inventory
        player_inventory = self.game_manager.player_sheet.inventory

        # Iterate through the inventory to find and remove the item
        for item in player_inventory:
            if item['name'] == item_name:
                if item['quantity'] > quantity:
                    # Reduce the quantity of the item
                    item['quantity'] -= quantity
                    return
                elif item['quantity'] == quantity:
                    # Remove the item completely if the quantity matches
                    player_inventory.remove(item)
                    return

    def player_has_item(self, item_name, quantity):
        ic(f"Checking if player has {quantity} of {item_name}")
        # Normalize the item name for comparison
        normalized_item_name = self.normalize_name(item_name)
        player_inventory = self.game_manager.player_sheet.inventory
        ic(f"Player inventory: {player_inventory}")

        for item in player_inventory:
            ic(f"Checking item: {item}")
            # Normalize the name of the item in the inventory before comparison
            if self.normalize_name(item['name']) == normalized_item_name and item['quantity'] >= quantity:
                return True

        return False

    def add_item_to_target_inventory(self, target, item_name, quantity):
        # Assuming the target's inventory is a list of item dictionaries
        target_inventory = target.get('inventory', [])

        # Check if the item already exists in the target's inventory
        for item in target_inventory:
            if item['name'] == item_name:
                # If the item exists, just update the quantity
                item['quantity'] += quantity
                return

        # If the item is not in the inventory, add it as a new entry
        new_item = {'name': item_name, 'quantity': quantity}
        target_inventory.append(new_item)


    def list_container_contents(self, container):
        contents_text = f"{container['name']} contains:\n"
        for item in container.get('contains', []):
            contents_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        ic(f"Contents text: {contents_text}")
        return contents_text.strip()

    def get_current_location_data(self):
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)
        if location_data:
            ic(f"Current location data retrieved for: {current_location_str}")
        else:
            ic(f"No data found for current location: {current_location_str}")
        return location_data

    def find_location_data(self, location_name):
        if isinstance(location_name, dict):
            location_name = location_name.get("location/sublocation", "Unknown Location")

        normalized_location_name = self.normalize_name(location_name)
        ic("finding location debug")
        ic(self.world_data)
        for location in self.world_data.get('locations', []):
            ic(f"Searching for location: {normalized_location_name}")
            if isinstance(location, dict) and 'name' in location:
                if self.normalize_name(location['name']) == normalized_location_name:
                    ic(f"Found location: {location_name}")
                    return location
                for sublocation in location.get('sublocations', []):
                    if self.normalize_name(sublocation['name']) == normalized_location_name:
                        ic(f"Found sublocation: {location_name}")
                        return sublocation
                    for room in sublocation.get('rooms', []):
                        if self.normalize_name(room['name']) == normalized_location_name:
                            ic(f"Found room: {location_name}")
                            room['parent_sublocation'] = sublocation['name']  # This is optional, for context
                            return room
        ic(f"Location or room not found: {location_name}")
        return None

    def fast_travel_to_world(self, world_name):
        available_worlds = [world.replace(" ", "").lower() for world in self.game_manager.player_sheet.get_fast_travel_worlds()]
        formatted_world_name = world_name.replace(" ", "").lower()

        if formatted_world_name not in available_worlds:
            text = f"{world_name} is not available for fast travel."
            self.display_text_signal.emit(text)  # Emit signal instead of direct call
            return False  # Return a boolean based on the outcome
        
        try:
            self.game_manager.save_game()  # Save the game before fast traveling

            self.world_data = load_working_world_data(formatted_world_name)  # Load the world data for the new world

            main_entry_location = next((loc for loc in self.world_data['locations'] if loc.get('main-entry', False)), None)
            if main_entry_location:
                new_location = {"world": formatted_world_name, "location/sublocation": main_entry_location['name']}
                self.game_manager.player_sheet.location = new_location
                self.update_game_state_for_fast_travel(formatted_world_name)  
                self.game_manager.update_location(new_location)  # Update the game manager with the new location

                # Since where_am_i might try to directly modify the UI, it should return a plain string, which can be formatted and emitted as a signal
                text = self.where_am_i()
                html_command = convert_text_to_display(f"{text}.")
                self.display_text_signal.emit(html_command)
                return html_command 
            else:
                text = convert_text_to_display(f"No main entry location found in {world_name}.")
                self.display_text_signal.emit(text)  # Emit signal instead of direct call
                return text
        except Exception as e:
            text = f"Error loading world data for {world_name}: {e}"
            html_text = convert_text_to_display(text)
            self.display_text_signal.emit(text)  # Emit signal instead of direct call
            return html_text


    def update_game_state_for_fast_travel(self, new_world_name):
        # Update any world-specific game state here
        CapitalizedWorldName = new_world_name.capitalize()
        self.game_manager.world_data = self.world_data  # Synchronize GameManager's world data
        html_command = convert_text_to_display(f"You have arrived in {CapitalizedWorldName}.")
        self.display_text_signal.emit(f'{html_command}')  # Emit signal instead of direct call

    def list_entities(self, entity_type, location_data):
        entities_text = f"{entity_type.capitalize()} here:\n"
        entities = location_data.get(entity_type, [])

        for entity in entities:
            if entity_type == 'rooms' or entity_type == 'sublocations':
                name = entity.get('name', 'Unnamed')
                description = entity.get('description', 'No description available')
                entities_text += f"- {name}: {description}\n"
            elif entity_type == 'items':
                name = entity.get('name', 'Unnamed Item')
                quantity = entity.get('quantity', 1)
                description = entity.get('description', 'No description available')
                entities_text += f"- {name} ({quantity}) - {description}\n"
            elif entity_type == 'npcs':
                name = entity.get('name', 'Unnamed NPC')
                description = entity.get('description', 'An interesting character.')
                entities_text += f"- {name}: {description}\n\n"
            elif entity_type == 'containers':
                name = entity.get('name', 'Unnamed Container')
                description = entity.get('description', 'No description available')
                entities_text += f"- {name} - {description}\n"
            elif entity_type == 'paths':
                for direction, destination in entity.items():
                    entities_text += f"- {direction.title()}: {destination}\n"
                break  # Assuming 'paths' is a dictionary, not a list
            elif entity_type == 'interactables':
                name = entity.get('name', 'Unnamed Interactable')
                description = entity.get('description', 'No description available')
                entities_text += f"- {name} - {description}\n"

        ic(f"{entity_type.capitalize()} text: {entities_text}")
        return entities_text.strip()



    def build_scene_text(self, location_data):
        if not location_data:
            return "You are in an unknown location."

        scene_text = self.describe_location(location_data) + "\n"
        scene_text += self.list_entities('items', location_data) + "\n"
        scene_text += self.list_entities('containers', location_data) + "\n"
        scene_text += self.list_entities('npcs', location_data) + "\n"
        scene_text += self.list_entities('paths', location_data) + "\n"
        scene_text += self.list_entities('sublocations', location_data) + "\n"
        scene_text += self.list_entities('rooms', location_data) + "\n"

        return scene_text.strip()
    
    def normalize_name(self, name):
        ic(f"Normalizing name: {name}")
        normalized_name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
        normalized_name = re.sub(r'\s+', ' ', normalized_name).strip().lower()
        ic(f"Normalized name: {normalized_name}")
        return normalized_name

    def describe_room(self, room_data):
        description = f"You are in {room_data['name']}. {room_data['description']}"
        if 'keywords' in room_data:
            keywords_text = ", ".join(room_data['keywords'])
            description += f" \n Keywords: {keywords_text}\n"
        ic(f"Room description: {description}")
        return description


    def describe_location(self, location_data):
        description = f"You are at {location_data['name']}. {location_data['description']}"
        if 'keywords' in location_data:
            keywords_text = ", ".join(location_data['keywords'])
            description += f" \n\n Keywords: {keywords_text}\n"
        ic(f"Location description: {description}")
        return description


    def is_item_in_open_container(self, item_name, location_data):
        normalized_item_name = self.normalize_name(item_name)
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == normalized_item_name:
                        return True
        return False
        
    def move_player(self, location_name):
        # Get the current location data from the player's current location
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location.get("location/sublocation", "Unknown Location")
        
        ic(f"Attempting to move. Current location: {current_location_str}, Destination: {location_name}") 

        current_location_data = self.find_location_data(current_location_str)
        if not current_location_data:
            return "You are in an unknown location and cannot move."

        sanitized_location_name = self.normalize_name(location_name)
        ic(f"Sanitized destination name: {sanitized_location_name}") 

        if 'paths' in current_location_data:
            for direction, destination in current_location_data['paths'].items():
                normalized_destination = self.normalize_name(destination)
                ic(f"Checking path: {direction} to {normalized_destination}") 
                if normalized_destination == sanitized_location_name:
                    self.game_manager.player_sheet.location = {"world": current_location['world'], "location/sublocation": destination}
                    ic(f"Player moved to {destination}.")
                    text = convert_text_to_display(f"Moving to {destination}.")
                    self.display_text_signal.emit(text)
                    return f"{self.where_am_i()}."

        if 'sublocations' in current_location_data:
            for sublocation in current_location_data['sublocations']:
                normalized_sublocation_name = self.normalize_name(sublocation['name'])
                ic(f"Checking sublocation: {normalized_sublocation_name}") 
                if normalized_sublocation_name == sanitized_location_name:
                    new_location_dict = {"world": current_location['world'], "location/sublocation": sublocation['name']}
                    self.game_manager.player_sheet.location = new_location_dict
                    ic(f"Player moved to {sublocation['name']}.")
                    text = convert_text_to_display(f"Moving to {sublocation['name']}.")
                    self.display_text_signal.emit(text)
                    return f"{self.where_am_i()}."
                if 'rooms' in sublocation:
                    for room in sublocation['rooms']:
                        normalized_room_name = self.normalize_name(room['name'])
                        ic(f"Checking room: {normalized_room_name} in sublocation: {normalized_sublocation_name}")  
                        if normalized_room_name == sanitized_location_name:
                            new_location_dict = {
                                "world": current_location['world'],
                                "location/sublocation": f"{sublocation['name']}/{room['name']}"
                            }
                            self.game_manager.player_sheet.location = new_location_dict
                            ic(f"Player moved to {room['name']} within {sublocation['name']}.")
                            text = convert_text_to_display(f"Moving to {room['name']} within {sublocation['name']}.")
                            self.display_text_signal.emit(text)
                            return f"{self.where_am_i()}."
                        else:
                            return "You cannot access this area yet."

        ic(f"Could not find path to: {sanitized_location_name} from {current_location_str}")
        return f"Cannot determine how to move to '{location_name}'."

    def examine_item(self, item_name):
        current_location_data = self.get_current_location_data()
        item = self.get_item_data(item_name, current_location_data)

        if item:
            return f"{item['name']}: {item['description']}"
        return f"{item_name} not found."

    def where_am_i(self):
        # Extract location name from the player's location
        location = self.game_manager.player_sheet.location
        location_name = location.get("location/sublocation", "Unknown Location") if isinstance(location, dict) else location

        return f"You are in {location_name}."

    def look_around(self):
        current_location_data = self.get_current_location_data()
        if current_location_data:
            return self.create_scene_description(current_location_data)
        return "It's too dark to see anything."

    def display_help(self):
        help_text = (
            "Available commands:\n\n"
            "take <item> - Take an item from a NPC or container.\n Example: 'take potion'\n\n"
            "give <quantity> <item> - Give an item to a NPC or container.\n Example: 'give 2 potions'\n\n"
            "move <location> - Move to new location.\n Example: 'move to the garden'\n\n"
            "examine <item> - Examine an items.\n Example: 'examine key'\n\n"
            "whereami - Find out your current location.\n Example: 'whereami'\n\n"
            "look around: Look around at your environment.\n Example: 'look around'\n\n"
            "open <container>: Open a container.\n Example: 'open chest'\n\n"
            "Fast travel to <world>: Fast travel to a different world.\n Example: 'fast travel to the moon'\n\n"
            "talk to <NPC>: Talk to an NPC.\n Example: 'talk to the guard'\n\n"
            "interact with <interactable>: Interact with an object.\n Example: 'interact with computer'\n\n"
            "close: Close container.\n Example: 'close'\n\n"
            "help: Display this list of commands.\n"
        )
        return help_text
    
    def update_world_data(self, location_name, update_dict=None, new_world_name=None):
        """
        Update the world_data based on the provided location and update dictionary or load a new world.

        Args:
        location_name (str): The name of the location to update.
        update_dict (dict, optional): A dictionary containing the keys to be updated.
        new_world_name (str, optional): The name of the new world to load. If provided, 
                                        it will update the entire world data.
        """
        if new_world_name:
            # Load and update the world data for a new world
            new_world_data = load_working_world_data(new_world_name)
            if new_world_data:
                self.world_data = new_world_data
                ic(f"World data updated to {new_world_name}")
                return True
            else:
                ic(f"Failed to load world data for {new_world_name}")
                return False
        else:
            # Update specific location in the current world data
            for location in self.world_data.get('locations', []):
                if location['name'].lower() == location_name.lower():
                    self._apply_updates(location, update_dict)
                for sublocation in location.get('sublocations', []):
                    if sublocation['name'].lower() == location_name.lower():
                        self._apply_updates(sublocation, update_dict)
            return True


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


 
    def get_item_data(self, item_name, location_data):
        # Check in location items
        for item in location_data.get('items', []):
            if self.normalize_name(item['name']) == self.normalize_name(item_name):
                return item

        # Check in open containers
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == self.normalize_name(item_name):
                        return item
        return None
    
    def create_scene_description(self, location_data):
        description = f"You are at {location_data['name']}. {location_data['description']}\n"
        if 'keywords' in location_data:
            description += f"Keywords: {', '.join(location_data['keywords'])}\n"

        # Utilize the list_entities method for various entities
        if 'items' in location_data:
            description += self.list_entities('items', location_data) + "\n"
        if 'npcs' in location_data:
            description += self.list_entities('npcs', location_data) + "\n"
        if 'containers' in location_data:
            description += self.list_entities('containers', location_data) + "\n"

        return description.strip()
