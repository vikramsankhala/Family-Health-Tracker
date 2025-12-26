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
            password_hash TEXT NOT NULL,
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
    default_password = 'admin123'  # Change this to your desired password
    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ('admin', password_hash))
        conn.commit()
        print(f"Default admin user created. Username: admin, Password: {default_password}")
    except sqlite3.IntegrityError:
        pass  # User already exists
    
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

def authenticate_user(username, password):
    """Authenticate a user"""
    with get_db() as conn:
        cursor = conn.cursor()
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

