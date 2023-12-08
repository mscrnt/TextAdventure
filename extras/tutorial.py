from PySide6.QtCore import QTimer, Signal, QObject
from gui.game_ui import GameUI
from utilities import convert_text_to_display, normalize_name
from icecream import ic

class Tutorial(QObject):
    step_completed = Signal()

    def __init__(self, game_ui: GameUI, game_manager):
        super().__init__()
        self.game_ui = game_ui
        self.game_manager = game_manager
        self.game_ui.note_selected_signal.connect(self.check_notes_selection)
        self.game_ui.quest_selected_signal.connect(self.check_quest_log_selection)
        self.game_ui.email_selected_signal.connect(self.check_emails_selection)
        self.game_ui.special_command_signal.connect(self.check_text_input)
        self.current_step = 0
        self.steps = [
            ("intro", "Welcome to Odyssey. \n  In this tutorial will guide you through the basics of the game. \n It's pretty short, so don't worrry."),
            ("inventory", "Please click on 'Excalibur' in your inventory to begin."),
            ("notes", "When you click on an inventory item, It will show you the name and a short discription of the item \n \n Next up are Notes. Use the dropdown to select notes. Click on 'Thief's Confession' to continue."),
            ("quest log", "When you find note, they will appear in that section. They usually have hints to tell you what to do. Similar to your inventory, it will show you the name of the note and the contents. \n \n Now, let's move  onto the quest log. Use the dropdown to select the quest log. Click on 'Read Email' to continue."),
            ("emails", "As you complete the objectives, they will be marked as complete. \n\n Now to move on to Emails. Use the dropdown to select emails, then select an email to read."),
            ("help", "When you receive an email, they will appear in your inbox. \n \n Now, let's type 'help' in the command input box bellow to continue."),
            ("talk to Athena", "Finally, type 'talk to Athena' in the text input to continue."),
        ]
        self.step_completed.connect(self.next_step)
        ic("Tutorial initialized")

    def start(self):
        ic("Tutorial starting")
        self.game_ui.drop_down_menu.setCurrentIndex(self.game_ui.drop_down_menu.findText("Inventory"))
        self.game_ui.update_ui_from_dropdown(self.game_ui.drop_down_menu.currentIndex())
        self.display_instruction(self.steps[self.current_step][1])
        ic(f"Current step: {self.steps[self.current_step][0]}")
        QTimer.singleShot(3000, self.next_step)  # Wait 10 seconds before moving to the next step

    # In the next_step method, connect the step_completed signal to the next step only after a user interaction.
    def next_step(self):
        ic("Proceeding to the next tutorial step")
        ic(f"Current step: {self.steps[self.current_step][0]}")
        if self.current_step < len(self.steps) - 1:
            ic("Connecting step_completed signal to next_step")
            self.current_step += 1
            ic(f"Current step: {self.steps[self.current_step][0]}")
            step_name, instruction = self.steps[self.current_step]
            ic(f"Current step: {step_name}")
            ic(f"Current instruction: {instruction}")
            ic("Connecting step_completed signal to next_step")
            self.display_instruction(instruction)
            ic(f"Current step: {step_name}")
            self.set_up_current_step(step_name)
        else:
            ic("Tutorial completed")
            self.end_tutorial()

    def set_up_current_step(self, step_name):
        if step_name == "inventory":
            self.game_ui.inventory_list.itemClicked.connect(self.check_inventory_selection)
        elif step_name == "notes":
            self.game_ui.inventory_list.itemClicked.connect(self.check_notes_selection)
            ic("Connected to check_notes_selection")
        elif step_name == "quest log":
            self.game_ui.inventory_list.itemClicked.connect(self.check_quest_log_selection)
        elif step_name == "emails":
            self.game_ui.inventory_list.itemClicked.connect(self.check_emails_selection)
        elif step_name in ["talk to Athena", "help"]:
            # No automatic filling of the command_input
            self.game_ui.command_input.returnPressed.connect(self.check_text_input)
        else:
            ic(f"Unknown step name: {step_name}")


        
    def display_instruction(self, text):
        ic(f"Displaying instruction: {text}")
        self.game_ui.display_text(convert_text_to_display(text))

    def end_tutorial(self):
        ic("Tutorial completed")
        self.display_instruction("Tutorial completed! You're now ready to explore Exitium and all its tales.")
        self.game_manager.quest_tracker.check_all_quests()
        self.game_ui.update_quest_log()

    def check_notes_selection(self, item):
        ic("Checking notes selection")
        normalized_item_text = normalize_name(item.text())
        normalized_target_text = normalize_name("Thief's Confession")
        ic(f'Normalized item text: {normalized_item_text}')
        ic(f'Normalized target text: {normalized_target_text}')

        if normalized_item_text == normalized_target_text:
            ic("Correct note selected")
            # Disconnect the handle_note_selection method
            self.game_ui.inventory_list.itemClicked.disconnect(self.game_ui.handle_note_selection)
            QTimer.singleShot(5000, self.next_step)
        else:
            ic("Wrong note selected")
            self.display_instruction("Please select the 'Thief's Confession' note to proceed.")

    def check_quest_log_selection(self, item):
        ic("Checking quest log selection")
        if "Read Email" in item.text():
            ic("Correct quest selected")
            # Disconnect the handle_quest_selection method
            self.game_ui.inventory_list.itemClicked.disconnect(self.game_ui.handle_quest_selection)
            QTimer.singleShot(5000, self.next_step)  # Proceed to the next step after a 5-second delay
        else:
            ic("Wrong quest selected")
            self.display_instruction("Please select the 'Read Email' quest to proceed.")

    def check_emails_selection(self, item):
        ic("Checking email selection")

        # if an email is selected
        if item:
            ic("Email selected")
            # Disconnect the handle_email_selection method
            self.game_ui.inventory_list.itemClicked.disconnect(self.game_ui.handle_email_selection)
            QTimer.singleShot(5000, self.next_step)
        else:
            ic("No email selected")
            self.display_instruction("Please select an email to proceed.")


    # Example method with a QTimer to proceed
    def check_inventory_selection(self, item):
        ic("Checking inventory selection")
        if "Excalibur" in item.text():
            ic("Correct item selected")
            self.game_ui.inventory_list.itemClicked.disconnect(self.check_inventory_selection)
            QTimer.singleShot(5000, self.next_step)  # Proceed to the next step after a 5-second delay
        else:
            ic("Wrong item selected")
            self.display_instruction("Please select the 'Excalibur' item to proceed.")
            
    def check_text_input(self, command_text):
        ic("Checking text input")
        ic(f"Input text: {command_text}")

        if command_text == "talk to athena":
            ic("Correct text input: talk to Athena")
            self.proceed_with_next_step()
        elif command_text == "help":
            ic("Correct text input: help")
            self.proceed_with_next_step()
        else:
            ic("Wrong text input")
            self.display_instruction("Please type 'talk to Athena' or 'help' in the text input to proceed.")
            self.game_ui.command_input.setText("")

    def proceed_with_next_step(self):
        ic("Proceeding with next step")
        self.game_ui.command_input.returnPressed.disconnect(self.check_text_input)
        QTimer.singleShot(20000, self.next_step)
