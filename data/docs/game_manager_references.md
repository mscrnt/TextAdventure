
# GameManager Class Reference

## Overview

The `GameManager` class serves as the central coordinator for various aspects of the game, including the player's state, world building, quest tracking, and user interface updates. This document outlines its key functionalities and interactions with other game components.

## Key Responsibilities

### Initialization
- Initializes player data, quest tracking, and the world builder.
- Loads the world data corresponding to the player's location.

### Game State Management
- Manages the player's inventory, quests, notes, and emails.
- Tracks the player's current location and fast travel options.
- Handles saving and loading game states.

### User Interface Updates
- Updates the UI with changes in inventory, quests, notes, and emails.
- Emits signals to reflect changes in the game state.

## Method Descriptions

### `load_global_inventory`
- Loads the global inventory items from a JSON file.
- Returns a list of all available items in the game.

### `load_worlds_data`
- Loads the data of all available worlds in the game.
- Returns a list of world data.

### `load_notes`
- Loads the player's notes from a JSON file.
- Returns a list of notes available to the player.

### `load_emails`
- Loads the player's emails from a JSON file.
- Returns a list of emails available to the player.

### `populate_initial_game_state`
- Sets up the initial game state, including inventory, fast travel locations, notes, and emails.
- Activates initial quests and adds relevant items to the player's inventory.

### `update_inventory_ui`, `update_fast_travel_ui`, `update_notes_ui`, `update_quests_ui`
- Placeholder methods for updating various UI elements related to inventory, fast travel, notes, and quests.

### `get_inventory_items`, `get_fast_travel_locations`, `get_player_notes`, `get_player_quests`, `get_player_emails`
- Retrieve formatted lists or details of the player's inventory, fast travel locations, notes, quests, and emails.

### `get_inventory_item_details`, `get_fast_travel_location_details`, `get_note_details`, `get_quest_details`
- Fetch detailed information about a specific inventory item, fast travel location, note, or quest.

### `mark_email_as_read`
- Marks an email as read and triggers quest checks related to email reading.

### `save_game`
- Saves the current game state to a file, including player data and world data.

### `load_game`
- Loads a saved game state from a file and updates the `GameManager` with the loaded data.

### `update_location`
- Updates the player's current location in the game world.

## Usage and Integration

- The `GameManager` is instantiated with the player's name and a reference to the UI.
- It interacts with other classes like `PlayerSheet`, `QuestTracker`, and `WorldBuilder` to manage different aspects of the game.
- Methods in `GameManager` are called throughout the game to reflect changes in the game state and update the UI accordingly.

---
