import streamlit as st
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import time


# =========================================================
# LIFEOS CONSTANTS & HELPERS
# =========================================================

PRIORITIES = ["Low", "Medium", "High"]
CATEGORIES = [
    "General",
    "Work",
    "Study",
    "Personal",
    "Health",
    "Project"
]

NOTE_CATEGORIES = [
    "General",
    "Study",
    "Work",
    "Project",
    "Ideas",
    "Personal"
]


def priority_icon(priority):
    return {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢"
    }.get(priority, "⚪")


def format_minutes(minutes):
    minutes = int(minutes or 0)
    hours = minutes // 60
    remaining = minutes % 60

    if hours:
        return f"{hours}h {remaining}m"

    return f"{remaining} min"


def safe_progress(value, target):
    if not target:
        return 0.0

    return min(max(value / target, 0), 1)


def get_today_tasks(tasks):
    today = date.today().isoformat()

    return [
        task
        for task in tasks
        if task[4] == today
    ]


from database import initialize_database

from tasks import (
    add_task,
    get_tasks,
    complete_task,
    reopen_task,
    update_task,
    delete_task
)

from habits import (
    add_habit,
    get_habits,
    log_habit,
    is_habit_completed_today,
    calculate_current_streak,
    calculate_best_streak,
    get_habit_completion_percentage,
    get_last_7_days,
    get_last_30_days,
    get_habit_summary,
    delete_habit
)

from goals import (
    add_goal,
    get_goals,
    update_goal_progress,
    update_goal,
    delete_goal,
    get_goal_history,
    get_goal_percentage,
    get_goal_status,
    get_days_remaining
)

from focus import (
    add_focus_session,
    get_focus_sessions,
    get_today_focus_time,
    delete_focus_session,
    get_total_focus_time,
    get_focus_by_type,
    get_daily_focus_history,
    get_weekly_focus_time,
    get_average_session_length,
    get_focus_session_count,
    get_focus_streak
)

from analytics import (
    get_task_stats,
    get_habit_stats,
    get_goal_stats,
    calculate_productivity_score,
    get_daily_task_stats,
    get_daily_focus_stats,
    get_daily_habit_stats,
    get_weekly_task_stats,
    get_weekly_focus_stats,
    get_weekly_habit_stats,
    get_overall_focus_time,
    get_overall_habit_completions,
    get_goal_progress_stats,
    get_productivity_summary,
    get_today_summary,
    get_consistency_score,
    get_best_focus_day,
    get_best_task_day,
    get_total_completed_tasks,
    get_total_completed_goals,
    get_productivity_insights
)

from notes import (
    add_note,
    get_notes,
    update_note,
    toggle_pin,
    delete_note,
    get_note_statistics
)

from achievements import (
    initialize_achievements,
    check_achievements,
    get_achievements,
    get_unlocked_count,
    get_total_xp,
    get_level_from_xp,
    get_level_progress,
    get_achievement_summary
)

from weekly_review import get_weekly_review

from search import global_search

from settings import (
    initialize_settings,
    get_setting,
    update_setting,
    get_all_settings
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LifeOS",
    page_icon="🚀",
    layout="wide"
)


# =========================================================
# LOAD CUSTOM CSS
# =========================================================

css_path = Path("style.css")

if css_path.exists():

    with open(
        css_path,
        "r",
        encoding="utf-8"
    ) as file:

        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

initialize_database()

initialize_settings()

initialize_achievements()
check_achievements()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("# 🚀 LifeOS")

st.sidebar.caption(
    "Personal Productivity System"
)

st.sidebar.divider()

# Quick sidebar status
_sidebar_tasks = get_tasks()
_sidebar_habits = get_habits()
_sidebar_today_tasks = get_today_tasks(_sidebar_tasks)
_sidebar_completed_tasks = sum(
    1 for task in _sidebar_today_tasks if task[5] == 1
)
_sidebar_completed_habits = sum(
    1 for habit in _sidebar_habits
    if is_habit_completed_today(habit[0])
)

st.sidebar.metric(
    "Today's Progress",
    f"{_sidebar_completed_tasks}/{len(_sidebar_today_tasks)} tasks"
)
st.sidebar.caption(
    f"🔥 {_sidebar_completed_habits}/{len(_sidebar_habits)} habits completed"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📅 Today",
        "📋 Tasks",
        "🔥 Habits",
        "🎯 Goals",
        "⏱️ Focus",
        "📝 Notes",
        "📈 Analytics",
        "🏆 Achievements",
        "📊 Weekly Review",
        "⚙️ Settings"
    ]
)

# =========================================================
# GLOBAL SEARCH
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("🔎 Global Search")

search_query = st.sidebar.text_input(
    "Search LifeOS",
    placeholder="Tasks, habits, goals, notes...",
    key="global_search_input"
)

if search_query.strip():
    st.sidebar.caption("Press Enter or continue typing to search your workspace.")

# =========================================================
# SEARCH RESULTS
# =========================================================

if search_query.strip():

    search_results = global_search(search_query)

    total_results = (
        len(search_results["tasks"])
        + len(search_results["habits"])
        + len(search_results["goals"])
        + len(search_results["notes"])
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        f"**🔎 {total_results} result(s) found**"
    )

    # -------------------------
    # Tasks
    # -------------------------

    if search_results["tasks"]:

        st.sidebar.markdown(
            f"### 📋 Tasks ({len(search_results['tasks'])})"
        )

        for task in search_results["tasks"]:

            (
                task_id,
                title,
                priority,
                category,
                due_date,
                completed
            ) = task

            status = "✅" if completed else "⬜"

            st.sidebar.write(
                f"{status} **{title}**"
            )

            details = f"{priority} • {category}"

            if due_date:
                details += f" • Due: {due_date}"

            st.sidebar.caption(details)

    # -------------------------
    # Habits
    # -------------------------

    if search_results["habits"]:

        st.sidebar.markdown(
            f"### 🔥 Habits ({len(search_results['habits'])})"
        )

        for habit in search_results["habits"]:

            habit_id, name = habit

            st.sidebar.write(
                f"🔥 **{name}**"
            )

    # -------------------------
    # Goals
    # -------------------------

    if search_results["goals"]:

        st.sidebar.markdown(
            f"### 🎯 Goals ({len(search_results['goals'])})"
        )

        for goal in search_results["goals"]:

            (
                goal_id,
                title,
                target,
                progress
            ) = goal

            st.sidebar.write(
                f"🎯 **{title}**"
            )

            st.sidebar.caption(
                f"Progress: {progress}/{target}"
            )

    # -------------------------
    # Notes
    # -------------------------

    if search_results["notes"]:

        st.sidebar.markdown(
            f"### 📝 Notes ({len(search_results['notes'])})"
        )

        for note in search_results["notes"]:

            (
                note_id,
                title,
                content,
                category,
                pinned,
                created_at,
                updated_at
            ) = note

            pin_icon = "📌 " if pinned else ""

            st.sidebar.write(
                f"{pin_icon}**{title}**"
            )

            st.sidebar.caption(
                category
            )

    # -------------------------
    # No Results
    # -------------------------

    if total_results == 0:

        st.sidebar.info(
            "No matching items found."
        )

# =========================================================
# DASHBOARD 2.0
# =========================================================

