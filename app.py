"""
app.py – PawPal+ Premium Edition
All HTML uses inline styles only (100% reliable in Streamlit).
Pre-populated sample data renders immediately on first load.
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── 1. Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+ Pro",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Only override button color — no CSS classes on anything else
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* ── Base size-up ─────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    font-size: 17px;
}
/* ── Force dark mode — cannot be overridden by OS light preference ── */
html, body {
    background-color: #0E1117 !important;
    color: #FAFAFA !important;
}
[data-testid="stApp"] {
    background-color: #0E1117 !important;
}
[data-testid="stAppViewContainer"] {
    background-color: #0E1117 !important;
}
[data-testid="stSidebar"] {
    background-color: #1A1C24 !important;
}
/* Ensure all plain text gets the light color */
p, li, span, label, div, h1, h2, h3, h4 {
    color: inherit;
}
.block-container  { padding-top: 1.2rem; max-width: 1200px; }
#MainMenu, footer { visibility: hidden; }

/* ── Hide top Streamlit header strip ─────────────────────────── */
header[data-testid="stHeader"] {
    background: #0E1117 !important;
    border-bottom: none !important;
}
/* ── Tab labels — always visible ─────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #8B8FA8 !important;
    background: transparent !important;
    padding: .7rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: #FF4B6E !important;
    border-bottom: 2px solid #FF4B6E !important;
    font-weight: 700 !important;
}
/* ── Number input (spinButton) — dark pill ────────────────────── */
div[data-baseweb="spinButton"] {
    background: #1A1C24 !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 50px !important;
    height: 3.2rem !important;
}
div[data-baseweb="spinButton"] input {
    background: transparent !important;
    color: #FAFAFA !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
}
div[data-baseweb="spinButton"] button {
    background: transparent !important;
    color: #BDBDBD !important;
}
/* ── Date input — dark pill ───────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="input"] input[type="text"] {
    background: transparent !important;
    color: #FAFAFA !important;
    font-size: 1.05rem !important;
}
/* ── Select option text visible ───────────────────────────────── */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="placeholder"] {
    color: #FAFAFA !important;
}

/* ── Sidebar brand glow ───────────────────────────────────────── */
[data-testid="stSidebar"] { font-size: 1rem; }

/* ── Widget labels ────────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p { font-size: 0.95rem !important; font-weight: 600; }

/* ── Metric numbers ───────────────────────────────────────────── */
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; }

/* ── Pill-shaped inputs ────────────────────────────────────────── */
/* Text inputs */
div[data-baseweb="input"] {
    border-radius: 50px !important;
    overflow: hidden;
}
div[data-baseweb="base-input"] {
    background: #1A1C24 !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 50px !important;
    padding: 0 1.4rem !important;
    height: 3.2rem !important;
    transition: border-color .25s, box-shadow .25s;
}
div[data-baseweb="base-input"]:focus-within {
    border-color: #FF4B6E !important;
    box-shadow: 0 0 0 3px rgba(255,75,110,.18) !important;
}
div[data-baseweb="base-input"] input {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    color: #FAFAFA !important;
    background: transparent !important;
}
/* Selects / dropdowns */
div[data-baseweb="select"] > div {
    background: #1A1C24 !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 50px !important;
    padding: 0 1.4rem !important;
    height: 3.2rem !important;
    transition: border-color .25s, box-shadow .25s;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #FF4B6E !important;
    box-shadow: 0 0 0 3px rgba(255,75,110,.18) !important;
}
/* Widget labels — bigger & bolder */
[data-testid="stWidgetLabel"] p { font-size: 0.95rem !important; font-weight: 600 !important; letter-spacing:.3px; }
/* Date input */
div[data-baseweb="input"] input[type="text"] { padding:0 !important; }
/* ── Primary button: big oval ──────────────────────────────────── */
.stButton > button[kind="primary"] {
    border-radius: 50px !important;
    height: 3.2rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    background: #FF4B6E !important;
    border: none !important;
    letter-spacing: .5px;
    transition: transform .2s, box-shadow .2s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 28px rgba(255,75,110,.45) !important;
    background: #e0344e !important;
}
/* ── Secondary/default buttons: also rounded ───────────────────── */
.stButton > button:not([kind="primary"]) {
    border-radius: 50px !important;
    font-size: .95rem !important;
    font-weight: 600 !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #FF4B6E !important;
    box-shadow: 0 0 0 2px rgba(255,75,110,.2) !important;
}
/* ── Premium Add Task container box ───────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.03) !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 2rem !important;
    position: relative;
    box-shadow:
        0 0 0 1.5px rgba(255,75,110,0.25),
        0 8px 40px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    transition: box-shadow .35s;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow:
        0 0 0 1.5px rgba(255,75,110,0.5),
        0 12px 50px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ── 2. Session state + sample data seed ────────────────────────────────────
def _make_sample_owner():
    luna  = Pet("Luna",  "Labrador")
    bella = Pet("Bella", "Poodle")
    for task in [
        CareTask("Walk Luna",           "Luna",  30, 1, "daily",  date.today()),
        CareTask("Feed Bella",          "Bella", 30, 2, None,     date.today()),
        CareTask("Vet Appointment",     "Luna",  30, 1, None,     date.today()),
        CareTask("Grooming - Buddy",    "Bella", 60, 3, "weekly", date.today()),
    ]:
        if task.pet_name == "Luna":
            luna.add_task(task)
        else:
            bella.add_task(task)
    # Mark first three done for the progress bar demo
    luna.tasks[0].mark_complete()
    bella.tasks[0].mark_complete()
    luna.tasks[1].mark_complete()
    o = Owner("Sarah", 180)
    o.add_pet(luna); o.add_pet(bella)
    return o

for k, v in [("owner", None), ("plan", []), ("warnings", []), ("reasoning", ""), ("seeded", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-seed sample data on first load
if not st.session_state.seeded:
    st.session_state.owner  = _make_sample_owner()
    st.session_state.seeded = True

PMAP   = {"High": 1, "Medium": 2, "Low": 3}
PLABEL = {1: "HIGH", 2: "MED", 3: "NORMAL"}
PCOLOR = {1: "#FF4B6E", 2: "#F59E0B", 3: "#10B981"}

# ── helpers ─────────────────────────────────────────────────────────────────
def card_style(hover_glow=True):
    return (
        "display:flex;align-items:center;gap:1rem;"
        "background:rgba(255,255,255,0.04);"
        "border:1px solid rgba(255,255,255,0.09);"
        "border-radius:14px;padding:1rem 1.2rem;"
        "margin-bottom:.75rem;"
    )

def pill(label, color, bg=None):
    bg = bg or color + "22"
    return (
        f'<span style="background:{bg};color:{color};'
        f'padding:3px 10px;border-radius:50px;'
        f'font-size:.9rem;font-weight:700;margin-right:5px;">'
        f'{label}</span>'
    )

def chip(label):
    return (
        f'<span style="background:rgba(255,255,255,0.08);color:#BDBDBD;'
        f'padding:4px 12px;border-radius:50px;font-size:.9rem;margin-right:5px;font-weight:600;">'
        f'{label}</span>'
    )

def progress_bar(pct, label=""):
    pct = max(0, min(100, pct))
    return (
        f'<div style="margin:1rem 0 .5rem">'
        f'<div style="font-size:1rem;color:#8B8FA8;margin-bottom:.5rem;font-weight:600;">{label}</div>'
        f'<div style="background:rgba(255,255,255,.07);border-radius:99px;height:12px;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;border-radius:99px;'
        f'background:linear-gradient(90deg,#FF4B6E,#FF8E53);transition:width .6s ease;"></div>'
        f'</div></div>'
    )

# ── 3. SIDEBAR ──────────────────────────────────────────────────────────────
owner = st.session_state.owner
with st.sidebar:
    # Brand
    st.markdown(
        '<div style="font-size:2.4rem;font-weight:800;color:#FF4B6E;margin-bottom:.1rem;'
        'text-shadow:0 0 18px rgba(255,75,110,.55);">PawPal+</div>'
        '<div style="font-size:.95rem;color:#8B8FA8;margin-bottom:1rem;">Smart Pet Care Scheduling</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Avatar + owner info
    all_tasks = owner.get_all_tasks()
    done_n    = sum(1 for t in all_tasks if t.is_completed)
    pct_done  = int(done_n / max(1, len(all_tasks)) * 100)

    st.markdown(
        '<div style="font-size:3rem;text-align:center;">🐶</div>'
        f'<div style="text-align:center;font-weight:700;color:#FAFAFA;font-size:1.1rem;">Welcome, {owner.name}! (Owner)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        progress_bar(pct_done, "Weekly Activity  (" + str(pct_done) + "% Complete)"),
        unsafe_allow_html=True,
    )

    st.divider()
    with st.expander("⚙️ Edit Profile"):
        with st.form("profile_form"):
            n = st.text_input("Owner Name",       value=owner.name)
            t = st.number_input("Free Minutes",   15, 600, owner.available_time, step=15)
            p = st.text_input("Pet Name",         value=owner.pets[0].name)
            s = st.text_input("Breed / Species",  value=owner.pets[0].species_breed or "")
            if st.form_submit_button("Save Profile", type="primary"):
                pet = Pet(name=p.strip(), species_breed=s.strip() or None)
                own = Owner(name=n.strip(), available_time=int(t))
                own.add_pet(pet)
                st.session_state.owner    = own
                st.session_state.plan     = []
                st.session_state.warnings = []
                st.session_state.reasoning = ""
                st.rerun()

# ── 4. HERO ─────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:5.5rem;font-weight:800;color:#FF4B6E;text-align:center;'
    'letter-spacing:-3px;line-height:1;margin-bottom:.3rem;'
    'text-shadow:0 0 40px rgba(255,75,110,.6),0 0 80px rgba(255,75,110,.3);">PawPal+</h1>'
    '<p style="text-align:center;color:#8B8FA8;font-size:1.15rem;margin-bottom:1.5rem;letter-spacing:.5px;">'
    'Seamless Pet Care Scheduling &amp; Management</p>',
    unsafe_allow_html=True,
)

owner = st.session_state.owner

# ── 5. TABS ─────────────────────────────────────────────────────────────────
tab_add, tab_manage, tab_sched = st.tabs(["Add Task", "Manage Tasks", "Smart Schedule"])

# ══ TAB 1 · ADD TASK ════════════════════════════════════════════════════════
with tab_add:
    st.markdown(
        '<div style="margin-bottom:1.5rem;">'
        '<div style="display:inline-flex;align-items:center;gap:.7rem;margin-bottom:.5rem;">'
        '  <span style="font-size:2rem;">🐾</span>'
        '  <span style="font-size:1.5rem;font-weight:800;color:#FAFAFA;">Create a Care Mission</span>'
        '</div>'
        '<div style="height:3px;width:60px;background:linear-gradient(90deg,#FF4B6E,#FF8E53);'
        'border-radius:99px;"></div>'
        '<div style="color:#8B8FA8;font-size:.95rem;margin-top:.5rem;">'
        'Fill in the details below and add it to your pet\'s roster</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1.2, 1.2])
        t_name = c1.text_input("Task name *",   placeholder="e.g. Walk Luna")
        t_dur  = c2.number_input("Duration (min)", 5, 360, 30, step=5)
        t_pri  = c3.selectbox("Priority",       ["High", "Medium", "Low"])

        c4, c5, c6 = st.columns(3)
        t_pet = c4.selectbox("Pet",    [p.name for p in owner.pets])
        t_rep = c5.selectbox("Repeat", ["Never", "daily", "weekly"])
        t_due = c6.date_input("Due",   value=date.today())

        if st.button("🚀 Add to Roster", use_container_width=True, type="primary"):
            if not t_name.strip():
                st.error("Please enter a task name!")
            else:
                task = CareTask(
                    name=t_name.strip(), pet_name=t_pet,
                    duration=int(t_dur), priority=PMAP[t_pri],
                    recurrence=None if t_rep == "Never" else t_rep,
                    due_date=t_due,
                )
                for p in owner.pets:
                    if p.name == t_pet:
                        p.add_task(task); break
                st.success(f"✅ **{task.name}** added!")
                st.rerun()

    # ── Quick tips row to fill space ────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#8B8FA8;font-size:.9rem;font-weight:600;letter-spacing:.5px;'
        'text-transform:uppercase;margin-bottom:.8rem;">💡 Quick Tips</p>',
        unsafe_allow_html=True,
    )
    tip1, tip2, tip3 = st.columns(3)
    CARD = (
        'background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
        'border-radius:16px;padding:1.2rem 1.4rem;height:100%;'
    )
    tip1.markdown(
        f'<div style="{CARD}">'
        '<div style="font-size:1.8rem;margin-bottom:.5rem;">🔴</div>'
        '<div style="font-weight:700;color:#FAFAFA;font-size:1rem;margin-bottom:.4rem;">Priority Matters</div>'
        '<div style="color:#8B8FA8;font-size:.9rem;line-height:1.5;">High-priority tasks are always scheduled first, so your most urgent chores never get skipped.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    tip2.markdown(
        f'<div style="{CARD}">'
        '<div style="font-size:1.8rem;margin-bottom:.5rem;">🔄</div>'
        '<div style="font-weight:700;color:#FAFAFA;font-size:1rem;margin-bottom:.4rem;">Use Recurrence</div>'
        '<div style="color:#8B8FA8;font-size:.9rem;line-height:1.5;">Mark a task as daily or weekly and PawPal+ will automatically roll it over when you mark it complete.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    tip3.markdown(
        f'<div style="{CARD}">'
        '<div style="font-size:1.8rem;margin-bottom:.5rem;">⚡</div>'
        '<div style="font-weight:700;color:#FAFAFA;font-size:1rem;margin-bottom:.4rem;">Check Conflicts</div>'
        '<div style="color:#8B8FA8;font-size:.9rem;line-height:1.5;">Head to Smart Schedule to detect overlapping tasks and get an AI-optimised daily plan instantly.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ══ TAB 2 · MANAGE ══════════════════════════════════════════════════════════
with tab_manage:
    all_tasks = owner.get_all_tasks()
    scheduler = Scheduler(owner)

    # Filter bar
    fa, fb, fc = st.columns(3)
    f_pet    = fa.selectbox("Pet",    ["All"] + [p.name for p in owner.pets], key="fp2")
    f_status = fb.selectbox("Status", ["All", "Pending", "Completed"],        key="fs2")
    f_sort   = fc.selectbox("Sort",   ["Priority ↓","Duration ↑"],            key="fr2")

    filtered = scheduler.filter_tasks(
        pet_name  = None if f_pet    == "All" else f_pet,
        completed = None if f_status == "All" else (f_status == "Completed"),
    )
    tasks_to_show = (
        sorted(filtered, key=lambda x: (x.priority, x.duration))
        if f_sort == "Priority ↓"
        else scheduler.sort_by_time(filtered)
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-column layout: cards | timeline
    left_col, right_col = st.columns([3, 1.5])

    with left_col:
        if not tasks_to_show:
            st.info("No tasks match your filters.")
        else:
            for i, task in enumerate(tasks_to_show):
                pc    = PCOLOR.get(task.priority, "#10B981")
                plbl  = PLABEL.get(task.priority, "NORMAL")
                done  = task.is_completed

                title_style = (
                    "font-size:1.3rem;font-weight:700;color:#9ca3af;text-decoration:line-through;"
                    if done else
                    "font-size:1.3rem;font-weight:700;color:#FAFAFA;"
                )
                card_opacity = "opacity:.55;" if done else ""
                recur_pill   = pill(f"↺ {task.recurrence}", "#A5B4FC", "rgba(100,100,200,.2)") if task.recurrence else ""

                st.markdown(
                    f'<div style="{card_style()}{card_opacity}">'
                    f'  <div style="width:44px;height:44px;background:rgba(255,75,110,.15);'
                    f'      border-radius:10px;display:flex;align-items:center;justify-content:center;'
                    f'      font-size:1.5rem;flex-shrink:0;">🐾</div>'
                    f'  <div style="flex:1;">'
                    f'    <div style="{title_style}">{task.name}</div>'
                    f'    <div style="margin-top:.4rem;">'
                    f'      {pill(plbl, "#fff", pc)}'
                    f'      {chip(str(task.duration) + " min")}'
                    f'      {recur_pill}'
                    f'    </div>'
                    f'  </div>'
                    f'  <div style="color:#8B8FA8;font-size:.8rem;">{task.pet_name}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns(2)
                if b1.button("✓ Done" if not done else "↩ Undo", key=f"d{i}", use_container_width=True):
                    task.mark_complete(); st.rerun()
                if b2.button("🗑 Delete", key=f"x{i}", use_container_width=True):
                    for p in owner.pets:
                        if task in p.tasks: p.tasks.remove(task); break
                    st.rerun()

    # ── Right: visual timeline ───────────────────────────────────────────────
    with right_col:
        tl_tasks = tasks_to_show[:6]
        cursor_m = 8 * 60

        rows_html = ""
        for idx, t in enumerate(tl_tasks):
            h, m    = divmod(cursor_m, 60)
            ts      = f"{h:02d}:{m:02d}"
            is_last = idx == len(tl_tasks) - 1

            line = (
                "" if is_last else
                '<div style="position:absolute;left:6px;top:17px;width:2px;'
                'height:calc(100% + 14px);background:rgba(255,75,110,.25);"></div>'
            )
            rows_html += (
                f'<div style="display:flex;gap:.75rem;align-items:flex-start;margin-bottom:1rem;position:relative;">'
                f'  <div style="position:relative;flex-shrink:0;">'
                f'    <div style="width:14px;height:14px;background:#FF4B6E;border-radius:50%;'
                f'         box-shadow:0 0 8px rgba(255,75,110,.6);margin-top:3px;"></div>'
                f'    {line}'
                f'  </div>'
                f'  <div>'
                f'    <div style="font-size:.78rem;color:#FF4B6E;font-weight:600;">{ts}</div>'
                f'    <div style="font-size:.85rem;color:#FAFAFA;font-weight:600;">{t.name}</div>'
                f'  </div>'
                f'</div>'
            )
            cursor_m += t.duration

        today_str = date.today().strftime("%b %d, %Y")
        st.markdown(
            f'<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.09);'
            f'border-radius:14px;padding:1.2rem;height:100%;">'
            f'  <div style="font-size:.9rem;font-weight:700;color:#FAFAFA;margin-bottom:.3rem;">📅 Today\'s Visual Timeline</div>'
            f'  <div style="font-size:.75rem;color:#8B8FA8;margin-bottom:1rem;">Date: {today_str}</div>'
            f'  {rows_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Progress bar ─────────────────────────────────────────────────────────
    total_done_mins = sum(t.duration for t in all_tasks if t.is_completed)
    total_all_mins  = sum(t.duration for t in all_tasks)
    pct_sched       = int(total_done_mins / max(1, total_all_mins) * 100)
    st.markdown(
        progress_bar(pct_sched,
            f"Schedule Today: {pct_sched}% "
            f"({total_done_mins/60:.1f} hrs used)"
        ),
        unsafe_allow_html=True,
    )

    # Recurring rollover
    done_recur = [t for t in all_tasks if t.is_completed and t.recurrence]
    if done_recur:
        st.divider()
        st.caption(f"🔄 {len(done_recur)} recurring task(s) ready to roll over.")
        if st.button("Generate Next Occurrences", use_container_width=True):
            new = scheduler.refresh_recurring_tasks()
            for nt in new:
                st.success(f"✅ **{nt.name}** → due {nt.due_date}")
            if new: st.rerun()
            else:   st.info("Nothing new to generate.")

# ══ TAB 3 · SCHEDULE ════════════════════════════════════════════════════════
with tab_sched:
    all_tasks = owner.get_all_tasks()
    pending   = [t for t in all_tasks if not t.is_completed]

    if not all_tasks:
        st.info("Add tasks first.")
    elif not pending:
        st.success("🎉 All caught up!")
        st.balloons()
    else:
        st.markdown("### 🧠 Intelligent Daily Planner")
        left_s, right_s = st.columns([3, 1.5])

        with right_s:
            done_n2 = sum(1 for t in all_tasks if t.is_completed)
            for num, lbl, ac in [
                (len(all_tasks), "TOTAL TASKS", False),
                (done_n2,        "COMPLETED",   True),
                (f"{owner.available_time}m", "FREE TODAY", False),
            ]:
                nc = "#FF4B6E" if ac else "#FAFAFA"
                st.markdown(
                    f'<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.09);'
                    f'border-radius:12px;padding:.9rem 1rem;margin-bottom:.6rem;">'
                    f'  <div style="font-size:2rem;font-weight:800;color:{nc};line-height:1;">{num}</div>'
                    f'  <div style="font-size:.72rem;color:#8B8FA8;text-transform:uppercase;'
                    f'       letter-spacing:1px;margin-top:4px;">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        with left_s:
            if st.button("⚡ Generate Optimal Schedule", use_container_width=True, type="primary"):
                sched = Scheduler(owner)
                st.session_state.plan      = sched.generate_plan()
                st.session_state.warnings  = sched.detect_conflicts()
                st.session_state.reasoning = sched.explain_plan()
                st.rerun()

            plan      = st.session_state.plan
            warnings  = st.session_state.warnings
            reasoning = st.session_state.reasoning

            if warnings:
                for w in warnings: st.warning(w)
            elif plan:
                st.success("✅ Clean schedule — no conflicts!")

            if plan:
                total = sum(t.duration for t in plan)
                cursor = 0
                for idx, task in enumerate(plan):
                    h1, m1 = divmod(cursor, 60)
                    h2, m2 = divmod(cursor + task.duration, 60)
                    s = f"{h1:02d}:{m1:02d}"
                    e = f"{h2:02d}:{m2:02d}"
                    pc   = PCOLOR.get(task.priority, "#10B981")
                    plbl = PLABEL.get(task.priority, "NORMAL")
                    recur_p = pill(f"↺ {task.recurrence}", "#A5B4FC", "rgba(100,100,200,.2)") if task.recurrence else ""

                    st.markdown(
                        f'<div style="{card_style()}">'
                        f'  <div style="width:44px;height:44px;background:rgba(255,75,110,.15);'
                        f'      border-radius:10px;display:flex;align-items:center;justify-content:center;'
                        f'      font-size:1.5rem;flex-shrink:0;">🗓️</div>'
                        f'  <div style="flex:1;">'
                        f'    <div style="font-size:1.3rem;font-weight:700;color:#FAFAFA;">{idx+1}. {task.name}</div>'
                        f'    <div style="margin-top:.4rem;">'
                        f'      {pill(plbl, "#fff", pc)}'
                        f'      {chip(s + " → " + e)}'
                        f'      {chip(str(task.duration) + " min")}'
                        f'      {recur_p}'
                        f'    </div>'
                        f'  </div>'
                        f'  <div style="color:#8B8FA8;font-size:.8rem;">{task.pet_name}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    cursor += task.duration

                skipped = len(pending) - len(plan)
                skip_note = f"  ·  {skipped} task(s) skipped" if skipped else ""
                pct_p = min(int(total / owner.available_time * 100), 100)
                st.markdown(
                    progress_bar(pct_p, f"Time Used: {total}/{owner.available_time} min{skip_note}"),
                    unsafe_allow_html=True,
                )

                with st.expander("🧠 Scheduling Reasoning"):
                    for line in reasoning.split("\n"):
                        if not line.strip(): continue
                        if line.startswith("Added"):    st.success(line)
                        elif line.startswith("Skipped"): st.warning(line)
                        else:                            st.info(line)

            elif reasoning:
                st.warning("No tasks fit your time budget.")
