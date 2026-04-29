import os
import pytest
from anthropic import Anthropic

def get_test_api_key():
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            return tomllib.load(f).get("ANTHROPIC_API_KEY")
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")

@pytest.mark.skipif(not get_test_api_key(), reason="Requires Anthropic API Key")
def test_ai_tool_calling_accuracy():
    """
    Tests if the Anthropic AI correctly maps natural language to the `add_care_task` tool.
    This measures the reliability of the Agentic Workflow.
    """
    client = Anthropic(api_key=get_test_api_key())
    
    # Define a mock of the tool schema exactly as it is in app.py
    add_care_task_tool = {
        "name": "add_care_task",
        "description": "Adds a new care task for a specific pet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pet_name": {"type": "string", "description": "The name of the pet (must match an existing pet)."},
                "task_name": {"type": "string", "description": "A short name for the task (e.g. 'Walk', 'Brush')."},
                "duration": {"type": "integer", "description": "Estimated time in minutes."},
                "priority": {"type": "integer", "description": "Priority level (1=High, 2=Medium, 3=Low)."},
                "recurrence": {"type": "string", "enum": ["daily", "weekly", "Never"], "description": "How often it repeats."}
            },
            "required": ["pet_name", "task_name", "duration", "priority"]
        }
    }

    system_instruction = "You are the PawPal+ AI Assistant. If the user asks to add a task, you MUST use the add_care_task tool."
    
    # Test Case 1: High priority task
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        temperature=0.0,
        system=system_instruction,
        messages=[{"role": "user", "content": "Add a 45 minute high priority grooming task for Bella."}],
        tools=[add_care_task_tool]
    )
    
    assert response.stop_reason == "tool_use", "AI failed to use the tool."
    
    tool_use_block = next((block for block in response.content if block.type == "tool_use"), None)
    assert tool_use_block is not None
    assert tool_use_block.name == "add_care_task"
    assert tool_use_block.input["pet_name"] == "Bella"
    assert tool_use_block.input["duration"] == 45
    assert tool_use_block.input["priority"] == 1  # 1 = High priority
    
    # Test Case 2: Daily recurrence
    response2 = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        temperature=0.0,
        system=system_instruction,
        messages=[{"role": "user", "content": "Please create a 10 min daily feeding task for Luna."}],
        tools=[add_care_task_tool]
    )
    
    assert response2.stop_reason == "tool_use"
    tool_use_block2 = next((block for block in response2.content if block.type == "tool_use"), None)
    assert tool_use_block2 is not None
    assert tool_use_block2.input["pet_name"] == "Luna"
    assert tool_use_block2.input["duration"] == 10
    assert tool_use_block2.input["recurrence"] == "daily"