if page == "📊 Dashboard":

    # =====================================================
    # LOAD DATA
    # =====================================================

    username = get_setting("username")

    today_summary = get_today_summary()
    productivity_score = calculate_productivity_score()
    consistency_score = get_consistency_score()

    achievement_summary = get_achievement_summary()
    level_progress = get_level_progress(
        achievement_summary["xp"]
    )

    insights = get_productivity_insights()

    # =====================================================
    # HEADER
    # =====================================================

    st.title(
        f"🚀 Welcome, {username}"
    )

    st.caption(
        "Your personal productivity command center."
    )

    st.divider()

    # =====================================================
    # TODAY OVERVIEW
    # =====================================================

    st.subheader("📊 Today's Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📋 Tasks",
            f"{today_summary['task_completed']}/"
            f"{today_summary['task_total']}"
        )

    with col2:

        st.metric(
            "🔥 Habits",
            f"{today_summary['habit_completed']}/"
            f"{today_summary['habit_total']}"
        )

    with col3:

        st.metric(
            "⏱️ Focus",
            f"{today_summary['focus_minutes']} min"
        )

    with col4:

        st.metric(
            "⚡ Productivity",
            f"{productivity_score}/100"
        )

    # =====================================================
    # PRODUCTIVITY SCORE
    # =====================================================

    st.divider()

    st.subheader("⚡ Today's Productivity")

    score_col1, score_col2 = st.columns(
        [1, 3]
    )

    with score_col1:

        st.metric(
            "Productivity Score",
            f"{productivity_score}/100"
        )

    with score_col2:

        st.write("Daily Performance")

        st.progress(
            productivity_score / 100
        )

        st.caption(
            f"{productivity_score}% of your "
            "productivity score achieved."
        )

    if productivity_score >= 80:

        st.success(
            "🔥 Excellent execution today."
        )

    elif productivity_score >= 60:

        st.info(
            "💪 Solid progress. Keep the momentum."
        )

    elif productivity_score >= 40:

        st.warning(
            "📈 You're moving, but there is room "
            "to improve today's execution."
        )

    else:

        st.error(
            "🎯 Today's performance needs attention."
        )

    # =====================================================
    # PROGRESS BREAKDOWN
    # =====================================================

    st.divider()

    st.subheader("📈 Today's Progress")

    progress_col1, progress_col2, progress_col3 = (
        st.columns(3)
    )

    # -------------------------
    # Tasks
    # -------------------------

    with progress_col1:

        task_total = today_summary["task_total"]
        task_completed = today_summary["task_completed"]

        task_progress = (
            task_completed / task_total
            if task_total > 0
            else 0
        )

        st.write("📋 Tasks")

        st.progress(
            task_progress
        )

        st.caption(
            f"{task_completed}/{task_total} completed "
            f"({task_progress * 100:.0f}%)"
        )

    # -------------------------
    # Habits
    # -------------------------

    with progress_col2:

        habit_total = today_summary["habit_total"]
        habit_completed = today_summary["habit_completed"]

        habit_progress = (
            habit_completed / habit_total
            if habit_total > 0
            else 0
        )

        st.write("🔥 Habits")

        st.progress(
            habit_progress
        )

        st.caption(
            f"{habit_completed}/{habit_total} completed "
            f"({habit_progress * 100:.0f}%)"
        )

    # -------------------------
    # Focus
    # -------------------------

    with progress_col3:

        daily_focus_goal = int(
            get_setting("daily_focus_goal")
        )

        focus_progress = (
            min(
                today_summary["focus_minutes"]
                / daily_focus_goal,
                1
            )
            if daily_focus_goal > 0
            else 0
        )

        st.write("⏱️ Focus")

        st.progress(
            focus_progress
        )

        st.caption(
            f"{today_summary['focus_minutes']}/"
            f"{daily_focus_goal} minutes"
        )

    # =====================================================
    # CONSISTENCY + LEVEL
    # =====================================================

    st.divider()

    st.subheader("🔥 Momentum")

    momentum_col1, momentum_col2 = st.columns(2)

    # -------------------------
    # Consistency
    # -------------------------

    with momentum_col1:

        st.write("🔥 7-Day Consistency")

        st.metric(
            "Consistency Score",
            f"{consistency_score}%"
        )

        st.progress(
            consistency_score / 100
        )

        if consistency_score >= 80:

            st.caption(
                "Excellent consistency."
            )

        elif consistency_score >= 50:

            st.caption(
                "You're building a reliable rhythm."
            )

        else:

            st.caption(
                "Build consistency one day at a time."
            )

    # -------------------------
    # XP / Level
    # -------------------------

    with momentum_col2:

        st.write("🏆 LifeOS Level")

        st.metric(
            "Level",
            level_progress["level"]
        )

        st.progress(
            level_progress["percentage"]
        )

        st.caption(
            f"{level_progress['progress_xp']} / "
            f"{level_progress['required_xp']} XP "
            f"to Level "
            f"{level_progress['level'] + 1}"
        )

    # =====================================================
    # DAILY TARGETS
    # =====================================================

    st.divider()

    st.subheader("🎯 Daily Targets")

    daily_task_goal = int(
        get_setting("daily_task_goal")
    )

    daily_focus_goal = int(
        get_setting("daily_focus_goal")
    )

    target_col1, target_col2 = st.columns(2)

    # -------------------------
    # Task Target
    # -------------------------

    with target_col1:

        task_target_progress = (
            min(
                today_summary["task_completed"]
                / daily_task_goal,
                1
            )
            if daily_task_goal > 0
            else 0
        )

        st.write(
            f"📋 Task Target: "
            f"{daily_task_goal}"
        )

        st.progress(
            task_target_progress
        )

        st.caption(
            f"{today_summary['task_completed']} / "
            f"{daily_task_goal} tasks"
        )

    # -------------------------
    # Focus Target
    # -------------------------

    with target_col2:

        focus_target_progress = (
            min(
                today_summary["focus_minutes"]
                / daily_focus_goal,
                1
            )
            if daily_focus_goal > 0
            else 0
        )

        st.write(
            f"⏱️ Focus Target: "
            f"{daily_focus_goal} minutes"
        )

        st.progress(
            focus_target_progress
        )

        st.caption(
            f"{today_summary['focus_minutes']} / "
            f"{daily_focus_goal} minutes"
        )

    if (
        today_summary["task_completed"]
        >= daily_task_goal
        and
        today_summary["focus_minutes"]
        >= daily_focus_goal
    ):

        st.success(
            "🎉 Both daily targets completed!"
        )

    elif (
        today_summary["task_completed"]
        >= daily_task_goal
        or
        today_summary["focus_minutes"]
        >= daily_focus_goal
    ):

        st.info(
            "💪 One daily target is complete. "
            "Finish the other."
        )

    else:

        st.caption(
            "Keep working toward today's targets."
        )

    # =====================================================
    # INSIGHTS
    # =====================================================

    st.divider()

    st.subheader("💡 LifeOS Insights")

    if insights:

        for insight in insights:

            st.write(
                f"• {insight}"
            )

    else:

        st.info(
            "Complete more activities to generate insights."
        )

    # =====================================================
    # QUICK STATUS
    # =====================================================

    st.divider()

    st.subheader("⚡ Quick Status")

    status_col1, status_col2, status_col3 = (
        st.columns(3)
    )

    # -------------------------
    # Tasks
    # -------------------------

    with status_col1:

        if today_summary["task_total"] == 0:

            st.info(
                "📋 No tasks scheduled today."
            )

        elif (
            today_summary["task_completed"]
            == today_summary["task_total"]
        ):

            st.success(
                "📋 All today's tasks are complete."
            )

        else:

            pending = (
                today_summary["task_total"]
                - today_summary["task_completed"]
            )

            st.warning(
                f"📋 {pending} task(s) remaining."
            )

    # -------------------------
    # Habits
    # -------------------------

    with status_col2:

        if today_summary["habit_total"] == 0:

            st.info(
                "🔥 No habits configured."
            )

        elif (
            today_summary["habit_completed"]
            == today_summary["habit_total"]
        ):

            st.success(
                "🔥 All habits completed today."
            )

        else:

            remaining = (
                today_summary["habit_total"]
                - today_summary["habit_completed"]
            )

            st.warning(
                f"🔥 {remaining} habit(s) remaining."
            )

    # -------------------------
    # Focus
    # -------------------------

    with status_col3:

        if today_summary["focus_minutes"] == 0:

            st.info(
                "⏱️ No focus time recorded yet."
            )

        elif (
            today_summary["focus_minutes"]
            >= daily_focus_goal
        ):

            st.success(
                "⏱️ Daily focus target reached."
            )

        else:

            remaining_focus = (
                daily_focus_goal
                - today_summary["focus_minutes"]
            )

            st.warning(
                f"⏱️ {remaining_focus} min "
                "of focus remaining."
            )

    # =====================================================
    # FOOTER
    # =====================================================

    st.divider()

    st.caption(
        "🚀 LifeOS Dashboard 2.0 • "
        "Plan less. Execute more."
    )
    

# =========================================================
# TODAY
# =========================================================


elif page == "📅 Today":

    st.markdown("## 📅 Today")
    st.caption(
        f"{date.today().strftime('%A, %d %B %Y')}"
    )

    # -------------------------
    # Load Data
    # -------------------------

    tasks = get_tasks()
    habits = get_habits()
    goals = get_goals()

    # -------------------------
    # Today's Task Statistics
    # -------------------------

    # Keep the Today page focused on today's workload rather than
    # accidentally mixing it with the lifetime task total.
    overdue_today = [
        task for task in tasks
        if task[4] and task[4] < date.today().isoformat() and task[5] == 0
    ]


    today = date.today()

    today_tasks = []

    for task in tasks:

        task_id = task[0]
        task_title = task[1]
        task_priority = task[2]
        task_category = task[3]
        task_due_date = task[4]
        task_completed = task[5]

        if task_due_date:

            try:

                task_date = date.fromisoformat(
                    task_due_date
                )

                if task_date == today:

                    today_tasks.append(task)

            except ValueError:

                pass

    total_today_tasks = len(today_tasks)

    completed_today_tasks = sum(
        1
        for task in today_tasks
        if task[5] == 1
    )

    pending_today_tasks = (
        total_today_tasks
        - completed_today_tasks
    )

    # -------------------------
    # Habit Statistics
    # -------------------------

    total_habits = len(habits)

    completed_habits = sum(
        1
        for habit in habits
        if is_habit_completed_today(
            habit[0]
        )
    )

    # -------------------------
    # Goal Statistics
    # -------------------------

    active_goals = [
        goal
        for goal in goals
        if goal[3] < goal[2]
    ]

    completed_goals = sum(
        1
        for goal in goals
        if goal[3] >= goal[2]
    )

    # -------------------------
    # Focus Statistics
    # -------------------------

    today_focus = get_today_focus_time()

    focus_hours = today_focus // 60
    focus_minutes = today_focus % 60

    # -------------------------
    # Overview Metrics
    # -------------------------

    st.markdown("### 📊 Today's Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📋 Tasks",
            f"{completed_today_tasks}/{total_today_tasks}"
        )

    with col2:

        st.metric(
            "🔥 Habits",
            f"{completed_habits}/{total_habits}"
        )

    with col3:

        st.metric(
            "🎯 Active Goals",
            len(active_goals)
        )

    with col4:

        if focus_hours > 0:

            focus_display = (
                f"{focus_hours}h {focus_minutes}m"
            )

        else:

            focus_display = (
                f"{focus_minutes} min"
            )

        st.metric(
            "⏱️ Focus",
            focus_display
        )

    st.divider()

    # -------------------------
    # Today's Tasks
    # -------------------------

    task_col, habit_col = st.columns(2)

    with task_col:

        st.markdown("### 📋 Today's Tasks")

        if not today_tasks:

            st.info(
                "No tasks scheduled for today."
            )

        else:

            for task in today_tasks:

                (
                    task_id,
                    task_title,
                    task_priority,
                    task_category,
                    task_due_date,
                    task_completed
                ) = task

                if task_completed:

                    st.markdown(
                        f"✅ ~~{task_title}~~"
                    )

                else:

                    priority_icon = {
                        "High": "🔴",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }.get(
                        task_priority,
                        "⚪"
                    )

                    st.markdown(
                        f"⬜ {priority_icon} "
                        f"**{task_title}**"
                    )

                    st.caption(
                        f"🏷️ {task_category}"
                    )

                    if st.button(
                        "Complete",
                        key=f"today_task_{task_id}"
                    ):

                        complete_task(task_id)
                        check_achievements()
                        st.rerun()

    # -------------------------
    # Today's Habits
    # -------------------------

    with habit_col:

        st.markdown("### 🔥 Today's Habits")

        if not habits:

            st.info(
                "No habits created yet."
            )

        else:

            for habit in habits:

                habit_id = habit[0]
                habit_name = habit[1]

                completed = (
                    is_habit_completed_today(
                        habit_id
                    )
                )

                current_streak = (
                    calculate_current_streak(
                        habit_id
                    )
                )

                if completed:

                    st.success(
                        f"✅ {habit_name} "
                        f"• 🔥 {current_streak} day streak"
                    )

                else:

                    st.warning(
                        f"○ {habit_name}"
                    )

                    if st.button(
                        "Complete",
                        key=f"today_habit_{habit_id}"
                    ):

                        log_habit(habit_id)
                        check_achievements()
                        st.rerun()

    if overdue_today:
        st.markdown("### 🔴 Overdue Tasks")

        for task in overdue_today[:5]:
            st.error(
                f"{priority_icon(task[2])} **{task[1]}** • Due {task[4]}"
            )

        if len(overdue_today) > 5:
            st.caption(
                f"+ {len(overdue_today) - 5} more overdue task(s)."
            )

    st.divider()

    # -------------------------
    # Goals
    # -------------------------

    st.markdown("### 🎯 Goals")

    if not goals:

        st.info(
            "No goals created yet."
        )

    else:

        goal_columns = st.columns(
            min(len(goals), 3)
        )

        for index, goal in enumerate(goals):

            goal_id = goal[0]
            goal_title = goal[1]
            target = goal[2]
            progress = goal[3]

            percentage = min(
                progress / target,
                1
            ) if target > 0 else 0

            with goal_columns[
                index % len(goal_columns)
            ]:

                st.markdown(
                    f"**{goal_title}**"
                )

                st.progress(
                    percentage
                )

                st.caption(
                    f"{progress} / {target} "
                    f"({round(percentage * 100)}%)"
                )

    st.divider()

    # -------------------------
    # Daily Productivity
    # -------------------------

    st.markdown(
        "### 📈 Today's Productivity"
    )

    productivity_score = (
        calculate_productivity_score()
    )

    st.metric(
        "Productivity Score",
        f"{productivity_score}/100"
    )

    st.progress(
        safe_progress(productivity_score, 100)
    )

    if productivity_score >= 80:

        st.success(
            "🔥 Excellent day. Keep the momentum."
        )

    elif productivity_score >= 50:

        st.info(
            "💪 Solid progress. There is still room to improve."
        )

    else:

        st.warning(
            "🚀 Get one small win done and build from there."
        )

