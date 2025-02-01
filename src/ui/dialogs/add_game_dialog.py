from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QTimeEdit, QFormLayout
)
from datetime import datetime
from models.game import Game

class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Game")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Create input fields
        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.description_input = QTextEdit()
        self.score_type_input = QLineEdit()
        self.reminder_time = QTimeEdit()
        self.reminder_time.setDisplayFormat("HH:mm")

        # Add fields to form layout
        form_layout.addRow("Game Name:", self.name_input)
        form_layout.addRow("Game URL:", self.url_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Score Type:", self.score_type_input)
        form_layout.addRow("Reminder Time:", self.reminder_time)

        # Add form to main layout
        layout.addLayout(form_layout)

        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_game_data(self) -> Game:
        return Game(
            id=None,
            name=self.name_input.text(),
            url=self.url_input.text(),
            description=self.description_input.toPlainText(),
            score_type=self.score_type_input.text(),
            reminder_time=self.reminder_time.time().toString("HH:mm"),
            created_at=datetime.now()
        )
