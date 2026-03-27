"""
PawPal+ Logic Layer
-------------------
All backend classes for the pet care scheduling system.
Classes: CareTask, Pet, Owner, Scheduler
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# CareTask — a single pet care activity
# ---------------------------------------------------------------------------

@dataclass
class CareTask:
    name: str
    pet_name: str           # The pet this task belongs to
    duration: int           # in minutes
    priority: int           # 1 = High, 2 = Medium, 3 = Low
    is_completed: bool = False
    recurrence: Optional[str] = None    # "daily", "weekly", or None
    due_date: Optional[date] = None     # date this task is due

    def mark_complete(self) -> None:
        """Toggle the task as completed for today."""
        self.is_completed = not self.is_completed

    def update_priority(self, new_priority: int) -> None:
        """Change the urgency level of this task (1=High, 2=Medium, 3=Low)."""
        if new_priority not in (1, 2, 3):
            raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low).")
        self.priority = new_priority

    def next_occurrence(self) -> Optional["CareTask"]:
        """Return a new CareTask for the next occurrence if this recurring task is completed."""
        if not self.is_completed or self.recurrence is None:
            return None

        if self.recurrence == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None

        return CareTask(
            name=self.name,
            pet_name=self.pet_name,
            duration=self.duration,
            priority=self.priority,
            is_completed=False,
            recurrence=self.recurrence,
            due_date=next_due,
        )

    def __str__(self) -> str:
        status = "✓" if self.is_completed else "○"
        priority_label = {1: "High", 2: "Medium", 3: "Low"}.get(self.priority, "?")
        recur = f" [{self.recurrence}]" if self.recurrence else ""
        due = f" due {self.due_date}" if self.due_date else ""
        return (
            f"[{status}] {self.name} ({self.pet_name}) — "
            f"{self.duration} min | {priority_label}{recur}{due}"
        )


# ---------------------------------------------------------------------------
# Pet — the animal that receives care
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species_breed: Optional[str] = None
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a new CareTask to this pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_all_tasks(self) -> list[CareTask]:
        """Return all care tasks for this pet."""
        return list(self.tasks)

    def __str__(self) -> str:
        breed_info = f" ({self.species_breed})" if self.species_breed else ""
        return f"{self.name}{breed_info} — {len(self.tasks)} task(s)"


# ---------------------------------------------------------------------------
# Owner — the user of the app
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_time: int):
        self.name: str = name
        self.available_time: int = available_time   # in minutes
        self.pets: list[Pet] = []

    def update_availability(self, new_time: int) -> None:
        """Update how many minutes the owner has available today."""
        if new_time < 0:
            raise ValueError("Available time cannot be negative.")
        self.available_time = new_time

    def add_pet(self, pet: Pet) -> None:
        """Associate a new pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[CareTask]:
        """Retrieve all tasks across all pets owned by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_all_tasks())
        return all_tasks

    def __str__(self) -> str:
        return f"Owner: {self.name} | Available: {self.available_time} min | Pets: {len(self.pets)}"


# ---------------------------------------------------------------------------
# Scheduler — generates and explains the daily care plan
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.daily_plan: list[CareTask] = []
        self.reasoning: str = ""

    # ── Core plan generation ────────────────────────────────────────────────

    def generate_plan(self) -> list[CareTask]:
        """Generate a prioritized daily care plan based on the owner's time and tasks."""
        all_tasks = self.owner.get_all_tasks()

        # Sort by priority (1=High first), then by duration (shorter tasks first)
        sorted_tasks = sorted(all_tasks, key=lambda t: (t.priority, t.duration))

        time_remaining = self.owner.available_time
        self.daily_plan = []
        reasons = []

        for task in sorted_tasks:
            if task.is_completed:
                reasons.append(f"Skipped '{task.name}' ({task.pet_name}): already completed.")
                continue

            if task.duration <= time_remaining:
                self.daily_plan.append(task)
                time_remaining -= task.duration
                reasons.append(
                    f"Added '{task.name}' for {task.pet_name} ({task.duration} min, "
                    f"priority {task.priority}). Time remaining: {time_remaining} min."
                )
            else:
                reasons.append(
                    f"Skipped '{task.name}' ({task.pet_name}): needs {task.duration} min "
                    f"but only {time_remaining} min left."
                )

        if not self.daily_plan:
            reasons.append("No tasks could be scheduled within the available time.")

        self.reasoning = "\n".join(reasons)
        return self.daily_plan

    def explain_plan(self) -> str:
        """Return a natural language explanation of why tasks were chosen or skipped."""
        if not self.reasoning:
            return "No plan has been generated yet. Call generate_plan() first."
        return self.reasoning

    # ── Step 2: Sorting ─────────────────────────────────────────────────────

    def sort_by_time(self, tasks: Optional[list[CareTask]] = None) -> list[CareTask]:
        """Sort tasks by duration (shortest first); defaults to all owner tasks."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: t.duration)

    # ── Step 2: Filtering ───────────────────────────────────────────────────

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[CareTask]:
        """Filter owner tasks by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]

        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]

        return tasks

    # ── Step 3: Recurring task refresh ─────────────────────────────────────

    def refresh_recurring_tasks(self) -> list[CareTask]:
        """Generate and add next-occurrence instances for completed recurring tasks."""
        new_tasks: list[CareTask] = []

        for pet in self.owner.pets:
            for task in list(pet.tasks):
                next_task = task.next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                    new_tasks.append(next_task)

        return new_tasks

    # ── Step 4: Conflict detection ──────────────────────────────────────────

    def detect_conflicts(self) -> list[str]:
        """Detect overlaps in the daily plan and return a list of warning strings."""
        if not self.daily_plan:
            return []

        warnings: list[str] = []
        current_time = 0          # minutes from start of day
        schedule: list[tuple[int, int, CareTask]] = []  # (start, end, task)

        for task in self.daily_plan:
            start = current_time
            end   = current_time + task.duration

            # Check overlap with every already-placed task
            for s_start, s_end, s_task in schedule:
                if start < s_end and end > s_start:          # overlap condition
                    warnings.append(
                        f"⚠️  CONFLICT: '{task.name}' ({task.pet_name}) "
                        f"overlaps with '{s_task.name}' ({s_task.pet_name}) "
                        f"[{s_start}–{s_end} min vs {start}–{end} min]"
                    )

            schedule.append((start, end, task))
            current_time = end      # tasks run back-to-back by default

        return warnings

    def __str__(self) -> str:
        task_count = len(self.daily_plan)
        total_time = sum(t.duration for t in self.daily_plan)
        return (
            f"Today's plan for {self.owner.name}: "
            f"{task_count} task(s) scheduled, {total_time} min total."
        )


if __name__ == "__main__":
    owner = Owner("Alex", available_time=60)
    dog = Pet("Fido", "Labrador")
    dog.add_task(CareTask("Morning Walk", "Fido", 30, priority=1))
    dog.add_task(CareTask("Give Medication", "Fido", 10, priority=1))
    dog.add_task(CareTask("Grooming", "Fido", 45, priority=3))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print(scheduler)
    print()
    for task in scheduler.daily_plan:
        print(task)
    print("\n--- Reasoning ---")
    print(scheduler.explain_plan())
