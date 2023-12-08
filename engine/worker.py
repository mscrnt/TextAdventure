# engine/worker.py

from PySide6.QtCore import QObject, Signal, Slot, QTimer
from icecream import ic
import threading
from utilities import convert_text_to_display

class Worker(QObject):
    # Signal to emit when processing is done
    finished = Signal(str)

    def __init__(self, game_manager, command_text):
        super().__init__()
        self.game_manager = game_manager
        self.command_text = command_text
        ic(f"Worker initialized with command: {command_text}")

    @Slot()
    def process_command(self):
        ic("Entered Worker process_command", threading.get_ident())

        if not self.game_manager:
            raise ValueError("Worker requires a GameManager instance.")
        
        response = self.game_manager.world_builder.incoming_command(self.command_text)
        ic("Response from WorldBuilder: ", response)
        
        # Emit the signal
        self.finished.emit(response)


class TriggerWorker(QObject):
    # Signal to emit when trigger processing is done
    triggerProcessed = Signal(str)

    def __init__(self, game_manager, trigger):
        super().__init__()
        self.game_manager = game_manager
        self.trigger = trigger
        ic("TriggerWorker initialized with trigger:", trigger)

    @Slot()
    def process_trigger(self):
        # First, process any dialog related to the trigger
        if 'dialog' in self.trigger:
            dialog = self.trigger['dialog']
            self.emit_dialog(dialog)

        # Then, after a delay, process the fast travel addition
        QTimer.singleShot(5000, self.process_fast_travel_trigger)  # 5000 ms = 5 seconds

    def emit_dialog(self, dialog):
        # Convert and emit the dialog text
        response = convert_text_to_display(dialog)
        self.triggerProcessed.emit(response)

    def process_fast_travel_trigger(self):
        # Check and add the fast travel location
        if self.trigger['type'] == 'fast travel':
            fast_travel_location = {
                'name': self.trigger['name'],
                'description': self.trigger['description'],
                'world_name': self.trigger['world'],
                'location': self.trigger['location']
            }
            # Call the method to add the fast travel location to the player's data
            self.game_manager.player_sheet.add_fast_travel_location(fast_travel_location)
            ic(f"Fast travel location added: {self.trigger['name']}")

            # Emit the response to update the UI accordingly
            response = f"Fast travel location added: {self.trigger['name']}"
            self.triggerProcessed.emit(response)
