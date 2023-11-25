from icecream import ic
import utilities

class PlayerSheet:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.health = 100
        self.action_points = 10
        self.inventory = []
        self.location = "Start Location"
        self.fast_travel_locations = []
        self.quests = []
        self.notes = []
        self.emails = []
        ic("Player sheet initialized")

    def add_item(self, item):
        ic("Adding item to inventory")
        ic(item)
        # Add an item dictionary to the inventory if it's not already there
        if not any(existing_item['name'] == item['name'] for existing_item in self.inventory):
            self.inventory.append(item)

    def remove_item(self, item_name):
        ic("Removing item from inventory")
        ic(item_name)
        # Remove an item from the inventory by its name
        self.inventory = [item for item in self.inventory if item["name"] != item_name]

    def add_fast_travel_location(self, location):
        ic("Adding fast travel location")
        ic(location)
        self.fast_travel_locations.append(location)

    def remove_fast_travel_location(self, location_name):
        ic("Removing fast travel location")
        ic(location_name)
        self.fast_travel_locations = [location for location in self.fast_travel_locations if location["name"] != location_name]

    def add_note(self, note):
        ic("Adding note")
        ic(note)
        # Add a note dictionary to the notes if it's not already there
        if not any(existing_note['name'] == note['name'] for existing_note in self.notes):
            self.notes.append(note)

    def remove_note(self, note_name):
        ic("Removing note")
        ic(note_name)
        self.notes = [note for note in self.notes if note["name"] != note_name]

    def add_quest(self, quest):
        ic("Adding quest")
        ic(quest)
        if isinstance(quest, dict) and 'name' in quest:
            # Check if the quest is already active to prevent duplicates
            if quest['name'] not in [q['name'] for q in self.quests]:
                self.quests.append(quest)
        else:
            raise ValueError('The quest must be a dictionary with a "name" key.')
        
    def update_quest(self, updated_quest):
        for i, quest in enumerate(self.quests):
            if quest['name'] == updated_quest['name']:
                self.quests[i] = updated_quest
                ic(f"Updated quest: {updated_quest['name']}")
                break

    def complete_quest(self, quest_name, quest_tracker):
        ic("Completing quest")
        ic(quest_name)
        quest = next((q for q in self.quests if q['name'] == quest_name), None)
        if quest:
            quest['completed'] = True
            quest_tracker.update_quest_data(quest)
            
    def add_email(self, email):
        ic("Adding email")
        ic(email)
        # Add an email dictionary to the emails if it's not already there
        if not any(existing_email['name'] == email['name'] for existing_email in self.emails):
            self.emails.append(email)

    def remove_email(self, email_name):
        ic("Removing email")
        ic(email_name)
        self.emails = [email for email in self.emails if email["name"] != email_name]


    def remove_note(self, note):
        ic("Removing note")
        ic(note)
        if note in self.notes:
            self.notes.remove(note)

    def add_fast_travel_location(self, location):
        ic("Adding fast travel location")
        ic(location)
        if location not in self.fast_travel_locations:
            self.fast_travel_locations.append(location)

    def remove_fast_travel_location(self, location):
        ic("Removing fast travel location")
        ic(location)
        if location in self.fast_travel_locations:
            self.fast_travel_locations.remove(location)

    def get_email(self, email_name):
        ic("Getting email")
        ic(email_name)
        return next((email for email in self.emails if email['name'] == email_name), None)

    def save_game(self):
        filename = f"{self.name}_savegame.pkl"  # Creates a file name based on the player's name
        utilities.save_game(self, filename)
        ic(f"Game state saved for player: {self.name}")

    def load_game(self):
        # This will call the load_game function from utilities.py and will try to set the loaded state to the current object
        try:
            loaded_state = utilities.load_game()
            if loaded_state:
                self.__dict__.update(loaded_state.__dict__)
                ic("Game state loaded.")
            else:
                ic("No game state to load.")
        except AttributeError as e:
            ic(f"Failed to load game state: {e}")
    ##TODO Additional methods to manage level, experience, stats, etc.
