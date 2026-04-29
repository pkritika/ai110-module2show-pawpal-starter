import os
from typing import Optional
from pawpal_system import CareTask, Pet, Owner

def get_ai_client():
    """
    Returns an Anthropic client. 
    Loads the API key from Streamlit secrets (secrets.toml) first,
    then falls back to the ANTHROPIC_API_KEY environment variable.
    """
    try:
        import streamlit as st
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    except Exception as e:
        return None


def get_system_instruction(owner: Owner) -> str:
    """Creates a system prompt dynamically based on the user's current profile."""
    
    pet_info = []
    for p in owner.pets:
        pet_info.append(f"- {p.name} ({p.species_breed or 'Unknown breed'})")
        
    tasks_info = []
    for t in owner.get_all_tasks():
        status = "Completed" if t.is_completed else "Pending"
        tasks_info.append(f"- {t.name} for {t.pet_name} ({t.duration} min, {status})")

    pet_str = "\n".join(pet_info) if pet_info else "No pets added yet."
    task_str = "\n".join(tasks_info) if tasks_info else "No tasks added yet."
    
    return f"""You are the PawPal+ AI Assistant, a friendly and knowledgeable expert in pet care and scheduling.
Your goal is to help the user manage their pet care routine effectively.

Current Context:
User Name: {owner.name}
Available Free Time Today: {owner.available_time} minutes

Pets:
{pet_str}

Current Care Tasks:
{task_str}

Instructions:
1. You can provide advice on pet care, suggest schedules, or help debug pet care issues.
2. If the user asks you to add a new task, use the `add_care_task` tool. 
3. IMPORTANT: When suggesting a task, consider their available free time ({owner.available_time} minutes) and what is already scheduled.
4. If they mention a pet that doesn't exist in the list above, ask which existing pet the task is for.
5. Be concise and friendly.
"""
