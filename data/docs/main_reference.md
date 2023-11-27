
# Main Application Reference

## Overview

This document serves as a reference for the `main.py` file, which is the entry point for the game application developed using PySide6.

## Functionality

- **Initialization**: The file sets up the main application environment, including argument parsing for debug mode and setting up the dark theme palette for the application.
- **Debug Mode**: It includes a command-line argument `--debug` to enable or disable debug mode.
- **Dark Theme Palette**: The application uses a custom color palette to create a dark theme UI.
- **Main Window**: Initializes and displays the main window of the application.

## Key Components

### Argument Parsing

- Uses `argparse` to handle command-line arguments.
- `--debug` argument enables or disables the debug mode.

### Application Setup

- Creates an instance of `QApplication` which is essential for any PySide6 application.
- Sets a dark theme palette for the application.
- Instantiates `MainWindow` from `gui.main_window` and displays it.

### Debug Configuration

- Uses `icecream` (ic) for debugging.
- When debug mode is on, additional debug information is printed.

## Example Usage

To start the application in debug mode, use the following command:

```bash
python main.py --debug
```

In the normal mode, simply start the application without any arguments:

```bash
python main.py
```

## Important Methods

### `main()`

- The main function of the script.
- Handles the initialization of the application and the main window.
- Configures the application palette and enters the main event loop of the application.

### `sys.exit(app.exec())`

- Executes the application's main loop and exits the application with the return value from `exec()`.

