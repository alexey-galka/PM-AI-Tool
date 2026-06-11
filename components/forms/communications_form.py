import streamlit as st
from datetime import time


def render_communications_form():
    """Render communications form (meeting plan)"""
    st.markdown("**Communications (meeting plan)**")

    if 'communications_list' not in st.session_state:
        st.session_state.communications_list = [{
            "frequency": "Weekly",
            "time": time(10, 0),
            "name": "",
            "duration": 60,
            "description": "",
            "location": "",
            "link": ""
        }]

    for i, comm in enumerate(st.session_state.communications_list):
        st.markdown(f"**Meeting {i+1}**")

        col1, col2 = st.columns(2)
        with col1:
            comm['name'] = st.text_input(
                "Meeting name", value=comm.get('name', ''), key=f"comm_name_{i}")
            comm['frequency'] = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "On demand"],
                                             index=["Daily", "Weekly", "Monthly", "On demand"].index(
                                                 comm.get('frequency', 'Weekly')),
                                             key=f"comm_frequency_{i}")
            comm['time'] = st.time_input("Time", value=comm.get(
                'time', time(10, 0)), key=f"comm_time_{i}")
        with col2:
            comm['duration'] = st.number_input("Duration (minutes)", min_value=5, max_value=480, value=comm.get(
                'duration', 60), step=15, key=f"comm_duration_{i}")
            comm['location'] = st.text_input(
                "Location/Platform", value=comm.get('location', ''), key=f"comm_location_{i}")
            comm['link'] = st.text_input(
                "Meeting link", value=comm.get('link', ''), key=f"comm_link_{i}")

        comm['description'] = st.text_area("Description", value=comm.get(
            'description', ''), key=f"comm_description_{i}", height=68)
        st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.form_submit_button("Add meeting", width='stretch'):
            st.session_state.communications_list.append({
                "frequency": "Weekly",
                "time": time(10, 0),
                "name": "",
                "duration": 60,
                "description": "",
                "location": "",
                "link": ""
            })
            st.rerun()
    with col2:
        if len(st.session_state.communications_list) > 1 and st.form_submit_button("Remove last meeting", width='stretch'):
            st.session_state.communications_list.pop()
            st.rerun()

    return st.session_state.communications_list


def render_edit_communications_form():
    """Render communications form for editing"""
    st.markdown("**Communications (meeting plan)**")

    if 'edit_communications_list' not in st.session_state:
        st.session_state.edit_communications_list = []

    # Initialize action flags
    if 'add_communication' not in st.session_state:
        st.session_state.add_communication = False
    if 'remove_communication_index' not in st.session_state:
        st.session_state.remove_communication_index = -1

    # Handle adding new meeting
    if st.session_state.add_communication:
        st.session_state.edit_communications_list.append({
            "id": None,
            "name": "",
            "frequency": "Weekly",
            "time": time(10, 0),
            "duration": 60,
            "location": "",
            "link": "",
            "description": ""
        })
        st.session_state.add_communication = False
        st.rerun()

    # Handle removing meeting
    if st.session_state.remove_communication_index >= 0:
        st.session_state.edit_communications_list.pop(
            st.session_state.remove_communication_index)
        st.session_state.remove_communication_index = -1
        st.rerun()

    if not st.session_state.edit_communications_list:
        st.info("No scheduled meetings. Click 'Add meeting'")
        if st.form_submit_button("Add meeting", width='stretch'):
            st.session_state.add_communication = True
            st.rerun()
    else:
        # Create a new list for updated communications
        updated_comms_list = []

        for i, comm in enumerate(st.session_state.edit_communications_list):
            st.markdown(f"**Meeting {i+1}**")

            # Use columns for compactness
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Meeting name", value=comm.get(
                    'name', ''), key=f"edit_comm_name_{i}")
                frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "On demand"],
                                         index=["Daily", "Weekly", "Monthly", "On demand"].index(
                                             comm.get('frequency', 'Weekly')),
                                         key=f"edit_comm_frequency_{i}")
                comm_time = st.time_input("Time", value=comm.get(
                    'time', time(10, 0)), key=f"edit_comm_time_{i}")
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=5, max_value=480,
                                           value=comm.get('duration', 60), step=15, key=f"edit_comm_duration_{i}")
                location = st.text_input(
                    "Location/Platform", value=comm.get('location', ''), key=f"edit_comm_location_{i}")
                link = st.text_input("Meeting link", value=comm.get(
                    'link', ''), key=f"edit_comm_link_{i}")

            description = st.text_area("Description", value=comm.get(
                'description', ''), key=f"edit_comm_description_{i}", height=68)

            # Delete meeting button
            if st.form_submit_button("Delete meeting", key=f"del_comm_btn_{i}", width='stretch'):
                st.session_state.remove_communication_index = i
                st.rerun()

            # Save updated communication
            updated_comms_list.append({
                "id": comm.get('id'),
                "name": name,
                "frequency": frequency,
                "time": comm_time.strftime("%H:%M") if comm_time else "10:00",
                "duration": duration,
                "location": location,
                "link": link,
                "description": description
            })
            st.divider()

        # Update list in session state (save all, empty names will be filtered later)
        st.session_state.edit_communications_list = updated_comms_list

        # Add new meeting button
        if st.form_submit_button("Add meeting", width='stretch'):
            st.session_state.add_communication = True
            st.rerun()

    # Return only records with non-empty name
    return [c for c in st.session_state.edit_communications_list if c.get('name', '').strip()]