# =========================================================
# TASKS
# =========================================================

elif page == "📋 Tasks":

    st.title("📋 Tasks")
    st.caption(
        "Manage, prioritize, and complete your tasks."
    )

    # -------------------------
    # ADD TASK
    # -------------------------

    st.subheader("➕ Add Task")

    with st.form("add_task_form"):

        task_title = st.text_input(
            "Task Title",
            placeholder="Enter task name..."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            task_priority = st.selectbox(
                "Priority",
                PRIORITIES
            )

        with col2:

            task_category = st.selectbox(
                "Category",
                CATEGORIES
            )

        with col3:

            task_due_date = st.date_input(
                "Due Date",
                value=date.today()
            )

        add_task_button = st.form_submit_button(
            "➕ Add Task"
        )

        if add_task_button:

            if task_title.strip():

                add_task(
                    task_title.strip(),
                    task_priority,
                    task_category,
                    task_due_date.isoformat()
                )

                st.success(
                    "Task added successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter a task title."
                )

    st.divider()

    # -------------------------
    # GET TASKS
    # -------------------------

    tasks = get_tasks()

    # -------------------------
    # TASK STATISTICS
    # -------------------------

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if task[5] == 1
    )

    pending_tasks = total_tasks - completed_tasks

    today = date.today().isoformat()

    overdue_tasks = sum(
        1
        for task in tasks
        if (
            task[4]
            and task[4] < today
            and task[5] == 0
        )
    )

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:

        st.metric(
            "Total",
            total_tasks
        )

    with stat_col2:

        st.metric(
            "Completed",
            completed_tasks
        )

    with stat_col3:

        st.metric(
            "Pending",
            pending_tasks
        )

    with stat_col4:

        st.metric(
            "🔴 Overdue",
            overdue_tasks
        )

    st.divider()

    # -------------------------
    # FILTERS
    # -------------------------

    st.subheader("🔎 Filter Tasks")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Pending",
                "Completed",
                "Overdue"
            ],
            key="task_status_filter"
        )

    with filter_col2:

        priority_filter = st.selectbox(
            "Priority",
            [
                "All",
                "Low",
                "Medium",
                "High"
            ],
            key="task_priority_filter"
        )

    with filter_col3:

        sort_option = st.selectbox(
            "Sort By",
            [
                "Due Date",
                "Priority",
                "Newest"
            ],
            key="task_sort_option"
        )

    # -------------------------
    # FILTER TASKS
    # -------------------------

    filtered_tasks = tasks.copy()

    if status_filter == "Pending":

        filtered_tasks = [
            task
            for task in filtered_tasks
            if task[5] == 0
        ]

    elif status_filter == "Completed":

        filtered_tasks = [
            task
            for task in filtered_tasks
            if task[5] == 1
        ]

    elif status_filter == "Overdue":

        filtered_tasks = [
            task
            for task in filtered_tasks
            if (
                task[4]
                and task[4] < today
                and task[5] == 0
            )
        ]

    if priority_filter != "All":

        filtered_tasks = [
            task
            for task in filtered_tasks
            if task[2] == priority_filter
        ]

    # -------------------------
    # SORT TASKS
    # -------------------------

    if sort_option == "Due Date":

        filtered_tasks.sort(
            key=lambda task: (
                task[4] is None,
                task[4] or ""
            )
        )

    elif sort_option == "Priority":

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2
        }

        filtered_tasks.sort(
            key=lambda task: priority_order.get(
                task[2],
                3
            )
        )

    elif sort_option == "Newest":

        filtered_tasks.reverse()

    # -------------------------
    # TASK LIST
    # -------------------------

    st.subheader(
        f"📋 Tasks ({len(filtered_tasks)})"
    )

    if not filtered_tasks:

        st.info(
            "No tasks match your current filters."
        )

    else:

        for task in filtered_tasks:

            (
                task_id,
                title,
                priority,
                category,
                due_date,
                completed
            ) = task

            is_overdue = (
                due_date
                and due_date < today
                and completed == 0
            )

            # -------------------------
            # Task Container
            # -------------------------

            with st.container():

                task_col1, task_col2, task_col3 = st.columns(
                    [4, 1, 1]
                )

                with task_col1:

                    if is_overdue:

                        st.error(
                            f"🔴 **OVERDUE: {title}**"
                        )

                    elif completed:

                        st.markdown(
                            f"~~{title}~~"
                        )

                    else:

                        st.markdown(
                            f"### {title}"
                        )

                    st.caption(
                        f"{priority} • {category}"
                    )

                    if due_date:

                        if is_overdue:

                            st.caption(
                                f"🔴 Due: {due_date}"
                            )

                        else:

                            st.caption(
                                f"Due: {due_date}"
                            )

                with task_col2:

                    if completed:

                        if st.button(
                            "↩️ Reopen",
                            key=f"reopen_task_{task_id}"
                        ):

                            reopen_task(task_id)
                            check_achievements()
                            st.rerun()

                    else:

                        if st.button(
                            "✅ Complete",
                            key=f"complete_task_{task_id}"
                        ):

                            complete_task(task_id)
                            check_achievements()
                            st.rerun()

                with task_col3:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_task_{task_id}"
                    ):

                        delete_task(task_id)

                        st.rerun()

                # -------------------------
                # Edit Task
                # -------------------------

                with st.expander(
                    "✏️ Edit Task",
                    expanded=False
                ):

                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:

                        edited_title = st.text_input(
                            "Title",
                            value=title,
                            key=f"edit_title_{task_id}"
                        )

                        edited_priority = st.selectbox(
                            "Priority",
                            [
                                "Low",
                                "Medium",
                                "High"
                            ],
                            index=[
                                "Low",
                                "Medium",
                                "High"
                            ].index(priority),
                            key=f"edit_priority_{task_id}"
                        )

                    with edit_col2:

                        edited_category = st.selectbox(
                            "Category",
                            [
                                "General",
                                "Work",
                                "Study",
                                "Personal",
                                "Health",
                                "Project"
                            ],
                            index=(
                                [
                                    "General",
                                    "Work",
                                    "Study",
                                    "Personal",
                                    "Health",
                                    "Project"
                                ].index(category)
                                if category in [
                                    "General",
                                    "Work",
                                    "Study",
                                    "Personal",
                                    "Health",
                                    "Project"
                                ]
                                else 0
                            ),
                            key=f"edit_category_{task_id}"
                        )

                        if due_date:

                            edited_due_date = st.date_input(
                                "Due Date",
                                value=datetime.strptime(
                                    due_date,
                                    "%Y-%m-%d"
                                ).date(),
                                key=f"edit_due_date_{task_id}"
                            )

                        else:

                            edited_due_date = st.date_input(
                                "Due Date",
                                value=date.today(),
                                key=f"edit_due_date_{task_id}"
                            )

                    if st.button(
                        "💾 Save Changes",
                        key=f"save_task_{task_id}"
                    ):

                        if edited_title.strip():

                            update_task(
                                task_id,
                                edited_title.strip(),
                                edited_priority,
                                edited_category,
                                edited_due_date.isoformat()
                            )

                            st.success(
                                "Task updated successfully!"
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Task title cannot be empty."
                            )

                st.divider()

