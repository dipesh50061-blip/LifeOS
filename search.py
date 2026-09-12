import sqlite3

DB_NAME = "lifeos.db"


def global_search(query):

    query = query.strip()

    if not query:
        return {
            "tasks": [],
            "habits": [],
            "goals": [],
            "notes": []
        }

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    search_term = f"%{query}%"

    # -------------------------
    # Tasks
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            title,
            priority,
            category,
            due_date,
            completed
        FROM tasks
        WHERE
            title LIKE ?
            OR category LIKE ?
    """, (
        search_term,
        search_term
    ))

    tasks = cursor.fetchall()

    # -------------------------
    # Habits
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            name
        FROM habits
        WHERE name LIKE ?
    """, (
        search_term,
    ))

    habits = cursor.fetchall()

    # -------------------------
    # Goals
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            title,
            target,
            progress
        FROM goals
        WHERE title LIKE ?
    """, (
        search_term,
    ))

    goals = cursor.fetchall()

    # -------------------------
    # Notes
    # -------------------------

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
    """, (
        search_term,
        search_term,
        search_term
    ))

    notes = cursor.fetchall()

    connection.close()

    return {
        "tasks": tasks,
        "habits": habits,
        "goals": goals,
        "notes": notes
    }