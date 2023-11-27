
# Quests JSON Structure Reference

## Overview

This document serves as a guide for managing and expanding quests in the game world using the `quests.json` file.

## Structure of a Quest

```json
[
    {
        "name": "Quest Name",
        "slug": "uniqueQuestIdentifier",
        "description": "Description of the quest.",
        "isActive": false,
        "completed": false,
        "objectives": [
            // Array of objective objects
        ]
    }
    // Additional quests...
]
```

### Quest Attributes

- **name**: A string representing the quest's name.
- **slug**: A unique string identifier for the quest, used in mapping quest classes.
- **description**: A brief description of what the quest entails.
- **isActive**: Boolean indicating if the quest is currently active.
- **completed**: Boolean indicating if the quest is completed.
- **objectives**: An array of objective objects related to the quest.

## Adding Objectives

### Objective Structure

```json
{
    "type": "ObjectiveType",
    "target": "TargetCriteria",
    "completed": false
}
```

### Objective Attributes

- **type**: The type of the objective (e.g., "readEmail", "fetchQuest"). This is used to map to the corresponding objective class.
- **target**: Specifies the target criteria for the objective, which can vary based on the objective type.
- **completed**: Boolean indicating if the objective is completed.

## Quest Tracker and Quest Classes

### Quest Tracker

- The `QuestTracker` class is responsible for managing quests in the game.
- It reads quests from `quests.json`, tracks their progress, and handles quest activation and completion.

### Quest Classes

- Each quest type should have a corresponding Python class that extends `BaseQuest`.
- The quest class is responsible for handling specific logic related to the quest.

## Adding New Quests

1. Define the quest in the `quests.json` file with all necessary details.
2. Create a new quest class in Python that extends `BaseQuest` and handles the quest-specific logic.
3. Update the `quest_class_for_slug` method in `QuestTracker` to map the quest's slug to the new quest class.

## Example

### Quest in JSON

```json
{
    "name": "Find the Lost Sword",
    "slug": "findLostSword",
    "description": "Retrieve the legendary sword lost in the Whispering Forest.",
    "isActive": false,
    "completed": false,
    "objectives": [
        {
            "type": "fetchQuest",
            "target": "Legendary Sword",
            "completed": false
        }
    ]
}
```

### Corresponding Quest Class

```python
class FindLostSwordQuest(BaseQuest):
    # Implementation of quest-specific logic
```

### Quest Tracker Update

```python
def quest_class_for_slug(self, quest_slug):
    quest_classes = {
        # ...existing mappings...
        'findLostSword': FindLostSwordQuest,
    }
    return quest_classes.get(quest_slug)
```

This reference should provide a clear framework for adding and managing quests in the game world.
