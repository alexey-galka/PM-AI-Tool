"""
Service for generating RACI matrix based on project information
"""

import json
import re
import streamlit as st
from services.ai_service import call_ollama
import pandas as pd


def generate_raci_from_project(
    name: str,
    goals: str,
    stages: list = None,
    team_members: list = None,
    tasks: list = None
) -> list:
    """
    Generate RACI matrix based on project information

    Args:
        name: Project name
        goals: Project goals
        stages: List of project stages
        team_members: List of team members with names and roles
        tasks: List of project tasks

    Returns:
        List of RACI entries, each entry is a dict with fields:
        - artifact: Artifact or task name
        - role: Role or person name
        - code: RACI code (R, A, C, I)
    """

    if stages is None:
        stages = []
    if team_members is None:
        team_members = []
    if tasks is None:
        tasks = []

    # Format stages for prompt
    stages_text = ""
    for i, stage in enumerate(stages, 1):
        if stage.get('name'):
            stages_text += f"{i}. {stage.get('name')}\n"

    # Format tasks for prompt
    tasks_text = ""
    for i, task in enumerate(tasks, 1):
        if task.get('title'):
            tasks_text += f"{i}. {task.get('title')}\n"

    # Format team members
    team_text = ""
    for member in team_members:
        if member.get('name'):
            role = member.get('role', 'Team member')
            team_text += f"- {member.get('name')} ({role})\n"

    if not team_text:
        team_text = "- Project Manager\n- Business Analyst\n- Developer\n- Tester\n"

    prompt = f"""You are a project management expert. Create a RACI matrix for the project.

Project data:
- Name: {name or 'Not specified'}
- Goals: {goals or 'Not specified'}

Project stages:
{stages_text or 'Not specified'}

Key tasks:
{tasks_text or 'Not specified'}

Team members/roles available:
{team_text}

Create a RACI matrix with 8-12 entries. Each entry defines who is Responsible, Accountable, Consulted, or Informed for a specific artifact or task.

RACI codes:
- R (Responsible): Person who does the work
- A (Accountable): Person who approves and is ultimately responsible
- C (Consulted): Person who provides input and advice
- I (Informed): Person who needs to be kept updated

Return ONLY a JSON array. Each entry must contain:
- artifact: Artifact or task name (string)
- role: Role or person name (string)
- code: R, A, C, or I (string)

Example:
[
    {{
        "artifact": "Project Charter",
        "role": "Project Manager",
        "code": "A"
    }},
    {{
        "artifact": "Project Charter",
        "role": "Business Analyst",
        "code": "R"
    }},
    {{
        "artifact": "Requirements Document",
        "role": "Business Analyst",
        "code": "R"
    }},
    {{
        "artifact": "Requirements Document",
        "role": "Project Manager",
        "code": "A"
    }},
    {{
        "artifact": "Requirements Document",
        "role": "Developer",
        "code": "C"
    }}
]

Return ONLY the JSON array, no other text.
"""

    response = call_ollama(prompt)

    # Clean response
    response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response)
    response = re.sub(r'[\x00-\x1f\x7f]', '', response)

    # Extract JSON
    raci_entries = extract_raci_from_response(response)

    # if not raci_entries:
    #     return get_default_raci()

    return raci_entries


def extract_raci_from_response(text: str) -> list:
    """Extract RACI entries JSON from AI response"""

    # Strategy 1: Try to find JSON array
    try:
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)
            if isinstance(result, list):
                return validate_raci(result)
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
                return validate_raci(result)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract entries manually with regex
    try:
        entries = []
        pattern = r'"artifact"\s*:\s*"([^"]+)".*?"role"\s*:\s*"([^"]+)".*?"code"\s*:\s*"([RAIC])"'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            entries.append({
                "artifact": match[0],
                "role": match[1],
                "code": match[2].upper()
            })

        if entries:
            return validate_raci(entries)
    except Exception:
        pass

    return None


def validate_raci(entries: list) -> list:
    """Validate and fix RACI entries"""
    validated = []

    for entry in entries:
        artifact = entry.get('artifact', '').strip()
        if not artifact:
            continue

        role = entry.get('role', '').strip()
        if not role:
            continue

        code = entry.get('code', 'R').upper()
        if code not in ['R', 'A', 'C', 'I']:
            code = 'R'

        validated.append({
            "artifact": artifact,
            "role": role,
            "code": code
        })

    return validated


def render_ai_raci_button(
    project_info: dict,
    raci_list_key: str = 'raci_list'
) -> bool:
    """
    Render button for generating RACI matrix via AI

    Args:
        project_info: Dictionary with project fields:
            - name: Project name
            - goals: Project goals
            - stages: List of project stages
            - team: List of team members
        raci_list_key: Session state key for RACI list

    Returns:
        True if generation was successful, False otherwise
    """

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.form_submit_button("Generate RACI matrix", width='stretch'):
            has_info = any([
                project_info.get('name'),
                project_info.get('goals')
            ])

            if not has_info:
                st.error(
                    "Fill in at least the project name or goals "
                    "to generate RACI matrix"
                )
                return False

            with st.spinner("Analyzing project and generating RACI matrix..."):
                stages = st.session_state.get('stages_list', [])
                team = st.session_state.get('team_list', [])
                tasks = st.session_state.get('tasks_list', [])

                new_raci = generate_raci_from_project(
                    name=project_info.get('name', ''),
                    goals=project_info.get('goals', ''),
                    stages=stages,
                    team_members=team,
                    tasks=tasks
                )

                if new_raci:
                    current_raci = st.session_state.get(raci_list_key, [])

                    for entry in new_raci:
                        current_raci.append({
                            "artifact": entry.get('artifact', ''),
                            "role": entry.get('role', ''),
                            "code": entry.get('code', 'R')
                        })

                    st.session_state[raci_list_key] = current_raci
                    st.success(f"Generated {len(new_raci)} RACI entries!")
                    st.rerun()
                    return True
                else:
                    st.error("Failed to generate RACI matrix. Please try again.")
                    return False

    return False


def preview_raci_matrix(raci_list, key_suffix=""):
    """Preview RACI matrix in table format"""
    if not raci_list:
        return

    # Filter out empty entries
    valid_entries = [
        r for r in raci_list
        if r.get('artifact', '').strip() and r.get('role', '').strip()
    ]

    if not valid_entries:
        st.info("No RACI entries to display yet. Add some entries above.")
        return

    st.markdown("### Current RACI Matrix Preview")

    # Create DataFrame
    data = []
    for entry in valid_entries:
        data.append({
            'Artifact': entry.get('artifact', ''),
            'Role': entry.get('role', ''),
            'RACI': entry.get('code', 'R')
        })

    df = pd.DataFrame(data)

    # Create pivot table
    pivot_df = df.pivot_table(
        index='Artifact',
        columns='Role',
        values='RACI',
        aggfunc='first',
        fill_value=''
    )

    # Add styling
    def color_raci(val):
        if val == 'R':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'A':
            return 'background-color: #f8d7da; color: #721c24'
        elif val == 'C':
            return 'background-color: #fff3cd; color: #856404'
        elif val == 'I':
            return 'background-color: #d1ecf1; color: #0c5460'
        return ''

    styled_pivot = pivot_df.style.map(color_raci)
    st.dataframe(styled_pivot, width='stretch')
