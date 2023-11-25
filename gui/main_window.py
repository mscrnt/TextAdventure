# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QStackedLayout, QPushButton, QFileDialog, QInputDialog, QDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor
from engine.game_manager import GameManager
import json
from typing import Dict
from icecream import ic
import sys
from intro import IntroAnimation
from gui.game_ui import GameUI
import utilities


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window's properties
        self.setWindowTitle("Odyssey")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Menu Bar first
        self.init_menu_bar()

        # Create central widget and stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QStackedLayout(central_widget)

        # Initialize Splash Screen
        self.init_splash_screen()

        # Create the GameUI but don't display it yet
        # self.game_ui = GameUI()

        # Initialize Main Game Interface
        self.init_game_interface()

        self.init_entry_point()

    def init_entry_point(self):
        self.entry_point_widget = QWidget()  # Assign to an attribute
        entry_point_layout = QVBoxLayout(self.entry_point_widget)

        # New Game Button
        new_game_button = QPushButton("New Game")
        new_game_button.setMaximumWidth(200)  # Set maximum width
        new_game_button.setStyleSheet("QPushButton { background-color: #333; color: #fff; }")  # Set the style
        new_game_button.clicked.connect(self.start_new_game)
        entry_point_layout.addWidget(new_game_button, 0, Qt.AlignCenter)  # Align to center

        # Load Game Button
        load_game_button = QPushButton("Load Game")
        load_game_button.setMaximumWidth(200)  # Set maximum width
        load_game_button.setStyleSheet("QPushButton { background-color: #333; color: #fff; }")  # Set the style
        load_game_button.clicked.connect(self.select_save_file)
        entry_point_layout.addWidget(load_game_button, 0, Qt.AlignCenter)  # Align to center

        self.layout.addWidget(self.entry_point_widget)

    def on_intro_animation_complete(self):
        # Here, switch to the game UI
        self.setCentralWidget(self.game_ui)

    def init_splash_screen(self):
        splash_widget = QWidget()
        splash_layout = QVBoxLayout(splash_widget)

        # ASCII Art Splash
        ascii_splash_label = QLabel(self.create_ascii_banner("Click Anywhere to Start"))
        ascii_splash_label.setFont(QFont("Courier New", 10))
        ascii_splash_label.setAlignment(Qt.AlignCenter)
        splash_layout.addWidget(ascii_splash_label)

        # Event filter for mouse clicks on the splash screen
        splash_widget.mousePressEvent = self.start_game
        splash_widget.setFocusPolicy(Qt.StrongFocus)  # Ensure the widget can be focused to receive mouse events

        self.layout.addWidget(splash_widget)

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        # Set menu bar color to match
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: rgb(35, 35, 35);
                color: rgb(255, 255, 255);
            }
            QMenuBar::item {
                background-color: rgb(35, 35, 35);
                color: rgb(255, 255, 255);
            }
            QMenuBar::item::selected {
                background-color: rgb(75, 110, 175);
            }
        """)

        # File Menu
        file_menu = menu_bar.addMenu("File")
        new_game_action = file_menu.addAction("New Game")
        save_game_action = file_menu.addAction("Save Game")
        load_game_action = file_menu.addAction("Load Game")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")

        # Connect actions
        new_game_action.triggered.connect(self.start_new_game)
        save_game_action.triggered.connect(self.trigger_save_game)
        load_game_action.triggered.connect(self.select_save_file)
        exit_action.triggered.connect(self.close)

        # Add actions to menu
        file_menu.addAction(new_game_action)
        file_menu.addAction(save_game_action)
        file_menu.addAction(load_game_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Preferences")

        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Game Instructions")

    def init_game_interface(self):
        # Game interface setup
        game_widget = QWidget()
        game_layout = QVBoxLayout(game_widget)

        # Text area for game narrative
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        game_layout.addWidget(self.text_area)

        self.layout.addWidget(game_widget)

    def create_ascii_banner(self, text):
        banner_width = 80
        padding = (banner_width - len(text) - 2) // 2
        banner_text = "+" + "-" * (banner_width - 2) + "+\n"
        banner_text += "|" + " " * padding + text + " " * padding + "|\n"
        banner_text += "+" + "-" * (banner_width - 2) + "+"
        return banner_text

    def start_game(self, event):
        # This method is called when the splash screen is clicked
        if event.button() == Qt.LeftButton:
            # Change to the entry point screen
            self.layout.setCurrentIndex(self.layout.indexOf(self.entry_point_widget))


    def change_to_game_ui(self):
        # Instantiate the game UI and set it as the central widget
        self.game_ui = GameUI()
        self.setCentralWidget(self.game_ui)

    def start_new_game(self):
        player_name = self.prompt_for_player_name()  # Get the player's name
        if player_name:
            self.game_ui = GameUI(player_name)  # Pass the name to GameUI
            self.introAnimation = IntroAnimation(self)
            self.introAnimation.animationComplete.connect(self.on_intro_animation_complete)
            self.setCentralWidget(self.introAnimation)
        else:
            # Optionally, handle the case where no name was entered, such as showing a message to the user
            print("No player name entered, new game not started.")

    # Method to save the game
    def trigger_save_game(self):
        # You will need a reference to your game_manager to call its save method
        self.game_ui.game_manager.save_game()

    # Method to load the game
    def select_save_file(self):
        # Open a file dialog to select the save file, starting in the 'save_data/' directory
        filename, _ = QFileDialog.getOpenFileName(self, "Load Game", "save_data/", "Save Files (*.pkl)")
        if filename:
            # Create a GameUI instance if it does not exist
            if not hasattr(self, 'game_ui'):
                # Since we don't have the player's name, we might need to extract it from the save file or set a default
                player_name = 'Default'  # You should replace this with the actual name from the save file if possible
                self.game_ui = GameUI(player_name)

            if self.game_ui.game_manager.load_game(filename):
                # No need to call update_ui here as it's now connected to the signal
                self.setCentralWidget(self.game_ui)
                print(f"Game loaded successfully from {filename}.")
            else:
                print("Failed to load the game.")
        else:
            print("No file selected.")

    def prompt_for_player_name(self):
        dialog = QInputDialog(self)
        # Ensure text in QLineEdit and QPushButton is black
        dialog.setStyleSheet("""
            QLineEdit { color: black; }
            QPushButton { color: black; }
        """)
        dialog.setWindowTitle("Player Name")
        dialog.setLabelText("Enter your name:")
        if dialog.exec() == QDialog.Accepted:
            return dialog.textValue()
        return None