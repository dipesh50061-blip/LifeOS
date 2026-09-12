import sqlite3
from datetime import date, timedelta

DB_NAME = "lifeos.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# ADD FOCUS SESSION
# =========================================================

def add_focus_session(duration, session_type="Focus"):

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today().isoformat()

    # Add session_type column if it doesn't exist
    try:
        cursor.execute(
            """
            ALTER TABLE focus_sessions
            ADD COLUMN session_type TEXT DEFAULT 'Focus'
            """
        )
        connection.commit()

    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
        INSERT INTO focus_sessions
        (
            duration,
            session_date,
            session_type
        )
        VALUES (?, ?, ?)
        """,
        (
            duration,
            today,
            session_type
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# GET ALL FOCUS SESSIONS
# =========================================================

def get_focus_sessions():

    connection = get_connection()
    cursor = connection.cursor()

    # Make sure column exists
    try:
        cursor.execute(
            """
            ALTER TABLE focus_sessions
            ADD COLUMN session_type TEXT DEFAULT 'Focus'
            """
        )
        connection.commit()

    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
        SELECT
            id,
            duration,
            session_date,
            session_type
        FROM focus_sessions
        ORDER BY
            session_date DESC,
            id DESC
        """
    )

    sessions = cursor.fetchall()

    connection.close()

    return sessions


# =========================================================
# TODAY'S FOCUS TIME
# =========================================================

def get_today_focus_time():

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today().isoformat()

    cursor.execute(
        """
        SELECT COALESCE(
            SUM(duration),
            0
        )
        FROM focus_sessions
        WHERE session_date = ?
        """,
        (
            today,
        )
    )

    total = cursor.fetchone()[0]

    connection.close()

    return total or 0


# =========================================================
# TOTAL FOCUS TIME
# =========================================================

def get_total_focus_time():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COALESCE(
            SUM(duration),
            0
        )
        FROM focus_sessions
        """
    )

    total = cursor.fetchone()[0]

    connection.close()

    return total or 0


# =========================================================
# FOCUS BY SESSION TYPE
# =========================================================

def get_focus_by_type():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            session_type,
            COALESCE(SUM(duration), 0)
        FROM focus_sessions
        GROUP BY session_type
        ORDER BY
            SUM(duration) DESC
        """
    )

    results = cursor.fetchall()

    connection.close()

    return results


# =========================================================
# DAILY FOCUS HISTORY
# =========================================================

def get_daily_focus_history(days=30):

    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today()
        - timedelta(days=days - 1)
    )

    cursor.execute(
        """
        SELECT
            session_date,
            COALESCE(SUM(duration), 0)
        FROM focus_sessions
        WHERE session_date >= ?
        GROUP BY session_date
        ORDER BY session_date
        """,
        (
            start_date.isoformat(),
        )
    )

    rows = cursor.fetchall()

    connection.close()

    logged_dates = {
        row[0]: row[1]
        for row in rows
    }

    result = []

    for i in range(days):

        current_date = (
            start_date
            + timedelta(days=i)
        )

        date_string = (
            current_date.isoformat()
        )

        result.append(
            (
                date_string,
                logged_dates.get(
                    date_string,
                    0
                )
            )
        )

    return result


# =========================================================
# WEEKLY FOCUS TOTAL
# =========================================================

def get_weekly_focus_time():

    connection = get_connection()
    cursor = connection.cursor()

    start_date = (
        date.today()
        - timedelta(days=6)
    )

    cursor.execute(
        """
        SELECT COALESCE(
            SUM(duration),
            0
        )
        FROM focus_sessions
        WHERE session_date >= ?
        """,
        (
            start_date.isoformat(),
        )
    )

    total = cursor.fetchone()[0]

    connection.close()

    return total or 0


# =========================================================
# AVERAGE SESSION LENGTH
# =========================================================

def get_average_session_length():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COALESCE(
                AVG(duration),
                0
            )
        FROM focus_sessions
        """
    )

    average = cursor.fetchone()[0]

    connection.close()

    return round(
        average or 0,
        1
    )


# =========================================================
# FOCUS SESSION COUNT
# =========================================================

def get_focus_session_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM focus_sessions
        """
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count or 0


# =========================================================
# FOCUS STREAK
# =========================================================

def get_focus_streak():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT session_date
        FROM focus_sessions
        ORDER BY session_date DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    if not rows:
        return 0

    focus_dates = {
        date.fromisoformat(row[0])
        for row in rows
    }

    today = date.today()

    if today in focus_dates:

        current_date = today

    else:

        current_date = today - timedelta(days=1)

    streak = 0

    while current_date in focus_dates:

        streak += 1

        current_date -= timedelta(days=1)

    return streak


# =========================================================
# DELETE FOCUS SESSION
# =========================================================

def delete_focus_session(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM focus_sessions
        WHERE id = ?
        """,
        (
            session_id,
        )
    )

    connection.commit()
    connection.close()