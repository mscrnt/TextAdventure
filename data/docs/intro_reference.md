
# Intro Animation Reference

## Overview

The `IntroAnimation` class in the `intro.py` file is responsible for displaying the introductory animation sequence for the game Odyssey. It presents a scrolling text animation reminiscent of classic adventure games and movies.

## Key Components

### Class Definition

```python
class IntroAnimation(QWidget):
    animationComplete = Signal()
```

- Inherits from `QWidget`.
- Emits `animationComplete` signal upon completing the animation.

### Initialization

- Initializes UI components.
- Sets up timers for title display and intro text scrolling.
- Enables mouse click event to skip the intro.

### UI Setup

- Creates and centers a title label (`intro_title_label`).
- Applies custom font and color settings.
- Defines geometry to match the parent widget's size.

### Animation Logic

- **Title Display**: Shows a title text for a brief period.
- **Text Scrolling**: Scrolls introductory text upwards.
- **Skip Feature**: Allows users to skip the intro by clicking on the widget.

### Methods

- `init_ui()`: Initializes the UI components.
- `scroll_title()`: Handles the scrolling of the title text.
- `load_game_ui()`: Emits `animationComplete` to signal the end of the animation.
- `animate_intro_text()`: Starts the scrolling text animation.
- `scroll_text()`: Manages the scrolling mechanism for the intro text.
- `start_intro_crawl()`: Initiates the scrolling text animation after the title display.
- `show_intro_text()`: Replaces the title with scrolling intro text.
- `skip_intro()`: Stops the animation and emits `animationComplete` when clicked.
- `create_skip_label()`: Creates a label indicating the option to skip the intro.

## Usage

To use `IntroAnimation`:

1. Instantiate `IntroAnimation` as a widget.
2. Add it to the desired layout or set it as the central widget.
3. Connect the `animationComplete` signal to the desired slot to handle post-animation behavior.

Example:

```python
intro_animation = IntroAnimation(parent)
intro_animation.animationComplete.connect(load_game_ui)
```

This reference provides a comprehensive overview of the `IntroAnimation` class, aiding in understanding its role and implementation in the Odyssey game.
