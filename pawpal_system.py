"""
PawPal+ Logic Layer
-------------------
All backend classes for the pet care scheduling system.
Classes: CareTask, Pet, Owner, Scheduler
"""

from dataclasses import dataclass, field
from typing import Optional


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

    def mark_complete(self) -> None:
        """Toggle the task as completed for today."""
        self.is_completed = not self.is_completed

    def update_priority(self, new_priority: int) -> None:
        """Change the urgency level of this task (1=High, 2=Medium, 3=Low)."""
        if new_priority not in (1, 2, 3):
            raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low).")
        self.priority = new_priority

    def __str__(self) -> str:
        status = "✓" if self.is_completed else "○"
        priority_label = {1: "High", 2: "Medium", 3: "Low"}.get(self.priority, "?")
        return f"[{status}] {self.name} ({self.pet_name}) — {self.duration} min | Priority: {priority_label}"


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
        task.pet_name = self.name   # Ensure the task knows which pet it belongs to
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

    def generate_plan(self) -> list[CareTask]:
        """Generate a prioritized daily care plan based on the owner's time and tasks."""
        all_tasks = self.owner.get_all_tasks()

        # Sort by priority (1=High first), then by duration (shorter tasks first as tiebreaker)
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
