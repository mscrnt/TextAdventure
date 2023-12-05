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
        # Split the command into action and target
        command_parts = command.split(maxsplit=1)
        command_action = command_parts[0].lower()
        command_target = command_parts[1] if len(command_parts) > 1 else ""

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
                # Handlers that need the whole command
                full_command_handlers = {"open", "close", "talk to", "take", "give", "examine"}
                target_only_handlers = {"move to", "go to", "fast travel to"}

                # For handlers that require only the command action unlike 'interact_with'
                if command_action in full_command_handlers:
                    response = self.interact_with(command)
                elif command_action in target_only_handlers:
                    response = self.move_player(self.normalize_name(command_target))
                elif command_action == "look around" or command_action == "look":
                    response = self.look_around()
                elif command_action == "whereami" or command_action == "where am i":
                    response = self.where_am_i()
                elif command_action == "help":
                    response = self.display_help()
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
        
    def interact_with(self, command):
        ic(f"Interacting with: {command}")
        # Split the command into action and remaining parts
        command_parts = command.split(maxsplit=1)
        ic(f"Command parts: {command_parts}")
        ic(f"Command parts length: {len(command_parts)}")
        action = command_parts[0].lower()
        remaining_command = command_parts[1] if len(command_parts) > 1 else None

        current_location_data = self.get_current_location_data()

        if action in ["talk to", "trade with", "quest"]:
            ic(f"Interacting with NPC: {remaining_command}")
            return self._interact_with_npc(remaining_command, action, current_location_data)
        elif action in ["take", "examine"]:
            ic(f"Interacting with item: {remaining_command}")
            item_normalized = self.normalize_name(remaining_command)
            return self._interact_with_item(item_normalized, action, current_location_data)
        elif action in ["open", "close"]:
            ic(f"Interacting with container: {remaining_command}")
            container_normalized = self.normalize_name(remaining_command)
            return self._toggle_container(container_normalized, action, current_location_data)
        elif action == "give":
            ic(f"Interacting with give command: {remaining_command}")
            # Assuming the format "give quantity item_name"
            try:
                # Split the remaining portion to separate quantity and item
                give_parts = remaining_command.split(maxsplit=1)
                quantity = int(give_parts[0])
                item_name = give_parts[1]
                item_normalized = self.normalize_name(item_name)
                ic(f"Giving {quantity} of {item_normalized}")
                return self._handle_give_action(item_normalized, quantity, current_location_data)
            except (IndexError, ValueError):
                ic("Give command parts are incorrect")
                return "Invalid 'give' command format. Please specify quantity and item name."
        else:
            return "Unknown interaction."
            
    def _interact_with_npc(self, npc_name, action, location_data):
        normalized_npc_name = self.normalize_name(npc_name)

        # Find the NPC in the current location
        npc = next((n for n in location_data.get('npcs', []) if self.normalize_name(n['name']) == normalized_npc_name), None)
        if not npc:
            return f"No one named '{npc_name}' found here."

        # Check available interactions for the NPC
        for interaction in npc.get('interactions', []):
            if action == 'talk to' and interaction['type'] == 'talk':
                dialog = "\n".join(interaction.get('dialog', []))
                return f"{npc['name']} says: \"{dialog}\""
            elif action in ['trade with', 'quest'] and interaction['type'] == action.replace(" with", ""):
                return f"{npc['name']} interaction: {interaction['description']}"

        return f"{npc['name']} cannot perform this action."


    def _interact_with_item(self, item_name, action, location_data):
        normalized_item_name = self.normalize_name(item_name)

        # Search for the item in the current location and open containers
        item = self.get_item_data(normalized_item_name, location_data)
        if not item:
            return f"No item named '{item_name}' found here."

        if action == 'examine':
            return f"{item['name']}: {item.get('description', 'No description available.')}"
        elif action == 'take':
            if item.get('collectable', False):
                self.game_manager.player_sheet.add_item(item)
                # Remove the item from the location or container
                self.remove_item_from_environment(item, location_data)
                return f"You have taken {item['name']}."
            else:
                return f"{item['name']} cannot be taken."

        return f"You can't {action} {item['name']}."
    
    def _give_item(self, item_name, quantity, current_location_data):
        # Here implement fetching player inventory and checking for item and quantity
        player_inventory = self.get_player_inventory()  # This is conceptual, actual code may differ.

        # Check if player has enough of the item
        if player_inventory.get(item_name, 0) >= quantity:
            # Deduct the item from the player's inventory
            player_inventory[item_name] -= quantity

            # Check if any NPCs or containers in the location can receive the item
            # Assuming there's a method for adding items to the recipient
            # ...

            return f"Gave {quantity} of '{item_name}' to ..."
        else:
            return f"You do not have {quantity} of '{item_name}' to give."

    def remove_item_from_environment(self, item, location_data):
        # Remove the item from the location or container
        item_name = item['name']
        normalized_item_name = self.normalize_name(item_name)

        if self.is_item_in_open_container(normalized_item_name, location_data):
            for container in location_data.get('containers', []):
                if container.get('isOpen', False):
                    container['contains'] = [i for i in container.get('contains', []) if self.normalize_name(i['name']) != normalized_item_name]
        else:
            location_data['items'] = [i for i in location_data.get('items', []) if self.normalize_name(i['name']) != normalized_item_name]


    def _toggle_container(self, container_name, action, location_data):
        normalized_container_name = self.normalize_name(container_name)

        # Search for the container in the current location
        container = next((c for c in location_data.get('containers', []) if self.normalize_name(c['name']) == normalized_container_name), None)
        if not container:
            return f"No container named '{container_name}' found here."

        if action == 'open':
            if container.get('isOpen', False):
                return f"{container['name']} is already open."
            container['isOpen'] = True
            contents = self.list_container_contents(container)
            return f"You open {container['name']}. Contents: {contents}"

        elif action == 'close':
            if not container.get('isOpen', False):
                return f"{container['name']} is already closed."
            container['isOpen'] = False
            return f"You close {container['name']}."

        return f"Cannot perform the action '{action}' on {container['name']}."
    
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

    def get_container_data(self, container_name):
        location_data = self.get_current_location_data()
        if 'containers' in location_data:
            for container in location_data['containers']:
                if self.normalize_name(container['name']) == self.normalize_name(container_name):
                    return container
        return None
    
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
        location_data = self.get_current_location_data()
        if not location_data:
            return "You are in an unknown location."

        scene_text = ""
        if 'type' in location_data and location_data['type'] == 'room':
            scene_text += self.describe_room(location_data) + "\n"
            scene_text += self.list_entities('items', location_data) + "\n" if 'items' in location_data else ""
            scene_text += self.list_entities('npcs', location_data) + "\n" if 'npcs' in location_data else ""
            scene_text += self.list_entities('containers', location_data) + "\n" if 'containers' in location_data else ""
        else:
            scene_text += self.describe_location(location_data) + "\n"
            scene_text += self.list_entities('items', location_data) + "\n" if 'items' in location_data else ""
            scene_text += self.list_entities('containers', location_data) + "\n" if 'containers' in location_data else ""
            scene_text += self.list_entities('npcs', location_data) + "\n" if 'npcs' in location_data else ""
            scene_text += self.list_entities('paths', location_data) + "\n" if 'paths' in location_data else ""
            scene_text += self.list_entities('sublocations', location_data) + "\n" if 'sublocations' in location_data else ""
            scene_text += self.list_entities('rooms', location_data) + "\n" if 'rooms' in location_data else ""

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
