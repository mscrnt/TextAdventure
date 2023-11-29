# gui/game_ui.py

from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QComboBox, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QTextBlockFormat, QFontMetrics
import time
from engine.game_manager import GameManager
from icecream import ic
from engine.world_builder import WorldBuilder

class GameUI(QWidget):
    def __init__(self, player_name, parent=None):
        super(GameUI, self).__init__(parent)
        self.is_item_clicked_connected = False  
        self.current_category = None 
        self.init_ui()
        self.game_manager = GameManager(player_name, self)
        self.game_manager.gameLoaded.connect(self.on_game_loaded)
        self.world_builder = WorldBuilder(self.game_manager, self.game_manager.world_data) 
        ic("GameUI initialized")
        self.initialize_drop_down_menu() 

    def on_game_loaded(self):
        # This slot will be called when the GameManager emits the gameLoaded signal
        self.update_ui()

    def init_ui(self):
        # Create the main layout
        ic("Initializing UI")
        main_layout = QHBoxLayout(self)
        
        # Create the inventory panel
        inventory_layout = QVBoxLayout()

        # Add a label to the inventory panel for the category
        self.inventory_label = QLabel("Inventory")  
        self.inventory_label.setAlignment(Qt.AlignCenter)
        self.inventory_label.setFont(QFont("Arial", 16, QFont.Bold))
    
        self.inventory_list = QListWidget()
        self.drop_down_menu = QComboBox()
        inventory_layout.addWidget(self.inventory_label)
        inventory_layout.addWidget(self.inventory_list, 5)  
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
        right_panel_layout.addLayout(input_layout, 1)
        
        # Add both left and right panels to the main layout
        main_layout.addLayout(inventory_layout, 2)  
        main_layout.addLayout(right_panel_layout, 5)  

        # Set up interactions
        self.enter_button.clicked.connect(self.process_command)
        self.command_input.returnPressed.connect(self.process_command)

        # Set the dark theme palette for the entire widget
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 0)) 
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  
        self.setPalette(palette)

        # Create a new palette for the drop down menu and the command input
        input_palette = QPalette()
        input_palette.setColor(QPalette.Text, QColor(0, 0, 0)) 
        input_palette.setColor(QPalette.Base, QColor(255, 255, 255)) 
        self.drop_down_menu.setPalette(input_palette)
        self.command_input.setPalette(input_palette)

        # Ensure the game_text_area retains the yellow text color
        text_area_palette = self.game_text_area.palette()
        text_area_palette.setColor(QPalette.Text, QColor(255, 255, 0))  # Yellow text for game_text_area
        self.game_text_area.setPalette(text_area_palette)


    def initialize_drop_down_menu(self):
        ic("Initializing drop down menu")
        # Add categories to the drop-down menu
        self.drop_down_menu.addItem("Inventory")
        self.drop_down_menu.addItem("Fast Travel")
        self.drop_down_menu.addItem("Notes")
        self.drop_down_menu.addItem("Quest Log")
        self.drop_down_menu.addItem("Emails")

        # Connect the selection change to update UI
        self.drop_down_menu.activated.connect(self.update_ui_from_dropdown)

        # Set the default view to Inventory
        self.drop_down_menu.setCurrentIndex(3)  # Inventory is the first item
        self.update_ui_from_dropdown(3)  # Update the UI to show inventory items


    def update_ui_from_dropdown(self, index):
        ic("Updating UI from dropdown")
        # Get the current text of the selected item
        selected_item = self.drop_down_menu.currentText()
        self.current_category = selected_item
        
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
            self.update_quest_log(self.game_manager.get_player_quests())
        elif selected_item == "Emails":
            self.populate_emails()
        ic("Connecting item clicked")


        # Ensure to connect the item clicked signal to the display_item_information method
        self.inventory_list.itemClicked.connect(self.display_item_information)
        self.is_item_clicked_connected = True

    def populate_inventory(self):
        ic("Populating inventory")
        # Use the GameManager to get inventory items
        items = self.game_manager.get_inventory_items()
        for item_string in items:
            self.inventory_list.addItem(item_string)

    def populate_fast_travel_locations(self):
        ic("Populating fast travel locations")
        # Get fast travel locations from the game manager
        locations = self.game_manager.get_fast_travel_locations()
        for location in locations:
            # Add each location's name to the inventory list
            self.inventory_list.addItem(location['name'])  

    def populate_notes(self):
        ic("Populating notes")
        # Get notes from the game manager
        notes = self.game_manager.get_player_notes()
        for note in notes:
            # Add each note's name or a summary to the inventory list
            self.inventory_list.addItem(note['name'])

    def populate_quest_log(self):
        ic("Populating quest log")
        quests = self.game_manager.get_player_quests()
        for quest in quests:
            self.inventory_list.addItem(quest)

    def populate_emails(self):
        ic("Populating emails")
        # Clear the existing items in the list to refresh the list
        self.inventory_list.clear()
        # Get emails from the game manager
        emails = self.game_manager.get_player_emails()
        
        # Sort emails so that unread emails come first
        sorted_emails = sorted(emails, key=lambda x: x['read'])
        
        # Add emails to the list with a different style if read
        for email in sorted_emails:
            item_text = f"{email['name']} (Read)" if email['read'] else email['name']
            item = QListWidgetItem(item_text)
            
            # If the email is read, set the color to grey
            if email['read']:
                item.setForeground(QColor('grey'))
            else:
                # Ensure that unread emails are bold
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.inventory_list.addItem(item)

    def process_command(self):

        # Placeholder conditional in case I want to add other command interpretations
        if_not_dummy = False # Remove this line when you start implementing commands
        if if_not_dummy: # Revise this line when you start implementing commands
            pass
        else:
            command_text = self.command_input.text().strip().lower()
            self.command_input.clear()

        response = self.world_builder.incoming_command(command_text)
        self.display_text(response)


    def display_item_information(self, item_widget):
        ic("Displaying item information")
        # Retrieve the selected item's text
        selected_text = item_widget.text()

        # If the current category is "Quest Log", strip out the status from the item text
        if self.current_category == "Quest Log":
            selected_name = selected_text.split(":")[0].strip()  # Get the name part only before the colon
        else:
            selected_name = selected_text.split(' (')[0].strip()  # Removes the quantity, assuming it's in the format "Name (xQuantity)"

        item_details = None
        if self.current_category == "Inventory":
            item_details = self.game_manager.get_inventory_item_details(selected_name)
        elif self.current_category == "Fast Travel":
            item_details = self.game_manager.get_fast_travel_location_details(selected_name)
        elif self.current_category == "Notes":
            item_details = self.game_manager.get_note_details(selected_name)
        elif self.current_category == "Quest Log":
            item_details = self.game_manager.get_quest_details(selected_name)
        elif self.current_category == "Emails":
            item_details = self.game_manager.get_player_email_details(selected_name)
            self.game_manager.mark_email_as_read(selected_name)

        if item_details:
            # For quests, you want to display the status as well, so append it if it's a quest
            if self.current_category == "Quest Log":
                formatted_details = f"{selected_name}:\n{'Completed' if item_details['completed'] else 'In Progress'}\n\n{item_details['description']}"
            elif self.current_category == "Emails":
                formatted_details = f"{selected_name}:\nFrom: {item_details['sender']}\n\n {item_details['description']}"
            else:
                formatted_details = f"{selected_name}:\n\n{item_details['description']}"
            self.display_text(formatted_details)
        else:
            self.display_text("Item details not found.")

    def display_text(self, text):
        ic("Displaying text")
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
        font.setFamily("Consolas")  
        font.setPointSize(12) 
        self.game_text_area.setFont(font)

        # Calculate font metrics for the current font
        metrics = QFontMetrics(font)
        text_lines = text.split('\n')
        max_lines = 1000 // metrics.height()  # Calculate the maximum number of lines that can fit in the text area. This is basically limitless for our purposes.

        # Function to calculate padding
        def calculate_padding(text_block):
            text_height = metrics.height() * len(text_block)
            text_area_height = self.game_text_area.viewport().height() - 100
            padding_lines = max(0, (text_area_height - text_height) // (2 * metrics.height()))
            return '\n' #* padding_lines

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
                time.sleep(0.0001)

            # Wait for a moment after each chunk
            time.sleep(1)

            # Clear the area for the next chunk
            if i + max_lines < len(text_lines):
                self.game_text_area.clear()

        # Re-center the cursor after typing is complete
        self.game_text_area.setAlignment(Qt.AlignCenter)

        # Ensure the scrollbar is adjusted properly at the end of all text
        #self.game_text_area.verticalScrollBar().setValue(0)  # Reset scrollbar to the top
        #self.game_text_area.ensureCursorVisible()

    def update_quest_log(self, quests):
        ic("Updating quest log")
        self.inventory_list.clear()
        for quest in quests:
            self.inventory_list.addItem(quest)

    def update_ui(self):
        ic("Updating UI")
        # Set the dropdown to 'Quest Log'
        quest_log_index = self.drop_down_menu.findText('Quest Log')
        if quest_log_index >= 0:
            self.drop_down_menu.setCurrentIndex(quest_log_index)
            self.update_ui_from_dropdown(quest_log_index)
        else:
            print("Quest Log not found in dropdown.")

    def update_scene_display(self):
        scene_text = self.world_builder.build_scene_text()
        self.display_text(scene_text)