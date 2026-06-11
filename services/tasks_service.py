"""
Service for generating project tasks based on project information
"""

import json
import re
import streamlit as st
from services.ai_service import call_ollama


def generate_tasks_from_project(
    name: str,
    goals: str,
    problem: str,
    success_criteria: str,
    stages: list = None,
    risks: list = None,
    must_have: list = None
) -> list:
    """
    Generate project tasks based on project information

    Args:
        name: Project name
        goals: Project goals
        problem: Problem description
        success_criteria: Success criteria
        stages: List of project stages
        risks: List of risks
        must_have: List of must-have requirements

    Returns:
        List of tasks, each task is a dict with fields:
        - title: Task title
        - description: Task description
        - priority: Priority (HIGH, MEDIUM, LOW)
        - estimated_days: Estimated days to complete
    """

    if stages is None:
        stages = []
    if risks is None:
        risks = []
    if must_have is None:
        must_have = []

    # Format stages for prompt
    stages_text = ""
    for i, stage in enumerate(stages, 1):
        if stage.get('name'):
            stages_text += f"{i}. {stage.get('name')}: {stage.get('description', '')}\n"

    # Format risks for prompt
    risks_text = ""
    for i, risk in enumerate(risks, 1):
        if risk.get('description'):
            risks_text += f"{i}. {risk.get('impact', 'MEDIUM')}: {risk.get('description', '')}\n"

    # Format requirements
    must_have_text = "\n".join(
        [f"- {req}" for req in must_have]) if must_have else "Not specified"

    prompt = f"""You are an IT project manager. Generate a list of specific tasks for the project.

Project data:
- Name: {name or 'Not specified'}
- Goals: {goals or 'Not specified'}
- Problem: {problem or 'Not specified'}
- Success criteria: {success_criteria or 'Not specified'}

Project stages:
{stages_text or 'Not specified'}

Must have requirements:
{must_have_text}

Risks to mitigate:
{risks_text or 'Not specified'}

Generate 8-12 specific tasks that need to be completed. Each task should have:
- title: Clear task name (string)
- description: Brief description (string)
- priority: HIGH, MEDIUM, or LOW (string)
- estimated_days: Estimated days to complete (integer, 1-10)

Return ONLY a JSON array. Example:
[
    {{
        "title": "Conduct stakeholder interview",
        "description": "Interview key stakeholders to gather requirements",
        "priority": "HIGH",
        "estimated_days": 2
    }},
    {{
        "title": "Setup development environment",
        "description": "Configure development tools and repositories",
        "priority": "MEDIUM",
        "estimated_days": 1
    }}
]

Return ONLY the JSON array, no other text.
"""

    response = call_ollama(prompt)

    # Clean response
    response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response)
    response = re.sub(r'[\x00-\x1f\x7f]', '', response)

    # Extract JSON
    tasks = extract_tasks_from_response(response)

    return tasks


def extract_tasks_from_response(text: str) -> list:
    """Extract tasks JSON from AI response"""

    # Strategy 1: Try to find JSON array
    try:
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)
            if isinstance(result, list):
                return validate_tasks(result)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Fix common JSON issues
    try:
        fixed = re.sub(r"'", '"', text)
        fixed = re.sub(
            r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)
        fixed = re.sub(r',\s*}', '}', fixed)
        fixed = re.sub(r',\s*]', ']', fixed)

        match = re.search(r'\[\s*\{.*?\}\s*\]', fixed, re.DOTALL)
        if match:
            result = json.loads(match.group())
            if isinstance(result, list):
                return validate_tasks(result)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract tasks manually with regex
    try:
        tasks = []
        pattern = r'"title"\s*:\s*"([^"]+)".*?"description"\s*:\s*"([^"]+)".*?"priority"\s*:\s*"([^"]+)".*?"estimated_days"\s*:\s*(\d+)'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            tasks.append({
                "title": match[0],
                "description": match[1],
                "priority": match[2].upper(),
                "estimated_days": int(match[3])
            })

        if tasks:
            return validate_tasks(tasks)
    except Exception:
        pass

    return None


def validate_tasks(tasks: list) -> list:
    """Validate and fix tasks"""
    validated = []

    for i, task in enumerate(tasks):
        title = task.get('title', '').strip()
        if not title:
            title = f"Task {i + 1}"

        description = task.get('description', '').strip()
        if not description:
            description = f"Complete {title}"

        priority = task.get('priority', 'MEDIUM').upper()
        if priority not in ['HIGH', 'MEDIUM', 'LOW']:
            priority = 'MEDIUM'

        estimated_days = task.get('estimated_days', 3)
        if not isinstance(estimated_days, int):
            try:
                estimated_days = int(estimated_days)
            except (ValueError, TypeError):
                estimated_days = 3
        estimated_days = max(1, min(10, estimated_days))

        validated.append({
            "title": title,
            "description": description,
            "priority": priority,
            "estimated_days": estimated_days,
            "status": "TODO"
        })

    return validated


def render_ai_tasks_button(
    project_info: dict,
    tasks_list_key: str = 'tasks_list'
) -> bool:
    """
    Render button for generating tasks via AI

    Args:
        project_info: Dictionary with project fields:
            - name: Project name
            - goals: Project goals
            - problem: Problem description
            - success_criteria: Success criteria
            - stages: List of project stages
            - must_have: List of must-have requirements
        tasks_list_key: Session state key for tasks list

    Returns:
        True if generation was successful, False otherwise
    """

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.form_submit_button("Generate tasks", width='stretch'):
            has_info = any([
                project_info.get('name'),
                project_info.get('goals'),
                project_info.get('problem')
            ])

            if not has_info:
                st.error(
                    "Fill in at least the name, goals or problem description "
                    "to generate tasks"
                )
                return False

            with st.spinner("Analyzing project and generating tasks..."):
                risks = st.session_state.get('risks_list', [])
                stages = st.session_state.get('stages_list', [])

                new_tasks = generate_tasks_from_project(
                    name=project_info.get('name', ''),
                    goals=project_info.get('goals', ''),
                    problem=project_info.get('problem', ''),
                    success_criteria=project_info.get('success_criteria', ''),
                    stages=stages,
                    risks=risks,
                    must_have=project_info.get('must_have', [])
                )

                if new_tasks:
                    current_tasks = st.session_state.get(tasks_list_key, [])

                    for task in new_tasks:
                        current_tasks.append({
                            "title": task.get('title', ''),
                            "description": task.get('description', ''),
                            "status": "TODO"
                        })

                    st.session_state[tasks_list_key] = current_tasks
                    st.success(f"Generated {len(new_tasks)} tasks!")
                    st.rerun()
                    return True
                else:
                    st.error("Failed to generate tasks. Please try again.")
                    return False

    return False
