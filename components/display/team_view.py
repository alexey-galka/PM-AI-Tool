import streamlit as st
import pandas as pd


def render_team(project):
    """Display project team"""
    team = project.get('team', [])

    if not team:
        st.info("Project team is not filled in")
    else:
        display_team = []
        for member in team:
            display_team.append({
                'Full name': member.get('name', ''),
                'Role': member.get('role', '')
            })
        df = pd.DataFrame(display_team)
        # Configure index display
        df.index = range(1, len(df) + 1)
        st.dataframe(df, width='stretch', hide_index=False)