import streamlit as st


def render_risks_form():
    """Render risks form with AI generation"""

    st.info("To delete a risk, check the 'Delete' checkbox next to it.")

    # Initialize risks list
    if 'risks_list' not in st.session_state:
        st.session_state.risks_list = []

    # Initialize delete flags list
    if 'risks_to_delete' not in st.session_state:
        st.session_state.risks_to_delete = []

    # If list is empty, show button to add first risk
    if not st.session_state.risks_list:
        st.info("No risks. Click 'Add risk' or 'Generate risks' above")
        if st.form_submit_button("Add risk", width='stretch'):
            st.session_state.risks_list.append({
                "impact": "MEDIUM",
                "description": "",
                "impact_on_result": "",
                "impact_on_timeline": "",
                "mitigation_plan": ""
            })
            st.session_state.risks_to_delete = [
                False] * len(st.session_state.risks_list)
            st.rerun()
    else:
        # Synchronize delete flags list
        if len(st.session_state.risks_to_delete) != len(st.session_state.risks_list):
            st.session_state.risks_to_delete = [
                False] * len(st.session_state.risks_list)

        # Create a new list for updated risks
        updated_risks = []

        for i, risk in enumerate(st.session_state.risks_list):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**Risk {i+1}**")
            with col2:
                delete_flag = st.checkbox(
                    "Delete", key=f"del_risk_check_{i}", value=st.session_state.risks_to_delete[i])
                st.session_state.risks_to_delete[i] = delete_flag
            with col3:
                st.markdown("")

            if st.session_state.risks_to_delete[i]:
                st.warning(f"Risk {i+1} will be deleted.")
                st.divider()
                continue

            col1, col2 = st.columns([1, 3])
            with col1:
                impact = st.selectbox("Impact", ["HIGH", "MEDIUM", "LOW"],
                                      key=f"risk_impact_{i}",
                                      index=["HIGH", "MEDIUM", "LOW"].index(risk.get('impact', 'MEDIUM')))
            with col2:
                description = st.text_input("Risk description", value=risk.get('description', ''),
                                            key=f"risk_desc_{i}")

            impact_on_result = st.text_input("Impact on result", value=risk.get('impact_on_result', ''),
                                             key=f"risk_result_{i}")
            impact_on_timeline = st.text_input("Impact on timeline", value=risk.get('impact_on_timeline', ''),
                                               key=f"risk_timeline_{i}")
            mitigation = st.text_area("Mitigation plan", value=risk.get('mitigation_plan', ''),
                                      key=f"risk_mitigation_{i}", height=68)

            # Save updated risk
            updated_risks.append({
                "impact": impact,
                "description": description,
                "impact_on_result": impact_on_result,
                "impact_on_timeline": impact_on_timeline,
                "mitigation_plan": mitigation
            })
            st.divider()

        # Update risks list in session state
        st.session_state.risks_list = updated_risks

        # Risk management buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add risk", width='stretch'):
                st.session_state.risks_list.append({
                    "impact": "MEDIUM",
                    "description": "",
                    "impact_on_result": "",
                    "impact_on_timeline": "",
                    "mitigation_plan": ""
                })
                st.session_state.risks_to_delete = [
                    False] * len(st.session_state.risks_list)
                st.rerun()
        with col2:
            if st.form_submit_button("Delete marked risks", width='stretch'):
                # Delete marked risks
                new_risks = []
                for i, risk in enumerate(st.session_state.risks_list):
                    if i < len(st.session_state.risks_to_delete) and not st.session_state.risks_to_delete[i]:
                        new_risks.append(risk)
                st.session_state.risks_list = new_risks
                st.session_state.risks_to_delete = [
                    False] * len(st.session_state.risks_list)
                st.rerun()

    return st.session_state.risks_list


