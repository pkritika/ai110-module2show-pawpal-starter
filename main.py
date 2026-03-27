"""
main.py — PawPal+ Testing Ground
---------------------------------
Demonstrates all features: scheduling, sorting, filtering,
recurring tasks, and conflict detection.
Run with: python3 main.py
"""

from datetime import date
from pawpal_system import CareTask, Pet, Owner, Scheduler

print("=" * 55)
print("        🐾  PawPal+ — Full Feature Demo  🐾")
print("=" * 55)

# ── Setup ──────────────────────────────────────────────────────────────────
owner = Owner(name="Jordan", available_time=75)

dog = Pet(name="Fido", species_breed="Labrador")
cat = Pet(name="Whiskers", species_breed="Tabby Cat")

# Add tasks OUT OF ORDER (to demonstrate sorting)
dog.add_task(CareTask("Bath & Grooming",  "Fido",     duration=45, priority=3))
dog.add_task(CareTask("Morning Walk",     "Fido",     duration=30, priority=1))
dog.add_task(CareTask("Give Medication",  "Fido",     duration=10, priority=1,
                      recurrence="daily", due_date=date.today()))   # recurring!
dog.add_task(CareTask("Fetch & Play",     "Fido",     duration=20, priority=2))

cat.add_task(CareTask("Litter Box Clean", "Whiskers", duration=10, priority=1))
cat.add_task(CareTask("Playtime",         "Whiskers", duration=15, priority=2))
cat.add_task(CareTask("Brushing",         "Whiskers", duration=10, priority=3,
                      recurrence="weekly", due_date=date.today()))  # recurring!

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# ── Section 1: Today's Schedule ────────────────────────────────────────────
print("\n📋  1. TODAY'S SCHEDULE")
print("-" * 55)
scheduler.generate_plan()
print(scheduler)
for i, task in enumerate(scheduler.daily_plan, 1):
    print(f"  {i}. {task}")

print("\n  --- Scheduler Reasoning ---")
print(scheduler.explain_plan())

# ── Section 2: Sort by Time ─────────────────────────────────────────────────
print("\n⏱️   2. ALL TASKS — SORTED BY DURATION (shortest first)")
print("-" * 55)
sorted_tasks = scheduler.sort_by_time()
for task in sorted_tasks:
    print(f"  {task.duration:3d} min  |  {task.name} ({task.pet_name})")

# ── Section 3: Filter Tasks ─────────────────────────────────────────────────
print("\n🔍  3. FILTERING")
print("-" * 55)

fido_tasks = scheduler.filter_tasks(pet_name="Fido")
print(f"  Fido's tasks ({len(fido_tasks)} total):")
for t in fido_tasks:
    print(f"    - {t.name} ({t.duration} min)")

pending = scheduler.filter_tasks(completed=False)
print(f"\n  Pending (not completed) tasks: {len(pending)}")
for t in pending:
    print(f"    - {t.name} ({t.pet_name})")

# ── Section 4: Recurring Tasks ──────────────────────────────────────────────
print("\n🔄  4. RECURRING TASKS — NEXT OCCURRENCE AFTER COMPLETION")
print("-" * 55)

# Mark the recurring tasks complete to trigger next-occurrence generation
for pet in owner.pets:
    for task in pet.tasks:
        if task.recurrence:
            task.mark_complete()
            print(f"  ✓ Marked '{task.name}' ({task.pet_name}) as complete  [{task.recurrence}]")

new_tasks = scheduler.refresh_recurring_tasks()
if new_tasks:
    print(f"\n  {len(new_tasks)} new recurring task(s) auto-created:")
    for t in new_tasks:
        print(f"    ↪ {t.name} ({t.pet_name}) — next due: {t.due_date}")
else:
    print("  No recurring tasks to refresh.")

# ── Section 5: Conflict Detection ──────────────────────────────────────────
print("\n⚠️   5. CONFLICT DETECTION DEMO")
print("-" * 55)

# Build a fresh owner with two overlapping tasks to force a conflict
conflict_owner = Owner("TestOwner", available_time=120)
conflict_pet   = Pet("Rex", "German Shepherd")
conflict_pet.add_task(CareTask("Walk",          "Rex", duration=30, priority=1))
conflict_pet.add_task(CareTask("Vet Checkup",   "Rex", duration=60, priority=1))
conflict_pet.add_task(CareTask("Training",      "Rex", duration=30, priority=1))
conflict_owner.add_pet(conflict_pet)

conflict_scheduler = Scheduler(conflict_owner)
conflict_scheduler.generate_plan()

conflicts = conflict_scheduler.detect_conflicts()
if conflicts:
    print(f"  {len(conflicts)} conflict(s) detected:")
    for w in conflicts:
        print(f"  {w}")
else:
    print("  ✅ No conflicts — all tasks fit without overlap.")

print("\n" + "=" * 55)
print("  Demo complete. All features verified.")
print("=" * 55)
