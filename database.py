import sqlite3

DB_NAME = "lifeos.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # Tasks
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Add category column to older databases
    try:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN category TEXT DEFAULT 'General'
        """)
    except sqlite3.OperationalError:
        pass

    # -------------------------
    # Habits
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # Habit Logs
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        )
    """)

    # -------------------------
    # Goals
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            target INTEGER NOT NULL,
            progress INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # Focus Sessions
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duration INTEGER NOT NULL,
            session_date TEXT NOT NULL
        )
    """)

    # -------------------------
    # Notes
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            pinned INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

        # -------------------------
    # Achievements
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            unlocked INTEGER DEFAULT 0,
            unlocked_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            progress INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (goal_id) REFERENCES goals(id)
        )
    """)

    # -------------------------
    # Save Changes
    # -------------------------

    connection.commit()
    connection.close()