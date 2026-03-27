"""
tests/test_pawpal.py
---------------------
Basic unit tests for PawPal+ core logic.
Run with: pytest tests/test_pawpal.py -v
"""

import sys
import os

# Ensure the parent directory is on the path so we can import pawpal_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import CareTask, Pet


# ── Test 1: Task Completion ─────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Calling mark_complete() should toggle is_completed from False to True."""
    task = CareTask(name="Morning Walk", pet_name="Fido", duration=30, priority=1)

    assert task.is_completed is False, "Task should start as not completed."

    task.mark_complete()

    assert task.is_completed is True, "Task should be completed after calling mark_complete()."


# ── Test 2: Task Addition ───────────────────────────────────────────────────

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Fido", species_breed="Labrador")

    assert len(pet.tasks) == 0, "Pet should start with no tasks."

    task = CareTask(name="Give Medication", pet_name="Fido", duration=10, priority=1)
    pet.add_task(task)

    assert len(pet.tasks) == 1, "Pet should have 1 task after add_task() is called."
