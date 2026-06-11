import streamlit as st
from audio import save_audio_file
from audio.transcriber import transcribe_audio, extract_project_info


def render_audio_upload(project_id=None):
    """Render audio upload form for filling project passport"""
    st.markdown("Upload meeting audio recording")
    st.caption(
        "Upload an audio recording of a meeting to automatically fill in the project passport")

    # Initialize state
    if 'audio_extracted_data' not in st.session_state:
        st.session_state.audio_extracted_data = None
    if 'apply_audio_data' not in st.session_state:
        st.session_state.apply_audio_data = False
    if 'show_transcript' not in st.session_state:
        st.session_state.show_transcript = False

    uploaded_file = st.file_uploader(
        "Select audio file",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        key="project_audio_upload"
    )

    if uploaded_file is not None:
        if st.button("Process audio", width='stretch', key="process_audio_btn"):
            with st.spinner("Uploading and processing audio file (may take several minutes)..."):
                filename = uploaded_file.name
                temp_project_id = project_id or 999999
                file_path = save_audio_file(
                    uploaded_file, temp_project_id, filename)

                st.info("Performing audio transcription...")
                transcript = transcribe_audio(file_path)

                if transcript and not transcript.startswith("Error"):
                    st.session_state.transcript_text = transcript
                    st.session_state.show_transcript = True

                    st.success("Transcription completed!")

                    if len(transcript) > 100:
                        st.info("Extracting information from transcription...")
                        project_info = extract_project_info(transcript)

                        if project_info:
                            st.success("Information extracted successfully!")

                            # Save to session state
                            st.session_state.audio_extracted_data = project_info
                            st.rerun()
                        else:
                            st.error(
                                "Failed to extract information from audio recording")
                    else:
                        st.warning("Transcription is too short")
                else:
                    st.error(f"Transcription error: {transcript}")

    # Display transcription if available
    if st.session_state.get('transcript_text'):
        with st.expander("Show transcription", expanded=st.session_state.get('show_transcript', False)):
            st.text(st.session_state.transcript_text + (
                "..." if len(st.session_state.transcript_text) > 2000 else ""))

    # Display extracted data if available
    if st.session_state.get('audio_extracted_data'):
        data = st.session_state.audio_extracted_data

        with st.expander("Extracted data from audio", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Project name:** {data.get('name', '—')}")
                st.write(f"**Goals:** {data.get('goals', '—')[:200]}")
                st.write(
                    f"**Key results:** {data.get('key_results', '—')[:200]}")
                st.write(f"**Problem:** {data.get('problem', '—')[:200]}")
                st.write(f"**Hypothesis:** {data.get('hypothesis', '—')[:200]}")
            with col2:
                st.write(
                    f"**Success criteria:** {data.get('success_criteria', '—')[:200]}")

                must_have = data.get('must_have', [])
                if must_have:
                    st.write(f"**Must have:** {', '.join(must_have)}")
                else:
                    st.write("**Must have:** —")

                nice_to_have = data.get('nice_to_have', [])
                if nice_to_have:
                    st.write(f"**Nice to have:** {', '.join(nice_to_have)}")
                else:
                    st.write("**Nice to have:** —")

                not_in_scope = data.get('not_in_scope', [])
                if not_in_scope:
                    st.write(f"**Not in scope:** {', '.join(not_in_scope)}")
                else:
                    st.write("**Not in scope:** —")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Apply data to form", width='stretch', key="apply_data_btn"):
                st.session_state.apply_audio_data = True
                st.rerun()
        with col2:
            if st.button("Clear data", width='stretch', key="clear_data_btn"):
                st.session_state.audio_extracted_data = None
                st.session_state.transcript_text = None
                st.session_state.apply_audio_data = False
                st.rerun()

    # Return data if need to apply
    if st.session_state.get('apply_audio_data') and st.session_state.get('audio_extracted_data'):
        data = st.session_state.audio_extracted_data
        # DO NOT RESET the flag to apply the data
        return {
            'name': data.get('name', ''),
            'goals': data.get('goals', ''),
            'key_results': data.get('key_results', ''),
            'problem': data.get('problem', ''),
            'hypothesis': data.get('hypothesis', ''),
            'success_criteria': data.get('success_criteria', ''),
            'must_have': data.get('must_have', []),
            'nice_to_have': data.get('nice_to_have', []),
            'not_in_scope': data.get('not_in_scope', [])
        }

    return None