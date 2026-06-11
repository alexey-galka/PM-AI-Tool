import streamlit as st


def render_project_scope(defaults=None):
    if defaults is None:
        defaults = {}

    # Get lists from defaults
    must_have_list = defaults.get('must_have', [])
    nice_to_have_list = defaults.get('nice_to_have', [])
    not_in_scope_list = defaults.get('not_in_scope', [])

    # Convert lists to text with line breaks
    must_have_default = "\n".join(must_have_list) if must_have_list else ""
    nice_to_have_default = "\n".join(
        nice_to_have_list) if nice_to_have_list else ""
    not_in_scope_default = "\n".join(
        not_in_scope_list) if not_in_scope_list else ""

    with st.expander("Project scope", expanded=True):
        must_have = st.text_area(
            "Must have",
            value=st.session_state.get('must_have_area', must_have_default),
            height=120,
            key="must_have_area"
        )
        nice_to_have = st.text_area(
            "Nice to have",
            value=st.session_state.get(
                'nice_to_have_area', nice_to_have_default),
            height=100,
            key="nice_to_have_area"
        )
        not_in_scope = st.text_area(
            "Not in scope",
            value=st.session_state.get(
                'not_in_scope_area', not_in_scope_default),
            height=100,
            key="not_in_scope_area"
        )

    return {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "not_in_scope": not_in_scope
    }


def render_edit_project_scope(project):
    """Render project scope for editing"""
    with st.expander("Project scope", expanded=True):
        must_have_text = "\n".join(project.get(
            'must_have', [])) if project.get('must_have') else ""
        must_have = st.text_area("Must have", value=must_have_text, height=120)

        nice_to_have_text = "\n".join(project.get(
            'nice_to_have', [])) if project.get('nice_to_have') else ""
        nice_to_have = st.text_area(
            "Nice to have", value=nice_to_have_text, height=100)

        not_in_scope_text = "\n".join(project.get(
            'not_in_scope', [])) if project.get('not_in_scope') else ""
        not_in_scope = st.text_area(
            "Not in scope", value=not_in_scope_text, height=100)

    return {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "not_in_scope": not_in_scope
    }