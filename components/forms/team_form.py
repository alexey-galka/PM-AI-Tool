import streamlit as st


def render_team_form():
    """Render project team form with delete functionality"""
    st.markdown("**Project team**")

    if 'team_list' not in st.session_state:
        st.session_state.team_list = [{"name": "", "role": ""}]

    if 'team_to_delete' not in st.session_state:
        st.session_state.team_to_delete = [
            False] * len(st.session_state.team_list)

    # Sync delete flags
    if len(st.session_state.team_to_delete) != len(st.session_state.team_list):
        st.session_state.team_to_delete = [
            False] * len(st.session_state.team_list)

    updated_team = []
    for i, member in enumerate(st.session_state.team_list):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            name = st.text_input("Full name", value=member.get(
                'name', ''), key=f"team_name_{i}", label_visibility="collapsed")
        with col2:
            role = st.text_input("Role", value=member.get(
                'role', ''), key=f"team_role_{i}", label_visibility="collapsed")
        with col3:
            st.markdown("")
        with col4:
            delete_flag = st.checkbox(
                "Delete", key=f"del_team_check_{i}", value=st.session_state.team_to_delete[i])
            st.session_state.team_to_delete[i] = delete_flag

        if not st.session_state.team_to_delete[i]:
            updated_team.append({"name": name, "role": role})

    st.session_state.team_list = updated_team
    st.session_state.team_to_delete = [False] * len(updated_team)

    col1, col2 = st.columns(2)
    with col1:
        if st.form_submit_button("Add member", width='stretch'):
            st.session_state.team_list.append({"name": "", "role": ""})
            st.session_state.team_to_delete = [
                False] * len(st.session_state.team_list)
            st.rerun()
    with col2:
        if len(st.session_state.team_list) > 0 and st.form_submit_button("Delete marked members", width='stretch'):
            st.rerun()

    return st.session_state.team_list


def render_edit_team_form():
    """Render team form for editing with delete functionality"""
    st.markdown("**Project team**")

    if 'edit_team_list' not in st.session_state:
        st.session_state.edit_team_list = []

    if 'edit_team_to_delete' not in st.session_state:
        st.session_state.edit_team_to_delete = []

    if not st.session_state.edit_team_list:
        st.info("No team members. Click 'Add member'")
        if st.form_submit_button("Add member", width='stretch'):
            st.session_state.edit_team_list.append(
                {"id": None, "name": "", "role": ""})
            st.session_state.edit_team_to_delete = [
                False] * len(st.session_state.edit_team_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.edit_team_to_delete) != len(st.session_state.edit_team_list):
            st.session_state.edit_team_to_delete = [
                False] * len(st.session_state.edit_team_list)

        updated_team = []
        for i, member in enumerate(st.session_state.edit_team_list):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                name = st.text_input("Full name", value=member.get(
                    'name', ''), key=f"edit_team_name_{i}", label_visibility="collapsed")
            with col2:
                role = st.text_input("Role", value=member.get(
                    'role', ''), key=f"edit_team_role_{i}", label_visibility="collapsed")
            with col3:
                st.markdown("")
            with col4:
                delete_flag = st.checkbox("Delete", key=f"del_edit_team_check_{i}",
                                          value=st.session_state.edit_team_to_delete[i] if i < len(st.session_state.edit_team_to_delete) else False)
                if i < len(st.session_state.edit_team_to_delete):
                    st.session_state.edit_team_to_delete[i] = delete_flag

            if not st.session_state.edit_team_to_delete[i]:
                updated_team.append({
                    "id": member.get('id'),
                    "name": name,
                    "role": role
                })

        st.session_state.edit_team_list = updated_team
        st.session_state.edit_team_to_delete = [False] * len(updated_team)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add member", width='stretch'):
                st.session_state.edit_team_list.append(
                    {"id": None, "name": "", "role": ""})
                st.session_state.edit_team_to_delete = [
                    False] * len(st.session_state.edit_team_list)
                st.rerun()
        with col2:
            if len(st.session_state.edit_team_list) > 0 and st.form_submit_button("Delete marked members", width='stretch'):
                st.rerun()

    return [m for m in st.session_state.edit_team_list if m.get('name', '').strip()]
