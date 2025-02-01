from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QLineEdit, QFrame, QPushButton, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
import webbrowser

class NoteDialog(QDialog):
    def __init__(self, existing_note="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Note")
        self.setup_ui(existing_note)
        self.setMinimumWidth(300)
        
    def setup_ui(self, existing_note):
        layout = QVBoxLayout(self)
        
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Enter your note here...")
        self.note_edit.setText(existing_note)
        layout.addWidget(self.note_edit)
        
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def get_note(self):
        return self.note_edit.toPlainText()

class ClickableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFrame(False)
        self.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #28a745;
                font-size: 14px;
            }
            QLineEdit:focus {
                background: white;
                border: 1px solid #4a90e2;
                border-radius: 4px;
            }
        """)

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        super().focusOutEvent(event)

class GameWidget(QWidget):
    game_completed = pyqtSignal(dict, str, str)  # Emits game data, score, and note
    
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.completed = game_data.get('completed', False)
        self.note = game_data.get('note', '')
        self.setup_ui()
        self.setProperty('completed', self.completed)
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left side (checkbox)
        self.checkbox = QLabel("☐" if not self.completed else "☑")
        self.checkbox.setStyleSheet("""
            QLabel {
                font-size: 24px;
                margin-right: 10px;
                padding: 5px;
            }
        """)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.mousePressEvent = self.checkbox_clicked
        layout.addWidget(self.checkbox)
        
        # Game info (middle)
        info_layout = QVBoxLayout()
        
        # Game name and score
        name_layout = QHBoxLayout()
        self.name_label = QLabel(self.game_data['game'].name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        name_layout.addWidget(self.name_label)
        
        # Only add score input if score_type exists
        if self.game_data['game'].score_type:
            self.score_input = ClickableLineEdit()
            self.score_input.setPlaceholderText("Click to add score")
            self.score_input.setText(self.game_data.get('score', ''))
            self.score_input.editingFinished.connect(self.on_score_changed)
            name_layout.addWidget(self.score_input)
        else:
            self.score_input = None
            
        name_layout.addStretch()
        
        # Note button
        self.note_btn = QPushButton("+" if not self.note else "📝")
        self.note_btn.setToolTip("Add/Edit Note")
        self.note_btn.setFixedSize(30, 30)
        self.note_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.note_btn.clicked.connect(self.show_note_dialog)
        name_layout.addWidget(self.note_btn)
        
        info_layout.addLayout(name_layout)
        
        if self.game_data['game'].description:
            description_label = QLabel(self.game_data['game'].description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet("color: #666;")
            info_layout.addWidget(description_label)
        
        layout.addLayout(info_layout)
        
        self.setStyleSheet("""
            GameWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            GameWidget:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Make the widget clickable for URL
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Only open URL if it exists
            if self.game_data['game'].url:
                webbrowser.open(self.game_data['game'].url)

    def checkbox_clicked(self, event):
        self.toggle_completion()

    def toggle_completion(self):
        self.completed = not self.completed
        self.checkbox.setText("☑" if self.completed else "☐")
        self.setProperty('completed', self.completed)
        self.style().unpolish(self)
        self.style().polish(self)
        self.emit_update()

    def on_score_changed(self):
        self.emit_update()

    def show_note_dialog(self):
        dialog = NoteDialog(self.note, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.note = dialog.get_note()
            self.note_btn.setText("📝" if self.note else "+")
            self.emit_update()

    def update_appearance(self):
        self.checkbox.setText("☑" if self.completed else "☐")
        self.setProperty('completed', self.completed)
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Update note button appearance
        self.note_btn.setText("📝" if self.note else "+")
        
        # Update score if it exists
        if self.score_input and self.game_data.get('score'):
            self.score_input.setText(self.game_data['score'])

    def emit_update(self):
        score = self.score_input.text() if self.score_input else ""
        self.game_completed.emit(self.game_data, score, self.note)
