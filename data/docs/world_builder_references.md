
# World Builder Class Reference

## Overview

The `WorldBuilder` class is an integral part of the game's backend, responsible for creating, managing, and manipulating the game world's environment and elements. It interacts closely with the `GameManager`, `PlayerSheet`, and `AIAssist` classes to provide a dynamic and interactive game world.

## Class Definition

```python
class WorldBuilder:
    def __init__(self, game_manager, world_data):
        # Initialization with GameManager instance and world data
```

### Key Methods

- `incoming_command(command)`: Processes a player's command using either AI assistance or direct command interpretation.
- `find_location_data(location_name)`: Retrieves data about a specified location.
- `load_world_data()`: Loads the world data from a JSON file.
- `build_scene_text()`: Constructs a textual representation of the current scene or location.
- `describe_location(location_data)`: Provides a description of a given location.
- `list_items(location_data)`: Lists items available in a location.
- `list_interactables(location_data)`: Lists interactable objects or NPCs in a location.
- `normalize_name(name)`: Normalizes names for consistent comparison.
- `open_container(container_name)`: Opens a specified container in the current location.
- `list_container_contents(container)`: Lists the contents of an opened container.
- `list_containers(location_data)`: Lists all containers in a location.
- `show_paths(location_data)`: Shows available paths or exits from the current location.
- `show_transport_options(location_data)`: Displays transport options available at the location.
- `take_item(item_name)`: Handles the logic for taking an item from the location or container.
- `_take_item_from_open_container(item_name, location_data)`: Helper method for taking an item from an open container.
- `is_container_open()`: Checks if a container is open in the current location.
- `close_container()`: Closes the currently open container.
- `move_player(location_name)`: Moves the player to a specified location.
- `examine_item(item_name)`: Examines a specified item in the current location.
- `where_am_i()`: Provides the player's current location and description.
- `look_around()`: Gives a description of the surroundings in the current location.
- `show_sublocations(location_data)`: Displays sublocations within the current location.
- `display_help()`: Lists available commands for player interaction.
- `update_world_data(location_name, update_dict)`: Updates the world data with new information.
- `_apply_updates(location_dict, update_dict)`: Helper method to apply updates to a location.
- `close_all_containers()`: Closes all open containers in the world.
- `give_item(command)`: Handles the logic for giving an item to an NPC or container.
- `_give_item_to_container(normalized_item_name, quantity, container_name)`: Helper method for adding an item to a container.
- `_add_item_to_container(container, item, quantity, normalized_item_name)`: Helper method for updating container contents.

## Usage

The `WorldBuilder` class is used by the `GameManager` to interpret and execute player commands, manage the game's locations and items, and provide detailed descriptions of the game world to enhance the player experience.

### Example

```python
# Creating an instance of WorldBuilder
world_builder = WorldBuilder(game_manager, world_data)

# Handling a player command to move to a different location
response = world_builder.incoming_command("move to Eldergrove Forest")
```

## Integration with AI Assist

The `WorldBuilder` class works in tandem with the `AIAssist` class for enhanced command processing and AI-driven narrative generation, creating a rich and interactive game world.
