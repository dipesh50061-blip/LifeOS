import sqlite3
from datetime import datetime

DB_NAME = "lifeos.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# INITIALIZE / MIGRATE NOTES TABLE
# =========================================================

def ensure_notes_table():

    connection = get_connection()
    cursor = connection.cursor()

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

    # Handle older databases
    try:
        cursor.execute(
            "ALTER TABLE notes ADD COLUMN category TEXT DEFAULT 'General'"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE notes ADD COLUMN pinned INTEGER DEFAULT 0"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE notes ADD COLUMN updated_at TEXT"
        )
    except sqlite3.OperationalError:
        pass

    # Fill missing timestamps in older records
    cursor.execute("""
        UPDATE notes
        SET updated_at = created_at
        WHERE updated_at IS NULL
    """)

    # Fill missing categories
    cursor.execute("""
        UPDATE notes
        SET category = 'General'
        WHERE category IS NULL
           OR category = ''
    """)

    connection.commit()
    connection.close()


# =========================================================
# ADD NOTE
# =========================================================

def add_note(title, content, category="General"):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO notes (
            title,
            content,
            category,
            pinned,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, 0, ?, ?)
    """, (
        title,
        content,
        category,
        now,
        now
    ))

    connection.commit()
    connection.close()


# =========================================================
# GET NOTES
# =========================================================

def get_notes():

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            content,
            category,
            pinned,
            created_at,
            updated_at
        FROM notes
        ORDER BY
            pinned DESC,
            updated_at DESC,
            id DESC
    """)

    notes = cursor.fetchall()

    connection.close()

    return notes


# =========================================================
# UPDATE NOTE
# =========================================================

def update_note(
    note_id,
    title,
    content,
    category="General"
):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    updated_at = datetime.now().isoformat()

    cursor.execute("""
        UPDATE notes
        SET
            title = ?,
            content = ?,
            category = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        title,
        content,
        category,
        updated_at,
        note_id
    ))

    connection.commit()
    connection.close()


# =========================================================
# TOGGLE PIN
# =========================================================

def toggle_pin(note_id):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE notes
        SET pinned =
            CASE
                WHEN pinned = 1 THEN 0
                ELSE 1
            END,
            updated_at = ?
        WHERE id = ?
    """, (
        datetime.now().isoformat(),
        note_id
    ))

    connection.commit()
    connection.close()


# =========================================================
# DELETE NOTE
# =========================================================

def delete_note(note_id):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM notes
        WHERE id = ?
    """, (
        note_id,
    ))

    connection.commit()
    connection.close()


# =========================================================
# GET NOTES BY CATEGORY
# =========================================================

def get_notes_by_category(category):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            content,
            category,
            pinned,
            created_at,
            updated_at
        FROM notes
        WHERE category = ?
        ORDER BY
            pinned DESC,
            updated_at DESC
    """, (
        category,
    ))

    notes = cursor.fetchall()

    connection.close()

    return notes


# =========================================================
# SEARCH NOTES
# =========================================================

def search_notes(query):

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    search_pattern = f"%{query}%"

    cursor.execute("""
        SELECT
            id,
            title,
            content,
            category,
            pinned,
            created_at,
            updated_at
        FROM notes
        WHERE
            title LIKE ?
            OR content LIKE ?
            OR category LIKE ?
        ORDER BY
            pinned DESC,
            updated_at DESC
    """, (
        search_pattern,
        search_pattern,
        search_pattern
    ))

    notes = cursor.fetchall()

    connection.close()

    return notes


# =========================================================
# NOTE STATISTICS
# =========================================================

def get_note_statistics():

    ensure_notes_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM notes
    """)

    total_notes = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM notes
        WHERE pinned = 1
    """)

    pinned_notes = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(DISTINCT category)
        FROM notes
        WHERE category IS NOT NULL
          AND category != ''
    """)

    categories_used = cursor.fetchone()[0] or 0

    connection.close()

    return {
        "total": total_notes,
        "pinned": pinned_notes,
        "categories": categories_used
    }