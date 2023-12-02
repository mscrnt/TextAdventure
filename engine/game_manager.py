# engine/game_manager.py
from icecream import ic
import utilities
from interfaces import IGameManager, IQuestTracker, IWorldBuilder, IPlayerSheet, IGameUI
from engine.player_sheet import PlayerSheet
from engine.quest_tracker import QuestTracker
from engine.world_builder import WorldBuilder
from PySide6.QtCore import QObject, Signal, QTimer


class GameManager(QObject, IGameManager):
    display_text_signal = Signal(str)
    gameLoaded = Signal()

    def __init__(self):
        super().__init__() 
        self.player_sheet = PlayerSheet("DefaultPlayer") 
        self.quest_tracker = QuestTracker()  
        self.quest_tracker.set_game_manager(self)
        self.quest_tracker.set_player_sheet(self.player_sheet) 
        self.quest_tracker.set_player_sheet(self.player_sheet)
        # Load dynamic world names
        self.world_data = self.load_world_data()
        self.world_builder = WorldBuilder(world_data=self.world_data)
        self.world_builder.set_game_manager(self)
        self.ui = None
        # self.populate_initial_game_state()
        ic("GameManager initialized")

    def load_world_data(self):
        world_full_names = utilities.load_all_worlds()

        # Loop through each world name
        for world_key in world_full_names.keys():
            world_data = utilities.load_working_world_data(world_key)

        return world_data

    def set_player_sheet(self, player_sheet: IPlayerSheet):
        self.player_sheet = player_sheet

    def set_quest_tracker(self, quest_tracker: IQuestTracker):
        self.quest_tracker = quest_tracker

    def set_world_builder(self, world_builder: IWorldBuilder):
        self.world_builder = world_builder
        if self.world_builder:
            self.world_builder.game_manager = self

    def set_ui(self, ui: IGameUI):
        self.ui = ui

        self.world_data = utilities.load_working_world_data(self.player_sheet.location['world'])

        self.world_full_names = self.load_worlds_data()
        ic("GameManager initialized")

    def emit_game_loaded(self):
        ic("Emitting game loaded signal")
        self.gameLoaded.emit()

    def start_new_game(self, player_name):
        # Set the player name and reset its state
        self.player_sheet.set_player_name(player_name)
        self.player_sheet.reset_state()

        # Load world data required for game state population
        self.world_data = self.load_worlds_data()

        # Now that world data is loaded, populate initial game state
        self.populate_initial_game_state()

        # Initialize the QuestTracker for a new game
        if self.quest_tracker is not None:
            self.quest_tracker.initialize_for_new_game()
        else:
            ic("Quest tracker is not initialized.")

        # Initialize the WorldBuilder for a new game
        # if self.world_builder is not None:
        #     self.world_builder.initialize_for_new_game()
        # else:
        #     ic("World builder is not initialized.")

        # If UI needs to be updated or initialized for a new game
        if self.ui is not None:
            self.ui.initialize_for_new_game()
        else:
            ic("UI is not initialized.")
        QTimer.singleShot(1000, self.emit_game_loaded)
        return True
    
    def activate_player_quest(self, quest_data):
        if self.player_sheet:
            self.player_sheet.add_quest(quest_data)
            ic(f"Quest {quest_data['name']} added to player")
        else:
            ic("PlayerSheet is not set in GameManager")

    def get_inventory_data(self):
        ic("Getting inventory data")
        return [f"{item['name']} (x{item['quantity']})" for item in self.player_sheet.inventory]

    def get_fast_travel_locations_data(self):
        ic("Getting fast travel locations data")
        return [
            f"{location['location']['name']} ({location['world_name']})"
            for location in self.player_sheet.fast_travel_locations
        ]

    def get_notes_data(self):
        ic("Getting notes data")
        return [note['name'] for note in self.player_sheet.notes]

    def get_quests_data(self):
        if self.player_sheet is None:
            ic("Warning: player_sheet is None in get_quests_data")
            return []
        ic("Getting quests data")
        ic(self.player_sheet.quests)
        return [
            f"{quest['name']}: {'Completed' if quest['completed'] else 'In Progress'}" 
            for quest in self.player_sheet.quests
        ]

    def get_emails_data(self):
        ic("Getting emails data")
        emails = sorted(self.player_sheet.emails, key=lambda x: x['read'])
        return [f"{email['name']} (Read)" if email['read'] else email['name'] 
                for email in emails]
        
    def load_global_inventory(self):
        ic("Loading global inventory")
        global_inventory = utilities.load_json("item_list", "items")
        return global_inventory
    
    def load_worlds_data(self):
        ic("Loading worlds data")
        worlds_data = utilities.load_all_worlds()
        return worlds_data
    
    def load_notes(self):
        ic("Loading notes")
        notes = utilities.load_json("notes", "notes")
        return notes
    
    def load_emails(self):
        ic("Loading emails")
        emails = utilities.load_json("emails", "emails")
        return emails

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

        # Verify global items have been loaded with expected content
        if not global_items:
            ic("Warning: global_items is empty after loading.")

        # Add items to the player's inventory and verify
        excalibur = find_item_by_name("Excalibur")
        if excalibur:
            self.player_sheet.add_item(excalibur)
            ic("Excalibur added to inventory", self.player_sheet.inventory)
        else:
            ic("Warning: Excalibur not found in global items.")

        health_potion = find_item_by_name("Health Potion")
        if health_potion:
            health_potion['quantity'] = 5
            self.player_sheet.add_item(health_potion)
            ic("Health potion added to inventory", self.player_sheet.inventory)
        else:
            ic("Warning: Health Potion not found in global items.")

        # Load dynamic world names
        world_full_names = utilities.load_all_worlds()

        # Loop through each world name
        for world_key, world_display_name in world_full_names.items():
            world_data = utilities.load_working_world_data(world_key)
            main_area = next((location for location in world_data['locations'] if location.get('main-entry', False)), None)
            if main_area:
                self.player_sheet.add_fast_travel_location(main_area, world_display_name)
                ic(f"{main_area['name']} (Main Area of {world_display_name}) added to fast travel locations")
            else:
                ic(f"Main entry not found for {world_key}")

        # Load the notes
        notes = self.load_notes()

        # Add the notes to the player's notes
        Enchanted_Cave = next((note for note in notes if note['name'] == "Enchanted Cave"), None)
        Thiefs_Confession = next((note for note in notes if note['name'] == "Thief's Confession"), None)

        if Enchanted_Cave:
            self.player_sheet.add_note(Enchanted_Cave)
            ic("Enchanted Cave note added")

        if Thiefs_Confession:
            self.player_sheet.add_note(Thiefs_Confession)
            ic("Thief's Confession note added")

        # Load the emails
        emails = self.load_emails()

        # Add the emails to the player's emails
        Welcome_to_Odyssey = next((email for email in emails if email['name'] == "Welcome to Odyssey"), None)
        Treasure_Map_Sale = next((email for email in emails if email['name'] == "Treasure Map Sale"), None)

        if Welcome_to_Odyssey:
            self.player_sheet.add_email(Welcome_to_Odyssey)
            ic("Welcome to Odyssey email added")

        if Treasure_Map_Sale:
            self.player_sheet.add_email(Treasure_Map_Sale)
            ic("Treasure Map Sale email added")

        read_email_quest = self.quest_tracker.get_quest("Read Email")
        if read_email_quest:
            ic("Activating Read Email quest")
            self.quest_tracker.activate_quest("Read Email") 


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
        ic(f"Getting fast travel location details for {location_name}")

        # Check if the location name is in the expected format with a separator
        if ' - ' in location_name:
            loc_name, world = location_name.split(' - ')
        else:
            loc_name = location_name
            world = None 

        for location_with_world in self.player_sheet.fast_travel_locations:
            if location_with_world['location']['name'] == location_name:
                return location_with_world['location']
        return None


    def get_note_details(self, note_name):
        # Return the details of a note
        return next((note for note in self.player_sheet.notes if note['name'] == note_name), None)

    def get_quest_details(self, quest_name):
        # Attempt to find the quest by name
        quest_detail = next((quest for quest in self.player_sheet.quests if quest['name'] == quest_name), None)
        ic(f"Quest search for '{quest_name}' found: {quest_detail}")
        
        if quest_detail:
            return quest_detail
        else:
            return None
        
    def mark_email_as_read(self, email_name):
        for email in self.player_sheet.emails:
            if email['name'] == email_name:
                ic(email)
                email['read'] = True
                ic(f"Email {email_name} marked as read")
                ic(email)
                self.quest_tracker.check_all_quests()
                self.ui.populate_emails()
                break

    def save_game(self):
        # Close all open containers before saving
        self.world_builder.close_all_containers()
        state = {
            'player_sheet': self.player_sheet,
            'world_data': self.world_data  # Include the in-memory world data
        }
        utilities.save_game(state, f"{self.player_sheet.name}_savegame.pkl")
        ic(f"State Saved: {state}")

    def load_game(self, filename):
        if filename:
            # Attempt to load the game state from the provided file
            state = utilities.load_game(filename)
            if state:
                # Update the game manager's state with the loaded data
                self.player_sheet.__dict__.update(state['player_sheet'].__dict__)
                self.world_data = state['world_data']
                self.emit_game_loaded()  # Corrected typo here
                ic(f"Game loaded. Player: {self.player_sheet.name}, Filename: {filename}")
                return True
            else:
                ic(f"Failed to load game from {filename}.")
        else:
            ic("No filename provided for loading the game.")
        return False
    
    def update_location(self, new_location):
        self.player_sheet.location = new_location
        #self.world_builder.build_scene()