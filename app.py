"""
app.py — PawPal+ Streamlit UI  (Clean Edition)
-----------------------------------------------
Clean flat design wired to ALL Scheduler methods:
  generate_plan · sort_by_time · filter_tasks
  refresh_recurring_tasks · detect_conflicts · explain_plan
"""

import streamlit as st
from datetime import date
import pandas as pd

from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens – one place to change everything ──────────────────────────
ACCENT    = "#5B4FE8"      # solid indigo
ACCENT_LT = "#EEF0FF"      # tint of accent
BG        = "#F8F9FC"      # page background
CARD_BG   = "#FFFFFF"      # card surface
BORDER    = "#E4E7EF"      # subtle border
TEXT_PRI  = "#1A1D2E"      # primary text
TEXT_SEC  = "#6B7280"      # secondary / muted text

HIGH  = ("#D92B2B", "#FFF0F0")   # red  (fg, bg)
MED   = ("#B45309", "#FFFBEB")   # amber
LOW   = ("#15803D", "#F0FDF4")   # green

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {TEXT_PRI};
}}
.stApp {{
    background: {BG};
}}
.block-container {{
    padding-top: 2rem;
    max-width: 1100px;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {CARD_BG} !important;
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .block-container {{
    padding-top: 1.5rem;
}}

/* ── Cards ── */
.card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}}

/* ── Stat grid ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.6rem;
    margin-bottom: 1.2rem;
}}
.stat-tile {{
    background: {ACCENT_LT};
    border-radius: 10px;
    padding: 0.9rem 0.75rem;
    text-align: center;
}}
.stat-tile .num {{
    font-size: 1.7rem;
    font-weight: 700;
    color: {ACCENT};
    line-height: 1;
}}
.stat-tile .lbl {{
    font-size: 0.68rem;
    font-weight: 600;
    color: {TEXT_SEC};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}}

/* ── Section labels ── */
.sec-label {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TEXT_SEC};
    margin: 1.4rem 0 0.6rem;
}}

