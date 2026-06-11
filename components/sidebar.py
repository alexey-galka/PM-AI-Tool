import streamlit as st
from database.models.projects import get_project_short


def render_sidebar():
    with st.sidebar:
        st.title("PM Tool")
        current_page = st.session_state.get('page', 'Dashboard')

        if current_page not in ["Project", "Editing"]:
            menu = st.radio("Navigation", ["Dashboard", "New project"])
            if menu != current_page:
                st.session_state.page = menu
                if 'current_project_id' in st.session_state:
                    del st.session_state.current_project_id
                st.rerun()
        else:
            if 'current_project_id' in st.session_state:
                project = get_project_short(
                    st.session_state.current_project_id)
                if project:
                    st.info(f"Current project: **{project['name']}**")

        return st.session_state.get('page', 'Dashboard')
