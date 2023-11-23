# game_manager.py
from PySide6.QtWidgets import QListWidget, QTextEdit, QLineEdit, QVBoxLayout, QWidget
import sys
from icecream import ic

class GameManager:
    def __init__(self, parent_widget):
        # Store the parent widget to add UI components to
        self.parent_widget = parent_widget
        
        # Create a layout for the parent widget
        self.layout = QVBoxLayout(self.parent_widget)
        
        # Initialize UI components
        self.inventory_list = QListWidget()
        self.game_text_area = QTextEdit()
        self.text_entry = QLineEdit()
        
        # Set up the UI components
        self.setup_ui()

    def setup_ui(self):
        # Since we already cleared the layout in the MainWindow class,
        # we can directly create a new layout and set it to the parent_widget
        layout = QVBoxLayout(self.parent_widget)
        layout.addWidget(self.inventory_list)
        layout.addWidget(self.game_text_area)
        layout.addWidget(self.text_entry)
        
        # Set the new layout to the parent widget
        self.parent_widget.setLayout(layout)
            
    def process_command(self):
        # Get the text from the entry box
        command = self.text_entry.text()
        # Process the command
        # ...
        # Clear the entry box
        self.text_entry.clear()
    
    # You can add more methods to manage game state, handle commands, etc.
