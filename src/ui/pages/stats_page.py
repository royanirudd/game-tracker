from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import pyqtSignal

class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def __init__(self, parent=None, game_data=None):
        super().__init__(parent)
        self.game_data = game_data

    def mousePressEvent(self, a0: 'QMouseEvent') -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(a0)

class GameDetailWidget(QWidget):
    def __init__(self, game_data, db, parent_page):
        super().__init__()
        self.game_data = game_data
        self.db = db
        self.parent_page = parent_page
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

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
        back_btn.clicked.connect(self.go_back)
        
        header_layout.addWidget(back_btn)
        
        title = QLabel(self.game_data[1])  # index 1 is name
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)

        # Times completed
        completed_label = QLabel("Times Completed")
        completed_value = QLabel(str(self.game_data[3]))  # index 3 is times_completed
        completed_label.setStyleSheet("color: #666; font-size: 16px;")
        completed_value.setStyleSheet("font-size: 20px; font-weight: bold;")
        stats_grid.addWidget(completed_label, 0, 0)
        stats_grid.addWidget(completed_value, 1, 0)

        # Best score (if applicable)
        if self.game_data[2] and self.game_data[2].isdigit():  # index 2 is score_type
            if self.game_data[6]:  # index 6 is best_score
                best_label = QLabel("Best Score")
                best_value = QLabel(f"{self.game_data[6]}/{self.game_data[2]}")
                best_date = self.game_data[7]  # index 7 is best_score_date
                if best_date:
                    best_value.setToolTip(f"Achieved on {best_date}")
                best_label.setStyleSheet("color: #666; font-size: 16px;")
                best_value.setStyleSheet("font-size: 20px; font-weight: bold; color: #28a745;")
                stats_grid.addWidget(best_label, 0, 1)
                stats_grid.addWidget(best_value, 1, 1)

        content_layout.addLayout(stats_grid)

        # Graphs section
        graphs_layout = QHBoxLayout()
        
        # Score line graph (if applicable)
        if self.game_data[2] and self.game_data[2].isdigit():
            current_date = datetime.now()
            scores_data = self.db.get_monthly_scores(
                self.game_data[0],  # game_id
                current_date.year,
                current_date.month
            )
            
            if scores_data:
                fig = Figure(figsize=(6, 4))
                ax = fig.add_subplot(111)
                
                dates = [row[0] for row in scores_data]
                scores = [int(row[1]) for row in scores_data]
                
                ax.plot(dates, scores, 'b-o')
                ax.set_ylim(0, int(self.game_data[2]))
                ax.set_xlabel('Date')
                ax.set_ylabel('Score')
                ax.set_title('Monthly Scores')
                
                canvas = FigureCanvas(fig)
                graphs_layout.addWidget(canvas)

        # Completion pie chart
        completion_data = self.db.get_completion_percentage(self.game_data[0])
        if completion_data:
            completed, total = completion_data
            if total > 0:
                fig = Figure(figsize=(4, 4))
                ax = fig.add_subplot(111)
                
                labels = ['Completed', 'Missed']
                sizes = [completed, total - completed]
                colors = ['#28a745', '#dc3545']
                
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
                ax.set_title('Completion Rate')
                
                canvas = FigureCanvas(fig)
                graphs_layout.addWidget(canvas)

        content_layout.addLayout(graphs_layout)

        # History section
        history_data = self.db.get_game_history(self.game_data[0])
        if history_data:
            history_label = QLabel("Game History")
            history_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
            content_layout.addWidget(history_label)

            for entry in history_data:
                entry_widget = QFrame()
                entry_widget.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                entry_layout = QVBoxLayout(entry_widget)
                
                date_label = QLabel(str(entry[0]))
                date_label.setStyleSheet("font-weight: bold;")
                entry_layout.addWidget(date_label)
                
                if entry[2]:  # Score
                    score_label = QLabel(f"Score: {entry[2]}")
                    entry_layout.addWidget(score_label)
                
                if entry[3]:  # Note
                    note_label = QLabel(f"Note: {entry[3]}")
                    note_label.setWordWrap(True)
                    entry_layout.addWidget(note_label)
                
                content_layout.addWidget(entry_widget)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def go_back(self):
        self.parent_page.stacked_widget.setCurrentWidget(self.parent_page.main_stats)

