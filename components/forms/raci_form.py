import streamlit as st


def render_raci_form():
    """Render RACI matrix form with delete functionality"""
    st.markdown("""
    **Legend:**
    - **R (Responsible)** - executes tasks
    - **A (Accountable)** - makes decisions
    - **C (Consulted)** - provides consultation
    - **I (Informed)** - receives updates
    """)

    if 'raci_list' not in st.session_state:
        st.session_state.raci_list = [
            {"artifact": "", "role": "", "code": "R"}]

    if 'raci_to_delete' not in st.session_state:
        st.session_state.raci_to_delete = [
            False] * len(st.session_state.raci_list)

    # Sync delete flags
    if len(st.session_state.raci_to_delete) != len(st.session_state.raci_list):
        st.session_state.raci_to_delete = [
            False] * len(st.session_state.raci_list)

    updated_raci = []
    for i, raci in enumerate(st.session_state.raci_list):
        # Delete checkbox row
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            artifact = st.text_input("Artifact/Task", value=raci.get(
                'artifact', ''), key=f"raci_artifact_{i}", label_visibility="collapsed")
        with col2:
            role = st.text_input("Role/Name", value=raci.get('role', ''),
                                 key=f"raci_role_{i}", label_visibility="collapsed")
        with col3:
            code = st.selectbox("RACI", ["R", "A", "C", "I"], key=f"raci_code_{i}",
                                index=["R", "A", "C", "I"].index(raci.get('code', 'R')), label_visibility="collapsed")
        with col4:
            delete_flag = st.checkbox(
                "Delete", key=f"del_raci_check_{i}", value=st.session_state.raci_to_delete[i])
            st.session_state.raci_to_delete[i] = delete_flag

        if not st.session_state.raci_to_delete[i]:
            updated_raci.append({
                "artifact": artifact,
                "role": role,
                "code": code
            })

    st.session_state.raci_list = updated_raci
    st.session_state.raci_to_delete = [False] * len(updated_raci)

    col1, col2 = st.columns(2)
    with col1:
        if st.form_submit_button("Add row", width='stretch'):
            st.session_state.raci_list.append(
                {"artifact": "", "role": "", "code": "R"})
            st.session_state.raci_to_delete = [
                False] * len(st.session_state.raci_list)
            st.rerun()
    with col2:
        if len(st.session_state.raci_list) > 0 and st.form_submit_button("Delete marked rows", width='stretch'):
            # Already filtered above
            st.rerun()

    return st.session_state.raci_list


def render_edit_raci_form():
    """Render RACI matrix form for editing with delete functionality"""
    st.markdown("""
    **Legend:**
    - **R (Responsible)** - executes tasks
    - **A (Accountable)** - makes decisions
    - **C (Consulted)** - provides consultation
    - **I (Informed)** - receives updates
    """)

    if 'edit_raci_list' not in st.session_state:
        st.session_state.edit_raci_list = []

    if 'edit_raci_to_delete' not in st.session_state:
        st.session_state.edit_raci_to_delete = []

    if not st.session_state.edit_raci_list:
        st.info("No entries in RACI matrix. Click 'Add RACI row'")
        if st.form_submit_button("Add first RACI row", width='stretch'):
            st.session_state.edit_raci_list.append(
                {"artifact": "", "role": "", "code": "R"})
            st.session_state.edit_raci_to_delete = [
                False] * len(st.session_state.edit_raci_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.edit_raci_to_delete) != len(st.session_state.edit_raci_list):
            st.session_state.edit_raci_to_delete = [
                False] * len(st.session_state.edit_raci_list)

        updated_raci = []
        for i, raci_item in enumerate(st.session_state.edit_raci_list):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                artifact = st.text_input("Artifact/Task", value=raci_item.get('artifact', ''),
                                         key=f"edit_raci_artifact_{i}", label_visibility="collapsed")
            with col2:
                role = st.text_input("Role/Name", value=raci_item.get('role', ''),
                                     key=f"edit_raci_role_{i}", label_visibility="collapsed")
            with col3:
                code = st.selectbox("RACI", ["R", "A", "C", "I"], key=f"edit_raci_code_{i}",
                                    index=["R", "A", "C", "I"].index(raci_item.get('code', 'R')), label_visibility="collapsed")
            with col4:
                delete_flag = st.checkbox("Delete", key=f"del_edit_raci_check_{i}",
                                          value=st.session_state.edit_raci_to_delete[i])
                st.session_state.edit_raci_to_delete[i] = delete_flag

            if not st.session_state.edit_raci_to_delete[i]:
                updated_raci.append({
                    "artifact": artifact,
                    "role": role,
                    "code": code
                })

        st.session_state.edit_raci_list = updated_raci
        st.session_state.edit_raci_to_delete = [False] * len(updated_raci)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add RACI row", width='stretch'):
                st.session_state.edit_raci_list.append(
                    {"artifact": "", "role": "", "code": "R"})
                st.session_state.edit_raci_to_delete = [
                    False] * len(st.session_state.edit_raci_list)
                st.rerun()
        with col2:
            if len(st.session_state.edit_raci_list) > 0 and st.form_submit_button("Delete marked rows", width='stretch'):
                st.rerun()

    return st.session_state.edit_raci_list
