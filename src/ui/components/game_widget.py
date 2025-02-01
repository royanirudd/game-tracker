from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class GameWidget(QWidget):
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Game info
        info_layout = QVBoxLayout()
        name_label = QLabel(self.game_data['game'].name)
        name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        info_layout.addWidget(name_label)
        
        description_label = QLabel(self.game_data['game'].description)
        description_label.setWordWrap(True)
        info_layout.addWidget(description_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Game controls
        controls_layout = QVBoxLayout()
        play_btn = QPushButton("Play")
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px 15px;
            }
        """)
        controls_layout.addWidget(play_btn)
        
        layout.addLayout(controls_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
