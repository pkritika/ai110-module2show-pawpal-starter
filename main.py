"""
main.py — PawPal+ Testing Ground
---------------------------------
Manually verifies that all core classes work correctly together.
Run with: python3 main.py
"""

from pawpal_system import CareTask, Pet, Owner, Scheduler

# ── 1. Create Owner ────────────────────────────────────────────────────────
owner = Owner(name="Jordan", available_time=75)  # 75 minutes available today

# ── 2. Create Pets ─────────────────────────────────────────────────────────
dog = Pet(name="Fido", species_breed="Labrador")
cat = Pet(name="Whiskers", species_breed="Tabby Cat")

# ── 3. Add Tasks to Dog ────────────────────────────────────────────────────
dog.add_task(CareTask(name="Morning Walk",      pet_name="Fido", duration=30, priority=1))
dog.add_task(CareTask(name="Give Medication",   pet_name="Fido", duration=10, priority=1))
dog.add_task(CareTask(name="Fetch & Play",      pet_name="Fido", duration=20, priority=2))
dog.add_task(CareTask(name="Bath & Grooming",   pet_name="Fido", duration=45, priority=3))

# ── 4. Add Tasks to Cat ────────────────────────────────────────────────────
cat.add_task(CareTask(name="Litter Box Clean",  pet_name="Whiskers", duration=10, priority=1))
cat.add_task(CareTask(name="Playtime",          pet_name="Whiskers", duration=15, priority=2))
cat.add_task(CareTask(name="Brushing",          pet_name="Whiskers", duration=10, priority=3))

# ── 5. Register Pets with Owner ────────────────────────────────────────────
owner.add_pet(dog)
owner.add_pet(cat)

# ── 6. Run Scheduler ───────────────────────────────────────────────────────
scheduler = Scheduler(owner)
scheduler.generate_plan()

# ── 7. Print Today's Schedule ──────────────────────────────────────────────
print("=" * 50)
print("       🐾  PawPal+ — Today's Schedule  🐾")
print("=" * 50)
print(f"Owner : {owner.name}")
print(f"Time  : {owner.available_time} min available\n")

if scheduler.daily_plan:
    for i, task in enumerate(scheduler.daily_plan, start=1):
        print(f"  {i}. {task}")
else:
    print("  No tasks could be scheduled today.")

print()
print("--- Scheduler Reasoning ---")
print(scheduler.explain_plan())
print("=" * 50)
