import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QScrollBar, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QComboBox
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QTextCursor, QTextBlockFormat, QTextCharFormat, QFontMetrics
import time

class GameUI(QWidget):
    def __init__(self, parent=None):
        super(GameUI, self).__init__(parent)
        self.is_item_clicked_connected = False  
        self.init_ui()
        self.initialize_drop_down_menu() 

    def init_ui(self):
        # Create the main layout
        main_layout = QHBoxLayout(self)
        
        # Create the inventory panel
        inventory_layout = QVBoxLayout()

        # Add a label to the inventory panel for the category
        self.inventory_label = QLabel("Inventory")  # Default text
        self.inventory_label.setAlignment(Qt.AlignCenter)
        self.inventory_label.setFont(QFont("Arial", 16, QFont.Bold))
    
        self.inventory_list = QListWidget()
        self.drop_down_menu = QComboBox()
        inventory_layout.addWidget(self.inventory_label)
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

        #self.initialize_drop_down_menu()


    def initialize_drop_down_menu(self):
        # Add categories to the drop-down menu
        self.drop_down_menu.addItem("Inventory")
        self.drop_down_menu.addItem("Fast Travel")
        self.drop_down_menu.addItem("Notes")
        self.drop_down_menu.addItem("Quest Log")

        # Connect the selection change to update UI
        self.drop_down_menu.activated.connect(self.update_ui_from_dropdown)

        # Set the default view to Inventory
        self.drop_down_menu.setCurrentIndex(0)  # Inventory is the first item
        self.update_ui_from_dropdown(0)  # Update the UI to show inventory items


    def update_ui_from_dropdown(self, index):
        # Get the current text of the selected item
        selected_item = self.drop_down_menu.currentText()
        
        # Set the inventory label text to the selected category
        self.inventory_label.setText(selected_item + " Locations" if selected_item == "Fast Travel" else selected_item)

        # Clear the inventory list
        self.inventory_list.clear()

        # Disconnect the itemClicked signal if it's connected
        if self.is_item_clicked_connected:
            self.inventory_list.itemClicked.disconnect()
            self.is_item_clicked_connected = False  # Reset the flag

        # Populate the inventory list based on the selection
        if selected_item == "Inventory":
            self.populate_inventory()
        elif selected_item == "Fast Travel":
            self.populate_fast_travel_locations()
        elif selected_item == "Notes":
            self.populate_notes()
        elif selected_item == "Quest Log":
            self.populate_quest_log()

        # Ensure to connect the item clicked signal to the display_item_information method
        self.inventory_list.itemClicked.connect(self.display_item_information)
        self.is_item_clicked_connected = True

    # Implement these new methods to handle the display of each section
    def populate_inventory(self):
        # Logic to populate inventory items
        # For demo purposes, we'll just add some dummy items
        items = ["Sword", "Shield", "Potion"]
        for item in items:
            self.inventory_list.addItem(item)

    def populate_fast_travel_locations(self):
        # Logic to populate fast travel locations
        locations = ["Town", "Forest", "Castle"]
        for location in locations:
            self.inventory_list.addItem(location)


    def populate_notes(self):
        # Logic to populate user notes
        notes = ["Note 1", "Note 2", "Note 3"]
        for note in notes:
            self.inventory_list.addItem(note)


    def populate_quest_log(self):
        # Logic to populate quests
        quests = ["Quest 1", "Quest 2", "Quest 3"]
        for quest in quests:
            self.inventory_list.addItem(quest)

    def process_command(self):
        # Get the command from the input
        command = self.command_input.text()
        # Clear the command input
        self.command_input.clear()
        # Process the command
        self.display_text(f"Command executed: {command}")

    def display_item_information(self, item):
        # This method will be called when an item in the inventory list is clicked
        # You should replace this with the actual logic to fetch the item's information
        item_info = f"Information about {item.text()}"
        self.display_text(item_info)


    def display_text(self, text):
        # Clear the game text area before displaying new text
        self.game_text_area.clear()
        self.game_text_area.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}") # Hides the scrollbar

        # Set the alignment to center for the new text block
        text_cursor = self.game_text_area.textCursor()
        text_block_format = QTextBlockFormat()
        text_block_format.setAlignment(Qt.AlignCenter)
        text_cursor.mergeBlockFormat(text_block_format)
        self.game_text_area.setTextCursor(text_cursor)

        # Optionally set a monospace font
        font = self.game_text_area.font()
        font.setFamily("Consolas")  # This is just an example, replace with the font of your choice
        font.setPointSize(12)  # Adjust the size as needed
        self.game_text_area.setFont(font)

        # Calculate font metrics for the current font
        metrics = QFontMetrics(font)
        text_lines = text.split('\n')
        max_lines = 16

        # Function to calculate padding
        def calculate_padding(text_block):
            text_height = metrics.height() * len(text_block)
            text_area_height = self.game_text_area.viewport().height() - 5
            padding_lines = max(0, (text_area_height - text_height) // (2 * metrics.height()))
            return '\n' * padding_lines

        # Display text in chunks of max_lines
        for i in range(0, len(text_lines), max_lines):
            chunk = text_lines[i:i + max_lines]
            padding = calculate_padding(chunk)
            display_text = padding + '\n'.join(chunk) + padding

            # Insert the chunk character by character to create a typing effect
            for char in display_text:
                # Append character to the text area
                self.game_text_area.insertPlainText(char)
                # Keep text centered
                self.game_text_area.setAlignment(Qt.AlignCenter)
                # Process events to update the text area immediately
                QApplication.processEvents()
                # Sleep for a short duration to create the typing effect
                time.sleep(0.05)

            # Wait for a moment after each chunk
            time.sleep(2)

            # Clear the area for the next chunk
            if i + max_lines < len(text_lines):
                self.game_text_area.clear()

        # Re-center the cursor after typing is complete
        self.game_text_area.setAlignment(Qt.AlignCenter)

        # Ensure the scrollbar is adjusted properly at the end of all text
        self.game_text_area.verticalScrollBar().setValue(0)  # Reset scrollbar to the top
        self.game_text_area.ensureCursorVisible()