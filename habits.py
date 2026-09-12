import sqlite3
from datetime import datetime, date, timedelta

DB_NAME = "lifeos.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# ADD HABIT
# =========================================================

def add_habit(name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO habits
        (
            name,
            created_at
        )
        VALUES (?, ?)
        """,
        (
            name,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# GET HABITS
# =========================================================

def get_habits():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name
        FROM habits
        ORDER BY id DESC
        """
    )

    habits = cursor.fetchall()

    connection.close()

    return habits


# =========================================================
# LOG HABIT
# =========================================================

def log_habit(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today().isoformat()

    cursor.execute(
        """
        SELECT id
        FROM habit_logs
        WHERE habit_id = ?
        AND date = ?
        """,
        (
            habit_id,
            today
        )
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE habit_logs
            SET completed = 1
            WHERE id = ?
            """,
            (
                existing[0],
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO habit_logs
            (
                habit_id,
                date,
                completed
            )
            VALUES (?, ?, 1)
            """,
            (
                habit_id,
                today
            )
        )

    connection.commit()
    connection.close()


# =========================================================
# CHECK TODAY
# =========================================================

def is_habit_completed_today(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today().isoformat()

    cursor.execute(
        """
        SELECT completed
        FROM habit_logs
        WHERE habit_id = ?
        AND date = ?
        """,
        (
            habit_id,
            today
        )
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0] == 1

    return False


# =========================================================
# CURRENT STREAK
# =========================================================

def calculate_current_streak(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT date
        FROM habit_logs
        WHERE habit_id = ?
        AND completed = 1
        ORDER BY date DESC
        """,
        (
            habit_id,
        )
    )

    rows = cursor.fetchall()

    connection.close()

    if not rows:
        return 0

    completed_dates = {
        date.fromisoformat(row[0])
        for row in rows
    }

    today = date.today()

    # If the habit wasn't completed today,
    # start checking from yesterday.
    if today not in completed_dates:

        current_date = today - timedelta(days=1)

    else:

        current_date = today

    streak = 0

    while current_date in completed_dates:

        streak += 1

        current_date -= timedelta(days=1)

    return streak


# =========================================================
# BEST STREAK
# =========================================================

def calculate_best_streak(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT date
        FROM habit_logs
        WHERE habit_id = ?
        AND completed = 1
        ORDER BY date
        """,
        (
            habit_id,
        )
    )

    rows = cursor.fetchall()

    connection.close()

    if not rows:
        return 0

    completed_dates = sorted(
        {
            date.fromisoformat(row[0])
            for row in rows
        }
    )

    best_streak = 1
    current_streak = 1

    for index in range(
        1,
        len(completed_dates)
    ):

        difference = (
            completed_dates[index]
            - completed_dates[index - 1]
        ).days

        if difference == 1:

            current_streak += 1

        else:

            current_streak = 1

        best_streak = max(
            best_streak,
            current_streak
        )

    return best_streak


# =========================================================
# COMPLETION PERCENTAGE
# =========================================================

def get_habit_completion_percentage(
    habit_id,
    days=30
):

    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today()
        - timedelta(days=days - 1)
    ).isoformat()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM habit_logs
        WHERE habit_id = ?
        AND date >= ?
        AND completed = 1
        """,
        (
            habit_id,
            start_date
        )
    )

    completed_days = (
        cursor.fetchone()[0]
        or 0
    )

    connection.close()

    if days <= 0:
        return 0

    return round(
        (completed_days / days) * 100
    )


# =========================================================
# LAST 7 DAYS
# =========================================================

def get_last_7_days(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today()
        - timedelta(days=6)
    )

    cursor.execute(
        """
        SELECT
            date,
            completed
        FROM habit_logs
        WHERE habit_id = ?
        AND date >= ?
        ORDER BY date
        """,
        (
            habit_id,
            start_date.isoformat()
        )
    )

    rows = cursor.fetchall()

    connection.close()

    logged_dates = {
        row[0]: row[1]
        for row in rows
    }

    result = []

    for i in range(7):

        current_date = (
            start_date
            + timedelta(days=i)
        )

        date_string = (
            current_date.isoformat()
        )

        completed = (
            logged_dates.get(
                date_string,
                0
            )
        )

        result.append(
            (
                date_string,
                completed
            )
        )

    return result


# =========================================================
# LAST 30 DAYS
# =========================================================

def get_last_30_days(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today()
        - timedelta(days=29)
    )

    cursor.execute(
        """
        SELECT
            date,
            completed
        FROM habit_logs
        WHERE habit_id = ?
        AND date >= ?
        ORDER BY date
        """,
        (
            habit_id,
            start_date.isoformat()
        )
    )

    rows = cursor.fetchall()

    connection.close()

    logged_dates = {
        row[0]: row[1]
        for row in rows
    }

    result = []

    for i in range(30):

        current_date = (
            start_date
            + timedelta(days=i)
        )

        date_string = (
            current_date.isoformat()
        )

        completed = (
            logged_dates.get(
                date_string,
                0
            )
        )

        result.append(
            (
                date_string,
                completed
            )
        )

    return result


# =========================================================
# HABIT SUMMARY
# =========================================================

def get_habit_summary(habit_id):

    current_streak = calculate_current_streak(
        habit_id
    )

    best_streak = calculate_best_streak(
        habit_id
    )

    weekly_percentage = (
        get_habit_completion_percentage(
            habit_id,
            7
        )
    )

    monthly_percentage = (
        get_habit_completion_percentage(
            habit_id,
            30
        )
    )

    completed_today = (
        is_habit_completed_today(
            habit_id
        )
    )

    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
        "weekly_percentage": weekly_percentage,
        "monthly_percentage": monthly_percentage,
        "completed_today": completed_today
    }


# =========================================================
# DELETE HABIT
# =========================================================

def delete_habit(habit_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM habit_logs
        WHERE habit_id = ?
        """,
        (
            habit_id,
        )
    )

    cursor.execute(
        """
        DELETE FROM habits
        WHERE id = ?
        """,
        (
            habit_id,
        )
    )

    connection.commit()
    connection.close()