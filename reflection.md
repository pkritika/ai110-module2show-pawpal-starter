# PawPal+ Project Reflection

## 1. System Design

**Core Actions**
Based on the application requirements, a user should be able to perform these three core actions:
1. **Profile Management**: Add and manage basic information about the owner and their pet(s).
2. **Task Scheduling**: Add, edit, or remove specific pet care tasks (e.g., schedule a walk, feeding, meds), specifying their duration and priority.
3. **Daily Plan Generation**: Generate an optimized daily schedule based on available time and priorities, and view today's tasks with explanations.

**a. Initial design**

My initial design included four core classes that map to the primary use cases of the app:
- **`Owner`**: Holds the user's details, such as their name, available time, and a list of `Pet` objects they own. Its responsibility is to represent the constraints (time) that the scheduler will use.
- **`Pet`**: Represents the animal receiving care. It holds basic info (name, species) and maintains a list of `CareTask` objects specific to that pet.
- **`CareTask`**: A data holder representing a specific activity (like walking or feeding). It tracks the task's name, expected duration, urgency/priority, and whether it has been completed.
- **`Scheduler`**: The core logic engine. It takes an `Owner` context, evaluates the owner's available time against the tasks of their pets, and generates a constrained, prioritized `daily_plan` (a list of tasks) along with a natural language `reasoning` trace.

**b. Design changes**

During a review of the initial class skeletons, a potential logical bottleneck was identified: once tasks from multiple pets are flattened into a single `daily_plan` list by the `Scheduler`, the UI would not know which task belonged to which pet (e.g., "Walk" could be for the dog or the cat).

To resolve this bottleneck, I modified the `CareTask` model by adding a `pet_name: str` attribute. This reverse reference ensures that when tasks are collected into the master schedule, the application retains the context of which pet the task belongs to, allowing the UI to display it clearly (e.g., "Walk - Fido").

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler primarily considers two constraints:
1. **Priority**: High (1), Medium (2), Low (3).
2. **Time**: The owner's `available_time` for the day versus the task's `duration`.

Priority matters most because skipping a critical medication (High) is far worse than skipping a grooming session (Low). Time is the hard limiting factor.

**b. Tradeoffs**

One major tradeoff my scheduler makes is using a **Greedy Algorithm** instead of a complex optimization algorithm (like the Knapsack DP algorithm). It sorts by priority and tries to pack them into the time budget one by one. 

The tradeoff is that it might not find the mathematically perfect combination of tasks to use exactly 100% of the available time. For example, it might schedule a 50-minute High priority task, leaving 10 minutes, and skip a 15-minute Medium task, when perhaps scheduling the 15-minute task plus a 40-minute task would have fit perfectly. 

This tradeoff is highly reasonable for this scenario because pet care isn't about perfectly packing minutes—it's about making sure the most urgent things happen. The greedy approach guarantees the highest priority tasks get picked first, and keeps the code incredibly readable and fast.

---

## 3. AI Collaboration

**a. How you used AI**

During this project, I used AI heavily for both frontend UI design and backend algorithm logic. For the UI, I used AI to generate complex inline CSS to build a premium, glassmorphic dark-themed interface in Streamlit, which isn't natively designed for such rich layouts. For the backend, I used AI to brainstorm the structure of my `Scheduler` class and to help write the `detect_conflicts` logic (checking for overlapping time windows). The most helpful prompts were highly specific visual references (e.g., asking to match a specific UI mockup with "pill-shaped inputs" and "coral glowing text") and clear constraints for the algorithms (e.g., "Sort tasks by priority first, then fit them into a specific time budget").

**b. Judgment and verification**

There were instances where the AI generated standard Streamlit UI components (like basic markdown headers and default checkboxes) when I explicitly wanted a highly customized "SaaS" look. Instead of accepting the basic code, I rejected those implementations and specifically prompted the AI to inject custom CSS classes or inline styles to override Streamlit's defaults. To verify the AI's suggestions, I continuously ran the app locally (`python3 -m streamlit run app.py`), visually inspected the rendered layout, and checked how it handled system features like dark/light mode toggling. When light mode made my text invisible, I realized the AI's transparent background approach was flawed, and I had to guide it to force solid dark background colors.

---

## 4. Testing and Verification

**a. What you tested**

I tested the core scheduling behaviors using a suite of `pytest` unit tests (21 tests in total). Specifically, I tested:
1. That high-priority tasks always get scheduled before medium or low-priority tasks.
2. That tasks correctly roll over (recurrence) when marked complete.
3. That the `detect_conflicts` algorithm accurately catches immediately overlapping or impossible schedules.
These tests were critical because the entire value proposition of the app is "Smart Pet Care Scheduling"; if the AI greedy algorithm accidentally skipped an urgent medication task for a standard grooming task, the app would be actively harmful to the user.

**b. Confidence**

I am highly confident that the scheduler works correctly for the current greedy algorithm implementation, as the test coverage is robust. If I had more time, the next edge cases I would test include handling tasks that span across midnight, dealing with precise overlapping timestamps down to the minute, and performance testing the conflict detection with a massive dataset (e.g., hundreds of tasks).

---

## 5. Reflection

**a. What went well**

I am most satisfied with the radical transformation of the Streamlit frontend. Pushing Streamlit out of its standard, rigid "data dashboard" feel into a sleek, glassmorphic, animated consumer app UI was a major win. The visual timeline feature is particularly satisfying as it clearly visualizes the backend algorithm's output in a very user-friendly way.

**b. What you would improve**

If I had another iteration, I would implement actual database persistence (like SQLite or PostgreSQL) instead of relying solely on `st.session_state`. Right now, refreshing the server wipes user data. I would also build out a proper "Multi-Pet Profile Manager" so users could dynamically add and edit multiple pets rather than replacing the owner profile entirely each time.

**c. Key takeaway**

The most important thing I learned working with AI on this project is that AI is incredible at writing complex algorithmic code and CSS very quickly, but it requires extreme specificity to achieve a highly polished final product. You can't just say "make it look good"; you have to act like an Art Director and explicitly ask for the exact padding, border-radius, color codes, and visual hierarchies you want.
