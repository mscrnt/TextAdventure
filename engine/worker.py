# engine/worker.py

from PySide6.QtCore import QObject, Signal, Slot
from icecream import ic
import threading

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