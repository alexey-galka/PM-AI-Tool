import re
import streamlit as st
from datetime import datetime, timedelta
from services.ai_service import call_ollama, trim_ai_response


def get_weekly_changes(project, days=7):
    """Collects project changes over the last N days"""

    today = datetime.now().date()

    stages = project.get('stages', [])
    risks = project.get('risks', [])
    communications = project.get('communications', [])

    completed_stages = []
    upcoming_stages = []
    overdue_stages = []

    for stage in stages:
        expected_date = stage.get('expected_date')
        status = stage.get('status')

        if expected_date:
            if isinstance(expected_date, str):
                expected_date = datetime.fromisoformat(expected_date).date()

            if status == 'DONE':
                completed_stages.append(stage)
            elif status == 'BLOCKED':
                overdue_stages.append(stage)
            elif expected_date <= today + timedelta(days=7):
                upcoming_stages.append(stage)

    high_risks = [r for r in risks if r.get('impact') == 'HIGH']

    return {
        "completed_stages": completed_stages,
        "upcoming_stages": upcoming_stages,
        "overdue_stages": overdue_stages,
        "high_risks": high_risks,
        "meetings_count": len(communications),
        "total_stages": len(stages),
        "completed_count": len(completed_stages),
        "completion_rate": round(len(completed_stages) / len(stages) * 100) if stages else 0
    }


def generate_digest(project):
    """Generates a weekly project digest"""

    changes = get_weekly_changes(project)

    completed_names = [s.get('name', 'Untitled')
                       for s in changes['completed_stages']]
    upcoming_names = [s.get('name', 'Untitled')
                      for s in changes['upcoming_stages']]
    high_risks_desc = [r.get('description', '')[:100]
                       for r in changes['high_risks']]

    prompt = f"""You are a project manager. Create a brief weekly digest.

Project data:
- Name: {project.get('name', 'Not specified')}
- Status: {project.get('status', 'Not specified')}
- Progress: {changes['completion_rate']}% ({changes['completed_count']} out of {changes['total_stages']} stages)

Completed stages: {', '.join(completed_names) if completed_names else 'none'}
Upcoming stages: {', '.join(upcoming_names) if upcoming_names else 'none'}
HIGH risks: {', '.join(high_risks_desc) if high_risks_desc else 'none'}

The response should be in this format (each item on a new line):

📊 **Progress:** text

⚠️ **Risks:** text

✅ **Completed stages:**
- stage 1
- stage 2
- etc.

📅 **Upcoming stages:**
- stage 1
- stage 2
- etc.

💡 **Recommendations:**
- recommendation 1
- recommendation 2
- etc.

Use line breaks to separate items. Don't write everything on one line.
"""

    response = call_ollama(prompt)
    response = trim_ai_response(response)  # Trim after ...done thinking.

    return {
        "digest": response,
        "stats": changes
    }


def render_weekly_digest(project):
    """Displays weekly digest in the UI"""

    st.markdown("## Weekly digest")

    if 'digest_data' not in st.session_state:
        st.session_state.digest_data = None

    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("Generate a digest based on the current project status")
    with col2:
        if st.button("Generate digest", width='stretch'):
            with st.spinner("Generating digest..."):
                st.session_state.digest_data = generate_digest(project)
                st.rerun()

    st.divider()

    if st.session_state.digest_data:
        digest_data = st.session_state.digest_data

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Progress", f"{digest_data['stats']['completion_rate']}%\n")
        with col2:
            st.metric("Completed", digest_data['stats']['completed_count'])
        with col3:
            st.metric("Risks", len(digest_data['stats']['high_risks']))
        with col4:
            st.metric("Upcoming", len(
                digest_data['stats']['upcoming_stages']))

        st.divider()

        # Display digest with forced formatting
        digest_text = digest_data['digest']

        # Replace possible markers with line breaks
        digest_text = digest_text.replace('📊', '\n')
        digest_text = digest_text.replace('⚠️', '\n')
        digest_text = digest_text.replace('✅', '\n')
        digest_text = digest_text.replace('📅', '\n')
        digest_text = digest_text.replace('💡', '\n')

        # Split into lines and display
        lines = digest_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith(''):
                st.markdown(f"{line}")
            elif line.startswith(''):
                st.markdown(f" {line}")
            elif line.startswith(''):
                st.markdown(f" {line}")
            elif line.startswith(''):
                st.markdown(f" {line}")
            elif line.startswith(''):
                st.markdown(f" {line}")
            elif line.startswith('-'):
                st.markdown(f"&nbsp;&nbsp;&nbsp;{line}")
            else:
                st.write(line)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Copy to clipboard", width='stretch'):
                st.write("Digest copied!")
                st.session_state.copy_digest = digest_data['digest']
        with col2:
            if st.button("Export to Markdown", width='stretch'):
                md_content = f"""# Weekly digest: {project.get('name')}

**Date:** {datetime.now().strftime('%d.%m.%Y')}
**Progress:** {digest_data['stats']['completion_rate']}%

{digest_data['digest']}

---
*Generated automatically*
"""
                st.download_button(
                    label="Download",
                    data=md_content,
                    file_name=f"digest_{project.get('name')}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    width='stretch',
                    key="download_digest"
                )
    else:
        st.info("Click 'Generate digest' to create a weekly report")
