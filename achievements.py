import sqlite3
from datetime import datetime, timedelta

DB_NAME = "lifeos.db"


ACHIEVEMENTS = [
    {
        "key": "first_task",
        "name": "First Step",
        "description": "Complete your first task.",
        "icon": "🌱",
        "xp": 10
    },
    {
        "key": "ten_tasks",
        "name": "Getting Things Done",
        "description": "Complete 10 tasks.",
        "icon": "✅",
        "xp": 25
    },
    {
        "key": "fifty_tasks",
        "name": "Task Machine",
        "description": "Complete 50 tasks.",
        "icon": "⚡",
        "xp": 50
    },
    {
        "key": "hundred_tasks",
        "name": "Execution Master",
        "description": "Complete 100 tasks.",
        "icon": "🏆",
        "xp": 100
    },
    {
        "key": "first_habit",
        "name": "Habit Builder",
        "description": "Complete your first habit.",
        "icon": "🔥",
        "xp": 10
    },
    {
        "key": "seven_day_streak",
        "name": "Week of Discipline",
        "description": "Maintain a 7-day habit streak.",
        "icon": "🔥",
        "xp": 50
    },
    {
        "key": "thirty_day_streak",
        "name": "Unstoppable",
        "description": "Maintain a 30-day habit streak.",
        "icon": "💎",
        "xp": 150
    },
    {
        "key": "first_focus",
        "name": "Deep Focus",
        "description": "Complete your first focus session.",
        "icon": "🧠",
        "xp": 10
    },
    {
        "key": "five_hours_focus",
        "name": "Focused Worker",
        "description": "Accumulate 5 hours of focus time.",
        "icon": "⏱️",
        "xp": 50
    },
    {
        "key": "twenty_five_hours_focus",
        "name": "Focus Master",
        "description": "Accumulate 25 hours of focus time.",
        "icon": "🎯",
        "xp": 150
    },
    {
        "key": "first_goal",
        "name": "Goal Setter",
        "description": "Complete your first goal.",
        "icon": "🎯",
        "xp": 25
    },
    {
        "key": "five_goals",
        "name": "Goal Crusher",
        "description": "Complete 5 goals.",
        "icon": "🚀",
        "xp": 75
    }
]


def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# DATABASE MIGRATION
# =========================================================

def migrate_achievements_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT DEFAULT '🏆',
            xp INTEGER DEFAULT 0,
            unlocked INTEGER DEFAULT 0,
            unlocked_at TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(achievements)")
    columns = {
        row[1]
        for row in cursor.fetchall()
    }

    # Add missing columns from older LifeOS versions.
    if "key" not in columns:
        cursor.execute("""
            ALTER TABLE achievements
            ADD COLUMN key TEXT
        """)

    if "icon" not in columns:
        cursor.execute("""
            ALTER TABLE achievements
            ADD COLUMN icon TEXT DEFAULT '🏆'
        """)

    if "xp" not in columns:
        cursor.execute("""
            ALTER TABLE achievements
            ADD COLUMN xp INTEGER DEFAULT 0
        """)

    if "unlocked" not in columns:
        cursor.execute("""
            ALTER TABLE achievements
            ADD COLUMN unlocked INTEGER DEFAULT 0
        """)

    if "unlocked_at" not in columns:
        cursor.execute("""
            ALTER TABLE achievements
            ADD COLUMN unlocked_at TEXT
        """)

    # Re-read columns after migration.
    cursor.execute("PRAGMA table_info(achievements)")
    columns = {
        row[1]
        for row in cursor.fetchall()
    }

    # Fill keys for existing achievements.
    cursor.execute("""
        SELECT id, name
        FROM achievements
        WHERE key IS NULL OR key = ''
    """)

    existing_rows = cursor.fetchall()

    for achievement_id, name in existing_rows:

        matching = next(
            (
                achievement
                for achievement in ACHIEVEMENTS
                if achievement["name"] == name
            ),
            None
        )

        if matching:
            key = matching["key"]
        else:
            key = f"legacy_{achievement_id}"

        cursor.execute("""
            UPDATE achievements
            SET key = ?
            WHERE id = ?
        """, (key, achievement_id))

    # Update old achievements with the new metadata.
    for achievement in ACHIEVEMENTS:

        cursor.execute("""
            UPDATE achievements
            SET
                description = ?,
                icon = ?,
                xp = ?
            WHERE key = ?
        """, (
            achievement["description"],
            achievement["icon"],
            achievement["xp"],
            achievement["key"]
        ))

    connection.commit()
    connection.close()


