# main.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt 
from gui.main_window import MainWindow
from icecream import ic
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_on = args.debug


def main():
    """
    This function initializes the main application and sets up the debug mode and dark theme palette.

    Args:
        None

    Returns:
        None
    """
    if not debug_on:
        ic.disable()
    else:
        ic.enable()
        ic.configureOutput(includeContext=True)
        ic.configureOutput(prefix='DEBUG - ')
        ic.configureOutput(includeContext=True, prefix='DEBUG - ')
        ic.configureOutput(includeContext=True, prefix='DEBUG - ', outputFunction=print)

    app = QApplication(sys.argv)

    # Set the palette for a dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(35, 35, 35))  
    palette.setColor(QPalette.ButtonText, Qt.white)  
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(75, 110, 175)) 
    palette.setColor(QPalette.HighlightedText, Qt.white)

    app.setPalette(palette)


    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

