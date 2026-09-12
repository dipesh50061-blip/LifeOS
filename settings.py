import sqlite3

DB_NAME = "lifeos.db"


def initialize_settings():

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    default_settings = {
        "username": "User",
        "daily_focus_goal": "60",
        "daily_task_goal": "5",
        "theme": "System",
        "show_completed_tasks": "Yes"
    }

    for key, value in default_settings.items():

        cursor.execute("""
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES (?, ?)
        """, (
            key,
            value
        ))

    connection.commit()
    connection.close()


def get_setting(key):

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
    """, (
        key,
    ))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


def update_setting(key, value):

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO settings
        (key, value)
        VALUES (?, ?)
    """, (
        key,
        str(value)
    ))

    connection.commit()
    connection.close()


def get_all_settings():

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT key, value
        FROM settings
        ORDER BY key
    """)

    settings = cursor.fetchall()

    connection.close()

    return settings