def render_edit_risks_form():
    """Render risks form for editing"""

    st.info("To delete a risk, check the 'Delete' checkbox next to it.")

    # Initialize risks list
    if 'edit_risks_list' not in st.session_state:
        st.session_state.edit_risks_list = []

    # Initialize delete flags list
    if 'edit_risks_to_delete' not in st.session_state:
        st.session_state.edit_risks_to_delete = []

    # If list is empty, show button to add first risk
    if not st.session_state.edit_risks_list:
        st.info("No risks. Click 'Add risk' or 'Generate risks' above")
        if st.form_submit_button("Add risk", width='stretch'):
            st.session_state.edit_risks_list.append({
                "impact": "MEDIUM",
                "description": "",
                "impact_on_result": "",
                "impact_on_timeline": "",
                "mitigation_plan": ""
            })
            st.session_state.edit_risks_to_delete = [
                False] * len(st.session_state.edit_risks_list)
            st.rerun()
    else:
        # Synchronize delete flags list
        if len(st.session_state.edit_risks_to_delete) != len(st.session_state.edit_risks_list):
            st.session_state.edit_risks_to_delete = [
                False] * len(st.session_state.edit_risks_list)

        # Create a new list for updated risks
        updated_risks = []

        for i, risk in enumerate(st.session_state.edit_risks_list):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**Risk {i+1}**")
            with col2:
                delete_flag = st.checkbox(
                    "Delete", key=f"edit_del_risk_check_{i}", value=st.session_state.edit_risks_to_delete[i])
                st.session_state.edit_risks_to_delete[i] = delete_flag
            with col3:
                st.markdown("")

            if st.session_state.edit_risks_to_delete[i]:
                st.warning(f"Risk {i+1} will be deleted.")
                st.divider()
                continue

            col1, col2 = st.columns([1, 3])
            with col1:
                impact = st.selectbox("Impact", ["HIGH", "MEDIUM", "LOW"],
                                      key=f"edit_risk_impact_{i}",
                                      index=["HIGH", "MEDIUM", "LOW"].index(risk.get('impact', 'MEDIUM')))
            with col2:
                description = st.text_input("Risk description", value=risk.get('description', ''),
                                            key=f"edit_risk_desc_{i}")

            impact_on_result = st.text_input("Impact on result", value=risk.get('impact_on_result', ''),
                                             key=f"edit_risk_result_{i}")
            impact_on_timeline = st.text_input("Impact on timeline", value=risk.get('impact_on_timeline', ''),
                                               key=f"edit_risk_timeline_{i}")
            mitigation = st.text_area("Mitigation plan", value=risk.get('mitigation_plan', ''),
                                      key=f"edit_risk_mitigation_{i}", height=68)

            # Save updated risk
            updated_risks.append({
                "impact": impact,
                "description": description,
                "impact_on_result": impact_on_result,
                "impact_on_timeline": impact_on_timeline,
                "mitigation_plan": mitigation
            })
            st.divider()

        # Update risks list in session state
        st.session_state.edit_risks_list = updated_risks

        # Risk management buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add risk", width='stretch'):
                st.session_state.edit_risks_list.append({
                    "impact": "MEDIUM",
                    "description": "",
                    "impact_on_result": "",
                    "impact_on_timeline": "",
                    "mitigation_plan": ""
                })
                st.session_state.edit_risks_to_delete = [
                    False] * len(st.session_state.edit_risks_list)
                st.rerun()
        with col2:
            if st.form_submit_button("Delete marked risks", width='stretch'):
                # Delete marked risks
                new_risks = []
                for i, risk in enumerate(st.session_state.edit_risks_list):
                    if i < len(st.session_state.edit_risks_to_delete) and not st.session_state.edit_risks_to_delete[i]:
                        new_risks.append(risk)
                st.session_state.edit_risks_list = new_risks
                st.session_state.edit_risks_to_delete = [
                    False] * len(st.session_state.edit_risks_list)
                st.rerun()

    return st.session_state.edit_risks_list
