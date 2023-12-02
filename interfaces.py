# interfaces.py

from abc import ABC, abstractmethod

class IGameManager:

    def start_new_game(self, player_name):
        """Start a new game with the given player name."""
        pass

    def get_inventory_data(self):
        """Return inventory data."""
        pass

    def get_fast_travel_locations_data(self):
        """Return fast travel locations data."""
        pass

    def get_notes_data(self):
        """Return notes data."""
        pass

    def get_quests_data(self):
        """Return quests data."""
        pass

    def get_emails_data(self):
        """Return emails data."""
        pass

    def load_global_inventory(self):
        """Load global inventory."""
        pass

    def load_worlds_data(self):
        """Load worlds data."""
        pass

    def load_notes(self):
        """Load notes."""
        pass

    def load_emails(self):
        """Load emails."""
        pass

    def populate_initial_game_state(self):
        """Populate initial game state."""
        pass

    def update_quests_ui(self):
        """Update quests UI."""
        pass

    def get_inventory_items(self):
        """Get inventory items."""
        pass

    def get_fast_travel_locations(self):
        """Get fast travel locations."""
        pass

    def get_player_notes(self):
        """Get player notes."""
        pass

    def get_player_quests(self):
        """Get player quests."""
        pass

    def get_player_emails(self):
        """Get player emails."""
        pass

    def get_player_email_details(self, email_name):
        """Get details of a specific email."""
        pass

    def get_inventory_item_details(self, item_name):
        """Get details of a specific inventory item."""
        pass

    def get_fast_travel_location_details(self, location_name):
        """Get details of a specific fast travel location."""
        pass

    def get_note_details(self, note_name):
        """Get details of a specific note."""
        pass

    def get_quest_details(self, quest_name):
        """Get details of a specific quest."""
        pass

    def mark_email_as_read(self, email_name):
        """Mark an email as read."""
        pass

    def save_game(self):
        """Save the game state."""
        pass

    def load_game(self, filename):
        """Load a game state from a file."""
        pass

    def update_location(self, new_location):
        """Update the player's location."""
        pass



class IQuestTracker(ABC):

    @abstractmethod
    def load_initial_quests(self):
        """Load the initial quests."""
        pass

    @abstractmethod
    def get_quest(self, quest_name):
        """Get a specific quest by name."""
        pass

    @abstractmethod
    def activate_quest(self, quest_name):
        """Activate a quest by name."""
        pass

    @abstractmethod
    def initialize_quest(self, quest_slug, quest_data):
        """Initialize a quest given its slug and data."""
        pass

    @abstractmethod
    def quest_class_for_slug(self, quest_slug):
        """Get the quest class for a given slug."""
        pass

    @abstractmethod
    def check_all_quests(self):
        """Check the status of all quests."""
        pass

    @abstractmethod
    def save_quests(self):
        """Save quests data to a file."""
        pass



class IGameUI:

    def on_game_loaded(self):
        """Handle the event when the game is loaded."""
        pass

    def update_ui(self):
        """Update the entire UI."""
        pass

    def update_ui_from_dropdown(self, index):
        """Update the UI based on a selection from a dropdown menu."""
        pass

    def populate_inventory(self):
        """Populate the inventory in the UI."""
        pass

    def populate_fast_travel_locations(self):
        """Populate the fast travel locations in the UI."""
        pass

    def populate_notes(self):
        """Populate the notes section in the UI."""
        pass

    def populate_quest_log(self):
        """Populate the quest log in the UI."""
        pass

    def populate_emails(self):
        """Populate the emails section in the UI."""
        pass

    def process_command(self):
        """Process a command entered by the user."""
        pass

    def display_item_information(self, item_widget):
        """Display information about an item selected in the UI."""
        pass

    def display_text(self, html_content):
        """Display text in the main text area of the UI."""
        pass

    def update_quest_log(self):
        """Update the quest log in the UI."""
        pass

    def update_scene_display(self):
        """Update the scene display in the UI."""
        pass



