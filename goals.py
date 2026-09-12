import sqlite3
from datetime import datetime, date

DB_NAME = "lifeos.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# ADD GOAL
# =========================================================

def add_goal(title, target, deadline=None):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    # Add deadline column if it does not exist yet
    try:
        cursor.execute(
            """
            ALTER TABLE goals
            ADD COLUMN deadline TEXT
            """
        )
    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
        INSERT INTO goals
        (
            title,
            target,
            progress,
            created_at,
            deadline
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            target,
            0,
            created_at,
            deadline.isoformat()
            if deadline
            else None
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# GET GOALS
# =========================================================

def get_goals():

    connection = get_connection()
    cursor = connection.cursor()

    # Make sure deadline exists
    try:
        cursor.execute(
            """
            ALTER TABLE goals
            ADD COLUMN deadline TEXT
            """
        )

        connection.commit()

    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
        SELECT
            id,
            title,
            target,
            progress,
            created_at,
            deadline
        FROM goals
        ORDER BY
            CASE
                WHEN progress >= target THEN 1
                ELSE 0
            END,
            deadline IS NULL,
            deadline,
            id DESC
        """
    )

    goals = cursor.fetchall()

    connection.close()

    return goals


# =========================================================
# UPDATE GOAL PROGRESS
# =========================================================

def update_goal_progress(goal_id, progress):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE goals
        SET progress = ?
        WHERE id = ?
        """,
        (
            progress,
            goal_id
        )
    )

    # Record progress history
    cursor.execute(
        """
        INSERT INTO goal_history
        (
            goal_id,
            progress,
            recorded_at
        )
        VALUES (?, ?, ?)
        """,
        (
            goal_id,
            progress,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# UPDATE GOAL DETAILS
# =========================================================

def update_goal(
    goal_id,
    title,
    target,
    deadline=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE goals
        SET
            title = ?,
            target = ?,
            deadline = ?
        WHERE id = ?
        """,
        (
            title,
            target,
            deadline.isoformat()
            if deadline
            else None,
            goal_id
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# DELETE GOAL
# =========================================================

def delete_goal(goal_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Delete history first
    cursor.execute(
        """
        DELETE FROM goal_history
        WHERE goal_id = ?
        """,
        (goal_id,)
    )

    cursor.execute(
        """
        DELETE FROM goals
        WHERE id = ?
        """,
        (goal_id,)
    )

    connection.commit()
    connection.close()


# =========================================================
# GET GOAL HISTORY
# =========================================================

def get_goal_history(goal_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            progress,
            recorded_at
        FROM goal_history
        WHERE goal_id = ?
        ORDER BY recorded_at
        """,
        (goal_id,)
    )

    history = cursor.fetchall()

    connection.close()

    return history


# =========================================================
# GOAL PERCENTAGE
# =========================================================

def get_goal_percentage(progress, target):

    if target <= 0:
        return 0

    percentage = (
        progress / target
    ) * 100

    return min(
        round(percentage),
        100
    )


# =========================================================
# GOAL STATUS
# =========================================================

def get_goal_status(
    progress,
    target,
    deadline=None
):

    if target <= 0:
        return "⚪ No Target"

    if progress >= target:
        return "🏆 Completed"

    if not deadline:
        return "🔵 In Progress"

    try:

        deadline_date = (
            date.fromisoformat(deadline)
            if isinstance(deadline, str)
            else deadline
        )

        today = date.today()

        days_remaining = (
            deadline_date - today
        ).days

        percentage = (
            progress / target
        )

        # Deadline passed
        if days_remaining < 0:
            return "🔴 Overdue"

        # Very close deadline
        if days_remaining <= 3:

            if percentage >= 0.75:
                return "🟢 On Track"

            return "🟠 At Risk"

        # Normal deadline
        if percentage >= 0.5:
            return "🟢 On Track"

        return "🟡 In Progress"

    except (ValueError, TypeError):

        return "🔵 In Progress"


# =========================================================
# DAYS REMAINING
# =========================================================

def get_days_remaining(deadline):

    if not deadline:
        return None

    try:

        deadline_date = (
            date.fromisoformat(deadline)
            if isinstance(deadline, str)
            else deadline
        )

        return (
            deadline_date - date.today()
        ).days

    except (ValueError, TypeError):

        return None