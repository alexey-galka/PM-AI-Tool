import streamlit as st
from audio import get_recordings_by_project, get_meeting_minutes
from audio.database import delete_recording, update_meeting_minutes
from audio.storage import delete_audio_file


def render_meetings(project):
    """Display list of project meetings with editing capability"""
    project_id = project.get('id')
    recordings = get_recordings_by_project(project_id)

    if not recordings:
        st.info(
            "No meeting records. Upload an audio recording of a meeting to create minutes.")
        return

    st.subheader("Meeting list")

    # Handle deletion
    if st.session_state.get('delete_recording_id'):
        recording_id = st.session_state.delete_recording_id
        recording_to_delete = None
        for rec in recordings:
            if rec['id'] == recording_id:
                recording_to_delete = rec
                break

        if recording_to_delete:
            try:
                delete_audio_file(project_id, recording_to_delete['filename'])
            except Exception as e:
                print(f"Error deleting file: {e}")
            delete_recording(recording_id)
            st.success("Recording successfully deleted")

        st.session_state.delete_recording_id = None
        st.rerun()

    for recording in recordings:
        recording_id = recording['id']
        filename = recording['filename']
        recorded_date = recording.get('recorded_date', '')
        transcript_status = recording.get('transcript_status', 'pending')
        transcript = recording.get('transcript', '')

        # Get meeting minutes
        minutes = get_meeting_minutes(
            recording_id) if transcript_status == 'completed' else None
        meeting_name = minutes.get(
            'meeting_name', filename) if minutes else filename

        title = f"{meeting_name} - {recorded_date[:10] if recorded_date else 'Date not specified'}"

        with st.expander(title):
            if transcript_status == 'pending':
                st.warning("Audio uploaded, transcription not performed")
                if st.button("Perform transcription", key=f"transcribe_{recording_id}"):
                    st.session_state.transcribe_recording_id = recording_id
                    st.rerun()
            elif transcript_status == 'processing':
                st.info("Transcription in progress...")
            elif transcript_status == 'completed':
                st.success("Transcription completed")

                if minutes:
                    # Edit mode
                    edit_mode_key = f"edit_mode_{recording_id}"
                    if st.session_state.get(edit_mode_key, False):
                        st.info("Edit mode")

                        new_meeting_name = st.text_input(
                            "Meeting name",
                            value=minutes.get('meeting_name', ''),
                            key=f"edit_name_{recording_id}"
                        )
                        new_decisions = st.text_area(
                            "Decisions made",
                            value=minutes.get('decisions', ''),
                            height=100,
                            key=f"edit_decisions_{recording_id}"
                        )
                        new_action_items = st.text_area(
                            "Actions and tasks",
                            value=minutes.get('action_items', ''),
                            height=100,
                            key=f"edit_actions_{recording_id}"
                        )
                        new_topics = st.text_area(
                            "Topics discussed",
                            value=minutes.get('topics', ''),
                            height=100,
                            key=f"edit_topics_{recording_id}"
                        )

                        participants = minutes.get('participants', [])
                        participants_str = "\n".join(
                            participants) if participants else ""
                        new_participants = st.text_area(
                            "Participants (one per line)",
                            value=participants_str,
                            height=100,
                            key=f"edit_participants_{recording_id}"
                        )

                        new_next_meeting = st.text_input(
                            "Next meeting date",
                            value=minutes.get('next_meeting_date', ''),
                            key=f"edit_next_meeting_{recording_id}"
                        )
                        new_summary = st.text_area(
                            "Brief summary",
                            value=minutes.get('summary', ''),
                            height=100,
                            key=f"edit_summary_{recording_id}"
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Save", key=f"save_minutes_{recording_id}"):
                                update_meeting_minutes(
                                    recording_id,
                                    new_meeting_name,
                                    new_decisions,
                                    new_action_items,
                                    [p.strip() for p in new_participants.split(
                                        '\n') if p.strip()],
                                    new_topics,
                                    new_next_meeting if new_next_meeting else None,
                                    new_summary
                                )
                                st.session_state[edit_mode_key] = False
                                st.rerun()
                        with col2:
                            if st.button("Cancel", key=f"cancel_edit_{recording_id}"):
                                st.session_state[edit_mode_key] = False
                                st.rerun()
                    else:
                        # View mode
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Decisions made:**")
                            st.write(minutes.get('decisions', '—'))
                            st.markdown("**Topics discussed:**")
                            st.write(minutes.get('topics', '—'))
                            if minutes.get('next_meeting_date'):
                                st.markdown("**Next meeting:**")
                                st.write(minutes.get('next_meeting_date'))
                        with col2:
                            st.markdown("**Actions and tasks:**")
                            st.write(minutes.get('action_items', '—'))
                            st.markdown("**Participants:**")
                            participants = minutes.get('participants', [])
                            for p in participants:
                                st.write(f"- {p}")

                        st.markdown("**Brief summary:**")
                        st.write(minutes.get('summary', '—'))

                        if st.button("Edit minutes", key=f"edit_btn_{recording_id}"):
                            st.session_state[edit_mode_key] = True
                            st.rerun()

                        with st.expander("Full transcription"):
                            st.text_area("Transcription", value=transcript, height=300,
                                         disabled=True, key=f"transcript_area_{recording_id}")
                else:
                    st.info("Meeting minutes not generated")
                    if st.button("Generate minutes", key=f"extract_minutes_{recording_id}"):
                        st.session_state.extract_minutes_id = recording_id
                        st.rerun()

            elif transcript_status == 'failed':
                st.error("Transcription error")

            # Delete button
            if st.button("Delete recording", key=f"delete_recording_{recording_id}"):
                st.session_state.delete_recording_id = recording_id
                st.rerun()