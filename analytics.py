import sqlite3
from datetime import date, timedelta

DB_NAME = "lifeos.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# BASIC STATISTICS
# =========================================================

def get_task_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END), 0)
        FROM tasks
    """)

    total, completed = cursor.fetchone()

    connection.close()

    total = total or 0
    completed = completed or 0

    rate = round((completed / total) * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "rate": rate
    }


def get_habit_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM habits
    """)

    total_habits = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed = 1
    """)

    completed_logs = cursor.fetchone()[0] or 0

    connection.close()

    return {
        "total": total_habits,
        "completed": completed_logs
    }


def get_goal_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM goals
    """)

    total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE progress >= target
    """)

    completed = cursor.fetchone()[0] or 0

    connection.close()

    rate = round((completed / total) * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "rate": rate
    }


# =========================================================
# PRODUCTIVITY SCORE
# =========================================================

def calculate_productivity_score():
    """
    Calculate today's productivity score.

    Weighting:
    Tasks  = 40%
    Habits = 25%
    Focus  = 25%
    Goals  = 10%
    """

    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # Tasks
    # -------------------------

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            )
        FROM tasks
        WHERE due_date = ?
    """, (today,))

    task_total, task_completed = cursor.fetchone()

    task_total = task_total or 0
    task_completed = task_completed or 0

    task_score = (
        (task_completed / task_total) * 40
        if task_total > 0
        else 0
    )

    # -------------------------
    # Habits
    # -------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM habits
    """)

    habit_total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(DISTINCT habit_id)
        FROM habit_logs
        WHERE date = ?
          AND completed = 1
    """, (today,))

    habit_completed = cursor.fetchone()[0] or 0

    habit_score = (
        (habit_completed / habit_total) * 25
        if habit_total > 0
        else 0
    )

    # -------------------------
    # Focus
    # -------------------------

    cursor.execute("""
        SELECT COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date = ?
    """, (today,))

    focus_minutes = cursor.fetchone()[0] or 0

    focus_score = min(focus_minutes / 60, 1) * 25

    # -------------------------
    # Goals
    # -------------------------

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(
                SUM(
                    CASE
                        WHEN progress >= target
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            )
        FROM goals
    """)

    goal_total, goal_completed = cursor.fetchone()

    goal_total = goal_total or 0
    goal_completed = goal_completed or 0

    goal_score = (
        (goal_completed / goal_total) * 10
        if goal_total > 0
        else 0
    )

    connection.close()

    score = (
        task_score
        + habit_score
        + focus_score
        + goal_score
    )

    return round(min(score, 100))


# =========================================================
# DAILY TASK ANALYTICS
# =========================================================

def get_daily_task_stats(days=30):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=days - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            due_date,
            COUNT(*),
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            )
        FROM tasks
        WHERE due_date IS NOT NULL
          AND due_date >= ?
        GROUP BY due_date
        ORDER BY due_date
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# DAILY FOCUS ANALYTICS
# =========================================================

def get_daily_focus_stats(days=30):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=days - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            session_date,
            COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date >= ?
        GROUP BY session_date
        ORDER BY session_date
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# DAILY HABIT ANALYTICS
# =========================================================

def get_daily_habit_stats(days=30):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=days - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            date,
            COUNT(*)
        FROM habit_logs
        WHERE date >= ?
          AND completed = 1
        GROUP BY date
        ORDER BY date
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# WEEKLY TASK ANALYTICS
# =========================================================

def get_weekly_task_stats(weeks=8):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=weeks * 7 - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            strftime('%Y-%W', due_date) AS week,
            COUNT(*),
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            )
        FROM tasks
        WHERE due_date IS NOT NULL
          AND due_date >= ?
        GROUP BY week
        ORDER BY week
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# WEEKLY FOCUS ANALYTICS
# =========================================================

def get_weekly_focus_stats(weeks=8):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=weeks * 7 - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            strftime('%Y-%W', session_date) AS week,
            COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date >= ?
        GROUP BY week
        ORDER BY week
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# WEEKLY HABIT ANALYTICS
# =========================================================

def get_weekly_habit_stats(weeks=8):
    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today() - timedelta(days=weeks * 7 - 1)
    ).isoformat()

    cursor.execute("""
        SELECT
            strftime('%Y-%W', date) AS week,
            COUNT(*)
        FROM habit_logs
        WHERE date >= ?
          AND completed = 1
        GROUP BY week
        ORDER BY week
    """, (start_date,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# OVERALL FOCUS
# =========================================================

def get_overall_focus_time():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration), 0)
        FROM focus_sessions
    """)

    total = cursor.fetchone()[0] or 0

    connection.close()

    return total


# =========================================================
# OVERALL HABIT COMPLETIONS
# =========================================================

