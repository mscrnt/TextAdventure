import sys
from PySide6.QtWidgets import QApplication
import argparse
from debug_config import DebugConfig
from gui.main_window import MainWindow
from gui.game_ui import GameUI
from engine.game_manager import GameManager
from engine.world_builder import WorldBuilder
from engine.player_sheet import PlayerSheet
from engine.quest_tracker import QuestTracker

# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
parser.add_argument('--use-ai', action='store_true', help='Enable AI assist feature')
args = parser.parse_args()
debug_on = args.debug
use_ai = args.use_ai

def main():
    DebugConfig.set_level('DEBUG' if debug_on else 'ERROR')

    app = QApplication(sys.argv)

    # Initialize components 
    player_sheet = PlayerSheet("Player1")
    quest_tracker = QuestTracker() 
    world_builder = WorldBuilder({}, use_ai)  
    game_manager = GameManager()  

    # Initialize GameUI
    game_ui = GameUI(game_manager, world_builder)
    game_ui.complete_initialization()

    # Initialize MainWindow with all components
    main_window = MainWindow(game_manager, world_builder, player_sheet, quest_tracker, game_ui)

    # Set up the game manager and UI relationships
    game_manager.set_ui(game_ui)
    game_ui.set_game_manager(game_manager)

    # Show the main window
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
