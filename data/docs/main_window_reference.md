
# Main Window Reference

## Overview
`MainWindow` in `gui/main_window.py` is the primary window for the Odyssey game. It manages the game's primary user interface elements, including the game menu, splash screen, and the game's main user interface.

## Key Functionalities

### Window Setup
- Sets the main window's title and geometry.
- Initializes the game menu bar and the central widget with a stacked layout.

### Menu Bar
- The menu bar includes File, Edit, and Help menus.
- The File menu provides options for starting a new game, saving/loading a game, and exiting the application.
- Edit and Help menus are placeholders for future functionalities.

### Splash Screen
- Displays an ASCII art splash screen as the game's intro.
- Responds to mouse clicks to proceed from the splash screen to the game's entry point.

### Entry Point
- Provides options for starting a new game or loading an existing game.
- Handles user interactions for these options.

### Game Interface
- Initializes the main game interface (but does not display it initially).
- The game interface includes a text area for displaying the game's narrative and other UI elements.

### ASCII Banner Creation
- Creates an ASCII art banner for the splash screen.

### Game Start
- Responds to the splash screen's mouse click event to transition to the game's entry point.

### Transition to Game UI
- Handles the transition from the intro animation to the main game user interface.

### Starting a New Game
- Prompts the user for a player name and starts a new game session.
- Initiates the intro animation sequence before displaying the game UI.

### Saving and Loading Game
- Provides functionality to save the current game state and load a saved game state.
- Includes dialogues for selecting save files and entering player names.

## Code Structure

### Initialization Methods
- `__init__()`: Initializes the main window and its components.
- `init_menu_bar()`: Sets up the game's menu bar.
- `init_splash_screen()`: Creates the splash screen.
- `init_game_interface()`: Sets up the main game interface.
- `init_entry_point()`: Prepares the entry point with options for new and load game.

### Utility Methods
- `create_ascii_banner(text: str)`: Generates an ASCII art banner.
- `start_game(event)`: Handles the event to start the game from the splash screen.
- `change_to_game_ui()`: Transitions to the main game UI.
- `start_new_game()`: Initiates a new game session.
- `trigger_save_game()`: Triggers saving the current game state.
- `select_save_file()`: Opens a dialogue to select a save file.
- `prompt_for_player_name()`: Displays a dialogue to enter the player's name.

### Event Handlers
- `on_intro_animation_complete()`: Handles the completion of the intro animation.
- `on_game_loaded()`: Slot to be called when the game is loaded.

This reference provides an overview of the `MainWindow` class's functionalities, aiding in understanding the flow and structure of the Odyssey game's main window.