# =========================================================
# GOALS 2.0
# =========================================================

elif page == "🎯 Goals":

    st.title("🎯 Goals")

    st.caption(
        "Turn ambitions into measurable outcomes."
    )

    # =====================================================
    # ADD GOAL
    # =====================================================

    st.subheader("➕ Create New Goal")

    with st.form("goal_form"):

        goal_title = st.text_input(
            "Goal Title",
            placeholder="Example: Complete Python course"
        )

        col1, col2 = st.columns(2)

        with col1:

            goal_target = st.number_input(
                "Target",
                min_value=1,
                value=100,
                step=1
            )

        with col2:

            goal_deadline = st.date_input(
                "Deadline",
                value=date.today()
            )

        submitted = st.form_submit_button(
            "➕ Add Goal"
        )

        if submitted:

            if goal_title.strip():

                add_goal(
                    goal_title.strip(),
                    goal_target,
                    goal_deadline
                )

                check_achievements()

                st.success(
                    "Goal created successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter a goal title."
                )

    st.divider()

    # =====================================================
    # LOAD GOALS
    # =====================================================

    goals = get_goals()

    if not goals:

        st.info(
            "No goals yet. Create your first goal above."
        )

    else:

        # =================================================
        # SUMMARY
        # =================================================

        total_goals = len(goals)

        completed_goals = sum(
            1
            for goal in goals
            if goal[3] >= goal[2]
        )

        active_goals = (
            total_goals - completed_goals
        )

        summary_col1, summary_col2, summary_col3 = st.columns(3)

        with summary_col1:

            st.metric(
                "🎯 Total Goals",
                total_goals
            )

        with summary_col2:

            st.metric(
                "🔥 Active",
                active_goals
            )

        with summary_col3:

            st.metric(
                "🏆 Completed",
                completed_goals
            )

        st.divider()

        # =================================================
        # GOAL CARDS
        # =================================================

        for goal in goals:

            (
                goal_id,
                title,
                target,
                progress,
                created_at,
                deadline
            ) = goal

            percentage = get_goal_percentage(
                progress,
                target
            )

            status = get_goal_status(
                progress,
                target,
                deadline
            )

            days_remaining = get_days_remaining(
                deadline
            )

            # =============================================
            # GOAL HEADER
            # =============================================

            st.markdown(
                f"### 🎯 {title}"
            )

            info_col1, info_col2, info_col3 = st.columns(3)

            with info_col1:

                st.metric(
                    "Progress",
                    f"{progress}/{target}"
                )

            with info_col2:

                st.metric(
                    "Completion",
                    f"{percentage}%"
                )

            with info_col3:

                st.write("Status")

                st.write(
                    status
                )

            # =============================================
            # PROGRESS BAR
            # =============================================

            st.progress(
                min(percentage / 100, 1.0)
            )

            # =============================================
            # DEADLINE
            # =============================================

            if deadline:

                if days_remaining is not None:

                    if days_remaining < 0:

                        st.error(
                            f"⏰ Deadline passed by "
                            f"{abs(days_remaining)} day(s)"
                        )

                    elif days_remaining == 0:

                        st.warning(
                            "⏰ Deadline is today!"
                        )

                    elif days_remaining <= 3:

                        st.warning(
                            f"⏰ {days_remaining} day(s) remaining"
                        )

                    else:

                        st.caption(
                            f"📅 Deadline: {deadline} • "
                            f"{days_remaining} day(s) remaining"
                        )

            # =============================================
            # UPDATE PROGRESS
            # =============================================

            st.markdown(
                "#### 📈 Update Progress"
            )

            progress_col1, progress_col2 = st.columns(
                [4, 1]
            )

            with progress_col1:

                new_progress = st.number_input(
                    "Progress",
                    min_value=0,
                    max_value=max(target, progress),
                    value=min(progress, target),
                    step=1,
                    key=f"goal_progress_{goal_id}"
                )

            with progress_col2:

                st.write("")

                if st.button(
                    "Update",
                    key=f"update_progress_{goal_id}"
                ):

                    update_goal_progress(
                        goal_id,
                        new_progress
                    )

                    check_achievements()

                    st.success(
                        "Progress updated!"
                    )

                    st.rerun()

            # =============================================
            # EDIT GOAL
            # =============================================

            with st.expander(
                "✏️ Edit Goal"
            ):

                edit_title = st.text_input(
                    "Goal Title",
                    value=title,
                    key=f"edit_goal_title_{goal_id}"
                )

                edit_target = st.number_input(
                    "Target",
                    min_value=1,
                    value=target,
                    step=1,
                    key=f"edit_goal_target_{goal_id}"
                )

                if deadline:

                    try:

                        current_deadline = date.fromisoformat(
                            deadline
                        )

                    except ValueError:

                        current_deadline = date.today()

                else:

                    current_deadline = date.today()

                edit_deadline = st.date_input(
                    "Deadline",
                    value=current_deadline,
                    key=f"edit_goal_deadline_{goal_id}"
                )

                if st.button(
                    "💾 Save Changes",
                    key=f"save_goal_{goal_id}"
                ):

                    if edit_title.strip():

                        update_goal(
                            goal_id,
                            edit_title.strip(),
                            edit_target,
                            edit_deadline
                        )

                        st.success(
                            "Goal updated!"
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Goal title cannot be empty."
                        )

            # =============================================
            # PROGRESS HISTORY
            # =============================================

            with st.expander(
                "📊 Progress History"
            ):

                history = get_goal_history(
                    goal_id
                )

                if history:

                    history_df = pd.DataFrame(
                        history,
                        columns=[
                            "Progress",
                            "Recorded At"
                        ]
                    )

                    history_df["Recorded At"] = (
                        pd.to_datetime(
                            history_df["Recorded At"]
                        )
                    )

                    history_df = history_df.set_index(
                        "Recorded At"
                    )

                    st.line_chart(
                        history_df["Progress"]
                    )

                else:

                    st.info(
                        "No progress history yet."
                    )

            # =============================================
            # DELETE
            # =============================================

            delete_col1, delete_col2 = st.columns(
                [5, 1]
            )

            with delete_col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_goal_{goal_id}"
                ):

                    delete_goal(
                        goal_id
                    )

                    st.success(
                        "Goal deleted."
                    )

                    st.rerun()

            st.divider()


# =========================================================
# FOCUS 2.0
# =========================================================

