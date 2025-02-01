from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class MenuButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a6;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Tracker")
        self.setMinimumSize(800, 600)
        
        # Create the stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create pages
        self.main_menu_page = self.create_main_menu()
        self.daily_page = self.create_page("Daily Games")
        self.calendar_page = self.create_page("Calendar")
        self.stats_page = self.create_page("Statistics")
        self.settings_page = self.create_page("Settings")
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_menu_page)
        self.stacked_widget.addWidget(self.daily_page)
        self.stacked_widget.addWidget(self.calendar_page)
        self.stacked_widget.addWidget(self.stats_page)
        self.stacked_widget.addWidget(self.settings_page)

    def create_main_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Game Tracker")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)

        # Main buttons
        daily_btn = MenuButton("Daily Games")
        calendar_btn = MenuButton("Calendar")
        stats_btn = MenuButton("Statistics")
        
        # Settings button
        settings_btn = QPushButton()
        settings_btn.setFixedSize(50, 50)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                border: none;
                border-radius: 25px;
                color: white;
                font-size: 18px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        settings_btn.setText("⚙")

        # Add buttons to layout
        layout.addWidget(daily_btn)
        layout.addWidget(calendar_btn)
        layout.addWidget(stats_btn)
        
        # Center settings button
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()
        settings_layout.addWidget(settings_btn)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
        
        layout.addStretch()

        # Connect buttons to their respective pages
        daily_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.daily_page))
        calendar_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.calendar_page))
        stats_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.stats_page))
        settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))

        return page

    def create_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        
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
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu_page))
        
        header_layout.addWidget(back_btn)
        
        page_title = QLabel(title)
        page_title.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)
        
        # Placeholder content
        content = QLabel(f"{title} Content Coming Soon")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
