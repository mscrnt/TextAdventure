# engine/game_manager.py

from engine.player_sheet import PlayerSheet
from engine.quest_tracker import QuestTracker
from icecream import ic
import utilities
from PySide6.QtCore import QObject, Signal


class GameManager(QObject):
    gameLoaded = Signal()

    def __init__(self, player_name, ui):
        super().__init__() 
        self.player_sheet = PlayerSheet(player_name)
        self.quest_tracker = QuestTracker(self)
        self.ui = ui

        self.populate_initial_game_state()
        self.update_quests_ui()
        
        # Initialize the game state with initial items, locations, etc.
        ic("GameManager initialized")   

    def load_global_inventory(self):
        ic("Loading global inventory")
        global_inventory = utilities.load_json("item_list", "items")
        return global_inventory

    def populate_initial_game_state(self):
        ic("Populating initial game state")

        # Function to find an item by name
        def find_item_by_name(name):
            for item in global_items:
                if item['name'] == name:
                    return item
            return None

        # Load the global inventory
        global_items = self.load_global_inventory()
        ic("Global items loaded")
        ic(global_items)

        # Add items to the player's inventory
        excalibur = find_item_by_name("Excalibur")
        if excalibur:
            self.player_sheet.add_item(excalibur)
            ic("Excalibur added to inventory")

        health_potion = find_item_by_name("Health Potion")
        if health_potion:
            # Modify the quantity here
            health_potion['quantity'] = 5
            self.player_sheet.add_item(health_potion)
            ic("Health potion added to inventory")

        self.player_sheet.add_fast_travel_location({"name": "Old Town", "description": "A small town with a few shops and a tavern"})
        self.player_sheet.add_fast_travel_location({"name": "Mystic Forest", "description": "A dark forest with strange creatures"})
        self.player_sheet.add_note({"name": "Enchanted Cave", "description": "Remember to check the enchanted cave."})
        self.player_sheet.add_email({"name": "Welcome to Odyssey", "description": "Welcome to Odyssey! We hope you enjoy your stay.", "read": False, "sender": "Odyssey Admin"})
        read_email_quest = self.quest_tracker.get_quest("Read Email")
        if read_email_quest:
            ic("Activating Read Email quest")
            self.quest_tracker.activate_quest("Read Email") 

    def update_inventory_ui(self):
        pass  # Update inventory UI here

    def update_fast_travel_ui(self):
        pass  # Update fast travel UI here

    def update_notes_ui(self):
        pass  # Update notes UI here

    def update_quests_ui(self):
        ic("Updating quests UI")
        # Call the update method on the UI instance
        self.ui.update_quest_log(self.get_player_quests())

    def get_inventory_items(self):
        # Return a formatted list of items from the player's inventory
        return [f"{item['name']} (x{item['quantity']})" for item in self.player_sheet.inventory]

    def get_fast_travel_locations(self):
        # Return the list of fast travel location dictionaries
        return self.player_sheet.fast_travel_locations

    def get_player_notes(self):
        ic("Getting player quests")
        # Return the list of note dictionaries
        return self.player_sheet.notes

    def get_player_quests(self):
        # Format the quests from the player_sheet
        return [f"{quest['name']}: {'Completed' if quest['completed'] else 'In Progress'}" for quest in self.player_sheet.quests]
    
    def get_player_emails(self):
        # Return the list of email dictionaries
        return self.player_sheet.emails
    
    def get_player_email_details(self, email_name):
        # Return the details of an email
        return next((email for email in self.player_sheet.emails if email['name'] == email_name), None)
    
    def get_inventory_item_details(self, item_name):
        # Return the details of an inventory item
        return next((item for item in self.player_sheet.inventory if item['name'] == item_name), None)

    def get_fast_travel_location_details(self, location_name):
        # Return the details of a fast travel location
        return next((location for location in self.player_sheet.fast_travel_locations if location['name'] == location_name), None)

    def get_note_details(self, note_name):
        # Return the details of a note
        return next((note for note in self.player_sheet.notes if note['name'] == note_name), None)

    def get_quest_details(self, quest_name):
        # Attempt to find the quest by name
        quest_detail = next((quest for quest in self.player_sheet.quests if quest['name'] == quest_name), None)
        
        # Debug print to check what is being retrieved
        ic(f"Quest search for '{quest_name}' found: {quest_detail}")
        
        if quest_detail:
            # If the quest is found, return its details
            return quest_detail
        else:
            # Return None if the quest is not found
            return None
        
    def mark_email_as_read(self, email_name):
        for email in self.player_sheet.emails:
            if email['name'] == email_name:
                ic(email)
                email['read'] = True
                ic(f"Email {email_name} marked as read")
                ic(email)
                self.quest_tracker.check_all_quests()
                break

    def save_game(self):
        # Create a state dictionary to save player data and any other game state information
        state = {
            'player_sheet': self.player_sheet,
            # Add other game state information as needed
        }
        utilities.save_game(state, f"{self.player_sheet.name}_savegame.pkl")

    def load_game(self, filename):
        if filename:
            # Attempt to load the game state from the provided file
            state = utilities.load_game(filename)
            if state:
                # Update the game manager's state with the loaded data
                self.player_sheet.__dict__.update(state['player_sheet'].__dict__)
                self.gameLoaded.emit()
                return True
            else:
                print(f"Failed to load game from {filename}.")
        else:
            print("No filename provided for loading the game.")
        return False