elif page == "⏱️ Focus":

    st.title("⏱️ Focus")

    st.caption(
        "Protect your attention. Do meaningful work."
    )

    # =====================================================
    # LOAD STATS
    # =====================================================

    today_focus = get_today_focus_time()
    weekly_focus = get_weekly_focus_time()
    total_focus = get_total_focus_time()

    average_session = get_average_session_length()
    session_count = get_focus_session_count()
    focus_streak = get_focus_streak()

    # =====================================================
    # TOP METRICS
    # =====================================================

    st.subheader("📊 Focus Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "⏱️ Today",
            f"{today_focus} min"
        )

    with col2:
        st.metric(
            "📅 Last 7 Days",
            f"{weekly_focus} min"
        )

    with col3:
        st.metric(
            "🔥 Focus Streak",
            f"{focus_streak} days"
        )

    with col4:
        st.metric(
            "📈 Average Session",
            f"{average_session} min"
        )

    with col5:
        st.metric(
            "🔢 Sessions",
            session_count
        )

    # =====================================================
    # DAILY TARGET
    # =====================================================

    daily_focus_goal = int(
        get_setting("daily_focus_goal")
    )

    if daily_focus_goal > 0:

        focus_target_progress = min(
            today_focus / daily_focus_goal,
            1.0
        )

    else:

        focus_target_progress = 0

    st.divider()

    st.subheader("🎯 Daily Focus Target")

    st.progress(
        focus_target_progress
    )

    st.caption(
        f"{today_focus} / "
        f"{daily_focus_goal} minutes"
    )

    if today_focus >= daily_focus_goal:

        st.success(
            "🎉 Daily focus target reached!"
        )

    else:

        remaining = (
            daily_focus_goal
            - today_focus
        )

        st.info(
            f"⏳ {remaining} minutes remaining "
            f"to reach today's target."
        )

    # =====================================================
    # POMODORO TIMER
    # =====================================================

    st.divider()

    st.subheader("🍅 Focus Timer")

    # Initialize timer state
    if "focus_timer_running" not in st.session_state:

        st.session_state.focus_timer_running = False

    if "focus_timer_end" not in st.session_state:

        st.session_state.focus_timer_end = None

    if "focus_timer_duration" not in st.session_state:

        st.session_state.focus_timer_duration = 25

    if "focus_timer_type" not in st.session_state:

        st.session_state.focus_timer_type = "Focus"

    timer_col1, timer_col2 = st.columns(2)

    with timer_col1:

        session_type = st.selectbox(
            "Session Type",
            [
                "Focus",
                "Deep Work",
                "Study",
                "Coding",
                "Reading"
            ],
            disabled=st.session_state.focus_timer_running,
            key="focus_session_type"
        )

    with timer_col2:

        timer_duration = st.selectbox(
            "Duration",
            [
                15,
                25,
                30,
                45,
                60,
                90
            ],
            format_func=lambda x: f"{x} minutes",
            disabled=st.session_state.focus_timer_running,
            key="focus_timer_duration_select"
        )

    # =====================================================
    # TIMER LOGIC
    # =====================================================

    if st.session_state.focus_timer_running:

        remaining_seconds = max(
            0,
            int(
                (
                    st.session_state.focus_timer_end
                    - time.time()
                )
            )
        )

        remaining_minutes = (
            remaining_seconds // 60
        )

        remaining_display_seconds = (
            remaining_seconds % 60
        )

        st.markdown(
            f"# {remaining_minutes:02d}:"
            f"{remaining_display_seconds:02d}"
        )

        st.caption(
            f"🔴 {st.session_state.focus_timer_type} session running..."
        )

        if remaining_seconds <= 0:

            add_focus_session(
                st.session_state.focus_timer_duration,
                st.session_state.focus_timer_type
            )

            check_achievements()

            st.session_state.focus_timer_running = False
            st.session_state.focus_timer_end = None

            st.success(
                "🎉 Focus session completed!"
            )

            st.rerun()

        if st.button(
            "⏹️ Stop Timer",
            key="stop_focus_timer"
        ):

            elapsed_seconds = (
                st.session_state.focus_timer_duration * 60
                - remaining_seconds
            )

            elapsed_minutes = (
                elapsed_seconds // 60
            )

            if elapsed_minutes > 0:

                add_focus_session(
                    elapsed_minutes,
                    st.session_state.focus_timer_type
                )

                check_achievements()

            st.session_state.focus_timer_running = False
            st.session_state.focus_timer_end = None

            st.rerun()

        time.sleep(1)

        st.rerun()

    else:

        if st.button(
            "▶️ Start Focus",
            key="start_focus_timer"
        ):

            st.session_state.focus_timer_running = True

            st.session_state.focus_timer_duration = (
                timer_duration
            )

            st.session_state.focus_timer_type = (
                session_type
            )

            st.session_state.focus_timer_end = (
                time.time()
                + timer_duration * 60
            )

            st.rerun()

    # =====================================================
    # MANUAL SESSION
    # =====================================================

    st.divider()

    with st.expander(
        "➕ Log Focus Session Manually"
    ):

        manual_col1, manual_col2 = st.columns(2)

        with manual_col1:

            manual_duration = st.number_input(
                "Duration",
                min_value=1,
                max_value=600,
                value=25,
                step=5,
                key="manual_focus_duration"
            )

        with manual_col2:

            manual_type = st.selectbox(
                "Session Type",
                [
                    "Focus",
                    "Deep Work",
                    "Study",
                    "Coding",
                    "Reading"
                ],
                key="manual_focus_type"
            )

        if st.button(
            "💾 Save Session",
            key="save_manual_focus"
        ):

            add_focus_session(
                manual_duration,
                manual_type
            )

            check_achievements()

            st.success(
                "Focus session logged!"
            )

            st.rerun()

    # =====================================================
    # FOCUS BY TYPE
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Focus by Session Type"
    )

    focus_by_type = get_focus_by_type()

    if focus_by_type:

        type_df = pd.DataFrame(
            focus_by_type,
            columns=[
                "Session Type",
                "Minutes"
            ]
        )

        st.bar_chart(
            type_df.set_index(
                "Session Type"
            )
        )

    else:

        st.info(
            "Complete focus sessions to see your breakdown."
        )

    # =====================================================
    # 30-DAY FOCUS HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "📈 30-Day Focus History"
    )

    focus_history = get_daily_focus_history(
        30
    )

    if focus_history:

        focus_df = pd.DataFrame(
            focus_history,
            columns=[
                "Date",
                "Minutes"
            ]
        )

        focus_df["Date"] = pd.to_datetime(
            focus_df["Date"]
        )

        focus_df = focus_df.set_index(
            "Date"
        )

        st.bar_chart(
            focus_df["Minutes"]
        )

    # =====================================================
    # SESSION HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "📝 Session History"
    )

    sessions = get_focus_sessions()

    if not sessions:

        st.info(
            "No focus sessions recorded yet."
        )

    else:

        for session in sessions:

            (
                session_id,
                duration,
                session_date,
                session_type
            ) = session

            history_col1, history_col2 = st.columns(
                [5, 1]
            )

            with history_col1:

                st.markdown(
                    f"⏱️ **{duration} minutes** "
                    f"• {session_type}"
                )

                st.caption(
                    f"📅 {session_date}"
                )

            with history_col2:

                if st.button(
                    "🗑️",
                    key=f"delete_focus_{session_id}"
                ):

                    delete_focus_session(
                        session_id
                    )

                    st.rerun()

    # =====================================================
    # TOTAL FOCUS
    # =====================================================

    st.divider()

    total_hours = total_focus // 60
    total_minutes_remaining = total_focus % 60

    st.subheader(
        "🏆 Total Focus"
    )

    if total_hours > 0:

        st.metric(
            "Lifetime Focus",
            f"{total_hours}h "
            f"{total_minutes_remaining}m"
        )

    else:

        st.metric(
            "Lifetime Focus",
            f"{total_minutes_remaining} min"
        )

# =========================================================
# HABITS 2.0
# =========================================================

elif page == "🔥 Habits":

    st.title("🔥 Habits")

    st.caption(
        "Build consistency. Track the streak. Become annoyingly disciplined."
    )

    # =====================================================
    # ADD HABIT
    # =====================================================

    st.subheader("➕ Create New Habit")

    with st.form("habit_form"):

        habit_name = st.text_input(
            "Habit Name",
            placeholder="Example: Study Python for 1 hour"
        )

        submitted = st.form_submit_button(
            "➕ Add Habit"
        )

        if submitted:

            if habit_name.strip():

                add_habit(
                    habit_name.strip()
                )

                check_achievements()

                st.success(
                    "Habit created successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter a habit name."
                )

    st.divider()

    # =====================================================
    # LOAD HABITS
    # =====================================================

    habits = get_habits()

    if not habits:

        st.info(
            "No habits yet. Create your first habit above."
        )

    else:

        # =================================================
        # OVERALL SUMMARY
        # =================================================

        total_habits = len(habits)

        completed_today = sum(
            1
            for habit in habits
            if is_habit_completed_today(
                habit[0]
            )
        )

        today_percentage = (
            completed_today / total_habits * 100
            if total_habits > 0
            else 0
        )

        summary_col1, summary_col2, summary_col3 = st.columns(3)

        with summary_col1:

            st.metric(
                "🔥 Total Habits",
                total_habits
            )

        with summary_col2:

            st.metric(
                "✅ Completed Today",
                f"{completed_today}/{total_habits}"
            )

        with summary_col3:

            st.metric(
                "📊 Today's Rate",
                f"{today_percentage:.0f}%"
            )

        st.progress(
            min(today_percentage / 100, 1.0)
        )

        st.divider()

        # =================================================
        # HABIT CARDS
        # =================================================

        for habit in habits:

            habit_id, habit_name = habit

            summary = get_habit_summary(
                habit_id
            )

            current_streak = summary[
                "current_streak"
            ]

            best_streak = summary[
                "best_streak"
            ]

            weekly_percentage = summary[
                "weekly_percentage"
            ]

            monthly_percentage = summary[
                "monthly_percentage"
            ]

            completed_today = summary[
                "completed_today"
            ]

            # =============================================
            # HABIT HEADER
            # =============================================

            status_icon = (
                "✅"
                if completed_today
                else "⬜"
            )

            st.markdown(
                f"### {status_icon} {habit_name}"
            )

            # =============================================
            # STATS
            # =============================================

            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:

                st.metric(
                    "🔥 Current Streak",
                    f"{current_streak} days"
                )

            with stat_col2:

                st.metric(
                    "🏆 Best Streak",
                    f"{best_streak} days"
                )

            with stat_col3:

                st.metric(
                    "📅 7-Day Rate",
                    f"{weekly_percentage}%"
                )

            with stat_col4:

                st.metric(
                    "📊 30-Day Rate",
                    f"{monthly_percentage}%"
                )

            # =============================================
            # TODAY'S ACTION
            # =============================================

            if completed_today:

                st.success(
                    "✅ Completed today. Keep the streak alive!"
                )

            else:

                if st.button(
                    "🔥 Complete Today",
                    key=f"complete_habit_{habit_id}"
                ):

                    log_habit(
                        habit_id
                    )

                    check_achievements()

                    st.success(
                        f"{habit_name} completed! 🔥"
                    )

                    st.rerun()

            # =============================================
            # 7-DAY TRACKER
            # =============================================

            st.markdown(
                "#### 📅 Last 7 Days"
            )

            last_7_days = get_last_7_days(
                habit_id
            )

            day_cols = st.columns(7)

            for index, day_data in enumerate(
                last_7_days
            ):

                day_string, completed = day_data

                current_day = date.fromisoformat(
                    day_string
                )

                day_name = current_day.strftime(
                    "%a"
                )

                day_number = current_day.strftime(
                    "%d"
                )

                with day_cols[index]:

                    if completed:

                        st.success(
                            f"✅\n{day_name}\n{day_number}"
                        )

                    else:

                        st.write(
                            f"⬜\n{day_name}\n{day_number}"
                        )

            # =============================================
            # 30-DAY CHART
            # =============================================

            with st.expander(
                "📈 30-Day Activity"
            ):

                last_30_days = get_last_30_days(
                    habit_id
                )

                habit_chart_df = pd.DataFrame(
                    last_30_days,
                    columns=[
                        "Date",
                        "Completed"
                    ]
                )

                habit_chart_df["Date"] = (
                    pd.to_datetime(
                        habit_chart_df["Date"]
                    )
                )

                habit_chart_df = (
                    habit_chart_df
                    .set_index("Date")
                )

                st.bar_chart(
                    habit_chart_df["Completed"]
                )

                st.caption(
                    "1 = completed • 0 = missed"
                )

            # =============================================
            # HABIT ACTIONS
            # =============================================

            with st.expander(
                "⚙️ Habit Management"
            ):

                st.write(
                    f"Created habit: **{habit_name}**"
                )

                st.write(
                    f"Current streak: "
                    f"**{current_streak} days**"
                )

                st.write(
                    f"Best streak: "
                    f"**{best_streak} days**"
                )

                st.write(
                    f"30-day completion: "
                    f"**{monthly_percentage}%**"
                )

                if st.button(
                    "🗑️ Delete Habit",
                    key=f"delete_habit_{habit_id}"
                ):

                    delete_habit(
                        habit_id
                    )

                    st.success(
                        "Habit deleted."
                    )

                    st.rerun()

            st.divider()

        # =================================================
        # MOTIVATION
        # =================================================

        if completed_today == total_habits:

            st.success(
                "🏆 All habits completed today. "
                "Your future self is mildly impressed."
            )

        elif completed_today > 0:

            remaining = (
                total_habits
                - completed_today
            )

            st.info(
                f"💪 {remaining} habit(s) remaining today."
            )

        else:

            st.warning(
                "🔥 No habits completed yet today. "
                "Start with one."
            )