# =========================================================
# INITIALIZE ACHIEVEMENTS
# =========================================================

def initialize_achievements():

    migrate_achievements_table()

    connection = get_connection()
    cursor = connection.cursor()

    for achievement in ACHIEVEMENTS:

        cursor.execute("""
            SELECT id
            FROM achievements
            WHERE key = ?
        """, (achievement["key"],))

        exists = cursor.fetchone()

        if not exists:

            cursor.execute("""
                INSERT INTO achievements
                (
                    key,
                    name,
                    description,
                    icon,
                    xp,
                    unlocked
                )
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                achievement["key"],
                achievement["name"],
                achievement["description"],
                achievement["icon"],
                achievement["xp"]
            ))

    connection.commit()
    connection.close()


# =========================================================
# CHECK ACHIEVEMENTS
# =========================================================

def check_achievements():

    initialize_achievements()

    connection = get_connection()
    cursor = connection.cursor()

    newly_unlocked = []

    # -----------------------------------------------------
    # TASK ACHIEVEMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 1
    """)

    completed_tasks = cursor.fetchone()[0] or 0

    task_requirements = [
        ("first_task", 1),
        ("ten_tasks", 10),
        ("fifty_tasks", 50),
        ("hundred_tasks", 100)
    ]

    for key, requirement in task_requirements:

        if completed_tasks >= requirement:

            newly_unlocked.extend(
                _unlock_if_needed(cursor, key)
            )

    # -----------------------------------------------------
    # HABIT ACHIEVEMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed = 1
    """)

    habit_completions = cursor.fetchone()[0] or 0

    if habit_completions >= 1:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "first_habit"
            )
        )

    cursor.execute("""
        SELECT DISTINCT habit_id
        FROM habit_logs
        WHERE completed = 1
    """)

    habit_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    for habit_id in habit_ids:

        streak = _calculate_streak(
            cursor,
            habit_id
        )

        if streak >= 7:

            newly_unlocked.extend(
                _unlock_if_needed(
                    cursor,
                    "seven_day_streak"
                )
            )

        if streak >= 30:

            newly_unlocked.extend(
                _unlock_if_needed(
                    cursor,
                    "thirty_day_streak"
                )
            )

    # -----------------------------------------------------
    # FOCUS ACHIEVEMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM focus_sessions
    """)

    focus_sessions = cursor.fetchone()[0] or 0

    if focus_sessions >= 1:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "first_focus"
            )
        )

    cursor.execute("""
        SELECT COALESCE(SUM(duration), 0)
        FROM focus_sessions
    """)

    total_focus = cursor.fetchone()[0] or 0

    if total_focus >= 300:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "five_hours_focus"
            )
        )

    if total_focus >= 1500:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "twenty_five_hours_focus"
            )
        )

    # -----------------------------------------------------
    # GOAL ACHIEVEMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE progress >= target
    """)

    completed_goals = cursor.fetchone()[0] or 0

    if completed_goals >= 1:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "first_goal"
            )
        )

    if completed_goals >= 5:

        newly_unlocked.extend(
            _unlock_if_needed(
                cursor,
                "five_goals"
            )
        )

    connection.commit()
    connection.close()

    return newly_unlocked


# =========================================================
# UNLOCK HELPER
# =========================================================

def _unlock_if_needed(cursor, key):

    cursor.execute("""
        SELECT
            name,
            description,
            icon,
            xp,
            unlocked
        FROM achievements
        WHERE key = ?
    """, (key,))

    result = cursor.fetchone()

    if not result:
        return []

    name, description, icon, xp, unlocked = result

    if unlocked:
        return []

    unlocked_at = datetime.now().isoformat()

    cursor.execute("""
        UPDATE achievements
        SET
            unlocked = 1,
            unlocked_at = ?
        WHERE key = ?
    """, (
        unlocked_at,
        key
    ))

    return [{
        "key": key,
        "name": name,
        "description": description,
        "icon": icon,
        "xp": xp
    }]


# =========================================================
# HABIT STREAK
# =========================================================

def _calculate_streak(cursor, habit_id):

    cursor.execute("""
        SELECT date
        FROM habit_logs
        WHERE habit_id = ?
          AND completed = 1
        ORDER BY date DESC
    """, (habit_id,))

    rows = cursor.fetchall()

    if not rows:
        return 0

    dates = set()

    for row in rows:

        try:
            dates.add(
                datetime.strptime(
                    row[0],
                    "%Y-%m-%d"
                ).date()
            )

        except (ValueError, TypeError):
            continue

    if not dates:
        return 0

    today = datetime.now().date()

    if today in dates:
        current_date = today

    elif today - timedelta(days=1) in dates:
        current_date = today - timedelta(days=1)

    else:
        return 0

    streak = 0

    while current_date in dates:

        streak += 1
        current_date -= timedelta(days=1)

    return streak


# =========================================================
# GET ACHIEVEMENTS
# =========================================================

def get_achievements():

    initialize_achievements()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            key,
            name,
            description,
            icon,
            xp,
            unlocked,
            unlocked_at
        FROM achievements
        ORDER BY
            unlocked DESC,
            xp ASC,
            id ASC
    """)

    achievements = cursor.fetchall()

    connection.close()

    return achievements


