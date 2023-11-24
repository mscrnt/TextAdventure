from utilities import load_text
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import QTimer, Qt, Signal
from engine.game_manager import GameManager
from gui.game_ui import GameUI

class IntroAnimation(QWidget):
    animationComplete = Signal()

    def __init__(self, parent=None):
        super(IntroAnimation, self).__init__(parent)
        self.init_ui()
        
        self.title_timer = QTimer(self)
        self.intro_timer = QTimer(self)
        
        # Connect signals to slots
        self.title_timer.timeout.connect(self.show_intro_text)
        self.intro_timer.timeout.connect(self.scroll_text)

        # Start the title display
        self.title_timer.start(2000)  # Adjust time as needed

        # Enable mouse click event to skip the intro
        self.setMouseTracking(True)  # Make sure the widget tracks mouse movement
        self.mousePressEvent = self.skip_intro

    def init_ui(self):
        # Set geometry for the widget to match the parent's size
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        # Create the title label and center it
        self.intro_title_label = QLabel("Welcome to Odyssey...", self)
        self.intro_title_label.setFont(QFont("Courier New", 24, QFont.Bold))
        self.intro_title_label.setAlignment(Qt.AlignCenter)
        self.intro_title_label.setPalette(self.get_palette_for_crawl())
        self.intro_title_label.setGeometry(0, (self.height() - 100) / 2, self.width(), 100)
        self.intro_title_label.show()


    def get_palette_for_crawl(self):
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(255, 255, 0))  # Example color
        return palette

    def scroll_title(self):
        current_y = self.intro_title_label.y()
        new_y = current_y - 2  # Adjust the speed as necessary
        
        if new_y < -self.intro_title_label.height():
            self.title_timer.stop()
            self.intro_title_label.deleteLater()
            self.animate_intro_text()
        else:
            self.intro_title_label.move(self.intro_title_label.x(), new_y)

    def load_game_ui(self):
        self.animationComplete.emit()

    def animate_intro_text(self):
        intro_text_data = load_text('intro_text')
        intro_text = intro_text_data.get('opening_crawl', 'Default opening crawl text if not found.')
        self.intro_text_label = QLabel(intro_text, self)
        self.intro_text_label.setFont(QFont("Courier New", 14))
        self.intro_text_label.setAlignment(Qt.AlignCenter)
        self.intro_text_label.setWordWrap(True)
        self.intro_text_label.setPalette(self.get_palette_for_crawl())
        self.intro_text_label.setGeometry(0, self.height(), self.width(), self.height()*.5)
        self.intro_text_label.show()
        self.create_skip_label()  # Recreate the skip label for the intro text

        self.intro_timer.start(30)

    def scroll_text(self):
        # Use a more substantial scroll amount for smoother scrolling
        scroll_amount = 1
        new_y = self.intro_text_label.y() - scroll_amount

        # Check if the new_y position is less than the negative height of the label
        if new_y < -self.intro_text_label.height():
            self.intro_timer.stop()
            self.intro_text_label.deleteLater()
            self.load_game_ui()
        else:
            self.intro_text_label.move(self.intro_text_label.x(), new_y)


    def start_intro_crawl(self):
        self.intro_title_label.deleteLater()
        self.animate_intro_text()

    def show_intro_text(self):
        # This function replaces the title with the scrolling intro text
        self.title_timer.stop()
        self.intro_title_label.deleteLater()  # Remove the title label
        self.animate_intro_text()

    def skip_intro(self, event):

        self.intro_timer.stop()

        if hasattr(self, 'intro_text_label') and self.intro_text_label.isVisible():
            self.intro_text_label.deleteLater()
        self.animationComplete.emit()  # Emit the signal to indicate completion

    def create_skip_label(self):
        self.skip_label = QLabel("Click to Skip", self)
        self.skip_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.skip_label.setStyleSheet("color: rgba(255, 255, 255, 150);")  # Semi-transparent white
        self.skip_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.skip_label.setGeometry(self.width() - 120, self.height() - 30, 110, 20)
        self.skip_label.show()
        self.skip_label.raise_()