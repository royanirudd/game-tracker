import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from models.game import Game

class DatabaseManager:
    def __init__(self, db_path: str = "game_tracker.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database and create necessary tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create games table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            score_type TEXT NOT NULL,
            reminder_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create daily_progress table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            date DATE NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            score TEXT,
            notes TEXT,
            FOREIGN KEY (game_id) REFERENCES games (id),
            UNIQUE (game_id, date)
        )
        ''')

        conn.commit()
        conn.close()

    def add_game(self, game: Game) -> int:
        """Add a new game to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO games (name, url, description, score_type, reminder_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (game.name, game.url, game.description, game.score_type, 
              game.reminder_time, game.created_at))
        
        game_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return game_id

    def get_all_games(self) -> List[Game]:
        """Retrieve all games from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM games')
        rows = cursor.fetchall()
        
        games = []
        for row in cursor.fetchall():
            games.append(Game(
                id=row[0],
                name=row[1],
                url=row[2],
                description=row[3],
                score_type=row[4],
                reminder_time=row[5],
                created_at=datetime.fromisoformat(row[6])
            ))
        
        conn.close()
        return games

    def update_game_progress(self, game_id: int, date: datetime.date, 
                           completed: bool, score: Optional[str] = None, 
                           notes: Optional[str] = None):
        """Update or create a daily progress entry for a game."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO daily_progress (game_id, date, completed, score, notes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (game_id, date) DO UPDATE SET
            completed = excluded.completed,
            score = excluded.score,
            notes = excluded.notes
        ''', (game_id, date.isoformat(), completed, score, notes))
        
        conn.commit()
        conn.close()

    def get_daily_progress(self, date: datetime.date) -> List[dict]:
        """Get progress for all games for a specific date."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT g.*, dp.completed, dp.score, dp.notes
        FROM games g
        LEFT JOIN daily_progress dp ON g.id = dp.game_id AND dp.date = ?
        ''', (date.isoformat(),))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'game': Game(
                    id=row[0],
                    name=row[1],
                    url=row[2],
                    description=row[3],
                    score_type=row[4],
                    reminder_time=row[5],
                    created_at=datetime.fromisoformat(row[6])
                ),
                'completed': bool(row[7]) if row[7] is not None else False,
                'score': row[8],
                'notes': row[9]
            })
        
        conn.close()
        return results
