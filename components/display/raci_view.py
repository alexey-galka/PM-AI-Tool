import streamlit as st
import pandas as pd


def render_raci(project):
    """Display RACI matrix as an interactive pivot table"""

    st.markdown("""
    **Legend:**
    - **R (Responsible)** - executes tasks
    - **A (Accountable)** - responsible for the final result
    - **C (Consulted)** - provides consultation
    - **I (Informed)** - receives updates
    """)

    raci_matrix = project.get('raci', [])

    if not raci_matrix:
        st.info("RACI matrix is not filled in")
        return

    # Create a DataFrame from the RACI entries
    data = []
    for entry in raci_matrix:
        artifact = entry.get('artifact_name', '')
        role = entry.get('role_name', '')
        code = entry.get('raci_code', '')
        if artifact and role and code:
            data.append({
                'Artifact': artifact,
                'Role': role,
                'RACI': code
            })

    if not data:
        st.info("No valid RACI entries found")
        return

    df = pd.DataFrame(data)

    # Create pivot table
    pivot_df = df.pivot_table(
        index='Artifact',
        columns='Role',
        values='RACI',
        aggfunc='first',
        fill_value=''
    )

    # Add styling
    def color_raci(val):
        if val == 'R':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'A':
            return 'background-color: #f8d7da; color: #721c24'
        elif val == 'C':
            return 'background-color: #fff3cd; color: #856404'
        elif val == 'I':
            return 'background-color: #d1ecf1; color: #0c5460'
        return ''

    # Apply styling
    styled_pivot = pivot_df.style.map(color_raci)

    # Display the styled pivot table
    st.markdown("### RACI Matrix")
    st.dataframe(styled_pivot, width='stretch')
