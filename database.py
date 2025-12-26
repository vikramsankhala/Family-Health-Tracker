import sqlite3
import hashlib
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE = 'health_tracker.db'

def init_database():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Health Tracker Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_tracker_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            weight REAL,
            blood_pressure TEXT,
            blood_sugar TEXT,
            sleep_hours REAL,
            exercise_minutes INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Diet Plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diet_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_type TEXT NOT NULL,
            day TEXT NOT NULL,
            food_item TEXT NOT NULL,
            quantity TEXT,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fats REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Exercise Plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            duration_minutes INTEGER,
            sets INTEGER,
            reps INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            author TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    
    # Budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT UNIQUE NOT NULL,
            total_budget REAL NOT NULL,
            categories TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    
    # Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            month TEXT NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            is_capital INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    ''')
    
    # Create default admin user if not exists
    default_password = 'admin123'
    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin@healthtracker.com', password_hash))
        conn.commit()
        print(f"Default admin user created. Username: admin, Password: {default_password}")
    except sqlite3.IntegrityError:
        pass  # User already exists
    
    # Create vikramsankhala user
    vikram_password = 'vikramsankhala'
    vikram_password_hash = hashlib.sha256(vikram_password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('vikramsankhala', 'vikramsankhala@healthtracker.com', vikram_password_hash))
        conn.commit()
        print(f"User vikramsankhala created. Password: {vikram_password}")
    except sqlite3.IntegrityError:
        # Update password if user exists
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE username = ?
        ''', (vikram_password_hash, 'vikramsankhala'))
        conn.commit()
        print(f"User vikramsankhala password updated.")
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def create_user(username, password):
    """Create a new user"""
    password_hash = hash_password(password)
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (username, password_hash))
            return True
        except sqlite3.IntegrityError:
            return False

def authenticate_user(username, password, email=None):
    """Authenticate a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        if email:
            cursor.execute('SELECT password_hash FROM users WHERE username = ? AND email = ?', (username, email))
        else:
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row and verify_password(password, row['password_hash']):
            return True
        return False

def create_session(username):
    """Create a new session"""
    import uuid
    from datetime import timedelta
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=24)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, username, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, username, expires_at))
    
    return session_id

def verify_session(session_id):
    """Verify if a session is valid"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username FROM sessions
            WHERE session_id = ? AND expires_at > datetime('now')
        ''', (session_id,))
        row = cursor.fetchone()
        if row:
            return row['username']
        return None

def delete_session(session_id):
    """Delete a session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))

def cleanup_expired_sessions():
    """Remove expired sessions"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE expires_at < datetime('now')")

# Initialize database on import
if not os.path.exists(DATABASE):
    init_database()
else:
    # Check if new tables exist, if not, add them
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check for new tables and add if missing
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='health_tracker_data'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_tracker_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                weight REAL,
                blood_pressure TEXT,
                blood_sugar TEXT,
                sleep_hours REAL,
                exercise_minutes INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='diet_plan'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_type TEXT NOT NULL,
                day TEXT NOT NULL,
                food_item TEXT NOT NULL,
                quantity TEXT,
                calories INTEGER,
                protein REAL,
                carbs REAL,
                fats REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise_plan'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                duration_minutes INTEGER,
                sets INTEGER,
                reps INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Check if email column exists in users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'email' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
    
    # Ensure vikramsankhala user exists
    vikram_password = 'vikramsankhala'
    vikram_password_hash = hashlib.sha256(vikram_password.encode()).hexdigest()
    cursor.execute('SELECT id FROM users WHERE username = ?', ('vikramsankhala',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('vikramsankhala', 'vikramsankhala@healthtracker.com', vikram_password_hash))
    else:
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (vikram_password_hash, 'vikramsankhala'))
    
    conn.commit()
    conn.close()

