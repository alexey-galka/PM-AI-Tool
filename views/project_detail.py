import streamlit as st
from database.models.projects import get_project_full
from services.helpers import render_multiline_field, render_list_field
from components.display.raci_view import render_raci
from components.display.risks_view import render_risks
from components.display.stages_view import render_stages
from components.display.materials_view import render_materials
from services.notifications_service import get_overdue_stages
from components.display.team_view import render_team
from components.dialogs.health_check import render_health_check
from components.display.communications_view import render_communications
from audio.meetings_manager import render_meetings_manager
from services.rag_service import render_rag_chat
from services.weekly_service import render_weekly_digest


def show_project_detail():
    if 'current_project_id' not in st.session_state:
        st.warning("No project selected")
        return

    project_id = st.session_state.current_project_id
    project = get_project_full(project_id)

    if not project:
        st.error("Project not found")
        return

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.header(f"{project['name']}")
    with col2:
        if st.button("Edit", width='stretch', key="edit_btn"):
            st.session_state.page = "Editing"
            st.rerun()
    with col3:
        if st.button("← Back", width='stretch', key="back_btn"):
            if 'current_project_id' in st.session_state:
                del st.session_state.current_project_id
            st.session_state.page = "Dashboard"
            st.rerun()

    overdue = get_overdue_stages(project)
    if overdue:
        days = overdue[0]['days_overdue']
        if days >= 14:
            st.error(
                f"**Critical!** Stage '{overdue[0]['stage_name']}' is overdue by {days} days")
        elif days >= 7:
            st.warning(
                f"**Warning!** Stage '{overdue[0]['stage_name']}' is overdue by {days} days")
        else:
            st.info(
                f"Stage '{overdue[0]['stage_name']}' is overdue by {days} days")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "Passport",
        "Risks",
        "Stages",
        "RACI",
        "Materials",
        "Health Check",
        "Team",
        "Communications",
        "Meetings",
        "Digest",
        "Q&A"
    ])

    # ==================== TAB 1: PROJECT PASSPORT ====================
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Basic information")
            st.write(f"**Status:** {project.get('status', '—')}")
            st.write(f"**Start date:** {project.get('start_date', '—')}")
            st.write(f"**End date:** {project.get('end_date', '—')}")
            st.write(
                f"**Actual date:** {project.get('actual_end_date', '—')}")
            st.write(
                f"**Related projects:** {', '.join(project.get('related_projects', [])) or '—'}")
            render_multiline_field("Replanning", project.get('replaning', ''))

            st.divider()

            st.subheader("Goals and results")
            render_multiline_field("Goals", project.get('goals', ''))
            render_multiline_field("Key results",
                                   project.get('key_results', ''))

            st.divider()

            st.subheader("Stakeholders")
            stakeholders = project.get('stakeholders', [])
            if stakeholders:
                for s in stakeholders:
                    st.write(f"- {s}")
            else:
                st.write("—")

        with col2:
            st.subheader("Problem description")
            render_multiline_field("Problem", project.get('problem', ''))
            render_multiline_field("Hypothesis", project.get('hypothesis', ''))
            render_multiline_field(
                "Success criteria", project.get('success_criteria', ''))

            st.divider()

            st.subheader("Project scope")
            render_list_field("Must have", project.get('must_have', []))
            render_list_field("Nice to have", project.get('nice_to_have', []))
            render_list_field("Not in scope", project.get('not_in_scope', []))

    # ==================== TAB 2: RISKS ====================
    with tab2:
        render_risks(project)

    # ==================== TAB 3: STAGES ====================
    with tab3:
        render_stages(project)

    # ==================== TAB 4: RACI MATRIX ====================
    with tab4:
        render_raci(project)

    # ==================== TAB 5: MATERIALS AND TASKS ====================
    with tab5:
        render_materials(project)

    # ==================== TAB 6: HEALTH CHECK ====================
    with tab6:
        render_health_check(project)

    # ==================== TAB 7: TEAM ====================
    with tab7:
        render_team(project)

    # ==================== TAB 8: COMMUNICATIONS ====================
    with tab8:
        render_communications(project)

    # ==================== TAB 9: MEETINGS ====================
    with tab9:
        render_meetings_manager(project_id)

    # ==================== TAB 10: DIGEST ====================
    with tab10:
        render_weekly_digest(project)

    # ==================== TAB 11: Q&A ====================
    with tab11:
        render_rag_chat(project)


if __name__ == "__main__":
    show_project_detail()