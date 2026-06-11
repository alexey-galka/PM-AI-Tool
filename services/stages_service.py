"""
Service for generating project stages based on project information
"""

import json
import re
import streamlit as st
from services.ai_service import call_ollama


def generate_stages_from_project(
    name: str,
    goals: str,
    problem: str,
    hypothesis: str,
    success_criteria: str,
    must_have: list = None,
    nice_to_have: list = None,
    risks: list = None
) -> list:
    """
    Generate project stages based on project information

    Args:
        name: Project name
        goals: Project goals
        problem: Problem description
        hypothesis: Project hypothesis
        success_criteria: Success criteria
        must_have: List of must-have requirements
        nice_to_have: List of nice-to-have requirements
        risks: List of risks (each risk is a dict with description and impact)

    Returns:
        List of stages, each stage is a dict with fields:
        - name: Stage name
        - description: Stage description
        - expected_date_offset_days: Days offset from start (0, 7, 14, etc.)
        - risk_text: Linked risk text (optional)
    """

    if must_have is None:
        must_have = []
    if nice_to_have is None:
        nice_to_have = []
    if risks is None:
        risks = []

    # Format risks for prompt
    risks_text = ""
    for i, risk in enumerate(risks, 1):
        if risk.get('description'):
            risks_text += f"{i}. {risk.get('impact', 'MEDIUM')}: {risk.get('description', '')}\n"

    # Format requirements
    must_have_text = "\n".join([f"- {req}" for req in must_have]) if must_have else "Not specified"
    nice_to_have_text = "\n".join([f"- {req}" for req in nice_to_have]) if nice_to_have else "Not specified"

    prompt = f"""You are an IT project management expert. Break down the project into logical stages (milestones).

Project data:
- Name: {name or 'Not specified'}
- Goals: {goals or 'Not specified'}
- Problem: {problem or 'Not specified'}
- Hypothesis: {hypothesis or 'Not specified'}
- Success criteria: {success_criteria or 'Not specified'}

Must have requirements:
{must_have_text}

Nice to have requirements:
{nice_to_have_text}

Project risks:
{risks_text or 'Not specified'}

Return ONLY a JSON array of stages. Each stage must contain:
- name: stage name (string)
- description: brief stage description (string)
- duration_days: stage duration in days (integer, minimum 1, maximum 30)

Rules:
1. Total should be 4-7 stages
2. Stages should be in logical order
3. Consider must-have requirements in stages
4. If there are HIGH risks, add a stage for their monitoring or mitigation
5. Add a final stage for acceptance and project closure

Example response:
[
    {{
        "name": "Requirements Analysis",
        "description": "Collecting and refining requirements, market analysis",
        "duration_days": 5
    }},
    {{
        "name": "Design",
        "description": "Developing architecture and solution design",
        "duration_days": 7
    }}
]

Return ONLY the JSON array, no other text.
"""

    response = call_ollama(prompt)

    # Clean response
    response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response)
    response = re.sub(r'[\x00-\x1f\x7f]', '', response)

    # Extract JSON
    stages = extract_stages_from_response(response)

    if not stages:
        # Fallback: return default stages
        return get_default_stages()

    # Add risk links if provided
    stages = link_risks_to_stages(stages, risks)

    return stages


def extract_stages_from_response(text: str) -> list:
    """Extract stages JSON from AI response"""
    
    # Strategy 1: Try to find JSON array
    try:
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)
            if isinstance(result, list):
                return validate_stages(result)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Fix common JSON issues
    try:
        # Replace single quotes with double quotes
        fixed = re.sub(r"'", '"', text)
        # Add quotes to keys without quotes
        fixed = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)
        # Remove trailing commas
        fixed = re.sub(r',\s*}', '}', fixed)
        fixed = re.sub(r',\s*]', ']', fixed)
        
        match = re.search(r'\[\s*\{.*?\}\s*\]', fixed, re.DOTALL)
        if match:
            result = json.loads(match.group())
            if isinstance(result, list):
                return validate_stages(result)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract stages manually with regex
    try:
        stages = []
        pattern = r'"name"\s*:\s*"([^"]+)".*?"description"\s*:\s*"([^"]+)".*?"duration_days"\s*:\s*(\d+)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            stages.append({
                "name": match[0],
                "description": match[1],
                "duration_days": int(match[2])
            })
        
        if stages:
            return validate_stages(stages)
    except Exception:
        pass

    return None


def validate_stages(stages: list) -> list:
    """Validate and fix stages"""
    validated = []
    
    for i, stage in enumerate(stages):
        # Ensure required fields exist
        name = stage.get('name', '').strip()
        if not name:
            name = f"Stage {i + 1}"
        
        description = stage.get('description', '').strip()
        if not description:
            description = f"Executing stage {name}"
        
        duration_days = stage.get('duration_days', 7)
        if not isinstance(duration_days, int):
            try:
                duration_days = int(duration_days)
            except (ValueError, TypeError):
                duration_days = 7
        
        duration_days = max(1, min(30, duration_days))
        
        validated.append({
            "name": name,
            "description": description,
            "duration_days": duration_days,
            "risk_text": "",  # Will be filled by link_risks_to_stages
            "risk_description": ""
        })
    
    return validated


