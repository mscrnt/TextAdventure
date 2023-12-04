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
        try:
            html_command = convert_text_to_display(f"Processing command: {command}")
            self.game_manager.display_text_signal.emit(html_command)
            ic(f'Ai assist: {self.use_ai_assist}')
            if self.use_ai_assist:
                ic("Sending command to AI for processing.")
                response = self.ai_assist.handle_player_command(command)
                ic(f"AI response: {response}")
                return response
            else:
                ic("Processing command directly.")
                command_dispatch = {
                    "take": (self.take_item, command[len("take"):].strip()),
                    "move to": (self.move_player, command[len("move to"):].strip()),
                    "go to": (self.move_player, command[len("go to"):].strip()),
                    "examine": (self.examine_item, command[len("examine"):].strip()),
                    "whereami": (self.where_am_i, ""),
                    "where am i": (self.where_am_i, ""),
                    "look around": (self.look_around, ""),
                    "look": (self.look_around, ""),
                    "talk to": (self.talk_to_npc, command[len("talk to"):].strip()),
                    "interact with": (self.interact_with, command[len("interact with"):].strip()),
                    "open": (self.open_container, command[len("open"):].strip()),
                    "close": (self.close_container, ""),
                    "fast travel to": (self.fast_travel_to_world, command[len("fast travel to"):].strip()),
                    "give": (self.give_item, command[len("give"):].strip()),
                    "help": (self.display_help, "")
                }
                for prefix, (method, argument) in command_dispatch.items():
                    if command.startswith(prefix):
                        text = method(argument) if argument else method()
                        html_text = convert_text_to_display(text)
                        return html_text
                text = f'Unknown command: {command}'
                html_text = convert_text_to_display(text)
                return html_text
        except Exception as e:
            ic(f"Error processing command: {e}")
            return f"Error processing command: {e}"

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

    def find_main_entry_location(self, world_data):
        # Find the main entry location in the new world data
        for location in world_data.get('locations', []):
            if location.get('main-entry', False):
                return location['name']
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


    def get_current_location_data(self):
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)
        if location_data:
            ic(f"Current location data retrieved for: {current_location_str}")
        else:
            ic(f"No data found for current location: {current_location_str}")
        return location_data


    def talk_to_npc(self, npc_name):
        normalized_npc_name = self.normalize_name(npc_name)

        # Get the current location data
        location_data = self.get_current_location_data()

        if 'npcs' in location_data:
            for npc in location_data['npcs']:
                if self.normalize_name(npc['name']) == normalized_npc_name:
                    # If we found the NPC, check quests for this NPC before initiating dialogue
                    self.last_spoken_npc = npc_name
                    ic(f'Checking objectives for {npc_name}')
                    self.game_manager.quest_tracker.check_npc_quests(npc_name)
                    # Handle the dialogue
                    return self.handle_npc_dialogue(npc)

        return f"No one named '{npc_name}' found here."

    def handle_npc_dialogue(self, npc):
        dialogue_text = "\n".join(npc['dialog']) if 'dialog' in npc else ""
        interactions_text = ""
        if 'interactions' in npc:
            for interaction in npc['interactions']:
                interactions_text += f"- {interaction['type']}: {interaction['description']}\n"
        return f"{npc['name']} says: \"{dialogue_text}\"\nInteractions: {interactions_text}"



    def interact_with(self, interactable_name):
        # Normalize the interactable name for comparison
        normalized_interactable_name = self.normalize_name(interactable_name)

        # Get the current location data using the new method
        location_data = self.get_current_location_data()

        if 'interactables' in location_data:
            for interactable in location_data['interactables']:
                if self.normalize_name(interactable['name']) == normalized_interactable_name:
                    # Found the interactable, now handle the specific interaction
                    return self.handle_interactable_interaction(interactable)

        return f"There is nothing to interact with named '{interactable_name}' here."


    def handle_interactable_interaction(self, interactable):
        # Check the type of interaction and perform the corresponding action
        interaction_type = interactable.get('type', 'generic')

        if interaction_type == 'puzzle':
            return self.solve_puzzle(interactable)
        elif interaction_type == 'machine':
            return self.operate_machine(interactable)
        else:
            # Handle generic or other types of interactions
            return f"You interact with {interactable['name']}. {interactable.get('description', 'It seems interesting.')}"

    def solve_puzzle(self, puzzle):
        # Add logic for solving puzzles
        return f"You attempt to solve the puzzle: {puzzle['name']}."

    def load_world_data(self, world_name):
        try:
            with open(f'data/worlds/{world_name}.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            ic(f"Error loading world data for {world_name}: {e}")
            return None

    def build_scene_text(self, location_data):
        location_data = self.get_current_location_data() 

        if not location_data:
            return "You are in an unknown location."

        scene_text = ""
        if 'type' in location_data and location_data['type'] == 'room':
            # If the player is in a room, prioritize room details
            scene_text += self.describe_room(location_data) + "\n"
            scene_text += self.list_items(location_data) + "\n" if 'items' in location_data else ""
            scene_text += self.list_npcs(location_data) + "\n" if 'npcs' in location_data else ""
            scene_text += self.list_containers(location_data) + "\n" if 'containers' in location_data else ""
        else:
            # If the player is not in a room, build the scene from the location or sublocation level
            scene_text += self.describe_location(location_data) + "\n"
            scene_text += self.list_items(location_data) + "\n" if 'items' in location_data else ""
            scene_text += self.list_containers(location_data) + "\n" if 'containers' in location_data else ""
            scene_text += self.list_npcs(location_data) + "\n" if 'npcs' in location_data else ""
            scene_text += self.show_paths(location_data) + "\n" if 'paths' in location_data else ""
            scene_text += self.show_sublocations(location_data) + "\n" if 'sublocations' in location_data else ""
            # Check for rooms only if in a sublocation
            scene_text += self.list_rooms(location_data) + "\n" if 'rooms' in location_data else ""

        return scene_text.strip()
    
    def build_room_scene_text(self, room_data):
        # Build scene text specifically for rooms
        scene_text = self.describe_room(room_data)
        scene_text += self.list_items(room_data)
        scene_text += self.list_npcs(room_data)
        return scene_text

    def describe_room(self, room_data):
        description = f"You are in {room_data['name']}. {room_data['description']}"
        if 'keywords' in room_data:
            keywords_text = ", ".join(room_data['keywords'])
            description += f" \n Keywords: {keywords_text}\n"
        ic(f"Room description: {description}")
        return description

    def list_npcs(self, location_data):
        npcs_text = "People here:\n"
        for npc in location_data.get('npcs', []):
            npc_description = npc.get('description', 'An interesting character.')
            npcs_text += f"- {npc['name']}: {npc_description}\n\n"
        return npcs_text

    def describe_location(self, location_data):
        description = f"You are at {location_data['name']}. {location_data['description']}"
        if 'keywords' in location_data:
            keywords_text = ", ".join(location_data['keywords'])
            description += f" \n\n Keywords: {keywords_text}\n"
        ic(f"Location description: {description}")
        return description
    
    def list_rooms(self, location_data):
        rooms_text = "Rooms here:\n"
        for room in location_data.get('rooms', []):
            room_name = room.get('name', 'Unnamed Room')
            room_description = room.get('description', 'No description available')
            rooms_text += f"- {room_name}: {room_description}\n"
        ic(f"Rooms text: {rooms_text}")
        return rooms_text

    def list_items(self, location_data):
        items_text = "Items here:\n"
        for item in location_data.get('items', []):
            items_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        ic(f"Items text: {items_text}")
        return items_text

    def list_interactables(self, location_data):
        interactables_text = "You can interact with:\n"
        for interactable in location_data.get('interactables', []):
            interactables_text += f"- {interactable['name']} - {interactable['description']}\n"
        ic(f"Interactables text: {interactables_text}")
        return interactables_text

    def normalize_name(self, name):
        ic(f"Normalizing name: {name}")
        normalized_name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
        normalized_name = re.sub(r'\s+', ' ', normalized_name).strip().lower()
        ic(f"Normalized name: {normalized_name}")
        return normalized_name


    def open_container(self, container_name):
        container_name = self.normalize_name(container_name)

        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        if location_data and 'containers' in location_data:
            for container in location_data['containers']:
                if self.normalize_name(container['name']) == container_name:
                    container['isOpen'] = True  
                    ic(f"Container opened: {container_name}, isOpen: {container['isOpen']}")
                    ic(f"Container opened: {container_name}, isOpen: {container['isOpen']}")
                    return self.list_container_contents(container)

        return f"No container named '{container_name}' found here."

    def list_container_contents(self, container):
        contents_text = f"{container['name']} contains:\n"
        for item in container.get('contains', []):
            contents_text += f"- {item['name']} ({item['quantity']}) - {item['description']}\n"
        ic(f"Contents text: {contents_text}")
        return contents_text.strip()

    def list_containers(self, location_data):
        containers_text = "Containers:\n"
        for container in location_data.get('containers', []):
            containers_text += f"- {container['name']} - {container['description']}\n"
        ic(f"Containers text: {containers_text}")
        return containers_text

    def show_paths(self, location_data):
        paths_text = "Paths available:\n"
        for direction, destination in location_data.get('paths', {}).items():
            paths_text += f"- {direction.title()}: {destination}\n"
        ic(f"Paths text: {paths_text}")
        return paths_text

    def show_transport_options(self, location_data):
        transport_text = "Transport options:\n"
        for transport in location_data.get('transport', []):
            transport_text += f"- {transport['type']} to {', '.join(transport['destinations'])}\n"
        ic(f"Transport text: {transport_text}")
        return transport_text

    def take_item(self, item_name):
        normalized_item_name = self.normalize_name(item_name)

        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        # Check if the item is in an open container
        item_taken = self._take_item_from_open_container(normalized_item_name, location_data)
        if item_taken:
            ic(f"Item taken: {item_taken}")
            return item_taken

        # If not in a container, try taking directly from the location
        for item in location_data.get('items', []):
            if self.normalize_name(item['name']) == normalized_item_name:
                # Remove the item from the location
                location_data['items'].remove(item)
                self.update_world_data(current_location_str, {'items': location_data['items']})
                self.game_manager.player_sheet.add_item(item)
                ic(f"Item taken: {item['name']}")
                return f"You have taken {item['name']}."

        ic(f"Item not found: {item_name}")
        return "You cannot take that item."


    def _take_item_from_open_container(self, item_name, location_data):
        normalized_item_name = self.normalize_name(item_name)  
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == normalized_item_name:
                        if not item.get('collectable', True):
                            return f"{item['name']} cannot be taken."
                        container['contains'].remove(item)
                        self.update_world_data(location_data['name'], {'containers': location_data['containers']})
                        self.game_manager.player_sheet.add_item(item)
                        ic(f"You have taken {item['name']} from {container['name']}.")
                        return f"You have taken {item['name']} from {container['name']}."

        ic(f"Item not found: {item_name}")
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
                    ic(f"Container open: {container['name']}")
                    return container['name']  
                
        ic("No container open.")
        return None # No container open
    
    def close_container(self):
        open_container_name = self.is_container_open()
        if open_container_name:
            current_location = self.game_manager.player_sheet.location
            location_data = self.find_location_data(current_location)
            
            if location_data and 'containers' in location_data:
                for container in location_data['containers']:
                    if container['name'] == open_container_name:
                        container['isOpen'] = False  
                        ic(f"Container closed: {open_container_name}, isOpen: {container['isOpen']}")
                        ic(f"Container closed: {open_container_name}, isOpen: {container['isOpen']}")
                        return f"You have closed {open_container_name}."
        
        ic("No container open.")
        return "You are not in an open container."

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
        # Normalize the item name for comparison
        normalized_item_name = self.normalize_name(item_name)

        # Get the current location data
        current_location = self.game_manager.player_sheet.location
        current_location_str = current_location if isinstance(current_location, str) else current_location.get("location/sublocation", "Unknown Location")
        location_data = self.find_location_data(current_location_str)

        # Check if the item is in an open container
        item_description = self._examine_item_in_open_container(item_name, location_data)
        if item_description:
            ic(f"Item description: {item_description}")
            return item_description

        # If not in a container, try examining directly from the location
        for item in location_data.get('items', []):
            if self.normalize_name(item['name']) == normalized_item_name:
                ic(f"Item description: {item['description']}")
                return f"{item['name']}: {item['description']}"

        return f"{item_name} not found."

    def _examine_item_in_open_container(self, item_name, location_data):
        normalized_item_name = self.normalize_name(item_name)  
        for container in location_data.get('containers', []):
            if container.get('isOpen', False):
                for item in container.get('contains', []):
                    if self.normalize_name(item['name']) == normalized_item_name: 
                        ic(f"Item description: {item['description']}")
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

        ic(f"Location: {location_str}, {location_description}. {container_info}")
        return f"You are at {location_str}. {location_description}.{container_info}"


    def look_around(self):
        # Get the current location data
        current_location_data = self.get_current_location_data()

        # Check if we're in a room within a sublocation
        if current_location_data and 'type' in current_location_data and current_location_data['type'] == 'room':
            # If in a room, build scene text for the room
            return self.build_room_scene_text(current_location_data)
        elif current_location_data:
            # If not in a room, build the normal scene text
            return self.build_scene_text(current_location_data)
        else:
            return "It's too dark to see anything."

    
    def show_sublocations(self, location_data):
        sublocations_text = "Sublocations here:\n"
        for sublocation in location_data.get('sublocations', []):
            sublocations_text += f"- {sublocation['name']}: {sublocation['description']}\n\n"
        ic(f"Sublocations text: {sublocations_text}")
        return sublocations_text

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

    def give_item(self, command):
        parts = command.split(maxsplit=1)  # Split command into at most three parts
        ic(f"Parts: {parts}")
        if len(parts) < 2:
            return "Please specify an item and quantity to give. E.g., 'give 2 potions'."

        try:
            quantity = int(parts[0])
            item_name = parts[1].strip()
            ic(f"Quantity: {quantity}, Item: {item_name}")
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

        ic(f"Looking for container '{container_name}' in location: {location_str}")

        for container in location_data.get('containers', []):
            normalized_container_name = self.normalize_name(container['name'])
            ic(f"Checking container: {container['name']} (isOpen: {container.get('isOpen', False)})")

            if normalized_container_name == container_name.lower() and container.get('isOpen', False):
                for item in player_inventory:
                    normalized_player_item_name = self.normalize_name(item['name'])
                    ic(f"Checking item in inventory: {item['name']} (Normalized: {normalized_player_item_name})")

                    if normalized_player_item_name == normalized_item_name:
                        if item.get('quantity', 1) >= quantity:
                            item['quantity'] = item.get('quantity', 1) - quantity
                            if item['quantity'] <= 0:
                                player_inventory.remove(item)

                            self._add_item_to_container(container, item, quantity)
                            ic(f"Item '{item['name']}' given to container '{container['name']}'")
                            return f"You have given {quantity} {item['name']} to {container['name']}."
                        else:
                            return f"You don't have enough {item['name']} to give."
            else:
                ic(f"Skipping container: {container['name']}, open: {container.get('isOpen', False)}, expected: {container_name}")

        ic(f"No container named '{container_name}' found here or it is not open.")
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
