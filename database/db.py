import sqlite3
from pathlib import Path

# Database file location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "clienttrack.db"


# Connect to database
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Create all database tables
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Clients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Leads Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            source TEXT,
            status TEXT DEFAULT 'New',
            value REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Projects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_id INTEGER,
            description TEXT,
            status TEXT DEFAULT 'Not Started',
            progress INTEGER DEFAULT 0,
            start_date TEXT,
            deadline TEXT,
            budget REAL DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # 4. Calls and Meetings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            title TEXT NOT NULL,
            meeting_type TEXT,
            meeting_date TEXT,
            meeting_time TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # 5. Follow-Ups Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            subject TEXT NOT NULL,
            method TEXT,
            followup_date TEXT,
            followup_time TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # 6. Daily Progress Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            progress_date TEXT,
            description TEXT,
            progress_percentage INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # 7. Notes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 8. Communication Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communication_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            communication_type TEXT,
            subject TEXT,
            details TEXT,
            communication_date TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # 9. Users and Roles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT DEFAULT 'Staff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Fetch records from any table
def fetch_data(query, parameters=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    records = cursor.fetchall()
    conn.close()
    return records


# Insert, update or delete records
def execute_query(query, parameters=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    conn.commit()
    conn.close()