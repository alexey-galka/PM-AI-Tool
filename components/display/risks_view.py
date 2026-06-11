import streamlit as st
import pandas as pd


def render_risks(project):
    """Display project risks as a table with text truncation"""
    risks = project.get('risks', [])

    if not risks:
        st.info("No risks added")
        return

    impact_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    sorted_risks = sorted(risks, key=lambda x: impact_order.get(
        x.get('impact', 'MEDIUM'), 1))

    display_data = []
    for i, risk in enumerate(sorted_risks, start=1):
        # Truncate long texts for compact display
        description = risk.get('description', '—')
        impact_on_result = risk.get('impact_on_result', '—')
        impact_on_timeline = risk.get('impact_on_timeline', '—')
        mitigation_plan = risk.get('mitigation_plan', '—')

        # Truncate to 100 characters
        if len(description) > 100:
            description = description[:97] + '...'
        if len(impact_on_result) > 80:
            impact_on_result = impact_on_result[:77] + '...'
        if len(impact_on_timeline) > 80:
            impact_on_timeline = impact_on_timeline[:77] + '...'
        if len(mitigation_plan) > 100:
            mitigation_plan = mitigation_plan[:97] + '...'

        display_data.append({
            '#': i,
            'Impact': risk.get('impact', 'MEDIUM'),
            'Description': description,
            'Impact on result': impact_on_result,
            'Impact on timeline': impact_on_timeline,
            'Mitigation plan': mitigation_plan,
            # Save full texts for tooltips
            '_full_description': risk.get('description', '—'),
            '_full_impact_on_result': risk.get('impact_on_result', '—'),
            '_full_impact_on_timeline': risk.get('impact_on_timeline', '—'),
            '_full_mitigation_plan': risk.get('mitigation_plan', '—')
        })

    df = pd.DataFrame(display_data)

    # Remove temporary columns from display
    cols_to_display = ['#', 'Impact', 'Description',
                       'Impact on result', 'Impact on timeline', 'Mitigation plan']
    df_display = df[cols_to_display].copy()
    df_display = df_display.set_index('#')

    def highlight_risks(row):
        impact = row['Impact']
        if impact == 'HIGH':
            return ['background-color: #ffebee'] * len(row)
        elif impact == 'MEDIUM':
            return ['background-color: #fff8e1'] * len(row)
        elif impact == 'LOW':
            return ['background-color: #e8f5e9'] * len(row)
        return [''] * len(row)

    styled_df = df_display.style.apply(highlight_risks, axis=1)
    st.dataframe(styled_df, width='stretch')

    # Detailed risk view with full text
    with st.expander("Detailed risk information"):
        for i, risk in enumerate(sorted_risks, start=1):
            impact = risk.get('impact', 'MEDIUM')
            impact_emoji = {'HIGH': '', 'MEDIUM': '',
                            'LOW': ''}.get(impact, '⚪')

            st.markdown(f"**Risk {i}** {impact_emoji} **[{impact}]**")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Description:**")
                st.write(risk.get('description', '—'))
                st.write(f"**Impact on result:**")
                st.write(risk.get('impact_on_result', '—'))
            with col2:
                st.write(f"**Impact on timeline:**")
                st.write(risk.get('impact_on_timeline', '—'))
                st.write(f"**Mitigation plan:**")
                st.write(risk.get('mitigation_plan', '—'))
            st.divider()