def link_risks_to_stages(stages: list, risks: list) -> list:
    """Link risks to relevant stages"""
    if not risks:
        return stages
    
    # Create a copy of stages
    linked_stages = []
    
    for stage in stages:
        # Try to find relevant risk for this stage
        relevant_risk = find_relevant_risk(stage, risks)
        
        stage_copy = stage.copy()
        if relevant_risk:
            stage_copy['risk_text'] = f"{relevant_risk.get('impact', 'MEDIUM')}: {relevant_risk.get('description', '')}"
            stage_copy['risk_description'] = relevant_risk.get('description', '')
        
        linked_stages.append(stage_copy)
    
    return linked_stages


def find_relevant_risk(stage: dict, risks: list) -> dict:
    """Find risk relevant to a stage"""
    # Keywords that indicate risk relevance
    stage_text = f"{stage.get('name', '')} {stage.get('description', '')}".lower()
    
    # HIGH risks are most important
    high_risks = [r for r in risks if r.get('impact') == 'HIGH' and r.get('description')]
    medium_risks = [r for r in risks if r.get('impact') == 'MEDIUM' and r.get('description')]
    
    # Try to match HIGH risks first
    for risk in high_risks:
        risk_text = risk.get('description', '').lower()
        # Check if risk keywords appear in stage description
        risk_keywords = risk_text.split()[:5]  # Take first 5 words as keywords
        for keyword in risk_keywords:
            if len(keyword) > 5 and keyword in stage_text:
                return risk
    
    # Then try MEDIUM risks
    for risk in medium_risks:
        risk_text = risk.get('description', '').lower()
        risk_keywords = risk_text.split()[:5]
        for keyword in risk_keywords:
            if len(keyword) > 5 and keyword in stage_text:
                return risk
    
    return None


def get_default_stages() -> list:
    """Return default stages if AI generation fails"""
    return [
        {
            "name": "Requirements Analysis",
            "description": "Collecting and analyzing project requirements",
            "duration_days": 5,
            "risk_text": "",
            "risk_description": ""
        },
        {
            "name": "Design",
            "description": "Developing architecture and technical solution",
            "duration_days": 7,
            "risk_text": "",
            "risk_description": ""
        },
        {
            "name": "Development",
            "description": "Implementing functionality according to requirements",
            "duration_days": 10,
            "risk_text": "",
            "risk_description": ""
        },
        {
            "name": "Testing",
            "description": "Quality assurance and defect fixing",
            "duration_days": 5,
            "risk_text": "",
            "risk_description": ""
        },
        {
            "name": "Deployment and Acceptance",
            "description": "Solution deployment and results acceptance",
            "duration_days": 3,
            "risk_text": "",
            "risk_description": ""
        }
    ]


def render_ai_stages_button(
    project_info: dict,
    stages_list_key: str = 'stages_list'
) -> bool:
    """
    Render button for generating stages via AI

    Args:
        project_info: Dictionary with project fields:
            - name: Project name
            - goals: Project goals
            - problem: Problem description
            - hypothesis: Project hypothesis
            - success_criteria: Success criteria
            - must_have: List of must-have requirements
            - nice_to_have: List of nice-to-have requirements
        stages_list_key: Session state key for stages list

    Returns:
        True if generation was successful, False otherwise
    """
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.form_submit_button("Generate stages", width='stretch'):
            # Check if we have enough information
            has_info = any([
                project_info.get('name'),
                project_info.get('goals'),
                project_info.get('problem')
            ])
            
            if not has_info:
                st.error(
                    "Fill in at least the name, goals or problem description "
                    "to generate stages"
                )
                return False
            
            with st.spinner("Analyzing project and generating stages..."):
                # Get risks from session state if available
                risks = st.session_state.get('risks_list', [])
                
                new_stages = generate_stages_from_project(
                    name=project_info.get('name', ''),
                    goals=project_info.get('goals', ''),
                    problem=project_info.get('problem', ''),
                    hypothesis=project_info.get('hypothesis', ''),
                    success_criteria=project_info.get('success_criteria', ''),
                    must_have=project_info.get('must_have', []),
                    nice_to_have=project_info.get('nice_to_have', []),
                    risks=risks
                )
                
                if new_stages:
                    # Calculate cumulative dates from today
                    from datetime import date, timedelta
                    
                    current_risks = st.session_state.get(stages_list_key, [])
                    
                    # Convert AI stages to full stage objects
                    start_date = date.today()
                    cumulative_days = 0
                    
                    for stage in new_stages:
                        duration = stage.get('duration_days', 7)
                        expected_date = start_date + timedelta(days=cumulative_days + duration)
                        
                        current_risks.append({
                            "name": stage.get('name', ''),
                            "description": stage.get('description', ''),
                            "risk_text": stage.get('risk_text', ''),
                            "risk_description": stage.get('risk_description', ''),
                            "risk_realization_date": None,
                            "expected_date": expected_date,
                            "actual_date": None,
                            "status": "PLANNED",
                            "comment": ""
                        })
                        
                        cumulative_days += duration
                    
                    st.session_state[stages_list_key] = current_risks
                    st.success(f"Generated {len(new_stages)} stages!")
                    st.rerun()
                    return True
                else:
                    st.error("Failed to generate stages. Please try again.")
                    return False
    
    return False