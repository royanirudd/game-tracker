from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCalendarWidget, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QTextCharFormat
from datetime import datetime
from ui.components.game_widget import GameWidget

class CalendarPage(QWidget):
    def __init__(self, db_manager, main_window):
        super().__init__()
        self.db = db_manager
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
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
        back_btn.clicked.connect(self.main_window.show_main_menu)
        header_layout.addWidget(back_btn)
        
        title = QLabel("Calendar")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Create Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
            QCalendarWidget QToolButton {
                color: #4a90e2;
                background-color: white;
                border: none;
            }
            QCalendarWidget QMenu {
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        self.calendar.clicked.connect(self.date_selected)
        layout.addWidget(self.calendar)
        
        # Scroll area for daily games
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.daily_games_widget = QWidget()
        self.daily_games_layout = QVBoxLayout(self.daily_games_widget)
        self.daily_games_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.daily_games_widget)
        layout.addWidget(self.scroll_area)
        
        # Update calendar data for current month
        self.update_calendar_data()
    
    def update_calendar_data(self):
        current_date = self.calendar.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        # Get completion stats for the month
        stats = self.db.get_month_completion_stats(year, month)
        
        # Create format for each day based on completion rate
        for date_str, day_stats in stats.items():
            date = QDate.fromString(date_str, Qt.DateFormat.ISODate)
            fmt = QTextCharFormat()
            
            if day_stats['total'] > 0:
                completion_rate = day_stats['completed'] / day_stats['total']
                
                # Create color gradient from red to green
                if completion_rate == 0:
                    color = QColor(255, 200, 200)  # Light red
                elif completion_rate == 1:
                    color = QColor(200, 255, 200)  # Light green
                else:
                    # Interpolate between red and green
                    red = int(255 * (1 - completion_rate))
                    green = int(255 * completion_rate)
                    color = QColor(red, green, 200)
                
                fmt.setBackground(color)
                self.calendar.setDateTextFormat(date, fmt)
    
    # In calendar_page.py

    def date_selected(self, date):
        # Clear existing games
        while self.daily_games_layout.count():
            child = self.daily_games_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get games for selected date
        date_str = date.toString(Qt.DateFormat.ISODate)
        games = self.db.get_day_games(date_str)
        
        if not games:
            no_games_label = QLabel("No games tracked on this date")
            no_games_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_games_label.setStyleSheet("color: #666; padding: 20px;")
            self.daily_games_layout.addWidget(no_games_label)
            return
        
        # Add date header
        date_header = QLabel(date.toString("MMMM d, yyyy"))
        date_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.daily_games_layout.addWidget(date_header)
        
        # Add games
        for game_data in games:
            # Create the proper game data structure
            formatted_game_data = {
                'game': {
                    'name': game_data['name'],
                    'url': game_data['url'],
                    'description': game_data['description'],
                    'score_type': game_data['score_type']
                },
                'completed': game_data.get('completed', False),
                'score': game_data.get('score', ''),
                'note': game_data.get('note', '')
            }
            
            # print("Raw game data:", game_data)
            game_widget = GameWidget(formatted_game_data, mode="calendar")  # Add mode parameter
            self.daily_games_layout.addWidget(game_widget) 
            