# =========================================================
# NOTES 2.0
# =========================================================

elif page == "📝 Notes":

    st.title("📝 Notes")

    st.caption(
        "Capture ideas, knowledge, plans, and everything "
        "your brain refuses to remember."
    )

    categories = [
        "General",
        "Study",
        "Work",
        "Project",
        "Ideas",
        "Personal"
    ]

    # =====================================================
    # CREATE NOTE
    # =====================================================

    with st.expander(
        "➕ Create New Note",
        expanded=True
    ):

        note_title = st.text_input(
            "Title",
            placeholder="e.g. Python OOP Concepts",
            key="new_note_title"
        )

        note_category = st.selectbox(
            "Category",
            categories,
            key="new_note_category"
        )

        note_content = st.text_area(
            "Content",
            placeholder="Write your note here...",
            height=220,
            key="new_note_content"
        )

        if st.button(
            "💾 Create Note",
            use_container_width=True,
            key="create_note_button"
        ):

            if not note_title.strip():

                st.warning(
                    "Please enter a title."
                )

            elif not note_content.strip():

                st.warning(
                    "Please enter some content."
                )

            else:

                add_note(
                    note_title.strip(),
                    note_content.strip(),
                    note_category
                )

                st.success(
                    "Note created successfully."
                )

                st.rerun()

    st.divider()

    # =====================================================
    # NOTE STATISTICS
    # =====================================================

    stats = get_note_statistics()

    stat1, stat2, stat3 = st.columns(3)

    with stat1:

        st.metric(
            "📝 Total Notes",
            stats["total"]
        )

    with stat2:

        st.metric(
            "📌 Pinned",
            stats["pinned"]
        )

    with stat3:

        st.metric(
            "🏷️ Categories",
            stats["categories"]
        )

    st.divider()

    # =====================================================
    # SEARCH & FILTER
    # =====================================================

    st.subheader("🔎 Find Notes")

    search_col, category_col = st.columns(2)

    with search_col:

        search_text = st.text_input(
            "Search",
            placeholder="Search title, content, or category...",
            key="notes_search_2"
        )

    with category_col:

        category_filter = st.selectbox(
            "Category",
            ["All"] + categories,
            key="notes_category_filter_2"
        )

    # =====================================================
    # LOAD NOTES
    # =====================================================

    notes = get_notes()

    filtered_notes = []

    for note in notes:

        (
            note_id,
            title,
            content,
            category,
            pinned,
            created_at,
            updated_at
        ) = note

        # Search
        if search_text.strip():

            search_lower = search_text.lower()

            searchable_text = (
                f"{title} "
                f"{content} "
                f"{category}"
            ).lower()

            if search_lower not in searchable_text:

                continue

        # Category
        if (
            category_filter != "All"
            and category != category_filter
        ):

            continue

        filtered_notes.append(note)

    # =====================================================
    # SORTING
    # =====================================================

    sort_option = st.selectbox(
        "Sort Notes",
        [
            "Recently Updated",
            "Recently Created",
            "Pinned First",
            "Title A-Z"
        ],
        key="notes_sort"
    )

    if sort_option == "Recently Updated":

        filtered_notes.sort(
            key=lambda x: x[6] or "",
            reverse=True
        )

    elif sort_option == "Recently Created":

        filtered_notes.sort(
            key=lambda x: x[5] or "",
            reverse=True
        )

    elif sort_option == "Pinned First":

        filtered_notes.sort(
            key=lambda x: (x[4], x[6] or ""),
            reverse=True
        )

    elif sort_option == "Title A-Z":

        filtered_notes.sort(
            key=lambda x: x[1].lower()
        )

    st.divider()

    # =====================================================
    # RESULTS
    # =====================================================

    st.subheader(
        f"📚 Notes ({len(filtered_notes)})"
    )

    if not filtered_notes:

        if notes:

            st.info(
                "No notes match your search or filter."
            )

        else:

            st.info(
                "No notes yet. Create your first note above."
            )

    else:

        for note in filtered_notes:

            (
                note_id,
                title,
                content,
                category,
                pinned,
                created_at,
                updated_at
            ) = note

            with st.container(border=True):

                # -----------------------------------------
                # HEADER
                # -----------------------------------------

                header_col1, header_col2 = st.columns(
                    [5, 1]
                )

                with header_col1:

                    icon = (
                        "📌"
                        if pinned
                        else "📝"
                    )

                    st.markdown(
                        f"### {icon} {title}"
                    )

                    st.caption(
                        f"🏷️ {category}"
                    )

                with header_col2:

                    pin_label = (
                        "📌 Unpin"
                        if pinned
                        else "📍 Pin"
                    )

                    if st.button(
                        pin_label,
                        key=f"notes2_pin_{note_id}",
                        use_container_width=True
                    ):

                        toggle_pin(note_id)

                        st.rerun()

                # -----------------------------------------
                # CONTENT
                # -----------------------------------------

                st.markdown(content)

                st.caption(
                    f"Created: {created_at[:10]} "
                    f"• Updated: {updated_at[:10]}"
                )

                # -----------------------------------------
                # ACTIONS
                # -----------------------------------------

                edit_col, delete_col = st.columns(2)

                with edit_col:

                    with st.expander(
                        "✏️ Edit Note"
                    ):

                        edit_title = st.text_input(
                            "Title",
                            value=title,
                            key=f"notes2_title_{note_id}"
                        )

                        edit_category = st.selectbox(
                            "Category",
                            categories,
                            index=(
                                categories.index(category)
                                if category in categories
                                else 0
                            ),
                            key=f"notes2_category_{note_id}"
                        )

                        edit_content = st.text_area(
                            "Content",
                            value=content,
                            height=220,
                            key=f"notes2_content_{note_id}"
                        )

                        if st.button(
                            "💾 Save Changes",
                            use_container_width=True,
                            key=f"notes2_save_{note_id}"
                        ):

                            if not edit_title.strip():

                                st.warning(
                                    "Title cannot be empty."
                                )

                            elif not edit_content.strip():

                                st.warning(
                                    "Content cannot be empty."
                                )

                            else:

                                update_note(
                                    note_id,
                                    edit_title.strip(),
                                    edit_content.strip(),
                                    edit_category
                                )

                                st.success(
                                    "Note updated."
                                )

                                st.rerun()

                with delete_col:

                    st.write("")

                    if st.button(
                        "🗑️ Delete Note",
                        use_container_width=True,
                        key=f"notes2_delete_{note_id}"
                    ):

                        delete_note(
                            note_id
                        )

                        st.success(
                            "Note deleted."
                        )

                        st.rerun()

    # =====================================================
    # EMPTY SPACE / FOOTER
    # =====================================================

    st.divider()

    st.caption(
        "🧠 LifeOS Notes • Capture it now, remember it later."
    )

# =========================================================
# ANALYTICS 2.0
# =========================================================

