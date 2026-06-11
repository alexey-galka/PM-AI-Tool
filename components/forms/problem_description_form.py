import streamlit as st


def render_problem_description(defaults=None):
    if defaults is None:
        defaults = {}

    with st.expander("Problem description", expanded=True):
        problem = st.text_area(
            "Problem",
            value=st.session_state.get(
                'problem_desc', defaults.get('problem', '')),
            height=100,
            key="problem_desc"
        )
        hypothesis = st.text_area(
            "Hypothesis",
            value=st.session_state.get(
                'hypothesis_desc', defaults.get('hypothesis', '')),
            height=100,
            key="hypothesis_desc"
        )
        success_criteria = st.text_area(
            "Success criteria",
            value=st.session_state.get(
                'success_criteria_desc', defaults.get('success_criteria', '')),
            height=100,
            key="success_criteria_desc"
        )

    return {
        "problem": problem,
        "hypothesis": hypothesis,
        "success_criteria": success_criteria
    }


def render_edit_problem_description(project):
    """Render problem description for editing"""
    with st.expander("Problem description", expanded=True):
        problem = st.text_area(
            "Problem", value=project.get('problem', ''), height=100)
        hypothesis = st.text_area(
            "Hypothesis", value=project.get('hypothesis', ''), height=100)
        success_criteria = st.text_area(
            "Success criteria", value=project.get('success_criteria', ''), height=100)

    return {
        "problem": problem,
        "hypothesis": hypothesis,
        "success_criteria": success_criteria
    }