# Mega Reference Guide for Game JSON Data Files

## Overview

This guide provides a comprehensive reference for the various JSON data files used in the game. These files define the core elements such as notes, locations, items, and emails, which are integral to the gameplay and narrative.

### Notes (`notes.json`)

The `notes.json` file contains a collection of notes that players can discover throughout the game. Each note provides lore, hints, or story elements.

#### Structure

```json
{
    "notes": [
        {
            "name": "Note Title",
            "description": "Description or content of the note."
        }
        // Additional notes...
    ]
}
```

#### Example Entries

- **Enchanted Cave**: Hints about a secret power in a cave.
- **Mystic Forest Map**: Reveals hidden pathways in a forest.
- **Ancient Ruins**: Warns about a slumbering beast in the ruins.
- **Herbalist's Recipe**: Provides a recipe for a healing potion.
- **Thief's Confession**: Mentions a gemstone with a curse.

### Locations (`locations.json`)

The `locations.json` file defines various worlds and locations within each world. These locations serve as the setting for the game's events and player exploration.

#### Structure

```json
{
    "worlds": [
        {
            "name": "World Name",
            "description": "Description of the world.",
            "locations": [
                {
                    "name": "Location Name",
                    "description": "Description of the location.",
                    "main_area": true or false
                }
                // Additional locations...
            ]
        }
        // Additional worlds...
    ]
}
```

#### Example Entries

- **Avalonia**: A mystical land with diverse biomes.
- **Central Avalonia**: The heart of Avalonia with a grand castle.
- **Eldergrove Forest**: An old forest with mystical properties.
- **Dreadmount Peaks**: A treacherous mountain range.

### Items (`item_list.json`)

The `item_list.json` file contains a list of items available in the game. Items can include consumables, weapons, notes, and other types.

#### Structure

```json
{
    "items": [
        {
            "name": "Item Name",
            "description": "Description of the item.",
            "type": "Item Type"
        }
        // Additional items...
    ]
}
```

### Quests and Worlds json files

The `quests.json` and `worlds.json` files define the quests and worlds in the game. These files are used by the `QuestTracker` and `WorldBuilder` classes to manage quests and locations.
You can find more information about these files in the [Quests JSON Structure Reference](Quests_References.md) and [Worlds JSON Structure Reference](Worlds_References.md).

#### Example Entries

- **Health Potion**: Restores health.
- **Excalibur**: The legendary sword.
- **Ancient Scroll**: Contains ancient wisdom.
- **Bitcoin**: Digital currency.

### Emails (`emails.json`)

The `emails.json` file stores emails that players can receive during the game. These emails can contain information, quests, offers, and more.

#### Structure

```json
{
    "emails": [
        {
            "name": "Email Subject",
            "description": "Content of the email.",
            "read": true or false,
            "sender": "Sender's Name"
        }
        // Additional emails...
    ]
}
```


