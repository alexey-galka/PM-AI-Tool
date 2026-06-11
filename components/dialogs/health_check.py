import re
import streamlit as st
from datetime import datetime
from services.ai_service import call_ollama, clean_response, trim_ai_response


def analyze_project_health(project):
    """Analyze project health based on data"""

    # Collect statistics (code remains unchanged)
    risks = project.get('risks', [])
    stages = project.get('stages', [])

    high_risks = sum(1 for r in risks if r.get('impact') == 'HIGH')
    medium_risks = sum(1 for r in risks if r.get('impact') == 'MEDIUM')
    low_risks = sum(1 for r in risks if r.get('impact') == 'LOW')

    total_stages = len(stages)
    completed_stages = sum(1 for s in stages if s.get('status') == 'DONE')
    in_progress_stages = sum(
        1 for s in stages if s.get('status') == 'IN_PROGRESS')
    blocked_stages = sum(1 for s in stages if s.get('status') == 'BLOCKED')
    planned_stages = sum(1 for s in stages if s.get('status') == 'PLANNED')

    today = datetime.now().date()
    overdue_stages = []
    for stage in stages:
        expected_date = stage.get('expected_date')
        if expected_date and stage.get('status') not in ['DONE', 'BLOCKED']:
            if isinstance(expected_date, str):
                expected_date = datetime.fromisoformat(expected_date).date()
            if expected_date < today:
                overdue_stages.append(stage)

    required_fields = {
        'Project name': project.get('name'),
        'Goals': project.get('goals'),
        'Problem': project.get('problem'),
        'Success criteria': project.get('success_criteria')
    }
    missing_fields = [k for k, v in required_fields.items() if not v]

    health_score = 100
    if high_risks > 0:
        health_score -= high_risks * 10
    if medium_risks > 2:
        health_score -= (medium_risks - 2) * 5
    if blocked_stages > 0:
        health_score -= blocked_stages * 15
    if len(overdue_stages) > 0:
        health_score -= len(overdue_stages) * 10
    if len(missing_fields) > 0:
        health_score -= len(missing_fields) * 15
    if total_stages == 0:
        health_score -= 20
    health_score = max(0, min(100, health_score))

    if health_score >= 80:
        status = "Green"
        status_emoji = "🟢"
        status_text = "Project is in good condition"
    elif health_score >= 50:
        status = "Yellow"
        status_emoji = "🟡"
        status_text = "There are risks, attention required"
    else:
        status = "Red"
        status_emoji = "🔴"
        status_text = "Critical condition, urgent action required"

    # NEW PROMPT - clear format
    ai_prompt = f"""You are an IT project management expert in a bank.
Conduct a project analysis and provide recommendations.

Project data:
- Name: {project.get('name', 'Not specified')}
- Status: {project.get('status', 'Not specified')}
- Risks: HIGH={high_risks}, MEDIUM={medium_risks}, LOW={low_risks}
- Stages: total={total_stages}, completed={completed_stages}, blocked={blocked_stages}
- Overdue stages: {len(overdue_stages)}
- Missing fields: {', '.join(missing_fields) if missing_fields else 'none'}

Provide the answer strictly in the following format (each item on a separate line, without markers or special characters):

ASSESSMENT: [one sentence]

PROBLEM 1: [description of first problem]
PROBLEM 2: [description of second problem]
PROBLEM 3: [description of third problem]

RECOMMENDATION 1: [first recommendation]
RECOMMENDATION 2: [second recommendation]
RECOMMENDATION 3: [third recommendation]
RECOMMENDATION 4: [fourth recommendation]
RECOMMENDATION 5: [fifth recommendation]

Do not use symbols *, **, -, #. Write plain text.
"""

    # Get AI recommendations
    ai_recommendations = call_ollama(ai_prompt)
    ai_recommendations = clean_response(ai_recommendations)
    # Trim after ...done thinking.
    ai_recommendations = trim_ai_response(ai_recommendations)

    return {
        "health_score": health_score,
        "status": status,
        "status_emoji": status_emoji,
        "status_text": status_text,
        "stats": {
            "high_risks": high_risks,
            "medium_risks": medium_risks,
            "low_risks": low_risks,
            "total_risks": len(risks),
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "in_progress_stages": in_progress_stages,
            "blocked_stages": blocked_stages,
            "planned_stages": planned_stages,
            "completion_rate": round(completed_stages / total_stages * 100) if total_stages > 0 else 0,
            "overdue_stages": len(overdue_stages),
            "missing_fields": missing_fields
        },
        "ai_recommendations": ai_recommendations,
        "last_check": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }


