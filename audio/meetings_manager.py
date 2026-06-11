import streamlit as st
from audio import (
    save_audio_file, save_recording_metadata,
    transcribe_audio, update_transcript, save_meeting_minutes
)
from audio.transcriber import extract_meeting_info
from audio.database import update_audio_status


def render_meetings_manager(project_id):
    """Project meetings manager"""
    st.markdown("### Upload new meeting recording")

    uploaded_file = st.file_uploader(
        "Select audio file",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        key=f"meeting_upload_{project_id}"
    )

    if uploaded_file is not None:
        # Show file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.caption(f"File size: {file_size_mb:.2f} MB")

        # Estimated processing time
        if file_size_mb > 50:
            st.warning("Large file. Processing may take 5-10 minutes.")

        col1, col2 = st.columns(2)
        with col1:
            meeting_name = st.text_input(
                "Meeting name",
                placeholder="e.g., Sprint planning",
                key=f"meeting_name_{project_id}"
            )
            meeting_date = st.date_input(
                "Meeting date", key=f"meeting_date_{project_id}")
        with col2:
            participants_input = st.text_area(
                "Participants (one per line)",
                placeholder="Ivanov Ivan\nPetrov Petr\nSidorova Anna",
                height=100,
                key=f"participants_{project_id}"
            )

        if st.button("Upload and process", key=f"upload_meeting_{project_id}", width='stretch'):
            if not meeting_name:
                st.error("Enter meeting name")
            else:
                with st.spinner("Uploading and processing audio file..."):
                    # Save file
                    filename = uploaded_file.name
                    file_path = save_audio_file(
                        uploaded_file, project_id, filename)

                    participants_list = [
                        p.strip() for p in participants_input.split('\n') if p.strip()]

                    # Save metadata
                    recording_id = save_recording_metadata(
                        project_id, filename, file_path, None, uploaded_file.size,
                        meeting_date.isoformat()
                    )

                    update_audio_status(recording_id, 'processing')

                    # Transcription
                    st.info("Performing audio transcription...")
                    transcript = transcribe_audio(file_path)

                    if transcript and not transcript.startswith("Error"):
                        update_transcript(
                            recording_id, transcript, 'completed')

                        # Show transcription
                        with st.expander("Transcription", expanded=False):
                            st.text_area("Transcription text", value=transcript,
                                         height=200, key=f"transcript_{recording_id}")

                        # AI information extraction
                        st.info("Extracting information from transcription...")
                        meeting_info = extract_meeting_info(
                            transcript, meeting_name)

                        # Show extracted data
                        with st.expander("Extracted data", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Decisions made:**")
                                st.write(meeting_info.get('decisions', '—'))
                                st.markdown("**Topics discussed:**")
                                st.write(meeting_info.get('topics', '—'))
                            with col2:
                                st.markdown("**Actions and tasks:**")
                                st.write(meeting_info.get('action_items', '—'))
                                st.markdown("**Brief summary:**")
                                st.write(meeting_info.get('summary', '—'))

                        # Save result
                        save_meeting_minutes(
                            recording_id,
                            meeting_info.get('decisions', ''),
                            meeting_info.get('action_items', ''),
                            participants_list,
                            meeting_info.get('topics', ''),
                            meeting_info.get('next_meeting_date'),
                            meeting_name,
                            str(meeting_info),
                            meeting_info.get('summary', '')
                        )
                        st.success(
                            f"Meeting '{meeting_name}' successfully processed!")
                        st.rerun()
                    else:
                        update_transcript(recording_id, transcript, 'failed')
                        st.error(f"Transcription error: {transcript}")

    st.divider()

    # Display meetings list
    from components.display.meetings_view import render_meetings
    render_meetings({'id': project_id})