class IPlayerSheet(ABC):

    @abstractmethod
    def add_item(self, item):
        """Add an item to the player's inventory."""
        pass

    @abstractmethod
    def remove_item(self, item_name):
        """Remove an item from the player's inventory by its name."""
        pass

    @abstractmethod
    def add_fast_travel_location(self, location, world_name=None):
        """Add a new fast travel location."""
        pass

    @abstractmethod
    def remove_fast_travel_location(self, location_name):
        """Remove a fast travel location."""
        pass

    @abstractmethod
    def add_note(self, note):
        """Add a note to the player's collection."""
        pass

    @abstractmethod
    def remove_note(self, note_name):
        """Remove a note from the player's collection."""
        pass

    @abstractmethod
    def add_quest(self, quest):
        """Add a quest to the player's quest log."""
        pass

    @abstractmethod
    def update_quest(self, updated_quest):
        """Update a quest in the player's quest log."""
        pass

    @abstractmethod
    def complete_quest(self, quest_name, quest_tracker):
        """Mark a quest as completed."""
        pass

    @abstractmethod
    def add_email(self, email):
        """Add an email to the player's inbox."""
        pass

    @abstractmethod
    def remove_email(self, email_name):
        """Remove an email from the player's inbox."""
        pass

    @abstractmethod
    def get_email(self, email_name):
        """Retrieve details of a specific email."""
        pass

    @abstractmethod
    def get_all_emails(self):
        """Retrieve all emails from the player's inbox."""
        pass

    @abstractmethod
    def get_fast_travel_worlds(self):
        """Return a list of unique world names from the fast travel locations."""
        pass



class IWorldBuilder(ABC):
    
    @abstractmethod
    def incoming_command(self, command):
        """Process an incoming command from the player."""
        pass

    @abstractmethod
    def fast_travel_to_world(self, world_name):
        """Handle fast travel to a specified world."""
        pass

    @abstractmethod
    def find_location_data(self, location_name):
        """Find and return data for a specified location."""
        pass

    @abstractmethod
    def talk_to_npc(self, npc_name):
        """Handle interactions with a non-player character (NPC)."""
        pass

    @abstractmethod
    def interact_with(self, interactable_name):
        """Handle interactions with an object in the game world."""
        pass

    @abstractmethod
    def where_am_i(self):
        """Provide information about the player's current location."""
        pass

    @abstractmethod
    def look_around(self):
        """Describe the player's current surroundings."""
        pass

    @abstractmethod
    def open_container(self, container_name):
        """Open a container in the game world."""
        pass

    @abstractmethod
    def move_player(self, location_name):
        """Move the player to a different location."""
        pass

    @abstractmethod
    def examine_item(self, item_name):
        """Examine an item in the player's vicinity or inventory."""
        pass

    @abstractmethod
    def give_item(self, item_name, quantity):
        """Give an item from the player's inventory to an NPC or container."""
        pass

    @abstractmethod
    def update_world_data(self, location_name, update_dict=None, new_world_name=None):
        """Update the game world's data."""
        pass

    @abstractmethod
    def build_scene_text(self):
        """Build and return a descriptive text of the current scene."""
        pass



class IMainWindow(ABC):

    @abstractmethod
    def set_dark_theme(self):
        """Set the dark theme for the main window."""
        pass

    @abstractmethod
    def init_entry_point(self):
        """Initialize the entry point of the application."""
        pass

    @abstractmethod
    def on_intro_animation_complete(self):
        """Handle the completion of the intro animation."""
        pass

    @abstractmethod
    def init_splash_screen(self):
        """Initialize the splash screen of the application."""
        pass

    @abstractmethod
    def init_menu_bar(self):
        """Initialize the menu bar of the main window."""
        pass

    @abstractmethod
    def init_game_interface(self):
        """Initialize the main game interface."""
        pass

    @abstractmethod
    def create_ascii_banner(self, text):
        """Create an ASCII banner for display."""
        pass

    @abstractmethod
    def start_game(self, event):
        """Start the game, usually triggered by an event."""
        pass

    @abstractmethod
    def change_to_game_ui(self):
        """Change the current UI to the game UI."""
        pass

    @abstractmethod
    def trigger_save_game(self):
        """Trigger a save game action."""
        pass

    @abstractmethod
    def select_save_file(self):
        """Select a save file for loading a game."""
        pass

    @abstractmethod
    def prompt_for_player_name(self):
        """Prompt the user to enter their player name."""
        pass
