
# Text Adventure Game - Project README

## Overview
This text-based adventure game, developed in Python, integrates artificial intelligence to enhance player interaction and world-building. The game revolves around exploring different locations, interacting with objects and NPCs, and solving puzzles or completing quests.

## File Descriptions
### main.py
- **Purpose**: Entry point of the application.
- **Functionality**: Initializes the game and manages the main loop.

### game_ui.py
- **Purpose**: Manages the game's user interface.
- **Functionality**: Handles display of game output, user inputs, and UI updates.

### main_window.py
- **Purpose**: Creates the main application window.
- **Functionality**: Integrates UI components and manages window events.

### game_manager.py
- **Purpose**: Core game logic controller.
- **Functionality**: Manages game states, player interactions, and game progression.

### player_sheet.py
- **Purpose**: Manages player data.
- **Functionality**: Tracks player inventory, stats, and specific characteristics.

### quest_tracker.py
- **Purpose**: Quest management system.
- **Functionality**: Monitors quest progress, triggers, and completions.

### world_builder.py
- **Purpose**: Constructs and manages the game world.
- **Functionality**: Generates locations, NPCs, events, and handles player interactions with the game world.

### ai_assist.py
- **Purpose**: Integrates AI for enhanced game interaction.
- **Functionality**: Processes player commands using AI, allowing for natural language processing and dynamic responses.

### utilities.py
- **Purpose**: Provides utility functions like JSON file handling.
- **Functionality**: Includes functions for loading and saving game data.

## AI Integration
The game uses OpenAI's GPT model to interpret player commands and generate immersive, dynamic responses. This integration allows for natural language understanding and creative storytelling.

## Getting Started
1. **Installation**: Clone the repository and ensure Python 3.7+ is installed.
2. **Dependencies**: Install required packages using `pip install -r requirements.txt`.
3. **Running the Game**: Execute `main.py` to start the game.
4. **Playing the Game**: Interact with the game using text commands. The AI assistant will interpret your inputs and provide appropriate responses based on the game's current state.

## Game Mechanics
- **Exploration**: Travel through various locations within the game world.
- **Inventory Management**: Collect, use, and manage items.
- **Quests**: Complete quests for rewards and story progression.
- **Interactions**: Engage with NPCs and objects within the game world.

## Data Structure
- The game's world and player data are stored in JSON format, allowing for easy modification and expansion.

## Contribution
- **Adding Content**: Modify the JSON files to add new items, locations, or quests.
- **Customization**: Adjust game mechanics or AI responses in the Python files as needed.

## Support
For any issues or suggestions, please open an issue on the project's GitHub page.
