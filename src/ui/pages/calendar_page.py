from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

class CalendarPage(QWidget):
    def __init__(self, db_manager, main_window):
        super().__init__()
        self.db = db_manager
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with back button and title
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("←")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        header_layout.addWidget(back_btn)
        
        title = QLabel("Calendar")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)
        
        # Placeholder content
        content = QLabel("Calendar Content Coming Soon")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)

    def go_back(self):
        self.main_window.show_main_menu()
