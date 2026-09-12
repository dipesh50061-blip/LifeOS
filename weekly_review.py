import sqlite3
from datetime import date, timedelta

DB_NAME = "lifeos.db"


def get_week_range():

    today = date.today()

    start_of_week = today - timedelta(
        days=today.weekday()
    )

    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week


def get_weekly_task_summary():

    start, end = get_week_range()

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(completed), 0)
        FROM tasks
        WHERE DATE(created_at)
        BETWEEN ? AND ?
    """, (
        start.isoformat(),
        end.isoformat()
    ))

    total, completed = cursor.fetchone()

    connection.close()

    return total, completed


def get_weekly_habit_summary():

    start, end = get_week_range()

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*)
        FROM habit_logs
        WHERE date BETWEEN ? AND ?
        AND completed = 1
    """, (
        start.isoformat(),
        end.isoformat()
    ))

    completed = cursor.fetchone()[0]

    connection.close()

    return completed


def get_weekly_focus_summary():

    start, end = get_week_range()

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date BETWEEN ? AND ?
    """, (
        start.isoformat(),
        end.isoformat()
    ))

    minutes = cursor.fetchone()[0]

    connection.close()

    return minutes


def get_weekly_goal_summary():

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE progress >= target
    """)

    completed = cursor.fetchone()[0]

    connection.close()

    return completed


def get_weekly_review():

    start, end = get_week_range()

    task_total, task_completed = get_weekly_task_summary()
    habit_completed = get_weekly_habit_summary()
    focus_minutes = get_weekly_focus_summary()
    goal_completed = get_weekly_goal_summary()

    if task_total > 0:
        task_rate = round(
            (task_completed / task_total) * 100
        )
    else:
        task_rate = 0

    return {
        "start": start,
        "end": end,
        "task_total": task_total,
        "task_completed": task_completed,
        "task_rate": task_rate,
        "habit_completed": habit_completed,
        "focus_minutes": focus_minutes,
        "goal_completed": goal_completed
    }