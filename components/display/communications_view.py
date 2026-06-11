import streamlit as st


def render_communications(project):
    """Display communications plan"""
    communications = project.get('communications', [])

    if not communications:
        st.info("Communications plan is not filled in")
    else:
        for comm in communications:
            with st.expander(f"{comm.get('name', 'Untitled')} - {comm.get('frequency', 'Not specified')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Frequency:** {comm.get('frequency', '—')}")
                    st.write(f"**Time:** {comm.get('time', '—')}")
                    st.write(
                        f"**Duration:** {comm.get('duration', '—')} min")
                with col2:
                    st.write(f"**Location:** {comm.get('location', '—')}")
                    if comm.get('link'):
                        st.markdown(
                            f"**Link:** [Open]({comm.get('link')})")
                st.write(f"**Description:** {comm.get('description', '—')}")