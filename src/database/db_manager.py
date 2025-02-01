import sqlite3
from datetime import datetime, date
from models.game import Game

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('game_tracker.db')
        self.conn.row_factory = sqlite3.Row
        self.current_version = 2  # Increment this when schema changes
        self.create_tables()
        self.migrate_database()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Version tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        ''')
        
        # Games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT,
                description TEXT,
                score_type TEXT,
                reminder_time TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                date DATE,
                completed BOOLEAN DEFAULT 0,
                score TEXT,
                note TEXT,
                FOREIGN KEY (game_id) REFERENCES games (id),
                UNIQUE(game_id, date)
            )
        ''')
        
        self.conn.commit()

    def get_db_version(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT version FROM schema_version ORDER BY version DESC LIMIT 1')
        result = cursor.fetchone()
        return result[0] if result else 0

    def migrate_database(self):
        current_version = self.get_db_version()
        
        if current_version < self.current_version:
            cursor = self.conn.cursor()
            
            # Migrations
            if current_version < 2:
                # Migrate to version 2: Add note column
                cursor.execute('''
                    CREATE TABLE progress_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        date DATE,
                        completed BOOLEAN DEFAULT 0,
                        score TEXT,
                        note TEXT,
                        FOREIGN KEY (game_id) REFERENCES games (id),
                        UNIQUE(game_id, date)
                    )
                ''')
                
                # Copy existing data
                cursor.execute('''
                    INSERT INTO progress_new (id, game_id, date, completed, score)
                    SELECT id, game_id, date, completed, score FROM progress
                ''')
                
                # Drop old table and rename new one
                cursor.execute('DROP TABLE progress')
                cursor.execute('ALTER TABLE progress_new RENAME TO progress')
            
            # Update schema version
            cursor.execute('DELETE FROM schema_version')
            cursor.execute('INSERT INTO schema_version (version) VALUES (?)', 
                         (self.current_version,))
            
            self.conn.commit()

    def get_daily_progress(self, target_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                g.*,
                p.completed,
                p.score,
                p.note
            FROM games g
            LEFT JOIN progress p ON g.id = p.game_id 
            AND p.date = ?
        ''', (target_date,))
        
        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            game = Game(
                id=row_dict['id'],
                name=row_dict['name'],
                url=row_dict['url'],
                description=row_dict['description'],
                score_type=row_dict['score_type'],
                reminder_time=row_dict['reminder_time'],
                created_at=row_dict['created_at']
            )
            results.append({
                'game': game,
                'completed': bool(row_dict['completed']),
                'score': row_dict['score'],
                'note': row_dict['note']
            })
        return results

    def update_game_progress(self, game_id, date, completed, score=None, note=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO progress (game_id, date, completed, score, note)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(game_id, date) 
            DO UPDATE SET completed = ?, score = ?, note = ?
        ''', (game_id, date, completed, score, note, completed, score, note))
        self.conn.commit()

    def add_game(self, game):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO games (name, url, description, score_type, reminder_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            game.name, game.url, game.description, 
            game.score_type, game.reminder_time, game.created_at
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_games(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM games')
        return [Game(**dict(row)) for row in cursor.fetchall()]


    def delete_game(self, game_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM progress WHERE game_id = ?', (game_id,))
        cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))
        self.conn.commit()
    

    def get_month_completion_stats(self, year, month):
        """Get completion statistics for each day in the specified month."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            WITH RECURSIVE dates(date) AS (
                SELECT date(?, '-01')
                UNION ALL
                SELECT date(date, '+1 day')
                FROM dates
                WHERE strftime('%m', date) = strftime('%m', ?)
            ),
            daily_stats AS (
                SELECT 
                    p.date,
                    COUNT(DISTINCT g.id) as total_games,
                    COUNT(DISTINCT CASE WHEN p.completed = 1 THEN g.id END) as completed_games
                FROM dates d
                CROSS JOIN games g
                LEFT JOIN progress p ON g.id = p.game_id AND p.date = d.date
                GROUP BY d.date
            )
            SELECT 
                date,
                COALESCE(total_games, 0) as total_games,
                COALESCE(completed_games, 0) as completed_games
            FROM daily_stats
            ORDER BY date
        ''', (f"{year}-{month:02d}", f"{year}-{month:02d}"))
        
        return {row[0]: {'total': row[1], 'completed': row[2]} 
                for row in cursor.fetchall()}

    def get_day_games(self, date):
        """Get detailed game information for a specific date."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                g.*,
                p.completed,
                p.score,
                p.note
            FROM games g
            LEFT JOIN progress p ON g.id = p.game_id AND p.date = ?
            ORDER BY g.name
        ''', (date,))
        
        results = []
        for row in cursor.fetchall():
            game_dict = dict(row)
            game = {
                'id': game_dict['id'],
                'name': game_dict['name'],
                'url': game_dict['url'],
                'description': game_dict['description'],
                'score_type': game_dict['score_type'],
                'completed': bool(game_dict['completed']),
                'score': game_dict['score'],
                'note': game_dict['note']
            }
            results.append(game)
        return results
