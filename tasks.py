import sqlite3
from datetime import datetime

DB_NAME = "lifeos.db"


def add_task(title, priority, category, due_date):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (title, priority, category, due_date, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        priority,
        category,
        due_date,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_tasks():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            priority,
            category,
            due_date,
            completed
        FROM tasks
        ORDER BY completed ASC, due_date ASC
    """)

    tasks = cursor.fetchall()

    connection.close()

    return tasks


def complete_task(task_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()


def reopen_task(task_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = 0
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()


def update_task(task_id, title, priority, category, due_date):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET
            title = ?,
            priority = ?,
            category = ?,
            due_date = ?
        WHERE id = ?
    """, (
        title,
        priority,
        category,
        due_date,
        task_id
    ))

    connection.commit()
    connection.close()


def delete_task(task_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()