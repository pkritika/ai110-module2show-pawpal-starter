```mermaid
classDiagram
    class Owner {
        +String name
        +int available_time
        +List~Pet~ pets
        +update_availability(new_time) None
        +add_pet(pet) None
        +get_all_tasks() List~CareTask~
    }

    class Pet {
        +String name
        +String species_breed
        +List~CareTask~ tasks
        +add_task(task) None
        +get_all_tasks() List~CareTask~
    }

    class CareTask {
        +String name
        +String pet_name
        +int duration
        +int priority
        +bool is_completed
        +String recurrence
        +date due_date
        +mark_complete() None
        +update_priority(new_priority) None
        +next_occurrence() CareTask
    }

    class Scheduler {
        +Owner owner
        +List~CareTask~ daily_plan
        +String reasoning
        +generate_plan() List~CareTask~
        +explain_plan() String
        +sort_by_time(tasks) List~CareTask~
        +filter_tasks(pet_name, completed) List~CareTask~
        +refresh_recurring_tasks() List~CareTask~
        +detect_conflicts() List~String~
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" CareTask : has
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler "1" --> "0..*" CareTask : selects into daily_plan
    CareTask ..> CareTask : next_occurrence() creates
```

## What changed from Phase 1

| Class | Change |
|---|---|
| `CareTask` | Added `pet_name`, `recurrence`, `due_date` fields; added `next_occurrence()` method |
| `Owner` | Added `get_all_tasks()` method |
| `Scheduler` | Added 4 Phase 3 methods: `sort_by_time`, `filter_tasks`, `refresh_recurring_tasks`, `detect_conflicts` |
| Relationships | Added `CareTask ..> CareTask` dashed arrow showing `next_occurrence()` self-association |