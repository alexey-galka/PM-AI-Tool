import streamlit as st
from database.models.projects import create_project
from components.forms.basic_info import render_basic_info
from components.forms.problem_description_form import render_problem_description
from components.forms.project_scope_form import render_project_scope
from components.forms.risks_form import render_risks_form
from components.forms.stages_form import render_stages_form
from components.forms.raci_form import render_raci_form
from components.forms.team_form import render_team_form
from components.forms.communications_form import render_communications_form
from components.forms.materials_form import render_materials_form
from components.dialogs.audio_upload import render_audio_upload
from services.risks_service import render_ai_risks_button


def show_new_project():
    st.header("Create new project")

    audio_data = render_audio_upload()

    if audio_data:
        basic_defaults = {
            'name': audio_data.get('name', ''),
            'goals': audio_data.get('goals', ''),
            'key_results': audio_data.get('key_results', ''),
            'problem': audio_data.get('problem', ''),
            'hypothesis': audio_data.get('hypothesis', ''),
            'success_criteria': audio_data.get('success_criteria', ''),
            'must_have': audio_data.get('must_have', []),
            'nice_to_have': audio_data.get('nice_to_have', []),
            'not_in_scope': audio_data.get('not_in_scope', [])
        }

        st.session_state.project_name = basic_defaults.get('name', '')
        st.session_state.project_goals = basic_defaults.get('goals', '')
        st.session_state.key_results = basic_defaults.get('key_results', '')
        st.session_state.problem_desc = basic_defaults.get('problem', '')
        st.session_state.hypothesis_desc = basic_defaults.get('hypothesis', '')
        st.session_state.success_criteria_desc = basic_defaults.get(
            'success_criteria', '')

        must_have_list = basic_defaults.get('must_have', [])
        st.session_state.must_have_area = "\n".join(
            must_have_list) if must_have_list else ""

        nice_to_have_list = basic_defaults.get('nice_to_have', [])
        st.session_state.nice_to_have_area = "\n".join(
            nice_to_have_list) if nice_to_have_list else ""

        not_in_scope_list = basic_defaults.get('not_in_scope', [])
        st.session_state.not_in_scope_area = "\n".join(
            not_in_scope_list) if not_in_scope_list else ""

        if st.session_state.get('apply_audio_data'):
            st.session_state.apply_audio_data = False
    else:
        basic_defaults = {}

    with st.form("new_project_form", clear_on_submit=False):
        # ==================== 1. BASIC INFORMATION ====================
        basic_info = render_basic_info(basic_defaults)

        # ==================== 2. PROBLEM DESCRIPTION ====================
        problem_desc = render_problem_description(basic_defaults)

        # ==================== 3. PROJECT SCOPE ====================
        project_scope = render_project_scope(basic_defaults)

        # ==================== 4. RISKS ====================
        with st.expander("Risks", expanded=False):
            render_ai_risks_button(
                problem=problem_desc['problem'],
                hypothesis=problem_desc['hypothesis'],
                success_criteria=problem_desc['success_criteria'],
                risks_list_key='risks_list'
            )

            risks = render_risks_form()

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

            render_ai_stages_button(project_info_for_stages, 'stages_list')

            current_risks = st.session_state.get('risks_list', [])
            stages = render_stages_form(current_risks)

        # ==================== 6. RACI MATRIX ====================
        with st.expander("RACI Matrix", expanded=False):
            from services.raci_service import render_ai_raci_button, preview_raci_matrix
            # Prepare project info for RACI generation
            project_info_for_raci = {
                'name': basic_info['name'],
                'goals': basic_info['goals'],
                'stages': st.session_state.get('stages_list', []),
                'team': st.session_state.get('team_list', [])
            }
            render_ai_raci_button(project_info_for_raci, 'raci_list')
            
            raci = render_raci_form()
            
            # Preview RACI matrix after the form
            st.divider()
            preview_raci_matrix(st.session_state.get('raci_list', []))
        # ==================== 7. PROJECT TEAM ====================
        with st.expander("Project team", expanded=False):
            team = render_team_form()

        # ==================== 8. COMMUNICATIONS ====================
        with st.expander("Communications (meeting plan)", expanded=False):
            communications = render_communications_form()

        # ==================== 9. ADDITIONAL MATERIALS ====================
        with st.expander("Additional materials", expanded=False):
            from services.tasks_service import render_ai_tasks_button

            project_info_for_tasks = {
                'name': basic_info['name'],
                'goals': basic_info['goals'],
                'problem': problem_desc['problem'],
                'success_criteria': problem_desc['success_criteria'],
                'stages': st.session_state.get('stages_list', []),
                'must_have': [m.strip() for m in project_scope['must_have'].split('\n') if m.strip()] if project_scope['must_have'] else []
            }
            render_ai_tasks_button(project_info_for_tasks, 'tasks_list')

            articles, tasks = render_materials_form()

        # ==================== SAVE BUTTON ====================
        st.divider()
        submitted = st.form_submit_button(
            "Create project", type="primary", width='stretch')

        if submitted:
            if not basic_info['name']:
                st.error("Project name is required!")
            else:
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
                            "impact": r.get('impact', 'MEDIUM'),
                            "description": r.get('description', ''),
                            "impact_on_result": r.get('impact_on_result', ''),
                            "impact_on_timeline": r.get('impact_on_timeline', ''),
                            "mitigation_plan": r.get('mitigation', '')
                        }
                        for r in st.session_state.get('risks_list', [])
                        if r.get('description', '').strip()
                    ],
                    "stages": [
                        {
                            "name": s.get('name'),
                            "description": s.get('description'),
                            "risk_text": s.get('risk_text', ''),
                            "risk_description": s.get('risk_description', ''),
                            "risk_realization_date": s.get('risk_realization_date').isoformat() if hasattr(s.get('risk_realization_date'), 'isoformat') else s.get('risk_realization_date'),
                            "expected_date": s.get('expected_date').isoformat() if hasattr(s.get('expected_date'), 'isoformat') else s.get('expected_date'),
                            "actual_date": s.get('actual_date').isoformat() if hasattr(s.get('actual_date'), 'isoformat') else s.get('actual_date'),
                            "status": s.get('status'),
                            "comment": s.get('comment')
                        }
                        for s in st.session_state.get('stages_list', [])
                        if s.get('name', '').strip()
                    ],
                    "raci": [
                        {
                            "artifact_name": r.get('artifact', ''),
                            "role_name": r.get('role', ''),
                            "raci_code": r.get('code', 'R')
                        }
                        for r in st.session_state.get('raci_list', [])
                        if r.get('artifact', '').strip() and r.get('role', '').strip()
                    ],
                    "team": [
                        {
                            "name": m.get('name'),
                            "role": m.get('role')
                        }
                        for m in st.session_state.get('team_list', [])
                        if m.get('name', '').strip()
                    ],
                    "communications": [
                        {
                            "name": c.get('name'),
                            "frequency": c.get('frequency'),
                            "time": c.get('time').strftime("%H:%M") if hasattr(c.get('time'), 'strftime') else c.get('time'),
                            "duration": c.get('duration'),
                            "description": c.get('description'),
                            "location": c.get('location'),
                            "link": c.get('link')
                        }
                        for c in st.session_state.get('communications_list', [])
                        if c.get('name', '').strip()
                    ],
                    "articles": [a for a in st.session_state.get('articles_list', []) if a.get('title', '').strip()],
                    "tasks": [t for t in st.session_state.get('tasks_list', []) if t.get('title', '').strip()]
                }

                project_id = create_project(project_data)

                st.success(
                    f"Project '{basic_info['name']}' successfully created!")
                st.balloons()

                # Clear session state
                for key in ['risks_list', 'risks_to_delete', 'stages_list', 'raci_list',
                            'team_list', 'communications_list', 'articles_list', 'tasks_list',
                            'audio_extracted_data', 'apply_audio_data',
                            'project_name', 'project_goals', 'key_results',
                            'problem_desc', 'hypothesis_desc', 'success_criteria_desc',
                            'must_have_area', 'nice_to_have_area', 'not_in_scope_area']:
                    if key in st.session_state:
                        del st.session_state[key]

                st.session_state.current_project_id = project_id
                st.session_state.page = "Project"
                st.rerun()


if __name__ == "__main__":
    show_new_project()
