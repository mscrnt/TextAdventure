# gui/game_ui.py

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QComboBox, QListWidgetItem, QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QPalette, QColor
from icecream import ic
import re
from interfaces import IGameManager, IWorldBuilder, IGameUI
from utilities import convert_text_to_display
from engine.worker import Worker
import threading

class GameUI(QWidget, IGameUI):
    ui_ready_to_show = Signal()
    update_text_signal = Signal(str)

    def __init__(self, game_manager=IGameManager, world_builder=IWorldBuilder, parent=None):
        super().__init__(parent)
        self.game_manager = game_manager
        self.world_builder = world_builder
        self.is_item_clicked_connected = False 
        self.was_command_help = False

        
        # UI initialization logic
        self.init_ui()

        # Connect signals and slots
        self.update_text_signal.connect(self.display_text)
        self.game_manager.display_text_signal.connect(self.display_text)
        self.world_builder.display_text_signal.connect(self.display_text)

        if not self.game_manager:
            raise ValueError("GameUI requires a GameManager instance.")
        else:
            ic("GameManager instance set in GameUI:", self.game_manager)
        
        ic("GameUI initialized")

    def set_game_manager(self, game_manager: IGameManager):
        self.game_manager = game_manager

    def set_world_builder(self, world_builder: IWorldBuilder):
        self.world_builder = world_builder

    def initialize_for_new_game(self):
        """
        Initialize the UI components for a new game.
        """
        ic("Initializing UI for a new game")
        self.game_text_area.clear()
        self.inventory_list.clear()
        self.command_input.clear()

    def complete_initialization(self):
        self.initialize_drop_down_menu()
        self.update_ui_from_dropdown(3) 

    def on_game_loaded(self):
        ic("Game loaded")
        self.update_quest_log()
        self.ui_ready_to_show.emit()
        ic("GameUI is now displayed")

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
        palette.setColor(QPalette.WindowText, QColor(255, 255, 0))  # Yellow text
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Text, Qt.black)  # Black text for input fields
        self.setPalette(palette)

        # Set the style for the command input with a white background and black text
        self.command_input.setStyleSheet("""
            QLineEdit {
                color: black; 
                background-color: white; 
                border: 1px solid yellow;
                padding: 1px;
                border-radius: 3px;
            }
        """)

        # Set placeholder text for the command input
        self.command_input.setPlaceholderText("Type 'Help' to start")

        # Set the button style with a dark background and yellow text
        self.enter_button.setStyleSheet("QPushButton { background-color: #333; color: yellow; }")

        # Set the drop-down menu to match the button's theme
        self.drop_down_menu.setStyleSheet("""
            QComboBox { 
                color: yellow; 
                background-color: #333; 
                border: 1px solid yellow;
            }
            QComboBox QAbstractItemView {
                color: yellow; 
                background-color: #333; 
                selection-background-color: #555;
            }
        """)

        # Ensure the game_text_area retains the yellow text color
        text_area_palette = self.game_text_area.palette()
        text_area_palette.setColor(QPalette.Text, QColor(255, 255, 0))  # Yellow text
        self.game_text_area.setPalette(text_area_palette)

        self.complete_initialization()


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
        selected_item = self.drop_down_menu.currentText()
        ic("Selected item from dropdown:", selected_item)
        self.current_category = selected_item
        
        self.inventory_label.setText(selected_item + " Locations" if selected_item == "Fast Travel" else selected_item)
        self.inventory_list.clear()

        if self.is_item_clicked_connected:
            self.inventory_list.itemClicked.disconnect()
            self.is_item_clicked_connected = False

        # Populate the list based on the selection
        if selected_item == "Inventory":
            self.populate_inventory()
        elif selected_item == "Fast Travel":
            self.populate_fast_travel_locations()
        elif selected_item == "Notes":
            self.populate_notes()
        elif selected_item == "Quest Log":
            self.populate_quest_log()
            self.update_quest_log()  
        elif selected_item == "Emails":
            self.populate_emails()

        self.inventory_list.itemClicked.connect(self.display_item_information)
        self.is_item_clicked_connected = True


    def populate_inventory(self):
        ic("Populating inventory")
        items = self.game_manager.get_inventory_data()
        ic("Inventory items:, items")
        self.inventory_list.clear()  # Clear the list before adding new items
        for item_string in items:
            self.inventory_list.addItem(item_string)
            ic("Item added to inventory list widget:", item_string)

    def populate_fast_travel_locations(self):
        ic("Populating fast travel locations")
        locations = self.game_manager.get_fast_travel_locations_data()
        ic("Fast travel locations:", locations)
        self.inventory_list.clear()  # Clear the list before adding new items
        for location_string in locations:
            self.inventory_list.addItem(location_string)
            ic("Location added to fast travel list widget:", location_string)

    def populate_notes(self):
        ic("Populating notes")
        notes = self.game_manager.get_notes_data()
        ic("Notes:", notes)
        self.inventory_list.clear()  # Clear the list before adding new items
        for note_name in notes:
            self.inventory_list.addItem(note_name)
            ic("Note added to notes list widget:", note_name)

    def populate_quest_log(self):
        ic("Populating quest log")
        quests = self.game_manager.get_quests_data()
        ic("Quests:", quests)
        self.inventory_list.clear()  # Clear the list before adding new items
        for quest_string in quests:
            self.inventory_list.addItem(quest_string)
            ic("Quest added to quest log list widget:", quest_string)

    def populate_emails(self):
        ic("Populating emails")
        emails = self.game_manager.get_emails_data()
        ic("Emails:", emails)
        self.inventory_list.clear()  # Clear the list before adding new items
        for email_string in emails:
            item = QListWidgetItem(email_string)
            if "(Read)" in email_string:
                item.setForeground(QColor('grey'))
            else:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.inventory_list.addItem(item)

    def process_command(self):
        ic("Entered process_command", threading.get_ident())
        ic(self.command_input.text())
        command_text = self.command_input.text().strip().lower()
        self.command_input.clear()
        self.command_input.setPlaceholderText("Processing...")
        self.command_input.setEnabled(False)
        self.game_text_area.clear()

        # Create a worker instance with the GameManager and command_text
        self.worker = Worker(self.game_manager, command_text)

        # Create a QThread instance
        self.thread = QThread()

        # Move the worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect the thread's started signal to the worker's process_command slot
        self.thread.started.connect(self.worker.process_command)

        # Connect signals and slots
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Ensure display_text is called in the main thread
        self.worker.finished.connect(self.display_text_wrapped)

        # Start the thread
        self.thread.start()

    def display_text_wrapped(self, processed_content):
        # Execute this only in the main thread
        if QThread.currentThread() == QThread.currentThread().thread():
            self.display_text(processed_content)

    def display_item_information(self, item_widget):
        ic("Displaying item information")
        selected_text = item_widget.text()
        ic("Selected item text:", selected_text)

        # Determine the selected name based on the current category
        if self.current_category == "Quest Log":
            selected_name = selected_text.split(":")[0].strip()
        else:
            selected_name = selected_text.split(' (')[0].strip()

        item_details = None
        # Retrieve the appropriate item details based on the current category
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

        # Check for item details and format appropriately
        if item_details:
            if self.current_category == "Emails":
                # For emails, include sender information
                formatted_details = f"{selected_name}:\nFrom: {item_details.get('sender', 'Unknown Sender')}\n\n{item_details.get('description', 'No description available.')}"
            elif self.current_category == "Quest Log":
                # For quests, include completion status
                status = 'Completed' if item_details.get('completed', False) else 'In Progress'
                formatted_details = f"{selected_name}:\n{status}\n\n{item_details.get('description', 'No description available.')}"
            else:
                # For other categories, just display the name and description
                formatted_details = f"{selected_name}:\n\n{item_details.get('description', 'No description available.')}"
                text = convert_text_to_display(formatted_details)
                
            text = convert_text_to_display(formatted_details)                
            self.display_text(text)
        else:
            text = convert_text_to_display(f"{selected_name}:\n\nNo details available.")
            self.display_text(text)

    def display_text(self, processed_content):
        ic("display_text thread ID", threading.get_ident())
        ic(processed_content)

        # Clear the game text area and apply any necessary styling
        self.game_text_area.clear()
        self.game_text_area.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}")

        # Ensure the game_text_area can interpret HTML
        self.game_text_area.setAcceptRichText(True)

        # Set the font for the game text area
        font = self.game_text_area.font()
        font.setFamily("Consolas")
        font.setPointSize(12)
        self.game_text_area.setFont(font)

        # Remove the Markdown code block delimiters, if any
        processed_content = processed_content.replace('```html', '').replace('```', '')

        # Wrap the content in <div> tags with a style attribute for centering text
        centered_html_content = f'<div style="text-align: center;">{processed_content}</div>'

        # Split the centered HTML content into chunks
        self.chunks = self.split_into_chunks(centered_html_content)
        self.current_chunk_index = 0  # Initialize a variable to keep track of the current chunk index

        # Start displaying the chunks from the beginning
        self.display_chunk()

        # Re-enable the command input and reset placeholder text
        self.command_input.setEnabled(True)
        self.command_input.setPlaceholderText("Type a command...")
        ic("Exiting display_text", threading.get_ident())

    def display_chunk(self):
        ic("Entered display_chunk", threading.get_ident())
        if self.current_chunk_index < len(self.chunks):
            chunk = self.chunks[self.current_chunk_index]
            ic("Current chunk content:", chunk)
            centered_chunk = f'<div style="text-align: center;">{chunk}</div>'
            
            if self.current_chunk_index > 0:
                ic("Appending chunk")
                # Append the new chunk to the existing content
                current_html = self.game_text_area.toHtml()
                self.game_text_area.setHtml(current_html + centered_chunk)
            else:
                ic("Setting chunk")
                # If it's the first chunk, set it as new content
                self.game_text_area.setHtml(centered_chunk)

            # Increment the chunk index
            self.current_chunk_index += 1
            ic("Setting timer")

            if self.current_chunk_index >= len(self.chunks):
                # If this was the last chunk, reset the command input
                if self.was_command_help:
                    self.command_input.clear()
                    self.command_input.setEnabled(True)
                    self.command_input.setPlaceholderText("Type a command...")
                else:
                    self.command_input.clear()
                    self.command_input.setEnabled(True)
                    self.command_input.setPlaceholderText("Type 'Help' to start")
            else:
                # Set up the timer to call this method again after a delay
                QTimer.singleShot(750, self.display_chunk)  # 500 ms delay

    def split_into_chunks(self, html_content):
        # Split by paragraphs and unordered lists
        ic("Splitting into chunks")
        chunks = re.split(r'(</p>|</ul>)', html_content)
        ic("Chunks:", chunks)

        # Re-add the split tags to each chunk and filter out empty strings
        chunks = [chunk + split_tag for chunk, split_tag in zip(chunks[0::2], chunks[1::2]) if chunk]
        ic("Chunks after filtering:", chunks)

        return chunks


    def update_quest_log(self):
        ic("Updating quest log")
        quests = self.game_manager.get_quests_data()
        ic(quests)
        self.inventory_list.clear()
        for quest in quests:
            self.inventory_list.addItem(quest)


    def update_ui(self):
        ic("Updating UI")
        # Determine what type of data to display based on the current selection in the dropdown
        current_selection = self.drop_down_menu.currentText()
        if current_selection == "Quest Log":
            self.update_quest_log()
        elif current_selection == "Inventory":
            self.populate_inventory()

    def update_scene_display(self):
        scene_text = self.game_manager.world_builder.build_scene_text()
        ic("Updating scene display")
        ic(scene_text)
        self.display_text(scene_text)