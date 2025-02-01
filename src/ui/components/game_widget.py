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
    game_completed = pyqtSignal(dict, str, str)
    
    def __init__(self, game_data, mode="daily", parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.mode = mode  # Store the mode
        self.completed = game_data.get('completed', False)
        self.note = game_data.get('note', '')
        self.score_input = None
        self.note_btn = None
        
        # Check if game is a dict or Game object
        self.game = game_data.get('game')
        if isinstance(self.game, dict):
            self.name = self.game['name']
            self.url = self.game['url']
            self.description = self.game['description']
            self.score_type = self.game['score_type']
        else:
            self.name = self.game.name
            self.url = self.game.url
            self.description = self.game.description
            self.score_type = self.game.score_type
            
        self.setup_ui()

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
        if self.mode == "daily":
            self.checkbox.mousePressEvent = self.checkbox_clicked
        layout.addWidget(self.checkbox)
        
        # Game info (middle)
        info_layout = QVBoxLayout()
        
        # Game name and score
        name_layout = QHBoxLayout()
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        name_layout.addWidget(self.name_label)
        
        # Score input only in daily mode or if there's a score in calendar mode
        if self.score_type and self.score_type.strip():
            score_container = QWidget()
            score_layout = QHBoxLayout(score_container)
            score_layout.setContentsMargins(0, 0, 0, 0)
            score_layout.setSpacing(2)
            
            if self.mode == "daily":
                self.score_input = ClickableLineEdit()
                self.score_input.setPlaceholderText("Score")
                current_score = str(self.game_data.get('score', ''))
                self.score_input.setText(current_score)
                self.score_input.editingFinished.connect(self.on_score_changed)
                self.score_input.setFixedWidth(max(50, len(current_score) * 10))
            else:
                # In calendar mode, just show score as text if it exists
                current_score = self.game_data.get('score', '')
                if current_score:
                    self.score_input = QLabel(str(current_score))
                else:
                    self.score_input = None

            if self.score_input:
                self.score_input.setStyleSheet("""
                    QLabel, QLineEdit {
                        color: #28a745;
                        font-size: 14px;
                        padding: 2px 4px;
                    }
                """)
                score_layout.addWidget(self.score_input)
            
            # Add denomination label
            if self.score_type:
                self.score_denomination = QLabel()
                self.score_denomination.setStyleSheet("color: #6c757d; font-size: 14px;")
                if self.score_type.strip().isdigit():
                    self.score_denomination.setText(f"/{self.score_type}")
                else:
                    self.score_denomination.setText(f" {self.score_type}")
                score_layout.addWidget(self.score_denomination)
            
            name_layout.addWidget(score_container)
        
        name_layout.addStretch()
        
        # Note button only in daily mode
        if self.mode == "daily":
            self.note_btn = QPushButton("📝" if self.note else "+")
            self.note_btn.setToolTip("Edit Note" if self.note else "Add Note")
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
        
        # Description
        if self.description:
            description_label = QLabel(self.description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet("color: #666;")
            info_layout.addWidget(description_label)
        
        # Note text in calendar mode
        if self.mode == "calendar" and self.note:
            note_label = QLabel(f"*note*: {self.note}")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("color: #666; font-style: italic;")
            info_layout.addWidget(note_label)
        
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
        # Only set cursor to pointing hand in daily mode
        if self.mode == "daily":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def show_note_dialog(self):
        dialog = NoteDialog(self.note, self)
        if not self.isEnabled():
            # Make the dialog read-only in calendar view
            dialog.note_edit.setReadOnly(True)
            dialog.findChild(QPushButton, "Save").hide()
        
        if dialog.exec() == QDialog.DialogCode.Accepted and self.isEnabled():
            self.note = dialog.get_note()
            if self.note_btn:
                self.note_btn.setText("📝" if self.note else "+")
            self.emit_update()

    def mousePressEvent(self, event):
        if self.mode == "calendar":
            # Do nothing in calendar mode
            return
            
        # Only handle URL clicks in daily mode
        if event.button() == Qt.MouseButton.LeftButton:
            # Handle differently based on if game is dict or object
            url = self.game.get('url') if isinstance(self.game, dict) else self.game.url
            if url:
                QDesktopServices.openUrl(QUrl(url))

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
        if self.score_input:
            # Update the width of the score input based on content
            current_text = self.score_input.text()
            self.score_input.setFixedWidth(max(50, len(current_text) * 10))
        self.emit_update()

    def update_appearance(self):
        self.checkbox.setText("☑" if self.completed else "☐")
        self.setProperty('completed', self.completed)
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Update note button if it exists
        if self.mode == "daily" and self.note_btn:
            self.note_btn.setText("📝" if self.note else "+")
        
        # Update score if it exists and we're in daily mode
        if self.mode == "daily" and self.score_input:
            current_score = self.game_data.get('score', '')
            self.score_input.setText(str(current_score))

    def emit_update(self):
        score = self.score_input.text() if self.score_input else ""
        self.game_completed.emit(self.game_data, score, self.note)
