import streamlit as st
import pandas as pd


def render_stages(project):
    """Display project stages as a table"""
    stages = project.get('stages', [])

    if not stages:
        st.info("No stages added")
        return

    # Prepare data for table
    display_data = []
    for i, stage in enumerate(stages, start=1):
        # Status with emoji
        status_emoji = {
            'PLANNED': '',
            'IN_PROGRESS': '',
            'DONE': '',
            'BLOCKED': ''
        }.get(stage.get('status', 'PLANNED'), '')

        # Risk (if linked) - first check risk_text, then risk_description
        risk_text = stage.get('risk_text', '')
        risk_description = stage.get('risk_description', '')
        risk_impact = stage.get('risk_impact', 'MEDIUM')

        if risk_text and risk_text != '' and risk_text != '--- No risk ---':
            risk_emoji = {'HIGH': '', 'MEDIUM': '',
                          'LOW': ''}.get(risk_impact, '⚪')
            risk_display = f"{risk_emoji} {risk_text[:50]}..." if len(
                risk_text) > 50 else f"{risk_emoji} {risk_text}"
        elif risk_description and risk_description != '':
            risk_emoji = {'HIGH': '', 'MEDIUM': '',
                          'LOW': ''}.get(risk_impact, '⚪')
            risk_display = f"{risk_emoji} {risk_description[:50]}..." if len(
                risk_description) > 50 else f"{risk_emoji} {risk_description}"
        else:
            risk_display = '—'

        # Safe value retrieval
        expected_date = stage.get('expected_date') or '—'
        actual_date = stage.get('actual_date') or '—'
        risk_realization_date = stage.get('risk_realization_date') or '—'
        comment = stage.get('comment') or '—'
        description = stage.get('description') or '—'
        stage_name = stage.get('name') or '—'

        # Truncate long texts
        if description != '—' and len(description) > 100:
            description = description[:100] + '...'
        if comment != '—' and len(comment) > 50:
            comment = comment[:50] + '...'

        display_data.append({
            '#': i,
            'Stage': stage_name,
            'Description': description,
            'Risk': risk_display,
            'Risk realization': risk_realization_date,
            'Expected date': expected_date,
            'Actual date': actual_date,
            'Status': f"{status_emoji} {stage.get('status', 'PLANNED')}",
            'Comment': comment
        })

    df = pd.DataFrame(display_data)
    df = df.set_index('#')
    st.dataframe(df, width='stretch')