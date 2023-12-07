# engine/player_sheet.py

from icecream import ic

class PlayerSheet:
    """
    Implementation of the IPlayerSheet interface.
    This class manages the player's state including inventory, quests, notes, emails, and fast travel locations.
    """
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self._location = {"world": "OdysseyVR", "location/sublocation": "Lobby"}
        self.fast_travel_locations = []
        self.quests = []
        self.notes = []
        self.emails = []
        self.tokens = 25
        ic("Player sheet initialized")

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, dict) or "world" not in value:
            raise ValueError("Location must be a dictionary with a 'world' key.")
        self._location = value

    def set_player_name(self, name):
        self.name = name

    def reset_state(self):
        """Reset the player's state to the initial values."""
        self.inventory = []
        self._location = {"world": "OdysseyVR", "location/sublocation": "Home"}
        self.fast_travel_locations = []
        self.quests = []
        self.notes = []
        self.emails = []
        self.tokens = 25
        ic("Player state has been reset for a new game.")

    def add_item(self, item):
        ic(f"Item added to inventory: {item['name']}, Quantity: {item.get('quantity', 1)}")
        # Check if the item already exists in the inventory
        for existing_item in self.inventory:
            if existing_item['name'] == item['name']:
                # Assuming all items have a 'quantity' key
                existing_item['quantity'] += item.get('quantity', 1)  # Add the quantity if specified
                break
        else:
            # If the item does not exist, set its quantity to 1 if not specified, then append it
            if 'quantity' not in item:
                item['quantity'] = 1
            self.inventory.append(item)

    def remove_item(self, item_name):
        ic(f"Item removed from inventory: {item_name}")
        # Remove an item from the inventory by its name
        self.inventory = [item for item in self.inventory if item["name"] != item_name]

    def remove_fast_travel_location(self, location_name):
        ic("Removing fast travel location")
        ic(location_name)
        self.fast_travel_locations = [location for location in self.fast_travel_locations if location["name"] != location_name]

    def add_tokens(self, token):
        ic("Adding token")
        ic(token)
        self.tokens += token

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

    def add_fast_travel_location(self, location, world_name=None):
        ic("Adding fast travel location")
        world_name = world_name or location.get('world_name')
        location_with_world = {
            'location': location,
            'world_name': world_name
        }
        # Ensure we're not adding duplicates
        if location_with_world not in self.fast_travel_locations:
            ic(f"Adding fast travel location: {location['name']}")
            self.fast_travel_locations.append(location_with_world)



    def get_fast_travel_worlds(self):
        """Return a list of unique world names from the fast travel locations."""
        return list({location['world_name'] for location in self.fast_travel_locations})



    def remove_fast_travel_location(self, location):
        ic("Removing fast travel location")
        ic(location)
        if location in self.fast_travel_locations:
            self.fast_travel_locations.remove(location)

    def get_email(self, email_name):
        ic(f"Getting email: {email_name}")
        return next((email for email in self.emails if email['name'] == email_name), None)

    def get_all_emails(self):
        ic("Getting all emails")
        return self.emails
    
    def get_state(self):
        """Return a serializable representation of the player sheet."""
        return {
            'name': self.name,
            'inventory': self.inventory,
            'location': self._location,
            'fast_travel_locations': self.fast_travel_locations,
            'quests': self.quests,
            'notes': self.notes,
            'emails': self.emails,
            'tokens': self.tokens
        }

    def set_state(self, state):
        if isinstance(state, PlayerSheet):
            self.__dict__.update(state.__dict__)
        else:
            raise TypeError("state must be an instance of PlayerSheet")

    def get_quest(self, quest_name):
        ic(f"Getting quest: {quest_name}")
        return next((quest for quest in self.quests if quest['name'] == quest_name), None)

    def get_all_quests(self):
        ic("Getting all quests")
        return self.quests

    def is_quest_active(self, quest_name):
        quest = self.get_quest(quest_name)
        return quest is not None and quest.get('isActive', False)

    def is_quest_completed(self, quest_name):
        quest = self.get_quest(quest_name)
        return quest is not None and quest.get('completed', False)

    def get_tokens(self):
        ic("Getting tokens")
        return self.tokens