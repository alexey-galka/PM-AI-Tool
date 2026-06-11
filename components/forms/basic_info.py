import streamlit as st
from datetime import date, datetime


def render_basic_info(defaults=None):
    if defaults is None:
        defaults = {}

    # Get key results (can be list or string)
    key_results = defaults.get('key_results', '')
    if isinstance(key_results, list):
        key_results = "\n".join(key_results)

    # Ensure all values are strings, not None
    name_value = st.session_state.get('project_name', defaults.get('name', ''))
    if name_value is None:
        name_value = ''

    goals_value = st.session_state.get(
        'project_goals', defaults.get('goals', ''))
    if goals_value is None:
        goals_value = ''

    key_results_value = st.session_state.get('key_results', key_results)
    if key_results_value is None:
        key_results_value = ''

    stakeholders_value = defaults.get('stakeholders', '')
    if stakeholders_value is None:
        stakeholders_value = ''
    if isinstance(stakeholders_value, list):
        stakeholders_value = "\n".join(stakeholders_value)

    related_projects_value = defaults.get('related_projects', '')
    if related_projects_value is None:
        related_projects_value = ''
    if isinstance(related_projects_value, list):
        related_projects_value = ", ".join(related_projects_value)

    replaning_value = defaults.get('replaning', '')
    if replaning_value is None:
        replaning_value = ''

    with st.expander("Basic information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Project name *",
                value=name_value,
                key="project_name"
            )
            goals = st.text_area(
                "Goals",
                value=goals_value,
                height=100,
                key="project_goals"
            )
            start_date = st.date_input(
                "Start date",
                value=date.today(),
                key="start_date"
            )
            stakeholders = st.text_area(
                "Stakeholders",
                value=stakeholders_value,
                height=100,
                key="stakeholders"
            )

        with col2:
            status = st.selectbox(
                "Status",
                ["PLANNING", "ACTIVE", "COMPLETED", "CANCELLED"],
                index=0,
                key="project_status"
            )
            key_results_area = st.text_area(
                "Key results",
                value=key_results_value,
                height=100,
                key="key_results"
            )
            end_date = st.date_input(
                "End date",
                key="end_date"
            )
            actual_end_date = st.date_input(
                "Actual end date",
                value=None,
                key="actual_end_date"
            )

        related_projects = st.text_input(
            "Related projects",
            value=related_projects_value,
            key="related_projects"
        )
        replaning = st.text_area(
            "Replanning",
            value=replaning_value,
            height=68,
            key="replaning"
        )

    return {
        "name": name,
        "goals": goals,
        "start_date": start_date,
        "stakeholders": stakeholders,
        "status": status,
        "key_results": key_results_area,
        "end_date": end_date,
        "actual_end_date": actual_end_date,
        "related_projects": related_projects,
        "replaning": replaning
    }


def render_edit_basic_info(project):
    """Render basic project information for editing"""
    # Ensure values are strings, not None
    name_value = project.get('name', '')
    if name_value is None:
        name_value = ''

    goals_value = project.get('goals', '')
    if goals_value is None:
        goals_value = ''

    key_results_value = project.get('key_results', '')
    if key_results_value is None:
        key_results_value = ''

    stakeholders_value = "\n".join(project.get(
        'stakeholders', [])) if project.get('stakeholders') else ''
    if stakeholders_value is None:
        stakeholders_value = ''

    related_projects_value = ", ".join(project.get(
        'related_projects', [])) if project.get('related_projects') else ''
    if related_projects_value is None:
        related_projects_value = ''

    replaning_value = project.get('replaning', '')
    if replaning_value is None:
        replaning_value = ''

    with st.expander("Basic information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Project name *", value=name_value)
            goals = st.text_area("Goals", value=goals_value, height=100)
            start_date = st.date_input("Start date",
                                       value=datetime.fromisoformat(project['start_date']).date() if project.get('start_date') else date.today())
            stakeholders = st.text_area(
                "Stakeholders", value=stakeholders_value, height=100)

        with col2:
            status = st.selectbox("Status", ["PLANNING", "ACTIVE", "COMPLETED", "CANCELLED"],
                                  index=["PLANNING", "ACTIVE", "COMPLETED", "CANCELLED"].index(project.get('status', 'PLANNING')))
            key_results = st.text_area(
                "Key results", value=key_results_value, height=100)
            end_date = st.date_input("End date",
                                     value=datetime.fromisoformat(project['end_date']).date() if project.get('end_date') else date.today())
            actual_end_date = st.date_input("Actual end date",
                                            value=datetime.fromisoformat(project['actual_end_date']).date() if project.get('actual_end_date') else None)

        related_projects = st.text_input(
            "Related projects", value=related_projects_value)
        replaning = st.text_area(
            "Replanning", value=replaning_value, height=68)

    return {
        "name": name,
        "goals": goals,
        "start_date": start_date,
        "stakeholders": stakeholders,
        "status": status,
        "key_results": key_results,
        "end_date": end_date,
        "actual_end_date": actual_end_date,
        "related_projects": related_projects,
        "replaning": replaning
    }