class StatsPage(QWidget):
    def __init__(self, db_manager, main_window):
        super().__init__()
        self.db = db_manager
        self.main_window = main_window
        self.setup_ui()
        self.current_detail_widget = None  # Add this to track current detail widget

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create stacked widget to handle main stats and detail views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create main stats widget
        self.main_stats = QWidget()
        self.setup_main_stats()  # This method contains all the stats UI setup
        
        # Add main stats to stacked widget
        self.stacked_widget.addWidget(self.main_stats)

    def show_game_details(self, game_data):
        # Remove previous detail widget if it exists
        if self.current_detail_widget:
            self.stacked_widget.removeWidget(self.current_detail_widget)
        
        # Create new detail widget
        self.current_detail_widget = GameDetailWidget(game_data, self.db, self)
        self.stacked_widget.addWidget(self.current_detail_widget)
        self.stacked_widget.setCurrentWidget(self.current_detail_widget)

    def go_back(self):
        if self.stacked_widget.currentWidget() == self.main_stats:
            self.main_window.show_main_menu()
        else:
            self.stacked_widget.setCurrentWidget(self.main_stats)

    def setup_main_stats(self):
        layout = QVBoxLayout(self.main_stats)
    
        # Add header with back button
        header_layout = self.create_header()
        layout.addLayout(header_layout) 

        # Overall Stats Section
        overall_stats = QFrame()
        overall_stats.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        overall_layout = QVBoxLayout(overall_stats)
        
        # Overall Stats Title
        overall_title = QLabel("Overall Statistics")
        overall_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        overall_layout.addWidget(overall_title)
        
        # Streaks Grid
        streaks_grid = QGridLayout()
        
        # Current Streak
        current_streak = self.db.get_current_streak()
        current_streak_label = QLabel("Current Streak")
        current_streak_value = QLabel(f"{current_streak} days")
        current_streak_label.setStyleSheet("color: #666;")
        current_streak_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #28a745;")
        
        # Longest Streak
        longest_streak = self.db.get_longest_streak()
        longest_streak_label = QLabel("Longest Streak")
        longest_streak_value = QLabel(f"{longest_streak} days")
        longest_streak_label.setStyleSheet("color: #666;")
        longest_streak_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #4a90e2;")
        
        streaks_grid.addWidget(current_streak_label, 0, 0)
        streaks_grid.addWidget(current_streak_value, 1, 0)
        streaks_grid.addWidget(longest_streak_label, 0, 1)
        streaks_grid.addWidget(longest_streak_value, 1, 1)
        
        overall_layout.addLayout(streaks_grid)
        layout.addWidget(overall_stats)
        
        # Games Stats Section
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        games_widget = QWidget()
        games_layout = QVBoxLayout(games_widget)
        games_layout.setSpacing(15)
        
        games_stats = self.db.get_game_stats()
        
        for game in games_stats:
            game_widget = ClickableFrame(self, game)
            game_widget.clicked.connect(lambda g=game: self.show_game_details(g))
            
            game_widget.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                }
                QFrame:hover {
                    background-color: #e9ecef;
                }
            """)
            game_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            
            game_layout = QVBoxLayout(game_widget)
            
            # Game Name
            name_label = QLabel(game[1])
            name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            game_layout.addWidget(name_label)
            
            # Stats Grid
            stats_grid = QGridLayout()
            stats_grid.setSpacing(10)
            
            # Times Completed - simplified styling
            completed_label = QLabel("Times Completed")
            completed_value = QLabel(str(game[3]))
            completed_label.setStyleSheet("color: #666;")
            completed_value.setStyleSheet("font-weight: bold;")
            stats_grid.addWidget(completed_label, 0, 0)
            stats_grid.addWidget(completed_value, 1, 0)
            
            # Score stats if applicable - simplified styling
            if game[2] and game[2].isdigit():
                if game[5]:
                    avg_score = round(game[5], 2)
                    avg_label = QLabel("Average Score")
                    avg_value = QLabel(f"{avg_score}/{game[2]}")
                    avg_label.setStyleSheet("color: #666;")
                    avg_value.setStyleSheet("font-weight: bold;")
                    stats_grid.addWidget(avg_label, 0, 1)
                    stats_grid.addWidget(avg_value, 1, 1)
                
                if game[6]:
                    best_label = QLabel("Best Score")
                    best_value = QLabel(f"{game[6]}/{game[2]}")
                    best_date = game[7]
                    if best_date:
                        best_value.setToolTip(f"Achieved on {best_date}")
                    best_label.setStyleSheet("color: #666;")
                    best_value.setStyleSheet("font-weight: bold; color: #28a745;")
                    stats_grid.addWidget(best_label, 0, 2)
                    stats_grid.addWidget(best_value, 1, 2)
            
            game_layout.addLayout(stats_grid)
            games_layout.addWidget(game_widget)
        
        games_layout.addStretch()
        scroll.setWidget(games_widget)
        layout.addWidget(scroll)

    def create_header(self):
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
        back_btn.clicked.connect(self.go_back)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        
        return header_layout
