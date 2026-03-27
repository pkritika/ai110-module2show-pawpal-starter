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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
