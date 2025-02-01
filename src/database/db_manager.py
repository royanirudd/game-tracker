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

    def get_current_streak(self):
        """Calculate current streak of consecutive days with completed games"""
        cursor = self.conn.cursor()
        cursor.execute("""
            WITH RECURSIVE dates AS (
                SELECT date('now', 'localtime') as date
                UNION ALL
                SELECT date(date, '-1 day')
                FROM dates
                WHERE EXISTS (
                    SELECT 1 FROM progress 
                    WHERE date = date(date, '-1 day')
                    AND completed = 1
                )
            )
            SELECT COUNT(*) FROM dates
        """)
        return cursor.fetchone()[0]

    def get_longest_streak(self):
        """Calculate longest streak of consecutive days with completed games"""
        cursor = self.conn.cursor()
        cursor.execute("""
            WITH consecutive_days AS (
                SELECT date,
                       date(date, 
                            '-' || ROW_NUMBER() OVER (ORDER BY date) || ' days'
                       ) as grp
                FROM progress
                WHERE completed = 1
                GROUP BY date
            )
            SELECT COUNT(*) as streak_length
            FROM consecutive_days
            GROUP BY grp
            ORDER BY streak_length DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_game_stats(self, game_id=None):
        """Get statistics for a specific game or all games"""
        cursor = self.conn.cursor()
        
        if game_id:
            cursor.execute("""
                SELECT g.name, g.score_type,
                       COUNT(CASE WHEN p.completed = 1 THEN 1 END) as times_completed,
                       COUNT(p.score) as times_scored,
                       AVG(CASE WHEN p.score GLOB '*[0-9]*' AND p.score NOT GLOB '*[A-Za-z]*' 
                               THEN CAST(p.score AS INTEGER) END) as avg_score,
                       MAX(CASE WHEN p.score GLOB '*[0-9]*' AND p.score NOT GLOB '*[A-Za-z]*' 
                               THEN CAST(p.score AS INTEGER) END) as best_score,
                       (SELECT date 
                        FROM progress 
                        WHERE game_id = g.id 
                        AND score = (SELECT MAX(score) FROM progress WHERE game_id = g.id)
                        LIMIT 1) as best_score_date
                FROM games g
                LEFT JOIN progress p ON g.id = p.game_id
                WHERE g.id = ?
                GROUP BY g.id
            """, (game_id,))
        else:
            cursor.execute("""
                SELECT g.id, g.name, g.score_type,
                       COUNT(CASE WHEN p.completed = 1 THEN 1 END) as times_completed,
                       COUNT(p.score) as times_scored,
                       AVG(CASE WHEN p.score GLOB '*[0-9]*' AND p.score NOT GLOB '*[A-Za-z]*' 
                               THEN CAST(p.score AS INTEGER) END) as avg_score,
                       MAX(CASE WHEN p.score GLOB '*[0-9]*' AND p.score NOT GLOB '*[A-Za-z]*' 
                               THEN CAST(p.score AS INTEGER) END) as best_score,
                       (SELECT date 
                        FROM progress 
                        WHERE game_id = g.id 
                        AND score = (SELECT MAX(score) FROM progress WHERE game_id = g.id)
                        LIMIT 1) as best_score_date
                FROM games g
                LEFT JOIN progress p ON g.id = p.game_id
                GROUP BY g.id
            """)
        
        return cursor.fetchall()


    def get_monthly_scores(self, game_id, year, month):
        """Get daily scores for a game in the specified month"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, score
            FROM progress
            WHERE game_id = ? 
            AND strftime('%Y-%m', date) = ?
            AND score IS NOT NULL
            AND score GLOB '*[0-9]*' 
            AND score NOT GLOB '*[A-Za-z]*'
            ORDER BY date
        """, (game_id, f"{year}-{month:02d}"))
        return cursor.fetchall()

    def get_completion_percentage(self, game_id):
        """Get completion percentage for days where any game was played"""
        cursor = self.conn.cursor()
        cursor.execute("""
            WITH active_days AS (
                SELECT DISTINCT date
                FROM progress
                WHERE completed = 1
            )
            SELECT 
                COUNT(CASE WHEN p.completed = 1 THEN 1 END) as completed_count,
                COUNT(p.date) as total_count
            FROM active_days ad
            LEFT JOIN progress p ON p.date = ad.date
            WHERE p.game_id = ?
        """, (game_id,))
        return cursor.fetchone()

    def get_game_history(self, game_id):
        """Get all completed entries for a game"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, completed, score, note
            FROM progress
            WHERE game_id = ?
            AND completed = 1
            ORDER BY date DESC
        """, (game_id,))
        return cursor.fetchall()
