
# World JSON Structure Reference

## Overview

This document serves as a guide for expanding the game world in 'Odyssey'. The world is structured in JSON format, comprising locations, sublocations, items, NPCs, and other interactive elements.

## Adding Locations

### Structure

```json
{
    "name": "Location Name",
    "description": "Description of the location.",
    "main-entry": true or false,
    "keywords": ["keyword1", "keyword2"],
    "paths": {
        "direction": "Connected Location or Sublocation",
        "room_direction": "Room within the current location"
    },
    "sublocations": [
        // Sublocation objects
    ]
}
```

### Instructions

- **name**: A string representing the location's name.
- **description**: A brief description of the location.
- **main-entry**: Boolean indicating if the location is the main entry point for the game.
- **keywords**: An array of strings that are key themes or elements of the location.
- **paths**: An object where each key is a direction or a descriptor (e.g., "north", "up", "entrance to X") and each value is the name of the location it connects to, which can be a top-level location, sublocation, or a room within the current location.
- **sublocations**: An array of sublocation objects.

## Adding Sublocations

### Structure

```json
{
    "name": "Sublocation Name",
    "description": "Description of the sublocation.",
    "keywords": ["keyword1", "keyword2"],
    "paths": {
        "exit": "Parent Location",
        "room_direction": "Room within the sublocation"
    },
    "items": [
        // Item objects
    ],
    "containers": [
        // Container objects
    ],
    "npcs": [
        // NPC objects
    ],
    "rooms": [
        // Room objects
    ]
}
```
## Adding Rooms

Rooms are specialized sublocations that exist within the hierarchy of a sublocation. They represent distinct areas players can explore and interact with.

### Structure

```json
{
    "name": "Room Name",
    "description": "Description of the room.",
    "keywords": ["keyword1", "keyword2"],
    "visible": true or false,
    "paths": {
        "entrance": "Parent Sublocation",
        "exit": "Connecting Room or Sublocation"
    },
    "items": [
        // Item objects
    ],
    "npcs": [
        // NPC objects
    ]
}
```

### Instructions

- **name**: A string representing the room's name.
- **description**: A description of the room's atmosphere, features, and any lore-related elements.
- **keywords**: Key terms associated with the room.
- **visible**: Boolean indicating if the room is visible to the player. If set to `false`, the room will be hidden until the player triggers an event that reveals it.
- **paths**: Directions leading into and out of the room. The "entrance" key leads back to the parent sublocation, while "exit" can lead to another room or back to the sublocation.
- **items**: Items that can be found or interacted with in the room.
- **npcs**: NPCs present within the room, each with their dialogue and interactions.

Remember, when specifying paths for rooms, ensure that they are consistent with the rest of the world's navigation structure. This will enable players to move seamlessly between locations, sublocations, and rooms.

``
### Instructions

- **name**: A string for the sublocation's name.
- **description**: A detailed description of the sublocation.
- **keywords**: An array of strings highlighting key themes or elements of the sublocation.
- **paths**: An object with keys for "exit" pointing to the parent location and other keys for each room within the sublocation.
- **items**: An array of item objects that can be found in the sublocation.
- **containers**: An array of container objects present in the sublocation.
- **npcs**: An array of NPC objects.
- **rooms**: An array of room objects that are part of the sublocation.

## Adding Items

### Structure

```json
{
    "name": "Item Name",
    "description": "Description of the item.",
    "type": "Item Type",
    "collectable": true or false,
    "interactions": [
        {
            "type": "Interaction Type",
            "description": "Description of the interaction."
        }
    ],
    "quantity": Number
}
```

### Instructions

- **name**: The item's name.
- **description**: What the item is or does.
- **type**: Category of the item (e.g., "Weapon", "Food").
- **collectable**: Boolean indicating if the item can be collected.
- **interactions**: An array of interactions available with the item, such as using it or combining it with another item.
- **quantity**: How many of this item are available.

## Adding Containers

### Structure

```json
{
    "name": "Container Name",
    "description": "Description of the container.",
    "paths": {
        "close": "Parent Sublocation"
    },
    "type": "Container",
    "isOpen": false,
    "collectable": false,
    "interactions": [
        {
            "type": "Interaction Type",
            "description": "Description of the interaction."
        }
    ],
    "invtentoy": [
        // Item objects
    ]
}
```

### Instructions

- **name**: Name of the container.
- **description**: Details about the container.
- **paths**: Object with a "close" key pointing back to the sublocation.
- **type**: Always set as "Container".
- **isOpen**: Boolean indicating if the container is open.
- **collectable**: Should be `false’ for containers.
- **contains**: An array of items within the container.

## Adding NPCs

### Structure

```json
{
    "name": "NPC Name",
    "description": "Description of the NPC.",
    "interactions": [
        {
            "type": "talk to",
            "dialogue": "Dialogue text.",
        },
        {
            "type": "Interaction Type",
            "description": "Description of the interaction."
        }
    ],
    "inventory": [
        // Item objects the NPC carries
    ]
}
```

### Instructions

- **name**: The NPC's name.
- **description**: A brief description of the NPC, including their appearance and role.
- **interactions**: An array of interactions available with the NPC, such as quests or trades.
- ***type 'talk to'***: Required to trigger the NPC's dialogue.
- **dialogue**: The NPC's dialogue.
- **inventory**: An array of items that the NPC carries and can offer to the player.


