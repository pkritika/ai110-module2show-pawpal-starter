"""
app.py — PawPal+ Streamlit UI
-------------------------------
Clean, native-component-first design.
Wires all Scheduler methods to the UI.
"""

import streamlit as st
from datetime import date
import pandas as pd
from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal CSS: only fix what Streamlit can't do natively ──────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Tighten the top padding */
.block-container { padding-top: 1.8rem; padding-bottom: 2rem; }

/* Primary button color — coral/teal warmth */
.stButton > button {
    background-color: #0D9488;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: background-color .2s;
}
.stButton > button:hover { background-color: #0F766E; }

/* Active tab underline */
.stTabs [aria-selected="true"] {
    color: #0D9488 !important;
    border-bottom-color: #0D9488 !important;
    font-weight: 600;
}

/* Sidebar top border accent */
section[data-testid="stSidebar"] {
    border-right: 3px solid #0D9488;
}

/* Make st.metric numbers teal */
[data-testid="stMetricValue"] { color: #0D9488 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("owner", None), ("plan", []), ("warnings", []), ("reasoning", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

PMAP   = {"High": 1, "Medium": 2, "Low": 3}
PLABEL = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/391/paw-prints_1f43e.png", width=52)
    st.title("PawPal+")
    st.caption("Smart pet care scheduling")
    st.divider()

    st.subheader("👤 Your Profile")
    with st.form("profile_form"):
        owner_name     = st.text_input("Your name", value="Jordan")
        available_time = st.number_input("Free time today (min)", 5, 480, 90)
        pet_name       = st.text_input("Pet name", value="Fido")
        species        = st.text_input("Breed / species", value="Labrador")
        saved = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if saved:
        pet = Pet(name=pet_name, species_breed=species or None)
        o   = Owner(name=owner_name, available_time=int(available_time))
        o.add_pet(pet)
        st.session_state.owner    = o
        st.session_state.plan     = []
        st.session_state.warnings = []
        st.session_state.reasoning = ""
        st.success(f"Hi {owner_name}! Profile saved 🎉")

    if st.session_state.owner:
        owner     = st.session_state.owner
        all_tasks = owner.get_all_tasks()
        done      = sum(1 for t in all_tasks if t.is_completed)
        needed    = sum(t.duration for t in all_tasks if not t.is_completed)

        st.divider()
        st.subheader("📊 Overview")
        c1, c2 = st.columns(2)
        c1.metric("Tasks", len(all_tasks))
        c2.metric("Done", done)
        c1.metric("Time needed", f"{needed}m")
        c2.metric("Available", f"{owner.available_time}m")


# ══════════════════════════════════════════════════════════════════════════════
# GUARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.owner is None:
    st.title("🐾 Welcome to PawPal+")
    st.info("Fill in your **Owner & Pet Profile** in the sidebar to get started.")
    st.stop()

owner = st.session_state.owner

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_add, tab_manage, tab_sched = st.tabs([
    "  ➕ Add Task  ",
    "  📋 Manage Tasks  ",
    "  🗓️ Schedule  ",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Add Task
# ─────────────────────────────────────────────────────────────────────────────
with tab_add:
    st.header("Add a Care Task")
    st.caption("Create tasks for your pet. Set a priority, duration, and optionally a recurrence.")

    with st.form("task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        task_name    = col1.text_input("Task name *", placeholder="e.g. Morning Walk")
        duration     = col2.number_input("Duration (min)", 1, 360, 30)
        priority_str = col3.selectbox("Priority", ["High", "Medium", "Low"])

        col4, col5, col6 = st.columns(3)
        target_pet   = col4.selectbox("Assign to", [p.name for p in owner.pets])
        recurrence   = col5.selectbox("Repeats", ["Never", "daily", "weekly"])
        due_date     = col6.date_input("Due date", value=date.today())

        submitted = st.form_submit_button("➕ Add Task", use_container_width=True)

    if submitted:
        if not task_name.strip():
            st.warning("Please enter a task name.")
        else:
            t = CareTask(
                name       = task_name.strip(),
                pet_name   = target_pet,
                duration   = int(duration),
                priority   = PMAP[priority_str],
                recurrence = None if recurrence == "Never" else recurrence,
                due_date   = due_date,
            )
            for p in owner.pets:
                if p.name == target_pet:
                    p.add_task(t)
            recur_note = f" · repeats {recurrence}" if recurrence != "Never" else ""
            st.success(f"✅ **{t.name}** added for **{target_pet}** — {duration} min · {priority_str}{recur_note}")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Manage Tasks
# ─────────────────────────────────────────────────────────────────────────────
with tab_manage:
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.info("No tasks yet. Head to **Add Task** to create your first one.")
    else:
        scheduler = Scheduler(owner)

        st.header("View & Manage Tasks")

        # Filter / sort bar
        f1, f2, f3 = st.columns(3)
        fp  = f1.selectbox("Filter by pet",    ["All"] + [p.name for p in owner.pets])
        fs  = f2.selectbox("Filter by status", ["All", "Pending", "Completed"])
        srt = f3.selectbox("Sort by",          ["Priority → Duration", "Duration (shortest first)"])

        filtered = scheduler.filter_tasks(
            pet_name  = None if fp == "All" else fp,
            completed = None if fs == "All" else (fs == "Completed"),
        )
        tasks_to_show = (
            scheduler.sort_by_time(filtered)
            if srt == "Duration (shortest first)"
            else sorted(filtered, key=lambda t: (t.priority, t.duration))
        )

        st.divider()

        if not tasks_to_show:
            st.info("No tasks match your filters.")
        else:
            for i, task in enumerate(tasks_to_show):
                status_icon = "✅" if task.is_completed else "⏳"
                recur_tag   = f"  `↺ {task.recurrence}`" if task.recurrence else ""
                due_tag     = f"  · due **{task.due_date}**" if task.due_date else ""
                priority_lbl = PLABEL.get(task.priority, "")

                with st.container():
                    tc1, tc2, tc3, tc4, tc5 = st.columns([.15, 2.5, 1, 1, 1])
                    tc1.markdown(f"### {status_icon}")
                    tc2.markdown(
                        f"**{task.name}** &nbsp; {priority_lbl}{recur_tag}\n\n"
                        f"<sub>{task.pet_name} · {task.duration} min{due_tag}</sub>",
                        unsafe_allow_html=True,
                    )
                    if tc3.button("✓ Done" if not task.is_completed else "↩ Undo", key=f"chk_{i}"):
                        task.mark_complete()
                        st.rerun()
                    if tc4.button("🗑 Delete", key=f"del_{i}"):
                        for p in owner.pets:
                            if task in p.tasks:
                                p.tasks.remove(task)
                        st.rerun()
                st.divider()

        # ── Sorted table ──────────────────────────────────────────────────────
        st.subheader("📊 Sorted Task Table")
        st.caption("Tasks sorted by duration (shortest first) via Scheduler.sort_by_time()")
        rows = [{
            "Task":       t.name,
            "Pet":        t.pet_name,
            "Duration":   f"{t.duration} min",
            "Priority":   PLABEL.get(t.priority, "—"),
            "Recurrence": t.recurrence or "—",
            "Due":        str(t.due_date) if t.due_date else "—",
            "Status":     "✅ Done" if t.is_completed else "⏳ Pending",
        } for t in scheduler.sort_by_time(filtered)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ── Recurring refresh ─────────────────────────────────────────────────
        st.divider()
        st.subheader("🔄 Recurring Task Refresh")
        done_recurring = [t for t in all_tasks if t.is_completed and t.recurrence]
        if done_recurring:
            st.caption(f"{len(done_recurring)} completed recurring task(s) ready for refresh.")
            if st.button("🔄 Generate next occurrences", use_container_width=True):
                new = scheduler.refresh_recurring_tasks()
                if new:
                    for nt in new:
                        st.success(f"✅ **{nt.name}** → {nt.pet_name} · due {nt.due_date}")
                    st.rerun()
                else:
                    st.info("Nothing new to generate.")
        else:
            st.caption("Mark a recurring task as done to auto-generate the next occurrence.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Schedule
# ─────────────────────────────────────────────────────────────────────────────
with tab_sched:
    pending = [t for t in owner.get_all_tasks() if not t.is_completed]

    if not owner.get_all_tasks():
        st.info("Add tasks first in the **Add Task** tab.")
        st.stop()
    elif not pending:
        st.success("🎉 All tasks complete for today! Add more or refresh recurring ones.")
        st.stop()

    st.header("Today's Schedule")
    st.caption("The scheduler picks the highest-priority tasks that fit within your available time.")

    if st.button("🚀 Generate Optimal Schedule", use_container_width=True):
        sched = Scheduler(owner)
        st.session_state.plan      = sched.generate_plan()
        st.session_state.warnings  = sched.detect_conflicts()
        st.session_state.reasoning = sched.explain_plan()

    plan      = st.session_state.plan
    warnings  = st.session_state.warnings
    reasoning = st.session_state.reasoning

    if plan:
        # Summary metrics
        total   = sum(t.duration for t in plan)
        left    = owner.available_time - total
        skipped = len(pending) - len(plan)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tasks Scheduled", len(plan))
        m2.metric("Total Time",      f"{total} min")
        m3.metric("Time Remaining",  f"{left} min")
        m4.metric("Skipped",         skipped, delta=f"-{skipped}" if skipped else None,
                  delta_color="inverse" if skipped else "off")

        st.divider()

        # Conflict warnings
        if warnings:
            st.subheader("⚠️ Conflict Warnings")
            for w in warnings:
                st.warning(w)
        else:
            st.success("✅ No scheduling conflicts — your plan is clean!")

        st.divider()

        # Plan steps
        st.subheader("📋 Your Plan")
        cursor = 0
        for i, task in enumerate(plan, 1):
            s = f"{cursor // 60:02d}:{cursor % 60:02d}"
            e_min = cursor + task.duration
            e = f"{e_min // 60:02d}:{e_min % 60:02d}"
            recur = f"  ·  ↺ {task.recurrence}" if task.recurrence else ""

            pc1, pc2, pc3 = st.columns([.5, 4, 1])
            pc1.markdown(f"### {i}")
            pc2.markdown(
                f"**{task.name}** &nbsp; {PLABEL.get(task.priority, '')}{recur}\n\n"
                f"<sub>{task.pet_name} &nbsp; · &nbsp; {s} → {e}</sub>",
                unsafe_allow_html=True,
            )
            pc3.markdown(f"**{task.duration} min**")
            st.divider()
            cursor += task.duration

        # Progress bar
        pct = min(total / owner.available_time, 1.0) if owner.available_time else 0
        st.subheader("⏱ Time Utilisation")
        st.progress(pct, text=f"{total} of {owner.available_time} min used ({pct*100:.0f}%)")

        # Reasoning
        st.divider()
        with st.expander("🧠 Scheduler Reasoning"):
            for line in reasoning.split("\n"):
                if not line.strip():
                    continue
                if line.startswith("Added"):
                    st.success(line)
                elif line.startswith("Skipped"):
                    st.warning(line)
                else:
                    st.info(line)

    elif reasoning:
        st.warning("⚠️ No tasks fit within your available time. Try increasing your free minutes or shortening task durations.")
