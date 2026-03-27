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
    duration: int           # in minutes
    priority: int           # 1 = High, 2 = Medium, 3 = Low
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Toggle the task as completed for today."""
        pass

    def update_priority(self, new_priority: int) -> None:
        """Change the urgency level of this task."""
        pass


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
        pass

    def get_all_tasks(self) -> list[CareTask]:
        """Return all care tasks for this pet."""
        pass


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
        pass

    def add_pet(self, pet: Pet) -> None:
        """Associate a new pet with this owner."""
        pass


# ---------------------------------------------------------------------------
# Scheduler — generates and explains the daily care plan
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.daily_plan: list[CareTask] = []
        self.reasoning: str = ""

    def generate_plan(self) -> list[CareTask]:
        """
        Select and order tasks from the owner's pets based on:
        - Available time (owner.available_time)
        - Task priority (lower number = higher priority)
        Returns the list of scheduled CareTask objects.
        """
        pass

    def explain_plan(self) -> str:
        """Return a natural language explanation of why tasks were chosen or skipped."""
        pass
