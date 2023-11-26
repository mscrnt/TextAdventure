
# World JSON Structure Reference

## Overview

This document serves as a guide for expanding the Avalonia game world. The world is structured in JSON format, comprising locations, sublocations, paths, items, and other interactive elements.

## Adding Locations

### Structure

```json
{
    "name": "Location Name",
    "description": "Description of the location.",
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
- **paths**: An object where each key is a direction (e.g., "north", "east", "south", "west", "up", "down") and each value is the name of the location it connects to.
- **sublocations**: An array of sublocation objects (see below for sublocation structure).

## Adding Sublocations

### Structure

```json
{
    "name": "Sublocation Name",
    "description": "Description of the sublocation.",
    "paths": {
        "exit": "Parent Location"
    },
    "items": [
        // Item objects
    ],
    "containers": [
        // Container objects
    ]
}
```

### Instructions

- **name**: A string for the sublocation's name.
- **description**: A detailed description of the sublocation.
- **paths**: An object with an "exit" key pointing to the parent location.
- **items**: An array of item objects that can be found in the sublocation.
- **containers**: An array of container objects present in the sublocation.

## Adding Paths

### Instructions

- To add a path, modify the "paths" object in the location or sublocation.
- Ensure the path direction is logical and connects to an existing location.

Example:

```json
"paths": {
    "north": "New Location"
}
```

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
- **collectable**: Should be `false` for containers.
- **contains**: An array of items within the container.

---

