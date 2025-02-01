from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from ui.components.menu_buttons import MenuButton
from ui.pages.daily_page import DailyPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.stats_page import StatsPage
from ui.pages.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Tracker")
        self.setMinimumSize(800, 600)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Create the stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create pages
        self.main_menu_page = self.create_main_menu()
        self.daily_page = DailyPage(self.db, self)
        self.calendar_page = CalendarPage(self.db, self)
        self.stats_page = StatsPage(self.db, self)
        self.settings_page = SettingsPage(self.db, self)
        
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
        daily_btn.clicked.connect(lambda: self.show_daily_page())
        calendar_btn.clicked.connect(lambda: self.show_calendar_page())
        stats_btn.clicked.connect(lambda: self.show_stats_page())
        settings_btn.clicked.connect(lambda: self.show_settings_page())

        return page

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_page)

    def show_daily_page(self):
        self.stacked_widget.setCurrentWidget(self.daily_page)

    def show_calendar_page(self):
        self.stacked_widget.setCurrentWidget(self.calendar_page)

    def show_stats_page(self):
        self.stacked_widget.setCurrentWidget(self.stats_page)

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)
