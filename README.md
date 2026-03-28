# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ isn't just a basic to-do list; it uses an intelligent scheduling engine to calculate the optimal care plan for your pets. 

- **Priority-based Knapsack Scheduling**: The core engine maximizes high-priority tasks while strictly adhering to the owner's available free time constraints.
- **Sorting by Time & Priority**: The `sort_by_time` algorithm organizes your pending chores logistically, grouping quick wins together or sorting strictly by urgency.
- **Conflict Warnings**: An O(n²) overlap detection algorithm (`detect_conflicts`) analyzes the generated schedule start-to-finish, gracefully flagging any impossible overlapping time windows with a warning pill.
- **Daily Recurrence Automation**: The `refresh_recurring_tasks` system listens for completed daily or weekly chores and automatically rolls over a new generated instance for the following period.

## 📸 Demo

Get a feel for the sleek, dark-themed interface:

<a href="/course_images/ai110/pawpal_dark_theme.png" target="_blank"><img src='/course_images/ai110/pawpal_dark_theme.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

To run the full test suite, use:
```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover:**
- **Task Management**: Marking tasks complete and adding tasks to pets.
- **Sorting Correctness**: Verifies the scheduler accurately returns tasks in chronological (duration-based) order.
- **Recurrence Logic**: Confirms that checking off a daily or weekly task creates a new corresponding task for the next required day.
- **Conflict Detection**: Flags duplicate/overlapping task times and prevents users from scheduling impossibilities.
- **Edge Cases**: Empty pet profiles, negative integer availability, zero-time limits, etc.

**Confidence Level**: ⭐⭐⭐⭐⭐ (5/5 stars) — All 21 tests pass flawlessly and successfully protect to the system's core scheduling logic and edge case restraints.
