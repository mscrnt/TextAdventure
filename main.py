import sys
from PySide6.QtWidgets import QApplication
import argparse
from debug_config import DebugConfig
from gui.main_window import MainWindow
from utilities import delete_working_files

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

    app.aboutToQuit.connect(delete_working_files)

    # Initialize MainWindow without all components
    main_window = MainWindow(use_ai)

    # Show the main window
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
