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
        self.game_ui = GameUI()

        self.title_timer.timeout.connect(self.scroll_title)
        self.intro_timer.timeout.connect(lambda: self.scroll_text())

    def init_ui(self):
        self.intro_title_label = QLabel("Welcome to Odyssey...", self)
        self.intro_title_label.setFont(QFont("Courier New", 24, QFont.Bold))
        # Set alignment to center within the label
        self.intro_title_label.setAlignment(Qt.AlignCenter)
        # Set the palette for the label
        self.intro_title_label.setPalette(self.get_palette_for_crawl())
        # Set label geometry: x, y, width, height
        self.intro_title_label.setGeometry(0, 0, self.width(), 100)
        # Center label within the parent widget
        self.intro_title_label.move(
            (self.width() - self.intro_title_label.width()) // 2,
            (self.height() - self.intro_title_label.height()) // 2
        )
        self.intro_title_label.show()

        QTimer.singleShot(3000, self.start_intro_crawl)

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
            # Center label within the parent widget as it moves
            self.intro_title_label.move(
                (self.width() - self.intro_title_label.width()) // 2,
                new_y
            )

    def animate_intro_text(self):
        intro_text_data = load_text('intro_text')
        intro_text = intro_text_data.get('opening_crawl', 'Default opening crawl text if not found.')
        self.intro_text_label = QLabel(intro_text, self)
        self.intro_text_label.setFont(QFont("Courier New", 14))
        self.intro_text_label.setAlignment(Qt.AlignCenter)
        self.intro_text_label.setWordWrap(True)
        self.intro_text_label.setPalette(self.get_palette_for_crawl())
        self.intro_text_label.setGeometry(0, self.height(), self.width(), self.height()*2)
        self.intro_text_label.show()

        self.intro_timer.start(50)

    def scroll_text(self):
        current_y = self.intro_text_label.y()
        new_y = current_y - 2
        
        if new_y < -self.intro_text_label.height():
            self.intro_timer.stop()
            self.intro_text_label.deleteLater()
            self.load_game_ui()
        else:
            self.intro_text_label.move(self.intro_text_label.x(), new_y)

    def start_intro_crawl(self):
        self.intro_title_label.deleteLater()
        self.animate_intro_text()