elif page == "📈 Analytics":

    st.title("📈 Analytics 2.0")

    st.caption(
        "Turn your LifeOS activity into useful performance insights."
    )

    # =====================================================
    # LOAD ANALYTICS DATA
    # =====================================================

    today_summary = get_today_summary()
    productivity_score = calculate_productivity_score()
    consistency_score = get_consistency_score()

    task_stats = get_task_stats()
    habit_stats = get_habit_stats()
    goal_stats = get_goal_stats()

    total_focus = get_overall_focus_time()
    completed_tasks = get_total_completed_tasks()
    completed_goals = get_total_completed_goals()

    best_focus_day = get_best_focus_day()
    best_task_day = get_best_task_day()

    insights = get_productivity_insights()

    # =====================================================
    # TOP KPI CARDS
    # =====================================================

    st.subheader("📊 Performance Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "⚡ Productivity",
            f"{productivity_score}/100"
        )

    with col2:
        st.metric(
            "📋 Tasks Done",
            completed_tasks
        )

    with col3:
        st.metric(
            "🔥 Habit Activity",
            habit_stats["completed"]
        )

    with col4:
        st.metric(
            "🎯 Goals Done",
            completed_goals
        )

    with col5:
        focus_hours = total_focus // 60
        focus_minutes = total_focus % 60

        st.metric(
            "⏱️ Focus Time",
            f"{focus_hours}h {focus_minutes}m"
        )

    st.divider()

    # =====================================================
    # PRODUCTIVITY SCORE
    # =====================================================

    st.subheader("⚡ Productivity Score")

    score_col1, score_col2 = st.columns([1, 3])

    with score_col1:

        st.metric(
            "Today's Score",
            f"{productivity_score}/100"
        )

    with score_col2:

        st.progress(
            productivity_score / 100
        )

        if productivity_score >= 80:
            st.success(
                "🔥 Excellent performance today."
            )

        elif productivity_score >= 60:
            st.info(
                "💪 Solid progress. Keep building momentum."
            )

        elif productivity_score >= 40:
            st.warning(
                "📈 Decent start. There is room to improve."
            )

        else:
            st.error(
                "🎯 Productivity is low today. Focus on one important action."
            )

    st.divider()

    # =====================================================
    # TODAY'S PERFORMANCE
    # =====================================================

    st.subheader("📅 Today's Performance")

    today_col1, today_col2, today_col3 = st.columns(3)

    with today_col1:

        st.markdown("### 📋 Tasks")

        task_rate = today_summary["task_rate"]

        st.progress(
            task_rate / 100
        )

        st.caption(
            f"{today_summary['task_completed']} / "
            f"{today_summary['task_total']} completed"
        )

        st.metric(
            "Completion",
            f"{task_rate}%"
        )

    with today_col2:

        st.markdown("### 🔥 Habits")

        habit_rate = today_summary["habit_rate"]

        st.progress(
            habit_rate / 100
        )

        st.caption(
            f"{today_summary['habit_completed']} / "
            f"{today_summary['habit_total']} completed"
        )

        st.metric(
            "Completion",
            f"{habit_rate}%"
        )

    with today_col3:

        st.markdown("### ⏱️ Focus")

        today_focus = today_summary["focus_minutes"]

        st.metric(
            "Focus Today",
            f"{today_focus} min"
        )

        if today_focus >= 60:
            st.success(
                "🧠 One hour+ of focused work."
            )
        elif today_focus > 0:
            st.info(
                "Keep going. Build toward 60 minutes."
            )
        else:
            st.warning(
                "No focus session recorded today."
            )

    st.divider()

    # =====================================================
    # CONSISTENCY
    # =====================================================

    st.subheader("🔥 Consistency Score")

    consistency_col1, consistency_col2 = st.columns([1, 3])

    with consistency_col1:

        st.metric(
            "7-Day Consistency",
            f"{consistency_score}%"
        )

    with consistency_col2:

        st.progress(
            consistency_score / 100
        )

        if consistency_score >= 80:
            st.success(
                "🔥 Very consistent. You're showing up."
            )

        elif consistency_score >= 50:
            st.info(
                "💪 Good consistency. Keep reducing inactive days."
            )

        else:
            st.warning(
                "📅 Your activity is inconsistent this week."
            )

    st.divider()

    # =====================================================
    # DAILY TRENDS
    # =====================================================

    st.subheader("📈 30-Day Activity Trends")

    daily_tasks = get_daily_task_stats(30)
    daily_habits = get_daily_habit_stats(30)
    daily_focus = get_daily_focus_stats(30)

    trend_col1, trend_col2 = st.columns(2)

    # -----------------------------------------------------
    # TASK TREND
    # -----------------------------------------------------

    with trend_col1:

        st.markdown("#### 📋 Task Completion")

        if daily_tasks:

            task_df = pd.DataFrame(
                daily_tasks,
                columns=[
                    "Date",
                    "Total",
                    "Completed"
                ]
            )

            task_df["Date"] = pd.to_datetime(
                task_df["Date"]
            )

            task_df = task_df.set_index(
                "Date"
            )

            st.line_chart(
                task_df[
                    ["Total", "Completed"]
                ]
            )

        else:

            st.info(
                "No task activity available yet."
            )

    # -----------------------------------------------------
    # FOCUS TREND
    # -----------------------------------------------------

    with trend_col2:

        st.markdown("#### ⏱️ Focus Time")

        if daily_focus:

            focus_df = pd.DataFrame(
                daily_focus,
                columns=[
                    "Date",
                    "Minutes"
                ]
            )

            focus_df["Date"] = pd.to_datetime(
                focus_df["Date"]
            )

            focus_df = focus_df.set_index(
                "Date"
            )

            st.bar_chart(
                focus_df[
                    ["Minutes"]
                ]
            )

        else:

            st.info(
                "No focus activity available yet."
            )

    st.markdown("#### 🔥 Habit Activity")

    if daily_habits:

        habit_df = pd.DataFrame(
            daily_habits,
            columns=[
                "Date",
                "Completed"
            ]
        )

        habit_df["Date"] = pd.to_datetime(
            habit_df["Date"]
        )

        habit_df = habit_df.set_index(
            "Date"
        )

        st.bar_chart(
            habit_df[
                ["Completed"]
            ]
        )

    else:

        st.info(
            "No habit activity available yet."
        )

    st.divider()

    # =====================================================
    # PERFORMANCE BREAKDOWN
    # =====================================================

    st.subheader("🧩 Performance Breakdown")

    breakdown_col1, breakdown_col2 = st.columns(2)

    with breakdown_col1:

        st.markdown("#### 📋 Tasks")

        st.metric(
            "Total Tasks",
            task_stats["total"]
        )

        st.metric(
            "Completed",
            task_stats["completed"]
        )

        st.progress(
            task_stats["rate"] / 100
        )

        st.caption(
            f"{task_stats['rate']}% overall completion"
        )

    with breakdown_col2:

        st.markdown("#### 🎯 Goals")

        st.metric(
            "Total Goals",
            goal_stats["total"]
        )

        st.metric(
            "Completed",
            goal_stats["completed"]
        )

        st.progress(
            goal_stats["rate"] / 100
        )

        st.caption(
            f"{goal_stats['rate']}% goal completion"
        )

    st.divider()

    # =====================================================
    # BEST DAYS
    # =====================================================

    st.subheader("🏆 Best Performance")

    best_col1, best_col2 = st.columns(2)

    with best_col1:

        st.markdown("#### ⏱️ Best Focus Day")

        if best_focus_day:

            best_date = best_focus_day[0]
            best_minutes = best_focus_day[1]

            st.metric(
                "Focus",
                f"{best_minutes} min"
            )

            st.caption(
                f"📅 {best_date}"
            )

        else:

            st.info(
                "No focus history yet."
            )

    with best_col2:

        st.markdown("#### 📋 Best Task Day")

        if best_task_day:

            best_date = best_task_day[0]
            best_completed = best_task_day[2]

            st.metric(
                "Tasks Completed",
                best_completed
            )

            st.caption(
                f"📅 {best_date}"
            )

        else:

            st.info(
                "No completed task history yet."
            )

    st.divider()

    # =====================================================
    # PRODUCTIVITY INSIGHTS
    # =====================================================

    st.subheader("🧠 LifeOS Insights")

    if insights:

        for insight in insights:

            st.info(
                insight
            )

    else:

        st.success(
            "No major issues detected. Keep building."
        )

    st.divider()

    # =====================================================
    # WEEKLY COMPARISON
    # =====================================================

    st.subheader("📆 Weekly Performance")

    weekly_tasks = get_weekly_task_stats(8)
    weekly_focus = get_weekly_focus_stats(8)
    weekly_habits = get_weekly_habit_stats(8)

    weekly_col1, weekly_col2 = st.columns(2)

    with weekly_col1:

        st.markdown("#### 📋 Tasks by Week")

        if weekly_tasks:

            weekly_task_df = pd.DataFrame(
                weekly_tasks,
                columns=[
                    "Week",
                    "Total",
                    "Completed"
                ]
            )

            weekly_task_df = weekly_task_df.set_index(
                "Week"
            )

            st.bar_chart(
                weekly_task_df[
                    ["Completed"]
                ]
            )

        else:

            st.info(
                "No weekly task data available."
            )

    with weekly_col2:

        st.markdown("#### ⏱️ Focus by Week")

        if weekly_focus:

            weekly_focus_df = pd.DataFrame(
                weekly_focus,
                columns=[
                    "Week",
                    "Minutes"
                ]
            )

            weekly_focus_df = weekly_focus_df.set_index(
                "Week"
            )

            st.bar_chart(
                weekly_focus_df[
                    ["Minutes"]
                ]
            )

        else:

            st.info(
                "No weekly focus data available."
            )

    st.markdown("#### 🔥 Habits by Week")

    if weekly_habits:

        weekly_habit_df = pd.DataFrame(
            weekly_habits,
            columns=[
                "Week",
                "Completed"
            ]
        )

        weekly_habit_df = weekly_habit_df.set_index(
            "Week"
        )

        st.bar_chart(
            weekly_habit_df[
                ["Completed"]
            ]
        )

    else:

        st.info(
            "No weekly habit data available."
        )

    st.divider()

    st.caption(
        "📈 LifeOS Analytics 2.0 • Measure the work, not just the intention."
    )

# =========================================================
# ACHIEVEMENTS 2.0
# =========================================================

