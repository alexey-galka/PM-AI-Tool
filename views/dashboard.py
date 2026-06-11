import streamlit as st
from database.models.projects import get_all_projects, get_project_full
from database.models.stages import get_next_milestone
from services.notifications_service import get_overdue_stages


def show_dashboard():
    st.header("Project dashboard")
    projects = get_all_projects()

    if not projects:
        st.info("No projects. Create your first project via the sidebar menu")
        return

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "PLANNING", "ACTIVE", "COMPLETED", "CANCELLED"]
        )
    with col2:
        search = st.text_input("Search by name", "")

    filtered_projects = []
    for p in projects:
        if status_filter != "All" and p['status'] != status_filter:
            continue
        if search and search.lower() not in p['name'].lower():
            continue
        filtered_projects.append(p)

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("In planning", sum(
            1 for p in filtered_projects if p['status'] == 'PLANNING'))
    with col2:
        st.metric("Active", sum(
            1 for p in filtered_projects if p['status'] == 'ACTIVE'))
    with col3:
        st.metric("Completed", sum(
            1 for p in filtered_projects if p['status'] == 'COMPLETED'))
    with col4:
        st.metric("Cancelled", sum(
            1 for p in filtered_projects if p['status'] == 'CANCELLED'))

    st.divider()

    for p in filtered_projects:
        full_project = get_project_full(p['id'])
        overdue = get_overdue_stages(full_project)
        has_overdue = len(overdue) > 0

        next_stage = get_next_milestone(p['id'])
        milestone_text = f"{next_stage['name']} ({next_stage['expected_date']})" if next_stage else "—"

        status_emoji = {'PLANNING': '🟡', 'ACTIVE': '🔵',
                        'COMPLETED': '🟢', 'CANCELLED': '🔴'}.get(p['status'], '⚪')

        if has_overdue:
            title = f"{status_emoji} {p['name']} ⚠️"
        else:
            title = f"{status_emoji} {p['name']}"

        with st.expander(title):
            if has_overdue:
                st.error(f"Overdue stages ({len(overdue)}):")
                for o in overdue:
                    st.write(
                        f"  - {o['stage_name']} (overdue by: {o['days_overdue']} days)")

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Goals:** {p['goals'] or '—'}")
                st.write(f"**Next milestone:** {milestone_text}")
            with col2:
                st.write(f"**Planned date:** {p['end_date'] or '—'}")
                st.write(f"**Status:** {p['status']}")
            with col3:
                st.write(
                    f"**Created:** {p.get('created_at', '—')[:10] if p.get('created_at') else '—'}")
                if st.button("Open project", key=f"open_{p['id']}"):
                    st.session_state.current_project_id = p['id']
                    st.session_state.page = "Project"
                    st.rerun()
