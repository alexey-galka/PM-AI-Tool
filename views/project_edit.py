import streamlit as st
from datetime import datetime
from database.models.projects import get_project_full, update_project_full
from components.forms.basic_info import render_edit_basic_info
from components.forms.problem_description_form import render_edit_problem_description
from components.forms.project_scope_form import render_edit_project_scope
from components.forms.risks_form import render_edit_risks_form
from components.forms.raci_form import render_edit_raci_form
from components.forms.materials_form import render_edit_materials_form
from components.forms.team_form import render_edit_team_form
from components.forms.communications_form import render_edit_communications_form
from components.forms.stages_form import render_edit_stages_form
from services.risks_service import render_ai_risks_button
from database.models.projects import delete_project
from services.raci_service import render_ai_raci_button
from services.tasks_service import render_ai_tasks_button


def show_edit_project():
    st.header("Edit project")

    if 'current_project_id' not in st.session_state:
        st.error("No project selected")
        if st.button("← Back to dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    project_id = st.session_state.current_project_id
    project = get_project_full(project_id)

    if not project:
        st.error("Project not found")
        if st.button("← Back to dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    # ==================== SESSION STATE INITIALIZATION ====================
    # Load project data ONLY if not already loaded
    if 'edit_risks_loaded' not in st.session_state:
        risks = project.get('risks', [])
        if risks:
            st.session_state.edit_risks_list = risks
        else:
            st.session_state.edit_risks_list = []
        st.session_state.edit_risks_loaded = True

    if 'edit_stages_loaded' not in st.session_state:
        stages = project.get('stages', [])
        if stages:
            # Convert dates from strings to date objects and save risk_text
            stages_converted = []
            for s in stages:
                s_copy = s.copy()
                if isinstance(s_copy.get('expected_date'), str):
                    s_copy['expected_date'] = datetime.fromisoformat(
                        s_copy['expected_date']).date()
                # Save risk_text and risk_description if they exist
                s_copy['risk_text'] = s.get('risk_text', '')
                s_copy['risk_description'] = s.get('risk_description', '')
                stages_converted.append(s_copy)
            st.session_state.edit_stages_list = stages_converted
        else:
            st.session_state.edit_stages_list = []
        st.session_state.edit_stages_loaded = True

    if 'edit_raci_loaded' not in st.session_state:
        raci = project.get('raci', [])
        if raci:
            st.session_state.edit_raci_list = []
            for r in raci:
                st.session_state.edit_raci_list.append({
                    "artifact": r.get('artifact_name', ''),
                    "role": r.get('role_name', ''),
                    "code": r.get('raci_code', 'R')
                })
        else:
            st.session_state.edit_raci_list = []
        st.session_state.edit_raci_loaded = True

    if 'edit_articles_loaded' not in st.session_state:
        articles = project.get('articles', [])
        if articles:
            st.session_state.edit_articles_list = articles
        else:
            st.session_state.edit_articles_list = []
        st.session_state.edit_articles_loaded = True

    if 'edit_tasks_loaded' not in st.session_state:
        tasks = project.get('tasks', [])
        if tasks:
            st.session_state.edit_tasks_list = tasks
        else:
            st.session_state.edit_tasks_list = []
        st.session_state.edit_tasks_loaded = True

    if 'edit_team_loaded' not in st.session_state:
        team = project.get('team', [])
        if team:
            st.session_state.edit_team_list = team
        else:
            st.session_state.edit_team_list = []
        st.session_state.edit_team_loaded = True

    if 'edit_communications_loaded' not in st.session_state:
        comms = project.get('communications', [])
        if comms:
            comms_converted = []
            for c in comms:
                c_copy = c.copy()
                if isinstance(c_copy.get('time'), str):
                    try:
                        c_copy['time'] = datetime.strptime(
                            c_copy['time'], "%H:%M").time()
                    except:
                        c_copy['time'] = datetime.strptime(
                            "10:00", "%H:%M").time()
                comms_converted.append(c_copy)
            st.session_state.edit_communications_list = comms_converted
        else:
            st.session_state.edit_communications_list = []
        st.session_state.edit_communications_loaded = True

    # ==================== DELETE BUTTON ====================
    col1, col2 = st.columns([5, 1])
    with col1:
        st.write(f"Project: **{project['name']}**")
    with col2:
        if st.button("Delete project", width='stretch', type="secondary"):
            st.session_state.show_delete_confirmation = True
            st.rerun()

    # Delete confirmation dialog
    if st.session_state.get('show_delete_confirmation', False):
        st.warning("WARNING: Project will be permanently deleted!")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(
                f"Are you sure you want to delete project **'{project['name']}'**?")
        with col2:
            if st.button("Delete", width='stretch'):
                if delete_project(project_id):
                    st.success(
                        f"Project '{project['name']}' successfully deleted!")
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        if key.startswith('edit_') or key == 'current_project_id' or key == 'show_delete_confirmation':
                            del st.session_state[key]
                    st.session_state.page = "Dashboard"
                    st.rerun()
                else:
                    st.error("Error deleting project")
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
        with col3:
            if st.button("Cancel", width='stretch'):
                st.session_state.show_delete_confirmation = False
                st.rerun()
        st.divider()

    with st.form("edit_project_form", clear_on_submit=False):
        # ==================== 1. BASIC INFORMATION ====================
        basic_info = render_edit_basic_info(project)

        # ==================== 2. PROBLEM DESCRIPTION ====================
        problem_desc = render_edit_problem_description(project)

        # ==================== 3. PROJECT SCOPE ====================
        project_scope = render_edit_project_scope(project)

        # ==================== 4. RISKS ====================
        with st.expander("Risks", expanded=False):
            render_ai_risks_button(
                problem=problem_desc['problem'],
                hypothesis=problem_desc['hypothesis'],
                success_criteria=problem_desc['success_criteria'],
                risks_list_key='edit_risks_list'
            )
            risks = render_edit_risks_form()

        # ==================== 5. STAGES AND DEADLINES ====================
        with st.expander("Stages and deadlines", expanded=False):
            # Add AI generation button for stages
            from services.stages_service import render_ai_stages_button

            # Prepare project info for stage generation
            project_info_for_stages = {
                'name': basic_info['name'],
                'goals': basic_info['goals'],
                'problem': problem_desc['problem'],
                'hypothesis': problem_desc['hypothesis'],
                'success_criteria': problem_desc['success_criteria'],
                'must_have': [m.strip() for m in project_scope['must_have'].split('\n') if m.strip()] if project_scope['must_have'] else [],
                'nice_to_have': [n.strip() for n in project_scope['nice_to_have'].split('\n') if n.strip()] if project_scope['nice_to_have'] else [],
            }

            render_ai_stages_button(
                project_info_for_stages, 'edit_stages_list')

            current_risks = st.session_state.get('edit_risks_list', [])
            stages = render_edit_stages_form(current_risks)

        # ==================== 6. RACI MATRIX ====================
        with st.expander("RACI Matrix", expanded=False):
            from services.raci_service import preview_raci_matrix
            # Prepare project info for RACI generation
            project_info_for_raci = {
                'name': basic_info['name'],
                'goals': basic_info['goals'],
                'stages': st.session_state.get('edit_stages_list', []),
                'team': st.session_state.get('edit_team_list', [])
            }
            render_ai_raci_button(project_info_for_raci, 'edit_raci_list')
            
            raci = render_edit_raci_form()
            
            # Preview RACI matrix after the form
            st.divider()
            preview_raci_matrix(st.session_state.get('edit_raci_list', []))

        # ==================== 7. PROJECT TEAM ====================
        with st.expander("Project team", expanded=False):
            team = render_edit_team_form()

        # ==================== 8. COMMUNICATIONS ====================
        with st.expander("Communications plan", expanded=False):
            communications = render_edit_communications_form()

        # ==================== 9. ADDITIONAL MATERIALS ====================
        with st.expander("Additional materials", expanded=False):
            # Prepare project info for tasks generation
            project_info_for_tasks = {
                'name': basic_info['name'],
                'goals': basic_info['goals'],
                'problem': problem_desc['problem'],
                'success_criteria': problem_desc['success_criteria'],
                'stages': st.session_state.get('edit_stages_list', []),
                'must_have': [m.strip() for m in project_scope['must_have'].split('\n') if m.strip()] if project_scope['must_have'] else []
            }
            render_ai_tasks_button(project_info_for_tasks, 'edit_tasks_list')
            
            articles, tasks = render_edit_materials_form()

        # ==================== FORM BUTTONS ====================
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Save changes", type="primary", width='stretch')
        with col2:
            cancelled = st.form_submit_button(
                "Cancel", width='stretch')

        if submitted:
            if not basic_info['name']:
                st.error("Project name is required!")
            else:
                # Collect data
                project_data = {
                    "name": basic_info['name'],
                    "status": basic_info['status'],
                    "goals": basic_info['goals'],
                    "key_results": basic_info['key_results'],
                    "start_date": basic_info['start_date'].isoformat(),
                    "end_date": basic_info['end_date'].isoformat(),
                    "actual_end_date": basic_info['actual_end_date'].isoformat() if basic_info['actual_end_date'] else None,
                    "stakeholders": [s.strip() for s in basic_info['stakeholders'].split('\n') if s.strip()] if basic_info['stakeholders'] else [],
                    "related_projects": [r.strip() for r in basic_info['related_projects'].split(',') if r.strip()] if basic_info['related_projects'] else [],
                    "replaning": basic_info['replaning'],
                    "problem": problem_desc['problem'],
                    "hypothesis": problem_desc['hypothesis'],
                    "success_criteria": problem_desc['success_criteria'],
                    "must_have": [m.strip() for m in project_scope['must_have'].split('\n') if m.strip()] if project_scope['must_have'] else [],
                    "nice_to_have": [n.strip() for n in project_scope['nice_to_have'].split('\n') if n.strip()] if project_scope['nice_to_have'] else [],
                    "not_in_scope": [n.strip() for n in project_scope['not_in_scope'].split('\n') if n.strip()] if project_scope['not_in_scope'] else [],
                    "risks": [
                        {
                            "id": r.get('id'),
                            "impact": r.get('impact', 'MEDIUM'),
                            "description": r.get('description', ''),
                            "impact_on_result": r.get('impact_on_result', ''),
                            "impact_on_timeline": r.get('impact_on_timeline', ''),
                            "mitigation_plan": r.get('mitigation', '')
                        }
                        for r in st.session_state.get('edit_risks_list', [])
                        if r.get('description', '').strip()
                    ],
                    "stages": [
                        {
                            "id": s.get('id'),
                            "name": s.get('name'),
                            "description": s.get('description'),
                            "risk_text": s.get('risk_text', ''),
                            "risk_description": s.get('risk_description', ''),
                            "risk_realization_date": s.get('risk_realization_date'),
                            "expected_date": s.get('expected_date'),
                            "actual_date": s.get('actual_date'),
                            "status": s.get('status'),
                            "comment": s.get('comment')
                        }
                        for s in st.session_state.get('edit_stages_list', [])
                        if s.get('name', '').strip()
                    ],
                    "raci": [
                        {
                            "artifact_name": r.get('artifact', ''),
                            "role_name": r.get('role', ''),
                            "raci_code": r.get('code', 'R')
                        }
                        for r in st.session_state.get('edit_raci_list', [])
                        if r.get('artifact', '').strip() and r.get('role', '').strip()
                    ],
                    "team": [
                        {
                            "id": m.get('id'),
                            "name": m.get('name'),
                            "role": m.get('role')
                        }
                        for m in st.session_state.get('edit_team_list', [])
                        if m.get('name', '').strip()
                    ],
                    "communications": [
                        {
                            "id": c.get('id'),
                            "name": c.get('name'),
                            "frequency": c.get('frequency'),
                            "time": c.get('time').strftime("%H:%M") if hasattr(c.get('time'), 'strftime') else c.get('time'),
                            "duration": c.get('duration'),
                            "description": c.get('description'),
                            "location": c.get('location'),
                            "link": c.get('link')
                        }
                        for c in st.session_state.get('edit_communications_list', [])
                        if c.get('name', '').strip()
                    ],
                    "articles": [a for a in st.session_state.get('edit_articles_list', []) if a.get('title', '').strip()],
                    "tasks": [t for t in st.session_state.get('edit_tasks_list', []) if t.get('title', '').strip()]
                }

                # Save to database
                update_project_full(project_id, project_data)

                st.success(
                    f"Project '{basic_info['name']}' successfully updated!")

                # Clear loading flags
                for key in ['edit_risks_loaded', 'edit_stages_loaded', 'edit_raci_loaded',
                            'edit_articles_loaded', 'edit_tasks_loaded', 'edit_team_loaded',
                            'edit_communications_loaded']:
                    if key in st.session_state:
                        del st.session_state[key]

                st.session_state.page = "Dashboard"
                st.rerun()

        if cancelled:
            # Clear all edit_ data
            for key in list(st.session_state.keys()):
                if key.startswith('edit_') or key == 'current_project_id':
                    del st.session_state[key]
            st.session_state.page = "Dashboard"
            st.rerun()


if __name__ == "__main__":
    show_edit_project()
