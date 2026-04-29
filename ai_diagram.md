# PawPal+ AI System Diagram

Here is a breakdown of how the new Agentic AI Workflow is integrated into the PawPal+ system.

```mermaid
flowchart TD
    %% Define User / Input
    User((Human User))
    
    %% Input Stage
    subgraph Input Phase
        UI[Streamlit Chat UI]
        Context[Owner Context]
    end
    
    %% Process Stage (The Agentic AI)
    subgraph Agentic Workflow Process
        Agent[Claude 3.5 Haiku Agent]
        RAG[RAG / Context Builder]
        Tools[[add_care_task Tool]]
    end
    
    %% Output Stage
    subgraph Output Phase
        DB[(Local JSON Data)]
        Display[Updated UI & Tasks]
    end

    %% Data Flow
    User -- "Types request (e.g., 'Add a walk for Luna')" --> UI
    UI -- "User Prompt" --> Agent
    
    %% Context Retrieval (RAG)
    Context -- "Current Pets, Tasks, Time" --> RAG
    RAG -- "System Prompt Context" --> Agent
    
    %% Agent Processing & Tool Calling
    Agent -- "1. Decides to call tool" --> Tools
    Tools -- "2. Executes python function" --> DB
    Tools -- "3. Returns success/fail" --> Agent
    
    %% Output Generation
    Agent -- "Generates response" --> Display
    DB -- "Reloads state" --> Display
    
    %% Human Verification Step
    Display -- "Shows generated tasks & response" --> User
    User -. "Human-in-the-loop: Verifies and Manages Tasks" .-> Context
    
    classDef ai fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff;
    classDef db fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef human fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;
    
    class Agent,RAG,Tools ai;
    class DB,Context db;
    class User human;
```

### Component Breakdown
1. **Input**: The human user interacts via the Streamlit Chat UI. The system also retrieves the `Owner Context` (pets, time limits, existing schedule).
2. **Process**: The **RAG / Context Builder** passes the user's data to the **Gemini Agent**. The agent processes the input and, if necessary, autonomously calls the **`add_care_task` tool** to act on the user's behalf.
3. **Output**: The tool modifies the underlying **Local JSON Data**, and the agent generates a conversational response shown to the user on the **Updated UI**.
4. **Human Involvement**: The human user acts as the evaluator (human-in-the-loop). Once the AI adds tasks to the system, the user verifies them in the "Manage Tasks" or "Smart Schedule" tabs and can delete or modify any hallucinations or incorrect priorities.
