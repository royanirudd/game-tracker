from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QScrollArea, QDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from ui.components.game_widget import GameWidget
from ui.dialogs.add_game_dialog import AddGameDialog

class DailyPage(QWidget):
    def __init__(self, db_manager, main_window):
        super().__init__()
        self.db = db_manager
        self.main_window = main_window
        self.setup_ui()
        self.load_daily_games()

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
        
        title = QLabel("Daily Games")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Progress indicator
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-size: 16px;
                margin-left: 20px;
            }
        """)
        header_layout.addWidget(self.progress_label)
        header_layout.addStretch()
        
        add_game_btn = QPushButton("Add Game")
        add_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
            }
        """)
        add_game_btn.clicked.connect(self.show_add_game_dialog)
        header_layout.addWidget(add_game_btn)
        
        layout.addLayout(header_layout)
        
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)
        
        # Create a scroll area for games
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Create a widget to hold the games list
        self.games_widget = QWidget()
        self.games_container = QVBoxLayout(self.games_widget)
        self.games_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.games_widget)
        layout.addWidget(scroll_area)

    def go_back(self):
        self.main_window.show_main_menu()

    def show_add_game_dialog(self):
        dialog = AddGameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            game = dialog.get_game_data()
            self.db.add_game(game)
            self.load_daily_games()

    def load_daily_games(self):
        # Clear existing games from container
        while self.games_container.count():
            child = self.games_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    item = child.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

        # Get today's progress for all games
        today_progress = self.db.get_daily_progress(datetime.now().date())
        
        # Track completed games
        completed_count = 0
        total_count = len(today_progress)

        # Add games to container
        for progress in today_progress:
            game_widget = GameWidget(progress)
            game_widget.game_completed.connect(self.handle_game_completion)
            
            # If game was already completed today
            if progress.get('completed'):
                game_widget.completed = True
                game_widget.update_appearance()
                completed_count += 1
            
            self.games_container.addWidget(game_widget)
        
        # Update progress label
        self.update_progress_label(completed_count, total_count)

    def handle_game_completion(self, game_data, score, note):
        # Get the game widget that emitted the signal
        game_widget = self.sender()
        
        # Update database with completion status, score, and note
        self.db.update_game_progress(
            game_data['game'].id,
            datetime.now().date(),
            completed=game_widget.completed,
            score=score,
            note=note
        )
        
        # Update progress label
        completed_count = sum(1 for i in range(self.games_container.count())
                            if self.games_container.itemAt(i).widget().completed)
        total_count = self.games_container.count()
        self.update_progress_label(completed_count, total_count)

    def update_progress_label(self, completed, total):
        if total > 0:
            percentage = (completed / total) * 100
            self.progress_label.setText(f"Progress: {completed}/{total} ({percentage:.0f}%)")
        else:
            self.progress_label.setText("No games added")
