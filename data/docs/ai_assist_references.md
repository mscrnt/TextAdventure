
# AI Assist Class Reference

## Overview

The `AIAssist` class in the game project integrates AI-driven narrative generation and command processing to enhance player interactions within the game world.

## Key Components

### Initialization

- **game_manager**: Reference to the game manager for accessing game state and data.
- **world_builder**: Reference to the world builder for manipulating the game world.
- **secrets_file**: Path to the `secrets.json` file containing the OpenAI API key.

### Method: `generate_ai_response`

Generates AI-driven narrative based on a given prompt.

- **Parameters**:
  - `prompt`: The narrative context or command to process.
  - `max_tokens`: The maximum length of the AI response.
- **Returns**: The AI-generated response as a string.

### Method: `handle_player_command`

Processes player commands using both natural language processing and direct command mapping.

- **Parameters**:
  - `command`: The player's input command.
- **Returns**: The game's response to the command.

### Method: `construct_ai_prompt`

Constructs a narrative prompt for the AI based on the current game state and player command.

- **Parameters**:
  - `command`: The player's input command.
  - `world_data`: Data about the game world.
  - `player_data`: Data about the player's state.
- **Returns**: A constructed AI prompt.

### Method: `generate_ai_response_after_action`

Generates an AI response after an action has been taken in the game.

- **Parameters**:
  - `command`: The player's input command.
  - `action_response`: The response from the game after an action.
  - `world_data`: Data about the game world.
  - `player_data`: Data about the player's state.
- **Returns**: The AI-generated narrative response post-action.

## Usage Example

```python
class WorldBuilder:
    def __init__(self, game_manager, world_data):
        self.game_manager = game_manager
        self.world_data = world_data

        self.use_ai_assist = True  # Set to False to disable AI Assist
        if self.use_ai_assist:
            self.ai_assist = AIAssist(game_manager, self)
```

This class empowers the game with AI-driven narrative generation, enabling dynamic storytelling and immersive player experiences.
