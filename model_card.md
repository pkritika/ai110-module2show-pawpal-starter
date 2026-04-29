# PawPal+ AI Advisor: Model & Ethics Card

This document reflects on the responsibility, limitations, and ethical considerations of the PawPal+ Agentic Workflow system, specifically focusing on its integration with Anthropic's Claude API.

## 1. Limitations and Biases
The AI relies heavily on its generalized training data for pet care advice, which inherently biases it toward common pets like dogs and cats. If an owner inputs an exotic pet (like a reptile or a rare bird), the AI might suggest inappropriate tasks (e.g., suggesting a walk for an iguana) because it lacks specialized veterinary knowledge. Additionally, the system is technically limited by its context window—it doesn't have a persistent long-term memory of past chat sessions beyond the current Streamlit state, meaning it forgets past advice once the app is refreshed.

## 2. Misuse and Prevention
A malicious user could theoretically misuse the AI by prompting it to infinitely loop or flood the system with hundreds of bogus tasks (e.g., *"Add 1000 tasks named 'test'"*), causing the Streamlit UI to crash or experience a denial-of-service (DoS) effect. 

**Prevention:** To prevent this, the system's architecture relies on Python backend guardrails rather than just LLM instructions. I would implement a hard cap inside the `add_care_task` Python tool (e.g., limiting a pet to a maximum of 20 pending tasks). This ensures that the backend explicitly rejects spam inputs regardless of what the LLM decides to execute, keeping the user interface safe and responsive.

## 3. Reliability Testing Surprises
While building the automated testing suite and reliability logs, I was surprised by two distinct behaviors:
1. **Data-Type Intuition:** Without explicitly providing few-shot examples, Claude perfectly mapped vague natural language requests like *"really urgent"* or *"top priority"* to the strict integer `1` expected by the backend Python function.
2. **Hallucinations vs Guardrails:** I was equally surprised that the AI confidently attempted to assign tasks to hallucinated pets (pets that were not provided in the RAG context) if the user tricked it. This proved why Agentic Workflows require strict backend validation—once I updated the Python tool to reject non-existent pets, the AI successfully adapted and started asking the user for clarification instead of failing silently.

## 4. AI Collaboration Experience
Throughout the development of this project, I relied on AI as a pair-programmer. 

- **Helpful Instance:** The AI was incredibly helpful when designing the `tests/test_ai_agent.py` script. It accurately suggested the specific syntax required to intercept and verify Claude's `stop_reason == "tool_use"` block without actually executing the tool in the test environment, saving me hours of reading SDK documentation.
- **Flawed Instance:** During the integration phase, the AI initially provided code that tried to maintain the chat history using standard Python lists inside the Streamlit script. Because Streamlit reruns the script top-to-bottom on every interaction, the list kept resetting, deleting the chat history instantly. I had to identify the architectural flaw myself and correct it by placing the chat array firmly inside `st.session_state`.
