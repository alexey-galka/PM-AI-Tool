import streamlit as st
from datetime import date, datetime


def render_stages_form(risks_list=None):
    """Render stages form with risk binding and delete functionality"""
    st.markdown("**Stages and milestones**")
    st.info("Each stage can be linked to a risk from the project risks list")

    if 'stages_list' not in st.session_state:
        st.session_state.stages_list = []

    if 'stages_to_delete' not in st.session_state:
        st.session_state.stages_to_delete = []

    # Get risks list for selection
    if risks_list is None:
        risks_list = st.session_state.get('risks_list', [])

    # Build risk options list
    risk_options = [("", "--- No risk ---")]
    for risk in risks_list:
        if risk.get('description', '').strip():
            risk_options.append((
                risk.get('description', ''),
                f"{risk.get('impact', 'MEDIUM')}: {risk.get('description', '')}"
            ))

    if not st.session_state.stages_list:
        st.info("No stages. Click 'Add stage'")
        if st.form_submit_button("Add stage", width='stretch'):
            st.session_state.stages_list.append({
                "name": "",
                "description": "",
                "risk_description": "",
                "risk_text": "",
                "risk_realization_date": None,
                "expected_date": date.today(),
                "actual_date": None,
                "status": "PLANNED",
                "comment": ""
            })
            st.session_state.stages_to_delete = [
                False] * len(st.session_state.stages_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.stages_to_delete) != len(st.session_state.stages_list):
            st.session_state.stages_to_delete = [
                False] * len(st.session_state.stages_list)

        updated_stages = []
        for i, stage in enumerate(st.session_state.stages_list):
            # Delete checkbox row
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**Milestone {i+1}**")
            with col2:
                delete_flag = st.checkbox(
                    "Delete", key=f"del_stage_check_{i}",
                    value=st.session_state.stages_to_delete[i] if i < len(
                        st.session_state.stages_to_delete) else False
                )
                if i < len(st.session_state.stages_to_delete):
                    st.session_state.stages_to_delete[i] = delete_flag
            with col3:
                st.markdown("")

            if st.session_state.stages_to_delete[i]:
                st.warning(f"Milestone {i+1} will be deleted.")
                st.divider()
                continue

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Stage", value=stage.get(
                        'name', ''), key=f"stage_name_{i}")
                    description = st.text_area("Description", value=stage.get(
                        'description', ''), key=f"stage_desc_{i}", height=68)

                    current_risk_desc = stage.get('risk_description', '')
                    risk_index = 0
                    for idx, (risk_desc, _) in enumerate(risk_options):
                        if risk_desc == current_risk_desc:
                            risk_index = idx
                            break

                    selected_risk = st.selectbox(
                        "Linked risk",
                        options=risk_options,
                        format_func=lambda x: x[1],
                        index=risk_index,
                        key=f"stage_risk_{i}"
                    )

                with col2:
                    expected_date = st.date_input("Expected date", value=stage.get(
                        'expected_date', date.today()), key=f"stage_expected_{i}")
                    risk_realization_date = st.date_input("Risk realization date", value=stage.get(
                        'risk_realization_date', None), key=f"stage_risk_date_{i}")
                    actual_date = st.date_input("Actual date", value=stage.get(
                        'actual_date', None), key=f"stage_actual_{i}")
                    status = st.selectbox("Status", ["PLANNED", "IN_PROGRESS", "DONE", "BLOCKED"],
                                          index=["PLANNED", "IN_PROGRESS", "DONE", "BLOCKED"].index(
                                              stage.get('status', 'PLANNED')),
                                          key=f"stage_status_{i}")
                    comment = st.text_input("Comment", value=stage.get(
                        'comment', ''), key=f"stage_comment_{i}")

                risk_description = selected_risk[0] if selected_risk[0] else ""
                risk_text = selected_risk[1] if selected_risk[1] != "--- No risk ---" else ""

                updated_stages.append({
                    "name": name,
                    "description": description,
                    "risk_description": risk_description,
                    "risk_text": risk_text,
                    "risk_realization_date": risk_realization_date.isoformat() if risk_realization_date else None,
                    "expected_date": expected_date.isoformat(),
                    "actual_date": actual_date.isoformat() if actual_date else None,
                    "status": status,
                    "comment": comment
                })
                st.divider()

        st.session_state.stages_list = updated_stages
        st.session_state.stages_to_delete = [False] * len(updated_stages)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add stage", width='stretch'):
                st.session_state.stages_list.append({
                    "name": "",
                    "description": "",
                    "risk_description": "",
                    "risk_text": "",
                    "risk_realization_date": None,
                    "expected_date": date.today(),
                    "actual_date": None,
                    "status": "PLANNED",
                    "comment": ""
                })
                st.session_state.stages_to_delete = [
                    False] * len(st.session_state.stages_list)
                st.rerun()
        with col2:
            if len(st.session_state.stages_list) > 0 and st.form_submit_button("Delete marked stages", width='stretch'):
                st.session_state.stages_list = [
                    s for i, s in enumerate(st.session_state.stages_list)
                    if i < len(st.session_state.stages_to_delete) and not st.session_state.stages_to_delete[i]
                ]
                st.session_state.stages_to_delete = [
                    False] * len(st.session_state.stages_list)
                st.rerun()

    return st.session_state.stages_list


