from engine.player_sheet import PlayerSheet
from engine.quest_tracker import QuestTracker
from icecream import ic

class GameManager:
    def __init__(self, player_name, ui):
        self.player_sheet = PlayerSheet(player_name)
        self.quest_tracker = QuestTracker(self)
        self.ui = ui  # Initialize the UI attribute with the UI instance passed in


        self.populate_initial_game_state()
        self.update_quests_ui()
        
        # Initialize the game state with initial items, locations, etc.
        self.populate_initial_game_state()
        ic("GameManager initialized")   

    def populate_initial_game_state(self):
        ic("Populating initial game state")

        # Add initial items, locations, notes, and quests
        self.player_sheet.add_item({"name": "Sword", "description": "A long pointy thing used to make people bleed", "quantity": 1})
        self.player_sheet.add_item({"name": "Health Potion", "description": "Restores 5 Hit Points", "quantity": 5})
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