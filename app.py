"""
app.py — PawPal+ Premium Interactive Edition
---------------------------------------------
Highly interactive, element-rich design for PawPal+.
Includes: inline editable tables, toast notifications, 
glassmorphic CSS, visual timelines, and popovers.
"""

import streamlit as st
from datetime import date
import pandas as pd
import time
from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── 1. Page Config & State ───────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+ Pro", page_icon="🐾", layout="wide", initial_sidebar_state="expanded")

for k, v in [("owner", None), ("plan", []), ("warnings", []), ("reasoning", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

PMAP   = {"High": 1, "Medium": 2, "Low": 3}
PLABEL = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}

# ── 2. Premium CSS Injection ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.block-container { padding-top: 1.5rem; max-width: 1050px; }

/* Animated Gradient Hero Text */
.hero-title {
    font-size: 4rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(−45deg, #FF4B6E, #FF8E53, #FF4B6E);
    background-size: 200% auto;
    color: #fff;
    background-clip: text;
    text-fill-color: transparent;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
@keyframes shine { to { background-position: 200% center; } }
.hero-sub { text-align: center; color: #8B8FA8; font-size: 1.1rem; margin-bottom: 2rem; font-weight:400; }

/* Glassmorphic Metric Cards */
.glass-metric {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-bottom: 1rem;
}
.glass-metric:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px 0 rgba(255, 75, 110, 0.15);
    border: 1px solid rgba(255, 75, 110, 0.3);
}
.gm-num { font-size: 2.2rem; font-weight: 800; color: #FAFAFA; line-height: 1; }
.gm-num.accent { color: #FF4B6E; }
.gm-lbl { font-size: 0.75rem; font-weight: 600; color: #8B8FA8; text-transform: uppercase; letter-spacing: 1px; margin-top: 6px; }

/* Timeline UI */
.timeline-item {
    display: flex; gap: 1rem; margin-bottom: 1rem;
    align-items: stretch;
}
.t-time {
    width: 60px; font-weight: 600; color: #FF4B6E; font-size: 0.9rem;
    text-align: right; margin-top: 4px; border-right: 2px solid rgba(255, 75, 110, 0.3); padding-right: 12px;
}
.t-content {
    flex: 1; background: rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 1rem;
    border: 1px solid rgba(255,255,255,0.08); transition: all 0.2s;
}
.t-content:hover { background: rgba(255, 75, 110, 0.08); border-color: rgba(255, 75, 110, 0.4); }
.t-title { font-weight: 800; font-size: 1.1rem; color: #FAFAFA; display:flex; justify-content:space-between; }
.t-sub { font-size: 0.85rem; color: #8B8FA8; margin-top: 4px; }

/* Floating action bar */
.fab-container {
    background: rgba(26, 28, 36, 0.8); border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px); border-radius: 12px; padding: 1rem; margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── 3. Sidebar Profile ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:2rem;text-align:left;">🐾 PawPal+</div>', unsafe_allow_html=True)
    st.caption("v2.0 Pro — Interactive Edition")
    st.divider()

    st.markdown("**👤 Who's organizing?**")
    with st.popover("⚙️ Edit Profile"):
        with st.form("profile_form"):
            owner_name = st.text_input("Owner Name", "Jordan")
            avail_time = st.number_input("Minutes Free Today", 15, 600, 120, step=15)
            pet_name   = st.text_input("Pet Name", "Fido")
            species    = st.text_input("Breed", "Golden Retriever")
            if st.form_submit_button("Save Details", type="primary"):
                p = Pet(name=pet_name, species_breed=species or None)
                o = Owner(name=owner_name, available_time=int(avail_time))
                o.add_pet(p)
                st.session_state.owner = o
                st.toast(f"Profile saved! Welcome {owner_name}.", icon="✅")
                time.sleep(0.5)
                st.rerun()

    if st.session_state.owner:
        o = st.session_state.owner
        tasks = o.get_all_tasks()
        done = sum(1 for t in tasks if t.is_completed)
        
        st.markdown(f"**Hi {o.name}!** You have **{o.available_time} min** free today.")
        st.progress(done / max(1, len(tasks)), text=f"Overall Completion: {done}/{len(tasks)}")
        
        st.markdown('<div style="margin-top:1.5rem"><b>📊 Quick Stats</b></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="glass-metric"><div class="gm-num">{len(tasks)}</div><div class="gm-lbl">Tasks</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-metric"><div class="gm-num accent">{o.available_time}</div><div class="gm-lbl">Mins</div></div>', unsafe_allow_html=True)

# ── Guard ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">PawPal+</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">The smartest way to plan your pet\'s day.</div>', unsafe_allow_html=True)

if not st.session_state.owner:
    st.info("👈 Open the sidebar and click **Edit Profile** to begin.")
    st.stop()
owner = st.session_state.owner

# ── 4. Main Interactive Tabs ─────────────────────────────────────────────────
tab_add, tab_manage, tab_plan = st.tabs(["✨ Add Task", "🛠️ Manage Tasks", "🗓️ Smart Schedule"])

# ── TAB 1: ADD TASK ──────────────────────────────────────────────────────────
with tab_add:
    st.markdown("### Create a Care Mission")
    with st.container(border=True):
        c1, c2, c3 = st.columns([2,1,1])
        t_name = c1.text_input("Mission Title *", placeholder="e.g., Afternoon Walk")
        t_dur  = c2.number_input("Duration (min)", 5, 240, 30, step=5)
        t_pri  = c3.selectbox("Importance", ["High", "Medium", "Low"])
        
        c4, c5, c6 = st.columns(3)
        t_pet = c4.selectbox("Pet", [p.name for p in owner.pets])
        t_rep = c5.selectbox("Repeat?", ["Never", "daily", "weekly"])
        t_due = c6.date_input("Due Date", value=date.today())
        
        if st.button("🚀 Add to Roster", use_container_width=True, type="primary"):
            if not t_name.strip():
                st.error("Title required!")
            else:
                task = CareTask(
                    name=t_name.strip(), pet_name=t_pet, duration=int(t_dur),
                    priority=PMAP[t_pri], recurrence=None if t_rep=="Never" else t_rep, due_date=t_due
                )
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
