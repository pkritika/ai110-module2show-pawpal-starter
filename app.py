"""
app.py – PawPal+ Premium Edition
Built to match the design mockup:
 - Glassmorphic task cards with paw icon + priority pill + duration chip
 - Visual timeline panel beside the task list
 - Sidebar nav with avatar, progress bar, and navigation links
 - Big coral hero title + progress bar at bottom of schedule
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── 1. Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+ Pro",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.block-container  { padding-top: 1.2rem; max-width: 1200px; }
#MainMenu, footer { visibility: hidden; }

/* ── Hero title ─────────────────────────────────────────────────── */
.hero {
    font-size: 4rem; font-weight: 800; text-align: center;
    color: #FF4B6E; letter-spacing: -2px; line-height: 1;
    margin-bottom: .2rem;
}
.hero-sub {
    text-align: center; color: #8B8FA8; font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* ── Task cards ─────────────────────────────────────────────────── */
.task-card {
    display: flex; align-items: center; gap: 1rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px; padding: 1rem 1.2rem;
    margin-bottom: .75rem;
    transition: border-color .25s, background .25s, transform .25s;
    cursor: pointer;
}
.task-card:hover {
    background: rgba(255,75,110,0.07);
    border-color: rgba(255,75,110,0.45);
    transform: translateX(4px);
}
.task-card.done { opacity: 0.5; }
.paw-icon {
    width: 44px; height: 44px; background: rgba(255,75,110,0.15);
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
}
.task-body { flex: 1; }
.task-title { font-size: 1.05rem; font-weight: 700; color: #FAFAFA; }
.task-title.done-text { text-decoration: line-through; color: #666; }
.task-chips { display: flex; gap: .5rem; margin-top: .4rem; flex-wrap: wrap; }
.chip-high   { background:#FF4B6E; color:#fff; padding:2px 10px; border-radius:50px; font-size:.72rem; font-weight:700; }
.chip-medium { background:#F59E0B; color:#fff; padding:2px 10px; border-radius:50px; font-size:.72rem; font-weight:700; }
.chip-low    { background:#10B981; color:#fff; padding:2px 10px; border-radius:50px; font-size:.72rem; font-weight:700; }
.chip-dur    { background:rgba(255,255,255,0.08); color:#BDBDBD; padding:2px 10px; border-radius:50px; font-size:.72rem; }
.chip-recur  { background:rgba(100,100,200,0.2); color:#A5B4FC; padding:2px 10px; border-radius:50px; font-size:.72rem; }

/* ── Progress bar ────────────────────────────────────────────────── */
.prog-wrap  { margin: 1.2rem 0 .5rem; }
.prog-label { font-size:.85rem; color:#8B8FA8; margin-bottom:.4rem; }
.prog-bar   { background:rgba(255,255,255,.07); border-radius:99px; height:10px; overflow:hidden; }
.prog-fill  { height:100%; border-radius:99px; background:linear-gradient(90deg,#FF4B6E,#FF8E53); transition:width .6s ease; }

/* ── Visual timeline ─────────────────────────────────────────────── */
.tl-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px; padding: 1.2rem; height: 100%;
}
.tl-header { font-size:.9rem; font-weight:700; color:#FAFAFA; margin-bottom:1rem; }
.tl-date   { font-size:.75rem; color:#8B8FA8; margin-bottom:1rem; }
.tl-row    { display:flex; gap:.75rem; align-items:flex-start; margin-bottom:1rem; position:relative; }
.tl-dot    { width:14px; height:14px; background:#FF4B6E; border-radius:50%;
             margin-top:3px; flex-shrink:0; box-shadow: 0 0 8px rgba(255,75,110,.6); }
.tl-line   { position:absolute; left:6px; top:17px; width:2px;
             height:calc(100% + 6px); background:rgba(255,75,110,.25); }
.tl-time   { font-size:.78rem; color:#FF4B6E; font-weight:600; white-space:nowrap; }
.tl-name   { font-size:.85rem; color:#FAFAFA; font-weight:600; }

/* ── Stat cards ────────────────────────────────────────────────────── */
.stat-card {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.09);
    border-radius:12px; padding: .9rem 1rem; margin-bottom:.6rem;
    transition: border-color .2s;
}
.stat-card:hover { border-color: rgba(255,75,110,.4); }
.stat-num  { font-size:2rem; font-weight:800; color:#FAFAFA; line-height:1; }
.stat-num.accent { color:#FF4B6E; }
.stat-lbl  { font-size:.72rem; color:#8B8FA8; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }

/* ── Active tab underline fix ──────────────────────────────────────── */
.stTabs [aria-selected="true"] {
    color: #FF4B6E !important;
    border-bottom-color: #FF4B6E !important;
    font-weight: 700;
}

/* ── Primary buttons ──────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: #FF4B6E !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #e0344e !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,75,110,.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── 3. Session State ───────────────────────────────────────────────────────────
for k, v in [("owner", None), ("plan", []), ("warnings", []), ("reasoning", ""), ("active_nav", "My Tasks")]:
    if k not in st.session_state:
        st.session_state[k] = v

PMAP   = {"High": 1, "Medium": 2, "Low": 3}
PLABEL = {1: "HIGH", 2: "MED", 3: "NORMAL"}
PCLASS = {1: "chip-high", 2: "chip-medium", 3: "chip-low"}

# ── 4. SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.8rem;font-weight:800;color:#FF4B6E;margin-bottom:.2rem;">PawPal+</div>',
        unsafe_allow_html=True,
    )
    st.caption("Smart Pet Care Scheduling")
    st.divider()

    # Profile popover
    owner = st.session_state.owner
    if owner:
        st.markdown(
            f'<div style="font-size:2rem;text-align:center;margin-bottom:.3rem;">🐶</div>'
            f'<div style="text-align:center;font-weight:700;color:#FAFAFA;">Welcome, {owner.name}!</div>'
            f'<div style="text-align:center;font-size:.8rem;color:#8B8FA8;">Owner</div>',
            unsafe_allow_html=True,
        )
        tasks = owner.get_all_tasks()
        done  = sum(1 for t in tasks if t.is_completed)
        pct   = int(done / max(1, len(tasks)) * 100)
        st.markdown(
            f'<div style="margin-top:1rem"><div class="prog-label">Weekly Activity ({pct}% Complete)</div>'
            f'<div class="prog-bar"><div class="prog-fill" style="width:{pct}%"></div></div></div>',
            unsafe_allow_html=True,
        )
        st.divider()

    # Nav links (visual only, tabs control actual view)
    for label, icon in [("Dashboard","📊"), ("Pet Profiles","🐾"), ("My Tasks","✅"), ("Notifications","🔔"), ("Settings","⚙️")]:
        is_active = st.session_state.active_nav == label
        bg = "rgba(255,75,110,0.2)" if is_active else "transparent"
        cl = "#FF4B6E" if is_active else "#BDBDBD"
        fw = "700" if is_active else "400"
        active_badge = '<span style="font-size:.7rem;color:#FF4B6E">Active</span>' if is_active else ""
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.7rem;padding:.55rem .8rem;'
            f'border-radius:10px;background:{bg};margin-bottom:.25rem;cursor:pointer;">'
            f'<span>{icon}</span>'
            f'<span style="color:{cl};font-weight:{fw};font-size:.9rem;">{label}</span>'
            f'{active_badge}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    # Profile editor
    with st.expander("⚙️ Edit Profile"):
        with st.form("profile_form"):
            n = st.text_input("Owner Name", value=owner.name if owner else "Sarah")
            t = st.number_input("Free Minutes Today", 15, 600, owner.available_time if owner else 120, step=15)
            p = st.text_input("Pet Name",       value=owner.pets[0].name if owner else "Luna")
            s = st.text_input("Breed / Species", value=owner.pets[0].species_breed if owner else "Labrador")
            if st.form_submit_button("Save Profile", type="primary"):
                pet = Pet(name=p.strip(), species_breed=s.strip() or None)
                own = Owner(name=n.strip(), available_time=int(t))
                own.add_pet(pet)
                st.session_state.owner    = own
                st.session_state.plan     = []
                st.session_state.warnings = []
                st.session_state.reasoning = ""
                st.rerun()

# ── Guard ──────────────────────────────────────────────────────────────────────
# Hero is always shown
st.markdown('<div class="hero">PawPal+</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Seamless Pet Care Scheduling &amp; Management</div>', unsafe_allow_html=True)

if not st.session_state.owner:
    st.info("👈 Open the sidebar, expand **Edit Profile**, and save to begin.")
    st.stop()

owner = st.session_state.owner

# ── 5. TABS ──────────────────────────────────────────────────────────────────
tab_add, tab_manage, tab_sched = st.tabs(["Add Task", "Manage Tasks", "Smart Schedule"])


# ─── TAB 1 · ADD TASK ────────────────────────────────────────────────────────
with tab_add:
    st.session_state.active_nav = "Dashboard"
    st.markdown("### Create a New Mission")

    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1.2, 1.2])
        t_name = c1.text_input("Task name *", placeholder="e.g. Walk Luna")
        t_dur  = c2.number_input("Duration (min)", 5, 360, 30, step=5)
        t_pri  = c3.selectbox("Priority", ["High", "Medium", "Low"])

        c4, c5, c6 = st.columns(3)
        t_pet = c4.selectbox("Pet", [p.name for p in owner.pets])
        t_rep = c5.selectbox("Repeats", ["Never", "daily", "weekly"])
        t_due = c6.date_input("Due Date", value=date.today())

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
                st.success(f"✅ **{task.name}** added to {t_pet}'s roster!")
                st.rerun()


# ─── TAB 2 · MANAGE TASKS ───────────────────────────────────────────────────
with tab_manage:
    st.session_state.active_nav = "My Tasks"
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.info("No tasks yet — head to **Add Task** to create some!")
    else:
        scheduler = Scheduler(owner)

        # ─ Filter bar
        fa, fb, fc = st.columns(3)
        f_pet    = fa.selectbox("Pet",    ["All"] + [p.name for p in owner.pets], key="fp")
        f_status = fb.selectbox("Status", ["All", "Pending", "Completed"],         key="fs")
        f_sort   = fc.selectbox("Sort",   ["Priority ↓", "Duration ↑"],            key="frt")

        filtered = scheduler.filter_tasks(
            pet_name  = None if f_pet    == "All" else f_pet,
            completed = None if f_status == "All" else (f_status == "Completed"),
        )
        tasks_to_show = (
            sorted(filtered, key=lambda x: (x.priority, x.duration))
            if f_sort == "Priority ↓"
            else scheduler.sort_by_time(filtered)
        )

        st.markdown(f"<br>", unsafe_allow_html=True)

        # ─ Two-panel layout: cards + timeline
        left_col, right_col = st.columns([3, 1.4])

        with left_col:
            if not tasks_to_show:
                st.info("No tasks match your filters.")
            else:
                for i, task in enumerate(tasks_to_show):
                    pclass = PCLASS.get(task.priority, "chip-low")
                    plabel = PLABEL.get(task.priority, "LOW")
                    done   = task.is_completed
                    title_class = "task-title done-text" if done else "task-title"
                    card_class  = "task-card done" if done else "task-card"
                    recur_chip  = (f'<span class="chip-recur">↺ {task.recurrence}</span>'
                                   if task.recurrence else "")

                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="paw-icon">🐾</div>
                        <div class="task-body">
                            <div class="{title_class}">{task.name}</div>
                            <div class="task-chips">
                                <span class="{pclass}">{plabel}</span>
                                <span class="chip-dur">{task.duration} min</span>
                                {recur_chip}
                            </div>
                        </div>
                        <div style="color:#8B8FA8;font-size:.8rem;">{task.pet_name}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Action buttons under each card
                    b1, b2 = st.columns([1, 1])
                    lbl = "↩ Undo" if done else "✓ Done"
                    if b1.button(lbl, key=f"done_{i}", use_container_width=True):
                        task.mark_complete()
                        st.rerun()
                    if b2.button("🗑 Delete", key=f"del_{i}", use_container_width=True):
                        for p in owner.pets:
                            if task in p.tasks:
                                p.tasks.remove(task); break
                        st.rerun()

        with right_col:
            # Build timeline from first 5 visible tasks
            total_done = sum(t.duration for t in all_tasks if t.is_completed)
            total_all  = sum(t.duration for t in all_tasks)
            pct = int(total_done / max(1, total_all) * 100)

            timeline_html = '<div class="tl-card">'
            timeline_html += '<div class="tl-header">📅 Today\'s Visual Timeline</div>'
            timeline_html += f'<div class="tl-date">Date: {date.today().strftime("%b %d, %Y")}</div>'

            cursor_min = 8 * 60  # start @ 08:00
            tl_tasks = tasks_to_show[:6]
            for idx, t in enumerate(tl_tasks):
                h, m = divmod(cursor_min, 60)
                time_str = f"{h:02d}:{m:02d}"
                is_last  = idx == len(tl_tasks) - 1
                line_html = "" if is_last else '<div class="tl-line"></div>'
                timeline_html += f"""
                <div class="tl-row">
                    <div style="position:relative;">
                        <div class="tl-dot"></div>
                        {line_html}
                    </div>
                    <div>
                        <div class="tl-time">{time_str}</div>
                        <div class="tl-name">{t.name}</div>
                    </div>
                </div>
                """
                cursor_min += t.duration
            timeline_html += '</div>'
            st.markdown(timeline_html, unsafe_allow_html=True)

        # ─ Progress bar bottom of task list
        st.markdown(
            f'<div class="prog-wrap">'
            f'<div class="prog-label">Schedule Today: {pct}% ({total_done/60:.1f} hrs used)</div>'
            f'<div class="prog-bar"><div class="prog-fill" style="width:{pct}%"></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ─ Recurring rollover
        done_recur = [t for t in all_tasks if t.is_completed and t.recurrence]
        if done_recur:
            st.divider()
            st.caption(f"🔄 {len(done_recur)} completed recurring task(s) ready to roll over.")
            if st.button("Generate Next Occurrences", use_container_width=True):
                new = scheduler.refresh_recurring_tasks()
                for nt in new:
                    st.success(f"✅ **{nt.name}** → due {nt.due_date}")
                if new:
                    st.rerun()
                else:
                    st.info("Nothing new.")


# ─── TAB 3 · SMART SCHEDULE ─────────────────────────────────────────────────
with tab_sched:
    st.session_state.active_nav = "Dashboard"
    all_tasks = owner.get_all_tasks()
    pending   = [t for t in all_tasks if not t.is_completed]

    if not all_tasks:
        st.info("Add tasks first in the **Add Task** tab.")
    elif not pending:
        st.success("🎉 All caught up! Mark tasks as done or add new ones.")
        st.balloons()
    else:
        st.markdown("### 🧠 Intelligent Daily Planner")
        st.caption("Picks the highest-priority tasks that fit your available time.")

        left, right = st.columns([3, 1.4])

        with right:
            # Quick stats
            tasks  = owner.get_all_tasks()
            done_n = sum(1 for t in tasks if t.is_completed)

            def _stat(num, label, accent=False):
                cls = "stat-num accent" if accent else "stat-num"
                return f'<div class="stat-card"><div class="{cls}">{num}</div><div class="stat-lbl">{label}</div></div>'

            st.markdown(_stat(len(tasks),              "Total Tasks"),       unsafe_allow_html=True)
            st.markdown(_stat(done_n,                  "Completed", True),   unsafe_allow_html=True)
            st.markdown(_stat(f"{owner.available_time}m", "Free Today"),     unsafe_allow_html=True)

        with left:
            if st.button("⚡ Generate Optimal Schedule", use_container_width=True, type="primary"):
                sched = Scheduler(owner)
                st.session_state.plan      = sched.generate_plan()
                st.session_state.warnings  = sched.detect_conflicts()
                st.session_state.reasoning = sched.explain_plan()
                st.rerun()

            plan     = st.session_state.plan
            warnings = st.session_state.warnings
            reasoning= st.session_state.reasoning

            if warnings:
                for w in warnings:
                    st.warning(w)
            elif plan:
                st.success("✅ Clean schedule — no time conflicts!")

            if plan:
                total = sum(t.duration for t in plan)
                pct_p = min(int(total / owner.available_time * 100), 100)

                # Timeline-style plan display
                cursor = 0
                for idx, task in enumerate(plan):
                    h1, m1 = divmod(cursor, 60)
                    h2, m2 = divmod(cursor + task.duration, 60)
                    s = f"{h1:02d}:{m1:02d}"
                    e = f"{h2:02d}:{m2:02d}"
                    pclass = PCLASS.get(task.priority, "chip-low")
                    plbl   = PLABEL.get(task.priority, "LOW")
                    recur  = f'<span class="chip-recur">↺ {task.recurrence}</span>' if task.recurrence else ""

                    st.markdown(f"""
                    <div class="task-card">
                        <div class="paw-icon">🗓️</div>
                        <div class="task-body">
                            <div class="task-title">{idx+1}. {task.name}</div>
                            <div class="task-chips">
                                <span class="{pclass}">{plbl}</span>
                                <span class="chip-dur">{s} → {e}</span>
                                <span class="chip-dur">{task.duration} min</span>
                                {recur}
                            </div>
                        </div>
                        <div style="color:#8B8FA8;font-size:.8rem;">{task.pet_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    cursor += task.duration

                # Progress bar
                skipped = len(pending) - len(plan)
                st.markdown(
                    f'<div class="prog-wrap">'
                    f'<div class="prog-label">Time Used: {total}/{owner.available_time} min'
                    f'{"  ·  " + str(skipped) + " task(s) skipped (not enough time)" if skipped else ""}</div>'
                    f'<div class="prog-bar"><div class="prog-fill" style="width:{pct_p}%"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("🧠 Scheduling Reasoning"):
                    for line in reasoning.split("\n"):
                        if not line.strip(): continue
                        if line.startswith("Added"):   st.success(line)
                        elif line.startswith("Skipped"): st.warning(line)
                        else:                            st.info(line)

            elif reasoning:
                st.warning("No tasks fit your time budget. Increase your free minutes or shorten some tasks.")