def get_overall_habit_completions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed = 1
    """)

    total = cursor.fetchone()[0] or 0

    connection.close()

    return total


# =========================================================
# GOAL PROGRESS
# =========================================================

def get_goal_progress_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            title,
            progress,
            target
        FROM goals
        ORDER BY progress DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# PRODUCTIVITY SUMMARY
# =========================================================

def get_productivity_summary():
    task_stats = get_task_stats()
    habit_stats = get_habit_stats()
    goal_stats = get_goal_stats()
    focus_minutes = get_overall_focus_time()

    return {
        "task_rate": task_stats["rate"],
        "habit_rate": habit_stats["completed"],
        "goal_rate": goal_stats["rate"],
        "focus_minutes": focus_minutes
    }


# =========================================================
# ADVANCED ANALYTICS 2.0
# =========================================================

def get_today_summary():
    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    # Tasks
    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            )
        FROM tasks
        WHERE due_date = ?
    """, (today,))

    task_total, task_completed = cursor.fetchone()

    # Habits
    cursor.execute("""
        SELECT COUNT(*)
        FROM habits
    """)

    habit_total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(DISTINCT habit_id)
        FROM habit_logs
        WHERE date = ?
          AND completed = 1
    """, (today,))

    habit_completed = cursor.fetchone()[0] or 0

    # Focus
    cursor.execute("""
        SELECT COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date = ?
    """, (today,))

    focus_minutes = cursor.fetchone()[0] or 0

    connection.close()

    task_total = task_total or 0
    task_completed = task_completed or 0

    task_rate = (
        round((task_completed / task_total) * 100)
        if task_total
        else 0
    )

    habit_rate = (
        round((habit_completed / habit_total) * 100)
        if habit_total
        else 0
    )

    return {
        "task_total": task_total,
        "task_completed": task_completed,
        "task_rate": task_rate,
        "habit_total": habit_total,
        "habit_completed": habit_completed,
        "habit_rate": habit_rate,
        "focus_minutes": focus_minutes
    }


def get_consistency_score(days=7):
    """
    Measures how consistently the user engages
    with tasks, habits and focus.

    Returns 0-100.
    """

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    connection = get_connection()
    cursor = connection.cursor()

    active_days = set()

    # Task activity
    cursor.execute("""
        SELECT DISTINCT due_date
        FROM tasks
        WHERE due_date >= ?
          AND completed = 1
    """, (start_date.isoformat(),))

    for row in cursor.fetchall():
        if row[0]:
            active_days.add(row[0])

    # Habit activity
    cursor.execute("""
        SELECT DISTINCT date
        FROM habit_logs
        WHERE date >= ?
          AND completed = 1
    """, (start_date.isoformat(),))

    for row in cursor.fetchall():
        if row[0]:
            active_days.add(row[0])

    # Focus activity
    cursor.execute("""
        SELECT DISTINCT session_date
        FROM focus_sessions
        WHERE session_date >= ?
    """, (start_date.isoformat(),))

    for row in cursor.fetchall():
        if row[0]:
            active_days.add(row[0])

    connection.close()

    return round(
        (len(active_days) / days) * 100
    )


def get_best_focus_day(days=30):
    history = get_daily_focus_stats(days)

    if not history:
        return None

    return max(
        history,
        key=lambda item: item[1]
    )


def get_best_task_day(days=30):
    history = get_daily_task_stats(days)

    if not history:
        return None

    return max(
        history,
        key=lambda item: item[2]
    )


def get_total_completed_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 1
    """)

    total = cursor.fetchone()[0] or 0

    connection.close()

    return total


def get_total_completed_goals():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE progress >= target
    """)

    total = cursor.fetchone()[0] or 0

    connection.close()

    return total


def get_productivity_insights():
    """
    Generate simple rule-based insights from
    current LifeOS activity.
    """

    summary = get_today_summary()

    insights = []

    if summary["task_total"] == 0:
        insights.append(
            "📋 No tasks are scheduled for today."
        )
    elif summary["task_rate"] >= 80:
        insights.append(
            "🔥 Strong task execution today."
        )
    elif summary["task_rate"] < 50:
        insights.append(
            "📋 Task completion is below 50% today."
        )

    if summary["habit_total"] == 0:
        insights.append(
            "🔥 You have no habits configured yet."
        )
    elif summary["habit_rate"] == 100:
        insights.append(
            "🔥 All habits are complete today."
        )
    elif summary["habit_rate"] < 50:
        insights.append(
            "🔥 Habit consistency needs attention today."
        )

    if summary["focus_minutes"] == 0:
        insights.append(
            "⏱️ No focus time recorded today."
        )
    elif summary["focus_minutes"] >= 60:
        insights.append(
            "🧠 You have completed at least one hour of focus."
        )
    else:
        insights.append(
            "⏱️ A focused session could improve today's score."
        )

    return insights