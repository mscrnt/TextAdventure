import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QStackedLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QComboBox
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QTextCursor
import time

class GameUI(QWidget):
    def __init__(self, parent=None):
        super(GameUI, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create the main layout
        main_layout = QHBoxLayout(self)
        
        # Create the inventory panel
        inventory_layout = QVBoxLayout()
        self.inventory_list = QListWidget()
        self.drop_down_menu = QComboBox()
        inventory_layout.addWidget(self.inventory_list, 5)  # Adjust the stretch factor to make it taller
        inventory_layout.addWidget(self.drop_down_menu, 1)

        # Create the right panel for output text and command input
        right_panel_layout = QVBoxLayout()
        self.game_text_area = QTextEdit()
        self.command_input = QLineEdit()
        self.enter_button = QPushButton("Enter")
        self.game_text_area.setReadOnly(True)


        # Add widgets to the right panel layout
        right_panel_layout.addWidget(self.game_text_area, 5)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.command_input, 4)
        input_layout.addWidget(self.enter_button)
        right_panel_layout.addLayout(input_layout, 1)  # Adjust the stretch factor to make it shorter
        
        # Add both left and right panels to the main layout
        main_layout.addLayout(inventory_layout, 2)  # Adjust the stretch factor to make the inventory panel wider
        main_layout.addLayout(right_panel_layout, 5)  # Adjust the stretch factor to control the width of the right panel

        # Set up interactions
        self.enter_button.clicked.connect(self.process_command)
        self.command_input.returnPressed.connect(self.process_command)

        # Set the dark theme palette for the entire widget
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 0))  # Yellow window text
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Yellow button text
        self.setPalette(palette)

        # Create a new palette for the drop down menu and the command input
        input_palette = QPalette()
        input_palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Black text for input
        input_palette.setColor(QPalette.Base, QColor(255, 255, 255))  # White background for input
        self.drop_down_menu.setPalette(input_palette)
        self.command_input.setPalette(input_palette)

        # Ensure the game_text_area retains the yellow text color
        text_area_palette = self.game_text_area.palette()
        text_area_palette.setColor(QPalette.Text, QColor(255, 255, 0))  # Yellow text for game_text_area
        self.game_text_area.setPalette(text_area_palette)

    def process_command(self):
        # Get the command from the input
        command = self.command_input.text()
        # Clear the command input
        self.command_input.clear()
        # Process the command
        self.display_text(f"Command executed: {command}")

    def display_text(self, text):
        # Clear the game text area
        self.game_text_area.clear()
        # Iterate over the string and append one character at a time
        for char in text:
            # Append character to the text area
            self.game_text_area.moveCursor(QTextCursor.End)
            self.game_text_area.insertPlainText(char)
            # Process events to update the text area immediately
            QApplication.processEvents()
            # Sleep for a short duration to create a typing effect
            time.sleep(0.05)