# =========================================================
# TOTAL XP
# =========================================================

def get_total_xp():

    initialize_achievements()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(xp), 0)
        FROM achievements
        WHERE unlocked = 1
    """)

    xp = cursor.fetchone()[0] or 0

    connection.close()

    return xp


# =========================================================
# LEVEL SYSTEM
# =========================================================

def get_level_from_xp(xp):

    if xp < 100:
        return 1

    if xp < 250:
        return 2

    if xp < 500:
        return 3

    if xp < 1000:
        return 4

    if xp < 2000:
        return 5

    return 5 + ((xp - 2000) // 500)


def get_level_progress(xp):

    level = get_level_from_xp(xp)

    if level == 1:

        current_level_xp = 0
        next_level_xp = 100

    elif level == 2:

        current_level_xp = 100
        next_level_xp = 250

    elif level == 3:

        current_level_xp = 250
        next_level_xp = 500

    elif level == 4:

        current_level_xp = 500
        next_level_xp = 1000

    elif level == 5:

        current_level_xp = 1000
        next_level_xp = 2000

    else:

        current_level_xp = (
            2000 + ((level - 5) * 500)
        )

        next_level_xp = (
            current_level_xp + 500
        )

    progress = xp - current_level_xp

    required = (
        next_level_xp - current_level_xp
    )

    percentage = (
        progress / required
        if required > 0
        else 1
    )

    return {
        "level": level,
        "current_xp": xp,
        "level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "progress_xp": progress,
        "required_xp": required,
        "percentage": min(
            max(percentage, 0),
            1
        )
    }


# =========================================================
# UNLOCKED COUNT
# =========================================================

def get_unlocked_count():

    initialize_achievements()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM achievements
        WHERE unlocked = 1
    """)

    count = cursor.fetchone()[0] or 0

    connection.close()

    return count


# =========================================================
# ACHIEVEMENT SUMMARY
# =========================================================

def get_achievement_summary():

    initialize_achievements()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM achievements
    """)

    total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM achievements
        WHERE unlocked = 1
    """)

    unlocked = cursor.fetchone()[0] or 0

    connection.close()

    xp = get_total_xp()

    return {
        "total": total,
        "unlocked": unlocked,
        "remaining": max(
            total - unlocked,
            0
        ),
        "xp": xp,
        "level": get_level_from_xp(xp)
    }