def render_edit_stages_form(risks_list=None):
    """Render stages form for editing with delete functionality"""
    st.markdown("**Stages and milestones**")
    st.info("Each stage can be linked to a risk from the project risks list")

    if 'edit_stages_list' not in st.session_state:
        st.session_state.edit_stages_list = []

    if 'edit_stages_to_delete' not in st.session_state:
        st.session_state.edit_stages_to_delete = []

    # Get risks list for selection
    if risks_list is None:
        risks_list = st.session_state.get('edit_risks_list', [])

    # Build risk options list
    risk_options = [("", "--- No risk ---")]
    for risk in risks_list:
        if risk.get('description', '').strip():
            risk_options.append((
                risk.get('description', ''),
                f"{risk.get('impact', 'MEDIUM')}: {risk.get('description', '')}"
            ))

    if not st.session_state.edit_stages_list:
        st.info("No stages. Click 'Add stage'")
        if st.form_submit_button("Add stage", width='stretch'):
            st.session_state.edit_stages_list.append({
                "name": "",
                "description": "",
                "risk_description": "",
                "risk_text": "",
                "risk_realization_date": None,
                "expected_date": date.today(),
                "actual_date": None,
                "status": "PLANNED",
                "comment": ""
            })
            st.session_state.edit_stages_to_delete = [
                False] * len(st.session_state.edit_stages_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.edit_stages_to_delete) != len(st.session_state.edit_stages_list):
            st.session_state.edit_stages_to_delete = [
                False] * len(st.session_state.edit_stages_list)

        updated_stages = []
        for i, stage in enumerate(st.session_state.edit_stages_list):
            # Delete checkbox row
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**Milestone {i+1}**")
            with col2:
                delete_flag = st.checkbox(
                    "Delete", key=f"del_edit_stage_check_{i}",
                    value=st.session_state.edit_stages_to_delete[i] if i < len(
                        st.session_state.edit_stages_to_delete) else False
                )
                if i < len(st.session_state.edit_stages_to_delete):
                    st.session_state.edit_stages_to_delete[i] = delete_flag
            with col3:
                st.markdown("")

            if st.session_state.edit_stages_to_delete[i]:
                st.warning(f"Milestone {i+1} will be deleted.")
                st.divider()
                continue

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Stage", value=stage.get(
                        'name', ''), key=f"edit_stage_name_{i}")
                    description = st.text_area("Description", value=stage.get(
                        'description', ''), key=f"edit_stage_desc_{i}", height=68)

                    current_risk_text = stage.get('risk_text', '')
                    current_risk_desc = stage.get('risk_description', '')
                    risk_index = 0
                    for idx, (risk_desc, risk_display) in enumerate(risk_options):
                        if risk_desc == current_risk_desc or risk_display == current_risk_text:
                            risk_index = idx
                            break

                    selected_risk = st.selectbox(
                        "Linked risk",
                        options=risk_options,
                        format_func=lambda x: x[1],
                        index=risk_index,
                        key=f"edit_stage_risk_{i}"
                    )

                with col2:
                    expected_date_value = stage.get(
                        'expected_date', date.today())
                    if isinstance(expected_date_value, str):
                        expected_date_value = datetime.fromisoformat(
                            expected_date_value).date()
                    expected_date = st.date_input(
                        "Expected date", value=expected_date_value, key=f"edit_stage_expected_{i}")

                    risk_realization_date_value = stage.get(
                        'risk_realization_date', None)
                    if risk_realization_date_value and isinstance(risk_realization_date_value, str):
                        risk_realization_date_value = datetime.fromisoformat(
                            risk_realization_date_value).date()
                    risk_realization_date = st.date_input(
                        "Risk realization date", value=risk_realization_date_value, key=f"edit_stage_risk_date_{i}")

                    actual_date_value = stage.get('actual_date', None)
                    if actual_date_value and isinstance(actual_date_value, str):
                        actual_date_value = datetime.fromisoformat(
                            actual_date_value).date()
                    actual_date = st.date_input(
                        "Actual date", value=actual_date_value, key=f"edit_stage_actual_{i}")

                    status = st.selectbox("Status", ["PLANNED", "IN_PROGRESS", "DONE", "BLOCKED"],
                                          index=["PLANNED", "IN_PROGRESS", "DONE", "BLOCKED"].index(
                                              stage.get('status', 'PLANNED')),
                                          key=f"edit_stage_status_{i}")
                    comment = st.text_input("Comment", value=stage.get(
                        'comment', ''), key=f"edit_stage_comment_{i}")

                risk_description = selected_risk[0] if selected_risk[0] else ""
                risk_text = selected_risk[1] if selected_risk[1] != "--- No risk ---" else ""

                updated_stages.append({
                    "id": stage.get('id'),
                    "name": name,
                    "description": description,
                    "risk_description": risk_description,
                    "risk_text": risk_text,
                    "risk_realization_date": risk_realization_date.isoformat() if risk_realization_date else None,
                    "expected_date": expected_date.isoformat(),
                    "actual_date": actual_date.isoformat() if actual_date else None,
                    "status": status,
                    "comment": comment
                })
                st.divider()

        st.session_state.edit_stages_list = updated_stages
        st.session_state.edit_stages_to_delete = [False] * len(updated_stages)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add stage", width='stretch'):
                st.session_state.edit_stages_list.append({
                    "name": "",
                    "description": "",
                    "risk_description": "",
                    "risk_text": "",
                    "risk_realization_date": None,
                    "expected_date": date.today(),
                    "actual_date": None,
                    "status": "PLANNED",
                    "comment": ""
                })
                st.session_state.edit_stages_to_delete = [
                    False] * len(st.session_state.edit_stages_list)
                st.rerun()
        with col2:
            if len(st.session_state.edit_stages_list) > 0 and st.form_submit_button("Delete marked stages", width='stretch'):
                st.session_state.edit_stages_list = [
                    s for i, s in enumerate(st.session_state.edit_stages_list)
                    if i < len(st.session_state.edit_stages_to_delete) and not st.session_state.edit_stages_to_delete[i]
                ]
                st.session_state.edit_stages_to_delete = [
                    False] * len(st.session_state.edit_stages_list)
                st.rerun()

    return st.session_state.edit_stages_list