/* ── Priority badges ── */
.badge {{
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.b-high  {{ color: {HIGH[0]}; background: {HIGH[1]}; }}
.b-med   {{ color: {MED[0]};  background: {MED[1]};  }}
.b-low   {{ color: {LOW[0]};  background: {LOW[1]};  }}
.b-done  {{ color: {TEXT_SEC}; background: #F1F3F9; }}
.b-recur {{ color: {ACCENT}; background: {ACCENT_LT}; }}

/* ── Task cards ── */
.task-card {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    transition: box-shadow .15s;
}}
.task-card:hover {{
    box-shadow: 0 3px 10px rgba(0,0,0,.09);
}}
.tc-name {{ flex: 1; font-weight: 600; font-size: 0.95rem; }}
.tc-meta {{ font-size: 0.8rem; color: {TEXT_SEC}; margin-top: 2px; }}
.tc-dur  {{ font-size: 0.9rem; font-weight: 700; color: {ACCENT}; white-space: nowrap; }}

/* ── Plan steps ── */
.plan-card {{
    display: flex;
    align-items: center;
    gap: 16px;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 4px solid {ACCENT};
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1rem;
    margin-bottom: 0.55rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}}
.pc-num  {{ font-size: 1.1rem; font-weight: 700; color: {ACCENT}; min-width: 26px; }}
.pc-info {{ flex: 1; }}
.pc-name {{ font-weight: 600; }}
.pc-sub  {{ font-size: 0.78rem; color: {TEXT_SEC}; margin-top: 2px; }}
.pc-dur  {{ font-weight: 700; color: {ACCENT}; white-space: nowrap; }}

/* ── Conflict pill ── */
.conflict-pill {{
    background: #FFF4F4;
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 0.65rem 1rem;
    color: {HIGH[0]};
    font-size: 0.85rem;
    margin-bottom: 0.45rem;
}}

/* ── Buttons ── */
.stButton > button {{
    background: {ACCENT};
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.45rem 1.1rem;
    font-size: 0.9rem;
    transition: opacity .15s;
}}
.stButton > button:hover {{ opacity: 0.88; }}

/* ── Forms ── */
div[data-testid="stForm"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    border-bottom: 2px solid {BORDER};
    background: transparent;
    gap: 0;
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 500;
    font-size: 0.9rem;
    color: {TEXT_SEC} !important;
    padding: 0.6rem 1.2rem;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}}
.stTabs [aria-selected="true"] {{
    color: {ACCENT} !important;
    border-bottom: 2px solid {ACCENT};
    background: transparent !important;
    font-weight: 600;
}}

/* ── Expander ── */
details {{
    background: {CARD_BG};
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}}
summary {{ font-weight: 600; color: {TEXT_PRI}; padding: 0.6rem 1rem; }}

/* ── Divider ── */
hr {{ border-color: {BORDER}; }}

/* ── Input labels ── */
label {{ font-weight: 500 !important; font-size: 0.88rem !important; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
for key, val in [
    ("owner", None),
    ("last_plan", []),
    ("last_warnings", []),
    ("last_reasoning", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Helpers ──────────────────────────────────────────────────────────────────
PMAP  = {"High": 1, "Medium": 2, "Low": 3}
PBADGE = {
    1: '<span class="badge b-high">High</span>',
    2: '<span class="badge b-med">Medium</span>',
    3: '<span class="badge b-low">Low</span>',
}
PLABEL = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}

def task_card_html(task: CareTask) -> str:
    badge  = PBADGE.get(task.priority, "")
    recur  = f'<span class="badge b-recur" style="margin-left:6px">↺ {task.recurrence}</span>' if task.recurrence else ""
    done   = '<span class="badge b-done" style="margin-left:6px">✓ done</span>' if task.is_completed else ""
    due    = f" · due {task.due_date}" if task.due_date else ""
    return f"""
<div class="task-card">
  <div style="flex:1">
    <div class="tc-name">{task.name}</div>
    <div class="tc-meta">{task.pet_name}{due}</div>
  </div>
  {badge}{recur}{done}
  <div class="tc-dur">{task.duration} min</div>
</div>
"""

# ── Sidebar — profile ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🐾 PawPal+")
    st.caption("Your intelligent pet care planner")
    st.divider()

    st.markdown("**👤 Owner & Pet Profile**")
    with st.form("profile_form"):
        owner_name     = st.text_input("Your name", value="Jordan")
        available_time = st.number_input("Available time today (min)", min_value=5, max_value=480, value=90)
        pet_name       = st.text_input("Pet name", value="Fido")
        species        = st.text_input("Species / breed (optional)", value="Labrador")
        save_btn       = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if save_btn:
        pet   = Pet(name=pet_name, species_breed=species or None)
        owner = Owner(name=owner_name, available_time=int(available_time))
        owner.add_pet(pet)
        st.session_state.owner          = owner
        st.session_state.last_plan      = []
        st.session_state.last_warnings  = []
        st.session_state.last_reasoning = ""
        st.success(f"Profile saved — hi, {owner_name}! 👋")

    if st.session_state.owner:
        o         = st.session_state.owner
        all_t     = o.get_all_tasks()
        completed = sum(1 for t in all_t if t.is_completed)
        needed    = sum(t.duration for t in all_t if not t.is_completed)

        st.divider()
        st.markdown("**📊 Overview**")
        st.markdown(f"""
<div class="stat-grid">
  <div class="stat-tile"><div class="num">{len(all_t)}</div><div class="lbl">Tasks</div></div>
  <div class="stat-tile"><div class="num">{completed}</div><div class="lbl">Done</div></div>
  <div class="stat-tile"><div class="num">{needed}m</div><div class="lbl">Needed</div></div>
  <div class="stat-tile"><div class="num">{o.available_time}m</div><div class="lbl">Available</div></div>
</div>
""", unsafe_allow_html=True)


# ── Guard ────────────────────────────────────────────────────────────────────
if st.session_state.owner is None:
    st.markdown(f"""
<div class="card" style="text-align:center; padding:3rem 2rem;">
  <div style="font-size:3rem; margin-bottom:1rem;">🐾</div>
  <div style="font-size:1.4rem; font-weight:700; margin-bottom:.5rem;">Welcome to PawPal+</div>
  <div style="color:{TEXT_SEC}">Fill in your profile in the sidebar to get started.</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

owner = st.session_state.owner

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_add, tab_view, tab_sched = st.tabs([
    "➕  Add Task",
    "📋  View & Manage",
    "🗓️  Schedule",
])


# =============================================================================
# TAB 1 — Add Task
# =============================================================================
with tab_add:
    st.markdown('<div class="sec-label">New care task</div>', unsafe_allow_html=True)

    with st.form("task_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1.5, 1.5])
        with c1:
            task_title   = st.text_input("Task name", placeholder="e.g. Morning Walk")
        with c2:
            duration     = st.number_input("Duration (min)", min_value=1, max_value=360, value=30)
        with c3:
            priority_str = st.selectbox("Priority", ["High", "Medium", "Low"])

        c4, c5, c6 = st.columns(3)
        with c4:
            target_pet = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        with c5:
            recurrence = st.selectbox("Recurrence", ["None", "daily", "weekly"])
        with c6:
            due_date = st.date_input("Due date", value=date.today())

        add_btn = st.form_submit_button("➕  Add Task", use_container_width=True)

    if add_btn and task_title.strip():
        task = CareTask(
            name       = task_title.strip(),
            pet_name   = target_pet,
            duration   = int(duration),
            priority   = PMAP[priority_str],
            recurrence = None if recurrence == "None" else recurrence,
            due_date   = due_date,
        )
        for p in owner.pets:
            if p.name == target_pet:
                p.add_task(task)
                break
        st.success(
            f"✅ **{task.name}** added for **{target_pet}** — "
            f"{duration} min · {priority_str}"
            + (f" · repeats {recurrence}" if recurrence != "None" else "")
        )
        st.rerun()
    elif add_btn:
        st.warning("Please enter a task name.")


# =============================================================================
# TAB 2 — View & Manage
# =============================================================================
with tab_view:
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.info("No tasks yet — add some in the **Add Task** tab.")
    else:
        scheduler = Scheduler(owner)

        # ── Filter / sort controls ───────────────────────────────────────────
        st.markdown('<div class="sec-label">Filter & Sort</div>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_pet  = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
        with fc2:
            filter_done = st.selectbox("Status", ["All", "Pending", "Completed"])
        with fc3:
            sort_opt    = st.selectbox("Sort by", ["Priority then duration", "Duration (shortest first)"])

        filtered = scheduler.filter_tasks(
            pet_name  = None if filter_pet  == "All pets" else filter_pet,
            completed = None if filter_done == "All" else (filter_done == "Completed"),
        )
        if sort_opt == "Duration (shortest first)":
            display = scheduler.sort_by_time(filtered)
        else:
            display = sorted(filtered, key=lambda t: (t.priority, t.duration))

        st.markdown(
            f'<div class="sec-label">{len(display)} task(s)</div>',
            unsafe_allow_html=True,
        )

        for i, task in enumerate(display):
            st.markdown(task_card_html(task), unsafe_allow_html=True)
            bc1, bc2, _ = st.columns([1, 1, 5])
            with bc1:
                if st.button("↩ Undo" if task.is_completed else "✓ Mark done", key=f"done_{id(task)}_{i}"):
                    task.mark_complete()
                    st.rerun()
            with bc2:
                if st.button("🗑 Delete", key=f"del_{id(task)}_{i}"):
                    for p in owner.pets:
                        if task in p.tasks:
                            p.tasks.remove(task)
                    st.rerun()

        # ── Sorted table ─────────────────────────────────────────────────────
        st.divider()
        st.markdown('<div class="sec-label">Sorted task table</div>', unsafe_allow_html=True)
        rows = [{
            "Task":       t.name,
            "Pet":        t.pet_name,
            "Duration":   f"{t.duration} min",
            "Priority":   PLABEL.get(t.priority, "—"),
            "Recurrence": t.recurrence or "—",
            "Due":        str(t.due_date) if t.due_date else "—",
            "Status":     "✓ Done" if t.is_completed else "○ Pending",
        } for t in scheduler.sort_by_time(filtered)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ── Recurring refresh ─────────────────────────────────────────────────
        st.divider()
        st.markdown('<div class="sec-label">Recurring tasks</div>', unsafe_allow_html=True)
        done_recurring = [t for t in all_tasks if t.is_completed and t.recurrence]
        if done_recurring:
            if st.button("🔄  Generate next occurrences"):
                new_tasks = scheduler.refresh_recurring_tasks()
                if new_tasks:
                    for nt in new_tasks:
                        st.success(f"✅ Created **{nt.name}** for {nt.pet_name} — due {nt.due_date}")
                    st.rerun()
                else:
                    st.info("No new recurring tasks generated.")
        else:
            st.caption("Mark a recurring task as done to generate the next occurrence automatically.")


# =============================================================================
# TAB 3 — Schedule & Insights
# =============================================================================
with tab_sched:
    pending = [t for t in owner.get_all_tasks() if not t.is_completed]

    if not owner.get_all_tasks():
        st.info("Add tasks first in the **Add Task** tab.")
    elif not pending:
        st.success("🎉 All tasks complete! Add more or refresh recurring tasks.")
    else:
        st.markdown('<div class="sec-label">Generate today\'s plan</div>', unsafe_allow_html=True)

        if st.button("🚀  Generate Optimal Schedule", use_container_width=True):
            sched = Scheduler(owner)
            st.session_state.last_plan      = sched.generate_plan()
            st.session_state.last_warnings  = sched.detect_conflicts()
            st.session_state.last_reasoning = sched.explain_plan()

        plan      = st.session_state.last_plan
        warnings  = st.session_state.last_warnings
        reasoning = st.session_state.last_reasoning

        if plan:
            # ── Summary tiles ─────────────────────────────────────────────────
            total   = sum(t.duration for t in plan)
            left    = owner.available_time - total
            skipped = len(pending) - len(plan)

            st.markdown(f"""
<div style="display:flex; gap:.8rem; margin: .8rem 0 1.2rem; flex-wrap:wrap;">
  <div class="card" style="flex:1; text-align:center; min-width:110px; padding:1rem;">
    <div style="font-size:1.8rem; font-weight:700; color:{ACCENT}">{len(plan)}</div>
    <div style="font-size:.72rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:.06em; margin-top:4px">Scheduled</div>
  </div>
  <div class="card" style="flex:1; text-align:center; min-width:110px; padding:1rem;">
    <div style="font-size:1.8rem; font-weight:700; color:{ACCENT}">{total}m</div>
    <div style="font-size:.72rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:.06em; margin-top:4px">Total time</div>
  </div>
  <div class="card" style="flex:1; text-align:center; min-width:110px; padding:1rem;">
    <div style="font-size:1.8rem; font-weight:700; color:{ACCENT}">{left}m</div>
    <div style="font-size:.72rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:.06em; margin-top:4px">Remaining</div>
  </div>
  <div class="card" style="flex:1; text-align:center; min-width:110px; padding:1rem;">
    <div style="font-size:1.8rem; font-weight:700; color:{ACCENT if skipped==0 else HIGH[0]}">{skipped}</div>
    <div style="font-size:.72rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:.06em; margin-top:4px">Skipped</div>
  </div>
</div>
""", unsafe_allow_html=True)

            # ── Conflicts ──────────────────────────────────────────────────────
            if warnings:
                st.markdown('<div class="sec-label">⚠️ Conflict warnings</div>', unsafe_allow_html=True)
                for w in warnings:
                    st.markdown(f'<div class="conflict-pill">{w}</div>', unsafe_allow_html=True)
            else:
                st.success("✅ No scheduling conflicts detected.")

            # ── Plan steps ────────────────────────────────────────────────────
            st.markdown('<div class="sec-label">Today\'s plan</div>', unsafe_allow_html=True)
            cursor = 0
            for i, task in enumerate(plan, 1):
                s = f"{cursor//60:02d}:{cursor%60:02d}"
                e = f"{(cursor+task.duration)//60:02d}:{(cursor+task.duration)%60:02d}"
                badge = PBADGE.get(task.priority, "")
                recur = f'<span class="badge b-recur" style="margin-left:6px">↺ {task.recurrence}</span>' if task.recurrence else ""
                st.markdown(f"""
<div class="plan-card">
  <div class="pc-num">{i}</div>
  <div class="pc-info">
    <div class="pc-name">{task.name} &nbsp;{badge}{recur}</div>
    <div class="pc-sub">{task.pet_name} &nbsp;·&nbsp; {s} → {e}</div>
  </div>
  <div class="pc-dur">{task.duration} min</div>
</div>
""", unsafe_allow_html=True)
                cursor += task.duration

            # ── Progress bar ──────────────────────────────────────────────────
            st.markdown('<div class="sec-label">Time utilisation</div>', unsafe_allow_html=True)
            pct = min(total / owner.available_time, 1.0) if owner.available_time else 0
            st.progress(pct, text=f"{total} of {owner.available_time} min used ({pct*100:.0f}%)")

            # ── Reasoning ─────────────────────────────────────────────────────
            with st.expander("🧠 Scheduler reasoning"):
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
            st.warning("No tasks fit within your available time. Try increasing your available minutes or shortening task durations.")
