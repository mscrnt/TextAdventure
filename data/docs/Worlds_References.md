Certainly! Here's a revised version of your `worlds_references.md` document, updated to reflect the latest structure and examples from the Grand Castle in Avalonia:

---

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
        "direction": "Connected Location"
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
- **paths**: An object where each key is a direction (e.g., "north", "east", "south", "west", "up", "down") and each value is the name of the location it connects to.
- **sublocations**: An array of sublocation objects (see below for sublocation structure).

## Adding Sublocations

### Structure

```json
{
    "name": "Sublocation Name",
    "description": "Description of the sublocation.",
    "keywords": ["keyword1", "keyword2"],
    "paths": {
        "exit": "Parent Location"
    },
    "items": [
        // Item objects
    ],
    "containers": [
        // Container objects
    ],
    "npcs": [
        // NPC objects
    ]
}
```

### Instructions

- **name**: A string for the sublocation's name.
- **description**: A detailed description of the sublocation.
- **keywords**: An array of strings highlighting key themes or elements of the sublocation.
- **paths**: An object with an "exit" key pointing to the parent location.
- **items**: An array of item objects that can be found in the sublocation.
- **containers**: An array of container objects present in the sublocation.
- **npcs**: An array of NPC objects, each with details about the NPC.

## Adding Items

### Structure

```json
{
    "name": "Item Name",
    "description": "Description of the item.",
    "type": "Item Type",
    "collectable": true or false,
    "quantity": Number
}
```

### Instructions

- **name**: The item's name.
- **description**: What the item is or does.
- **type**: Category of the item (e.g., "Weapon", "Food").
- **collectable**: Boolean indicating if the item can be collected.
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
    "contains": [
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
    "dialog": ["dialog line 1", "dialog line 2"],
    "interactions": [
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
- **dialog**: An array of strings, each representing a line of dialog the NPC can say.
- **interactions**: An array of interactions available with the NPC, such as quests or trades.
- **inventory**: An array of items that the NPC carries and can offer to the player.