elif page == "🏆 Achievements":

    st.title("🏆 Achievements")

    st.caption(
        "Build momentum, earn XP, level up, and turn consistency into progress."
    )

    # =====================================================
    # REFRESH ACHIEVEMENTS
    # =====================================================

    newly_unlocked = check_achievements()

    # =====================================================
    # NEW UNLOCK NOTIFICATIONS
    # =====================================================

    if newly_unlocked:

        for achievement in newly_unlocked:

            st.success(
                f"{achievement['icon']} "
                f"**Achievement Unlocked: "
                f"{achievement['name']}**  "
                f"+{achievement['xp']} XP"
            )

    # =====================================================
    # SUMMARY
    # =====================================================

    summary = get_achievement_summary()
    level_progress = get_level_progress(
        summary["xp"]
    )

    total = summary["total"]
    unlocked = summary["unlocked"]
    remaining = summary["remaining"]
    xp = summary["xp"]
    level = level_progress["level"]

    # =====================================================
    # LEVEL CARD
    # =====================================================

    st.subheader("⚡ Your Level")

    level_col1, level_col2, level_col3 = st.columns(3)

    with level_col1:

        st.metric(
            "🏅 Level",
            level
        )

    with level_col2:

        st.metric(
            "✨ Total XP",
            xp
        )

    with level_col3:

        st.metric(
            "🏆 Achievements",
            f"{unlocked}/{total}"
        )

    st.progress(
        level_progress["percentage"]
    )

    st.caption(
        f"{level_progress['progress_xp']} / "
        f"{level_progress['required_xp']} XP "
        f"to Level {level + 1}"
    )

    st.divider()

    # =====================================================
    # ACHIEVEMENT SUMMARY
    # =====================================================

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            "🏆 Unlocked",
            unlocked
        )

    with summary_col2:

        st.metric(
            "🔒 Remaining",
            remaining
        )

    with summary_col3:

        completion_rate = (
            round((unlocked / total) * 100)
            if total
            else 0
        )

        st.metric(
            "📈 Completion",
            f"{completion_rate}%"
        )

    st.divider()

    # =====================================================
    # ACHIEVEMENT LIST
    # =====================================================

    st.subheader("🏆 Milestones")

    achievements = get_achievements()

    unlocked_achievements = [
        achievement
        for achievement in achievements
        if achievement[6] == 1
    ]

    locked_achievements = [
        achievement
        for achievement in achievements
        if achievement[6] == 0
    ]

    # =====================================================
    # UNLOCKED
    # =====================================================

    if unlocked_achievements:

        st.markdown("### 🟢 Unlocked")

        for achievement in unlocked_achievements:

            (
                achievement_id,
                key,
                name,
                description,
                icon,
                achievement_xp,
                is_unlocked,
                unlocked_at
            ) = achievement

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [1, 5, 1]
                )

                with col1:

                    st.markdown(
                        f"# {icon}"
                    )

                with col2:

                    st.markdown(
                        f"### {name}"
                    )

                    st.write(
                        description
                    )

                    if unlocked_at:

                        unlocked_date = (
                            unlocked_at[:10]
                        )

                        st.caption(
                            f"Unlocked on {unlocked_date}"
                        )

                with col3:

                    st.metric(
                        "XP",
                        f"+{achievement_xp}"
                    )

    # =====================================================
    # LOCKED
    # =====================================================

    if locked_achievements:

        st.markdown("### 🔒 Locked")

        for achievement in locked_achievements:

            (
                achievement_id,
                key,
                name,
                description,
                icon,
                achievement_xp,
                is_unlocked,
                unlocked_at
            ) = achievement

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [1, 5, 1]
                )

                with col1:

                    st.markdown(
                        "# 🔒"
                    )

                with col2:

                    st.markdown(
                        f"### {name}"
                    )

                    st.write(
                        description
                    )

                with col3:

                    st.metric(
                        "XP",
                        f"+{achievement_xp}"
                    )

    st.divider()

    # =====================================================
    # XP BREAKDOWN
    # =====================================================

    st.subheader("✨ XP Progress")

    st.write(
        f"**{xp} XP** earned through achievements."
    )

    if level >= 5:

        st.success(
            "💎 You've reached Level 5. Keep building."
        )

    elif level >= 3:

        st.info(
            "🚀 You're building serious momentum."
        )

    elif level >= 2:

        st.info(
            "🔥 You're getting started. Keep stacking wins."
        )

    else:

        st.caption(
            "🌱 Every completed action contributes to your progress."
        )

    st.divider()

    st.caption(
        "🏆 LifeOS Achievements 2.0 • Progress is built one action at a time."
    )

# =========================================================
# WEEKLY REVIEW
# =========================================================

elif page == "📊 Weekly Review":

    st.title("📊 Weekly Review")
    st.caption("A quick look at how productive your week actually was.")

    review = get_weekly_review()

    start_date = review["start"]
    end_date = review["end"]

    st.write(
        f"### {start_date.strftime('%d %b %Y')} "
        f"→ {end_date.strftime('%d %b %Y')}"
    )

    st.divider()

    # -------------------------
    # Weekly Metrics
    # -------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tasks Completed",
            review["task_completed"]
        )

    with col2:
        st.metric(
            "Task Completion",
            f"{review['task_rate']}%"
        )

    with col3:
        st.metric(
            "Habit Completions",
            review["habit_completed"]
        )

    with col4:
        st.metric(
            "Focus Time",
            f"{review['focus_minutes']} min"
        )

    st.divider()

    # -------------------------
    # Weekly Progress
    # -------------------------

    st.subheader("📈 Weekly Progress")

    task_rate = review["task_rate"] / 100

    st.write("Task Completion")

    st.progress(task_rate)

    st.write(
        f"{review['task_completed']} / "
        f"{review['task_total']} tasks completed"
    )

    st.divider()

    # -------------------------
    # Focus Summary
    # -------------------------

    st.subheader("⏱️ Focus Summary")

    focus_hours = review["focus_minutes"] // 60
    focus_remaining_minutes = review["focus_minutes"] % 60

    if focus_hours > 0:

        st.write(
            f"**{focus_hours}h "
            f"{focus_remaining_minutes}m** "
            "of focused work this week."
        )

    else:

        st.write(
            f"**{review['focus_minutes']} minutes** "
            "of focused work this week."
        )

    st.divider()

    # -------------------------
    # Goals
    # -------------------------

    st.subheader("🎯 Goals")

    st.metric(
        "Completed Goals",
        review["goal_completed"]
    )

    st.divider()

    # -------------------------
    # Weekly Highlights
    # -------------------------

    st.subheader("✨ Weekly Highlights")

    if review["task_completed"] > 0:

        st.success(
            f"You completed {review['task_completed']} "
            "task(s) this week."
        )

    if review["habit_completed"] > 0:

        st.success(
            f"You logged {review['habit_completed']} "
            "habit completion(s)."
        )

    if review["focus_minutes"] > 0:

        st.success(
            f"You spent {review['focus_minutes']} "
            "minutes in focused work."
        )

    if review["goal_completed"] > 0:

        st.success(
            f"You completed {review['goal_completed']} "
            "goal(s)."
        )

    # -------------------------
    # Improvement Areas
    # -------------------------

    st.subheader("🔍 Areas to Improve")

    improvements = []

    if review["task_total"] == 0:
        improvements.append(
            "No tasks were created this week."
        )

    elif review["task_rate"] < 50:
        improvements.append(
            "Task completion is below 50%."
        )

    if review["habit_completed"] == 0:
        improvements.append(
            "No habit completions were recorded."
        )

    if review["focus_minutes"] == 0:
        improvements.append(
            "No focus sessions were recorded."
        )

    if review["goal_completed"] == 0:
        improvements.append(
            "No goals were completed."
        )

    if improvements:

        for improvement in improvements:
            st.warning(improvement)

    else:

        st.success(
            "No major weaknesses detected this week. "
            "Keep the momentum going."
        )

# =========================================================
# SETTINGS
# =========================================================


elif page == "⚙️ Settings":

    st.title("⚙️ Settings")
    st.caption("Customize your LifeOS experience.")

    # -------------------------
    # Profile
    # -------------------------

    st.subheader("👤 Profile")

    current_username = get_setting("username")

    username = st.text_input(
        "Your Name",
        value=current_username,
        key="settings_username"
    )

    # -------------------------
    # Daily Goals
    # -------------------------

    st.subheader("🎯 Daily Goals")

    col1, col2 = st.columns(2)

    with col1:

        current_task_goal = int(
            get_setting("daily_task_goal")
        )

        daily_task_goal = st.number_input(
            "Daily Task Goal",
            min_value=1,
            max_value=100,
            value=current_task_goal,
            step=1,
            key="settings_task_goal"
        )

    with col2:

        current_focus_goal = int(
            get_setting("daily_focus_goal")
        )

        daily_focus_goal = st.number_input(
            "Daily Focus Goal (minutes)",
            min_value=5,
            max_value=1440,
            value=current_focus_goal,
            step=5,
            key="settings_focus_goal"
        )

    # -------------------------
    # Task Preferences
    # -------------------------

    st.subheader("📋 Task Preferences")

    current_show_completed = get_setting(
        "show_completed_tasks"
    )

    show_completed_tasks = st.selectbox(
        "Show Completed Tasks",
        [
            "Yes",
            "No"
        ],
        index=(
            0
            if current_show_completed == "Yes"
            else 1
        ),
        key="settings_completed_tasks"
    )

    # -------------------------
    # Theme
    # -------------------------

    st.subheader("🎨 Appearance")

    current_theme = get_setting("theme")

    theme_options = [
        "System",
        "Light",
        "Dark"
    ]

    theme = st.selectbox(
        "Theme",
        theme_options,
        index=(
            theme_options.index(current_theme)
            if current_theme in theme_options
            else 0
        ),
        key="settings_theme"
    )

    # -------------------------
    # Save Settings
    # -------------------------

    st.divider()

    if st.button(
        "💾 Save Settings",
        key="save_settings_button",
        use_container_width=True
    ):

        if not username.strip():
            st.warning("Please enter a name before saving.")
            st.stop()

        update_setting(
            "username",
            username
        )

        update_setting(
            "daily_task_goal",
            daily_task_goal
        )

        update_setting(
            "daily_focus_goal",
            daily_focus_goal
        )

        update_setting(
            "show_completed_tasks",
            show_completed_tasks
        )

        update_setting(
            "theme",
            theme
        )

        st.success(
            "Settings saved successfully."
        )

        st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption(
    "🚀 LifeOS • Build your days. Track your progress. Improve continuously."
)