def render_health_check(project):
    """Display Health Check in UI with run button"""

    st.markdown("## Project Health Check")

    # Initialize session state for storing results
    if f'health_check_data_{project.get("id")}' not in st.session_state:
        st.session_state[f'health_check_data_{project.get("id")}'] = None

    # Check if there is a saved report
    health_data = st.session_state.get(
        f'health_check_data_{project.get("id")}', None)

    # Display button depending on report availability
    col1, col2 = st.columns([1, 1])
    with col1:
        if health_data is None:
            button_label = "Run project check"
            button_type = "primary"
        else:
            button_label = "Update report"
            button_type = "secondary"

        if st.button(button_label, type=button_type, width='stretch'):
            with st.spinner("Performing project analysis... This may take some time"):
                health_data = analyze_project_health(project)
                st.session_state[f'health_check_data_{project.get("id")}'] = health_data
                st.rerun()

    # If data exists, display the report
    if health_data is not None:
        st.success(f"Last check: {health_data['last_check']}")
        st.divider()

        # Overall assessment
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if health_data['health_score'] >= 80:
                bg_color = '#e8f5e9'
            elif health_data['health_score'] >= 50:
                bg_color = '#fff8e1'
            else:
                bg_color = '#ffebee'

            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 20px;
                    background-color: {bg_color};
                    border-radius: 10px;
                    margin: 10px 0;
                ">
                    <h1 style="font-size: 48px; margin: 0;">{health_data['health_score']}%</h1>
                    <p>{health_data['status_text']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Progress bar
        st.progress(health_data['health_score'] / 100)

        # Statistics
        st.subheader("Project statistics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total risks", health_data['stats']['total_risks'])
            st.caption(f"HIGH: {health_data['stats']['high_risks']}")
            st.caption(f"MEDIUM: {health_data['stats']['medium_risks']}")
            st.caption(f"LOW: {health_data['stats']['low_risks']}")

        with col2:
            st.metric("Total stages", health_data['stats']['total_stages'])
            st.caption(
                f"Completed: {health_data['stats']['completed_stages']}")
            st.caption(
                f"In progress: {health_data['stats']['in_progress_stages']}")
            st.caption(
                f"Blocked: {health_data['stats']['blocked_stages']}")

        with col3:
            st.metric("Completion",
                      f"{health_data['stats']['completion_rate']}%")
            st.caption(
                f"Overdue: {health_data['stats']['overdue_stages']}")
            if health_data['stats']['missing_fields']:
                st.warning(
                    f"Missing: {len(health_data['stats']['missing_fields'])}")
                with st.expander("Which fields are missing?"):
                    for field in health_data['stats']['missing_fields']:
                        st.write(f"- {field}")
            else:
                st.success("All required fields are filled")

        with col4:
            if health_data['stats']['high_risks'] > 0:
                st.error(
                    f"HIGH risks: {health_data['stats']['high_risks']}")
            if health_data['stats']['blocked_stages'] > 0:
                st.error(
                    f"Blocked stages: {health_data['stats']['blocked_stages']}")
            if health_data['stats']['overdue_stages'] > 0:
                st.warning(
                    f"Overdue stages: {health_data['stats']['overdue_stages']}")

        # AI recommendations
        st.divider()
        st.subheader("AI Recommendations")

        with st.expander("Detailed analysis and recommendations", expanded=True):
            recommendations = health_data['ai_recommendations']

            # Force line breaks before keywords
            formatted = recommendations
            formatted = formatted.replace(
                'ASSESSMENT:', '\n\n**Assessment:**')
            formatted = formatted.replace('PROBLEM 1:', '\n\n**Problem 1:**')
            formatted = formatted.replace('PROBLEM 2:', '\n\n**Problem 2:**')
            formatted = formatted.replace('PROBLEM 3:', '\n\n**Problem 3:**')
            formatted = formatted.replace(
                'RECOMMENDATION 1:', '\n\n**Recommendation 1:**')
            formatted = formatted.replace(
                'RECOMMENDATION 2:', '\n\n**Recommendation 2:**')
            formatted = formatted.replace(
                'RECOMMENDATION 3:', '\n\n**Recommendation 3:**')
            formatted = formatted.replace(
                'RECOMMENDATION 4:', '\n\n**Recommendation 4:**')
            formatted = formatted.replace(
                'RECOMMENDATION 5:', '\n\n**Recommendation 5:**')
            formatted = formatted.replace(
                'RECOMMENDATION', '\n\n**Recommendation')

            st.markdown(formatted)

        # Export and clear buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export report", width='stretch'):
                report_text = f"""# Health Check report for project: {project.get('name')}

**Check date:** {health_data['last_check']}
**Overall score:** {health_data['health_score']}% - {health_data['status']}
**Status:** {health_data['status_text']}

## Statistics
- Risks: {health_data['stats']['total_risks']} (HIGH: {health_data['stats']['high_risks']}, MEDIUM: {health_data['stats']['medium_risks']}, LOW: {health_data['stats']['low_risks']})
- Stages: {health_data['stats']['total_stages']} (Completed: {health_data['stats']['completed_stages']}, In progress: {health_data['stats']['in_progress_stages']}, Blocked: {health_data['stats']['blocked_stages']})
- Completion: {health_data['stats']['completion_rate']}%
- Overdue stages: {health_data['stats']['overdue_stages']}

## AI Recommendations
{health_data['ai_recommendations']}
"""
                st.download_button(
                    label="Download report",
                    data=report_text,
                    file_name=f"health_check_{project.get('name')}_{health_data['last_check'].replace('.', '_').replace(':', '_')}.md",
                    mime="text/markdown",
                    width='stretch'
                )
        with col2:
            if st.button("Clear report", width='stretch'):
                st.session_state[f'health_check_data_{project.get("id")}'] = None
                st.rerun()
