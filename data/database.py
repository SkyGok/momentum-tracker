"""SQLite database management for Momentum Tracker."""
import sqlite3
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


class Database:
    """Thread-safe SQLite database manager."""
    
    def __init__(self, db_path: Path, logger=None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            logger: Logger instance for logging operations
        """
        self.db_path = Path(db_path)
        self.logger = logger
        self._local = threading.local()
        self._lock = threading.Lock()
        
        # Create database and tables
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=10.0
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            with self._lock:
                yield conn
                conn.commit()
        except Exception as e:
            conn.rollback()
            if self.logger:
                self.logger.error(f"Database transaction error: {e}", exc_info=True)
            raise
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        
        with self._lock:
            try:
                # Users table (for future multi-user/sync support)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_sync_at TIMESTAMP
                    )
                """)
                
                # Categories table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        color TEXT,
                        icon TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                """)
                
                # Activity logs table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        category_id INTEGER NOT NULL,
                        description TEXT,
                        duration_minutes INTEGER DEFAULT 15,
                        logged_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (category_id) REFERENCES categories(id)
                    )
                """)
                
                # Weekly aggregations table (for performance)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS weekly_aggregations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        category_id INTEGER NOT NULL,
                        week_start DATE NOT NULL,
                        total_minutes INTEGER DEFAULT 0,
                        entry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, category_id, week_start),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (category_id) REFERENCES categories(id)
                    )
                """)
                
                # Monthly aggregations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS monthly_aggregations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        category_id INTEGER NOT NULL,
                        month_start DATE NOT NULL,
                        total_minutes INTEGER DEFAULT 0,
                        entry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, category_id, month_start),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (category_id) REFERENCES categories(id)
                    )
                """)
                
                # Create indexes for performance
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_activity_logs_logged_at 
                    ON activity_logs(logged_at)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_activity_logs_category 
                    ON activity_logs(category_id)
                """)
                
                conn.commit()
                
                # Create default user if not exists
                conn.execute("""
                    INSERT OR IGNORE INTO users (id, username) 
                    VALUES (1, 'default_user')
                """)
                
                conn.commit()
                
                if self.logger:
                    self.logger.info("Database initialized successfully")
                    
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error initializing database: {e}", exc_info=True)
                raise
    
    def get_or_create_category(self, name: str) -> int:
        """Get category ID or create if it doesn't exist."""
        conn = self._get_connection()
        
        with self._lock:
            cursor = conn.execute(
                "SELECT id FROM categories WHERE name = ? AND is_active = 1",
                (name,)
            )
            row = cursor.fetchone()
            
            if row:
                return row['id']
            else:
                cursor = conn.execute(
                    "INSERT INTO categories (name, is_active) VALUES (?, 1)",
                    (name,)
                )
                conn.commit()
                return cursor.lastrowid
    
    def add_activity_log(self, category_name: str, description: str = "",
                        duration_minutes: int = 15, logged_at: datetime = None) -> int:
        """
        Add a new activity log entry.
        
        Args:
            category_name: Name of the activity category
            description: Optional description
            duration_minutes: Duration in minutes (default: 15)
            logged_at: Timestamp (default: now)
        
        Returns:
            ID of the created log entry
        """
        if logged_at is None:
            logged_at = datetime.now()
        
        category_id = self.get_or_create_category(category_name)
        
        with self._transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO activity_logs 
                (user_id, category_id, description, duration_minutes, logged_at)
                VALUES (1, ?, ?, ?, ?)
            """, (category_id, description, duration_minutes, logged_at))
            
            log_id = cursor.lastrowid
            
            if self.logger:
                self.logger.info(
                    f"Added activity log: {category_name} "
                    f"({duration_minutes} min) at {logged_at}"
                )
            
            return log_id
    
    def get_activities_by_date(self, date: datetime) -> List[Dict]:
        """Get all activities for a specific date."""
        conn = self._get_connection()
        date_str = date.strftime('%Y-%m-%d')
        
        with self._lock:
            cursor = conn.execute("""
                SELECT 
                    al.id,
                    al.description,
                    al.duration_minutes,
                    al.logged_at,
                    c.name as category_name
                FROM activity_logs al
                JOIN categories c ON al.category_id = c.id
                WHERE DATE(al.logged_at) = ?
                ORDER BY al.logged_at ASC
            """, (date_str,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_activities_by_date_range(self, start_date: datetime, 
                                    end_date: datetime) -> List[Dict]:
        """Get all activities within a date range."""
        conn = self._get_connection()
        
        with self._lock:
            cursor = conn.execute("""
                SELECT 
                    al.id,
                    al.description,
                    al.duration_minutes,
                    al.logged_at,
                    c.name as category_name
                FROM activity_logs al
                JOIN categories c ON al.category_id = c.id
                WHERE DATE(al.logged_at) BETWEEN ? AND ?
                ORDER BY al.logged_at ASC
            """, (start_date.strftime('%Y-%m-%d'), 
                  end_date.strftime('%Y-%m-%d')))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_category_summary(self, start_date: datetime, 
                            end_date: datetime) -> List[Dict]:
        """Get summary of activities by category for a date range."""
        conn = self._get_connection()
        
        with self._lock:
            cursor = conn.execute("""
                SELECT 
                    c.name as category_name,
                    SUM(al.duration_minutes) as total_minutes,
                    COUNT(al.id) as entry_count
                FROM activity_logs al
                JOIN categories c ON al.category_id = c.id
                WHERE DATE(al.logged_at) BETWEEN ? AND ?
                GROUP BY c.name
                ORDER BY total_minutes DESC
            """, (start_date.strftime('%Y-%m-%d'), 
                  end_date.strftime('%Y-%m-%d')))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_categories(self, active_only: bool = True) -> List[Dict]:
        """Get all categories."""
        conn = self._get_connection()
        
        with self._lock:
            if active_only:
                cursor = conn.execute(
                    "SELECT * FROM categories WHERE is_active = 1 ORDER BY name"
                )
            else:
                cursor = conn.execute("SELECT * FROM categories ORDER BY name")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_category(self, name: str, color: str = None, icon: str = None) -> int:
        """Add a new category."""
        conn = self._get_connection()
        
        with self._lock:
            try:
                cursor = conn.execute("""
                    INSERT INTO categories (name, color, icon, is_active)
                    VALUES (?, ?, ?, 1)
                """, (name, color, icon))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Category already exists
                cursor = conn.execute(
                    "SELECT id FROM categories WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                return row['id'] if row else None
    
    def update_category(self, category_id: int, name: str = None, 
                       color: str = None, icon: str = None, is_active: bool = None):
        """Update a category."""
        conn = self._get_connection()
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if color is not None:
            updates.append("color = ?")
            params.append(color)
        if icon is not None:
            updates.append("icon = ?")
            params.append(icon)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(int(is_active))
        
        if updates:
            params.append(category_id)
            with self._lock:
                conn.execute(
                    f"UPDATE categories SET {', '.join(updates)} WHERE id = ?",
                    params
                )
                conn.commit()
    
    def delete_category(self, category_id: int):
        """Soft delete a category (set is_active = 0)."""
        self.update_category(category_id, is_active=False)
    
    def close(self):
        """Close database connection."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')

