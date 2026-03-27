"""
app.py — PawPal+  ·  Snowchat-inspired dark UI
------------------------------------------------
Dark theme driven by .streamlit/config.toml
All Scheduler methods wired: generate_plan, sort_by_time,
filter_tasks, refresh_recurring_tasks, detect_conflicts
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

# ── Minimal CSS: brand title + a few fine-tune tweaks ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Tighten main padding */
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 960px; }

/* Brand title */
.brand-title {
    font-size: 3.8rem;
    font-weight: 800;
    color: #FF4B6E;
    letter-spacing: -2px;
    line-height: 1;
    text-align: center;
}
.brand-sub {
    text-align: center;
    color: #8B8FA8;
    font-size: 1rem;
    margin-top: 6px;
    margin-bottom: 2rem;
}

/* Sidebar brand */
.sidebar-brand {
    font-size: 1.6rem;
    font-weight: 800;
    color: #FF4B6E;
    margin-bottom: 0.2rem;
}

/* Tab underline fix */
.stTabs [aria-selected="true"] {
    color: #FF4B6E !important;
    border-bottom-color: #FF4B6E !important;
    font-weight: 700;
}
.stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 500; }

/* Metric values */
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; }

/* Hide the hamburger and footer */
#MainMenu, footer { visibility: hidden; }
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
    st.markdown('<div class="sidebar-brand">🐾 PawPal+</div>', unsafe_allow_html=True)
    st.caption("Intelligent pet care scheduling")
    st.divider()

    # ── Profile form ──
    st.markdown("**👤 Owner & Pet Profile**")
    with st.form("profile_form"):
        owner_name     = st.text_input("Your name", value="Jordan", placeholder="Your name")
        available_time = st.number_input("Free time today (min)", 5, 480, 90)
        pet_name       = st.text_input("Pet name", value="Fido")
        species        = st.text_input("Breed / species", value="Labrador")
        saved = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if saved:
        pet = Pet(name=pet_name, species_breed=species or None)
        o   = Owner(name=owner_name, available_time=int(available_time))
        o.add_pet(pet)
        st.session_state.owner     = o
        st.session_state.plan      = []
        st.session_state.warnings  = []
        st.session_state.reasoning = ""
        st.success(f"Hi {owner_name}! Profile saved 🎉")

    # ── Stats + Features ──
    if st.session_state.owner:
        owner     = st.session_state.owner
        all_tasks = owner.get_all_tasks()
        done      = sum(1 for t in all_tasks if t.is_completed)
        needed    = sum(t.duration for t in all_tasks if not t.is_completed)

        st.divider()
        st.markdown("**📊 Overview**")
        c1, c2 = st.columns(2)
        c1.metric("Tasks",     len(all_tasks))
        c2.metric("Complete",  done)
        c1.metric("Needed",    f"{needed} min")
        c2.metric("Available", f"{owner.available_time} min")

    st.divider()
    st.markdown("**✨ Features**")
    st.markdown("""
