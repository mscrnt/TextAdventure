# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QStackedLayout, QPushButton, QFileDialog, QInputDialog, QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from icecream import ic
from interfaces import IGameUI
from gui.game_ui import GameUI
from engine.game_manager import GameManager
from engine.world_builder import WorldBuilder
from engine.quest_tracker import QuestTracker
from engine.player_sheet import PlayerSheet
from intro import IntroAnimation


class MainWindow(QMainWindow):
    def __init__(self, use_ai=False):
        super().__init__()
        self.game_manager = None
        self.world_builder = None
        self.player_sheet = None
        self.quest_tracker = None
        self.game_ui = None
        self.use_ai = use_ai
        ic("Initializing main window")

        # Set the main window's properties
        self.setWindowTitle("Odyssey")
        self.setGeometry(100, 100, 800, 600)

        # Set the theme
        self.set_dark_theme()

        # Initialize Menu Bar first
        self.init_menu_bar()

        # Create central widget and stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QStackedLayout(central_widget)

        # Initialize Splash Screen
        self.init_splash_screen()

        # Initialize Main Game Interface
        self.init_game_interface()

        self.init_entry_point()

    def initialize_game_components(self):
        if not self.game_manager:
            self.game_manager = GameManager(use_ai=self.use_ai)
            
            # This now occurs only after the game_manager has been initialized
            self.game_manager.initialize_game_data("Player")
            self.game_manager.initialize_world_builder()

            # Here, obtain the GameUI instance from game_manager instead of creating a new one
            self.game_ui = self.game_manager.game_ui  
            self.game_manager.gameLoaded.connect(self.game_ui.on_game_loaded)
            self.game_ui.ui_ready_to_show.connect(self.switch_to_game_ui)


    def set_game_ui(self, game_ui: IGameUI):
        self.game_ui = game_ui

    def set_dark_theme(self):
        # Set the palette for a dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(35, 35, 35))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(75, 110, 175))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.setPalette(palette)

    def init_entry_point(self):
        # Entry point widget setup
        ic("Initializing entry point")
        ic(self.layout)
        self.entry_point_widget = QWidget()  
        entry_point_layout = QVBoxLayout(self.entry_point_widget)

        # New Game Button
        new_game_button = QPushButton("New Game")
        new_game_button.setMaximumWidth(200)  
        new_game_button.setStyleSheet("QPushButton { background-color: #333; color: #fff; }") 
        new_game_button.clicked.connect(self.start_new_game)
        entry_point_layout.addWidget(new_game_button, 0, Qt.AlignCenter)  

        # Load Game Button
        load_game_button = QPushButton("Load Game")
        load_game_button.setMaximumWidth(200) 
        load_game_button.setStyleSheet("QPushButton { background-color: #333; color: #fff; }")
        load_game_button.clicked.connect(self.select_save_file)
        entry_point_layout.addWidget(load_game_button, 0, Qt.AlignCenter) 

        self.layout.addWidget(self.entry_point_widget)

    def on_intro_animation_complete(self):
        # Called when the intro animation is done
        if self.game_manager.start_new_game(self.player_name):
            self.switch_to_game_ui()
        else:
            ic("Failed to start new game.")

    def init_splash_screen(self):
        ic("Initializing splash screen")
        splash_widget = QWidget()
        splash_layout = QVBoxLayout(splash_widget)

        # ASCII Art Splash
        ascii_splash_label = QLabel(self.create_ascii_banner("Click Anywhere to Start"))
        ascii_splash_label.setFont(QFont("Courier New", 10))
        ascii_splash_label.setAlignment(Qt.AlignCenter)
        splash_layout.addWidget(ascii_splash_label)

        # Event filter for mouse clicks on the splash screen
        splash_widget.mousePressEvent = self.start_game
        splash_widget.setFocusPolicy(Qt.StrongFocus) 

        self.layout.addWidget(splash_widget)

    def init_menu_bar(self):
        ic("Initializing menu bar")
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
        ic("Initializing file menu")
        file_menu = menu_bar.addMenu("File")
        new_game_action = file_menu.addAction("New Game")
        save_game_action = file_menu.addAction("Save Game")
        load_game_action = file_menu.addAction("Load Game")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")

        # Connect actions
        ic("Connecting actions")
        new_game_action.triggered.connect(self.start_new_game)
        save_game_action.triggered.connect(self.trigger_save_game)
        load_game_action.triggered.connect(self.select_save_file)
        exit_action.triggered.connect(self.close)

        # Add actions to menu
        ic("Adding actions to menu")
        file_menu.addAction(new_game_action)
        file_menu.addAction(save_game_action)
        file_menu.addAction(load_game_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        ic("Initializing edit menu")
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Preferences")

        # Help Menu
        ic("Initializing help menu")
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Game Instructions")

    def init_game_interface(self):
        ic("Initializing game interface")
        # Game interface setup
        game_widget = QWidget()
        game_layout = QVBoxLayout(game_widget)

        # Text area for game narrative
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        game_layout.addWidget(self.text_area)

        self.layout.addWidget(game_widget)

    def create_ascii_banner(self, text):
        ic("Creating ASCII banner")
        banner_width = 80
        padding = (banner_width - len(text) - 2) // 2
        banner_text = "+" + "-" * (banner_width - 2) + "+\n"
        banner_text += "|" + " " * padding + text + " " * padding + "|\n"
        banner_text += "+" + "-" * (banner_width - 2) + "+"
        return banner_text

    def start_game(self, event):
        ic("Starting game")
        # This method is called when the splash screen is clicked
        if event.button() == Qt.LeftButton:
            # Change to the entry point screen
            self.layout.setCurrentIndex(self.layout.indexOf(self.entry_point_widget))

    def switch_to_game_ui(self):
        """
        Switch the central widget to the game UI.
        """
        ic("Switching to game UI")
        self.game_manager.gameLoaded.connect(self.game_ui.on_game_loaded)
        self.setCentralWidget(self.game_manager.game_ui)  
        self.game_manager.game_ui.show() 


    def start_new_game(self):
        self.initialize_game_components()
        self.player_name = self.prompt_for_player_name() # Store the player name
        if self.player_name:
            # Add intro animation here
            self.intro_animation = IntroAnimation(self)
            self.setCentralWidget(self.intro_animation)
            self.intro_animation.animationComplete.connect(self.on_intro_animation_complete)
            self.intro_animation.start()
        else:
            ic("No player name entered.")

    # Method to save the game
    def trigger_save_game(self):
        self.game_ui.game_manager.save_game()

    def select_save_file(self):
        self.initialize_game_components()
        filename, _ = QFileDialog.getOpenFileName(self, "Load Game", "save_data/", "Save Files (*.pkl)")
        if filename:
            if self.game_manager.load_game(filename):
                self.switch_to_game_ui()
            else:
                ic("Failed to load the game.")

    def prompt_for_player_name(self):
        dialog = QInputDialog(self)
        dialog.setStyleSheet("""
            QLineEdit { color: black; }
            QPushButton { color: black; }
        """)
        dialog.setWindowTitle("Player Name")
        dialog.setLabelText("Enter your name:")
        if dialog.exec() == QDialog.Accepted:
            return dialog.textValue()
        return None