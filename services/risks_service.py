from services.ai_service import call_ollama
import json
import re
import streamlit as st


def generate_risks_from_description(problem, hypothesis, success_criteria):
    """Generate risks based on problem description"""

    prompt = f"""You are an IT project management expert in a bank.
Generate 3-4 specific risks for the project.

Project data:
- Problem: {problem}
- Hypothesis: {hypothesis}
- Success criteria: {success_criteria}

For each risk, specify the fields:
- impact: HIGH, MEDIUM or LOW
- description: risk description (brief)
- impact_on_result: impact on the result
- impact_on_timeline: impact on timeline
- mitigation_plan: mitigation plan

Return ONLY a JSON array. Each risk must be a separate object in the array. ALL fields must be specified.
Example:
[
  {{"impact": "HIGH", "description": "text", "impact_on_result": "text", "impact_on_timeline": "text", "mitigation_plan": "text"}},
  {{"impact": "MEDIUM", "description": "text", "impact_on_result": "text", "impact_on_timeline": "text", "mitigation_plan": "text"}}
]

Do not add any other words, only the JSON array.
"""

    response = call_ollama(prompt)

    # Clean response from control characters
    response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response)
    response = re.sub(r'[\x00-\x1f\x7f]', '', response)

    # Save for debugging
    st.session_state['debug_raw_response'] = response

    # Try to extract JSON
    risks = extract_risks_from_response(response)

    if risks is None:
        st.session_state['debug_error'] = "Failed to extract risks"
        st.error("Failed to generate risks. Please try again.")
        return None

    # Validation
    validated_risks = []
    for risk in risks:
        if isinstance(risk, dict):
            # Skip empty ones
            if not risk.get('description') or len(risk.get('description', '')) < 5:
                continue

            validated_risks.append({
                "impact": risk.get('impact', 'MEDIUM').upper(),
                "description": risk.get('description', '')[:200],
                "impact_on_result": risk.get('impact_on_result', '')[:200],
                "impact_on_timeline": risk.get('impact_on_timeline', '')[:200],
                "mitigation_plan": risk.get('mitigation_plan', '')[:200]
            })

    if not validated_risks:
        st.error("Failed to extract risks. Please try again.")
        return None

    st.session_state['debug_parsed_risks'] = validated_risks
    st.session_state['debug_risks_count'] = len(validated_risks)

    return validated_risks


def extract_risks_from_response(text):
    """Extract JSON risks from response"""

    # Method 1: Try to find JSON array
    try:
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            json_str = match.group()
            result = json.loads(json_str)
            if isinstance(result, list):
                return result
    except:
        pass

    # Method 2: Split by pattern "}{" (merged objects)
    try:
        # Add commas between objects
        fixed = re.sub(r'\}\s*\{', '},{', text)
        # Wrap in array
        if fixed.startswith('{'):
            fixed = '[' + fixed + ']'
        result = json.loads(fixed)
        if isinstance(result, list):
            return result
    except:
        pass

    # Method 3: Look for individual JSON objects
    try:
        objects = re.findall(r'\{[^{}]*\}', text)
        risks = []
        for obj_str in objects:
            try:
                risk = json.loads(obj_str)
                if isinstance(risk, dict) and 'impact' in risk:
                    risks.append(risk)
            except:
                continue
        if risks:
            return risks
    except:
        pass

    return None


def render_ai_risks_button(problem, hypothesis, success_criteria, risks_list_key, on_success_callback=None):
    """Render button for generating risks via AI"""

    col_ai, col_empty = st.columns([1, 1])
    with col_ai:
        if st.form_submit_button("Generate risks", width='stretch'):
            if not problem and not hypothesis and not success_criteria:
                st.error(
                    "Fill in at least one of the fields: Problem, Hypothesis or Success criteria")
                return False

            with st.spinner("Analyzing project description and generating risks..."):
                new_risks = generate_risks_from_description(
                    problem or "not specified",
                    hypothesis or "not specified",
                    success_criteria or "not specified"
                )

                # Debug
                if new_risks:
                    st.info(f"Received {len(new_risks)} risks")
                    for i, risk in enumerate(new_risks):
                        st.write(
                            f"  Risk {i+1}: {risk.get('impact')} - {risk.get('description', '')[:50]}...")

                if new_risks is None or len(new_risks) == 0:
                    st.error(
                        "Failed to generate risks. Please try again.")
                    if st.session_state.get('debug_raw_response'):
                        with st.expander("🔧 Technical information"):
                            st.code(st.session_state.debug_raw_response[:500])
                    return False

                # Get current list of risks
                current_risks = st.session_state.get(risks_list_key, [])
                current_risks = [r for r in current_risks if r.get(
                    'description', '').strip()]

                # Add new risks
                for risk in new_risks:
                    current_risks.append({
                        "impact": risk.get('impact', 'MEDIUM'),
                        "description": risk.get('description', ''),
                        "impact_on_result": risk.get('impact_on_result', ''),
                        "impact_on_timeline": risk.get('impact_on_timeline', ''),
                        "mitigation_plan": risk.get('mitigation_plan', '')
                    })

                st.session_state[risks_list_key] = current_risks
                st.success(f"Added {len(new_risks)} risks!")

                if on_success_callback:
                    on_success_callback()

                st.rerun()
                return True
    return False