- 🔴 **Priority Scheduling** — High urgency tasks go first
- ⏱ **Time-aware** — Only fits what you have time for
- 🔄 **Recurring Tasks** — Auto-generates next occurrences
- 🔍 **Filter & Sort** — Find tasks by pet or status
- ⚠️ **Conflict Detection** — Flags overlapping tasks
- 🧠 **Reasoning** — Explains every scheduling decision
""")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Brand header always visible
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<h1 style="font-size:3.6rem;font-weight:800;color:#FF4B6E;letter-spacing:-2px;'
    'text-align:center;line-height:1;margin-bottom:4px;">pawpal+</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="text-align:center;color:#8B8FA8;font-size:1rem;margin-top:0;margin-bottom:1.5rem;">'
    'Your smart pet care planning assistant</p>',
    unsafe_allow_html=True,
)

if st.session_state.owner is None:
    st.info("👈  Set up your **Owner & Pet Profile** in the sidebar to get started.")
    st.stop()

owner = st.session_state.owner

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_add, tab_manage, tab_sched = st.tabs([
    "  ➕  Add Task  ",
    "  📋  Manage Tasks  ",
    "  🗓️  Schedule  ",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Add Task
# ─────────────────────────────────────────────────────────────────────────────
with tab_add:
    st.subheader("Add a Care Task")
    st.caption("Create a new task and assign it to your pet.")

    with st.form("task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        task_name    = col1.text_input("Task name *", placeholder="e.g. Morning Walk")
        duration     = col2.number_input("Duration (min)", 1, 360, 30)
        priority_str = col3.selectbox("Priority", ["High", "Medium", "Low"])

        col4, col5, col6 = st.columns(3)
        target_pet = col4.selectbox("Assign to", [p.name for p in owner.pets])
        recurrence = col5.selectbox("Repeats", ["Never", "daily", "weekly"])
        due_date   = col6.date_input("Due date", value=date.today())

        submitted = st.form_submit_button("➕  Add Task", use_container_width=True)

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
            recur_note = f" · repeats **{recurrence}**" if recurrence != "Never" else ""
            st.success(f"✅ **{t.name}** added for **{target_pet}** — {duration} min · {priority_str}{recur_note}")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Manage Tasks
# ─────────────────────────────────────────────────────────────────────────────
with tab_manage:
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.info("No tasks yet — add some in the **Add Task** tab.")
    else:
        scheduler = Scheduler(owner)

        st.subheader("Filter & Sort")
        f1, f2, f3 = st.columns(3)
        fp  = f1.selectbox("Pet",    ["All"] + [p.name for p in owner.pets])
        fs  = f2.selectbox("Status", ["All", "Pending", "Completed"])
        srt = f3.selectbox("Sort",   ["Priority → Duration", "Duration (shortest first)"])

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
                icon = "✅" if task.is_completed else "⏳"
                recur = f"  •  ↺ `{task.recurrence}`" if task.recurrence else ""
                due   = f"  •  due {task.due_date}" if task.due_date else ""

                tc1, tc2, tc3, tc4 = st.columns([0.3, 4, 1.1, 1.1])
                tc1.markdown(f"## {icon}")
                tc2.markdown(
                    f"**{task.name}**  &nbsp; {PLABEL.get(task.priority, '')}{recur}\n\n"
                    f"<sub style='color:#8B8FA8'>{task.pet_name}  •  {task.duration} min{due}</sub>",
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
        st.subheader("📊 Task Table  ·  sorted by duration")
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
            st.caption(f"{len(done_recurring)} completed recurring task(s) ready to roll over.")
            if st.button("🔄  Generate next occurrences", use_container_width=True):
                new = scheduler.refresh_recurring_tasks()
                if new:
                    for nt in new:
                        st.success(f"✅ **{nt.name}** → {nt.pet_name}  ·  due {nt.due_date}")
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
    if not pending:
        st.success("🎉 All tasks complete! Add more or refresh recurring ones.")
        st.stop()

    st.subheader("Generate Today's Plan")
    st.caption("The scheduler picks highest-priority tasks that fit within your available time.")

    if st.button("🚀  Generate Optimal Schedule", use_container_width=True):
        sched = Scheduler(owner)
        st.session_state.plan      = sched.generate_plan()
        st.session_state.warnings  = sched.detect_conflicts()
        st.session_state.reasoning = sched.explain_plan()

    plan      = st.session_state.plan
    warnings  = st.session_state.warnings
    reasoning = st.session_state.reasoning

    if plan:
        total   = sum(t.duration for t in plan)
        left    = owner.available_time - total
        skipped = len(pending) - len(plan)

        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scheduled",      len(plan))
        m2.metric("Total Time",     f"{total} min")
        m3.metric("Time Left",      f"{left} min")
        m4.metric("Skipped",        skipped)

        st.divider()

        # Conflict warnings
        if warnings:
            st.subheader("⚠️  Conflicts Detected")
            for w in warnings:
                st.warning(w)
        else:
            st.success("✅  No conflicts — your schedule is clean!")

        st.divider()

        # Plan steps
        st.subheader("📋  Today's Plan")
        cursor = 0
        for i, task in enumerate(plan, 1):
            s   = f"{cursor // 60:02d}:{cursor % 60:02d}"
            end = cursor + task.duration
            e   = f"{end // 60:02d}:{end % 60:02d}"
            recur = f"  ·  ↺ `{task.recurrence}`" if task.recurrence else ""

            pc1, pc2, pc3 = st.columns([0.4, 5, 1])
            pc1.markdown(f"### {i}.")
            pc2.markdown(
                f"**{task.name}**  &nbsp; {PLABEL.get(task.priority, '')}{recur}\n\n"
                f"<sub style='color:#8B8FA8'>{task.pet_name}  •  {s} → {e}</sub>",
                unsafe_allow_html=True,
            )
            pc3.markdown(f"**{task.duration} min**")
            st.divider()
            cursor += task.duration

        # Time bar
        pct = min(total / owner.available_time, 1.0) if owner.available_time else 0
        st.subheader("⏱  Time Used")
        st.progress(pct, text=f"{total} of {owner.available_time} min  ({pct*100:.0f}%)")

        # Reasoning
        st.divider()
        with st.expander("🧠  Scheduler Reasoning — why each task was chosen or skipped"):
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
        st.warning("No tasks fit within your available time. Try increasing your free minutes or shortening task durations.")
