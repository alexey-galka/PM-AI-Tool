from database.connection import init_db
import streamlit as st
from config import ensure_dirs
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="PM AI Tool",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialization
ensure_dirs()
init_db()

# If no page in session state, set dashboard
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# Render sidebar
page = render_sidebar()

# Page navigation
if page == "Dashboard":
    from views.dashboard import show_dashboard
    show_dashboard()
elif page == "New project":
    from views.project_new import show_new_project
    show_new_project()
elif page == "Project":
    from views.project_detail import show_project_detail
    show_project_detail()
elif page == "Editing":
    from views.project_edit import show_edit_project
    show_edit_project()