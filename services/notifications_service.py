from datetime import datetime, date


def get_overdue_stages(project):
    """Get overdue stages of the project"""
    stages = project.get('stages', [])
    today = date.today()

    overdue = []
    for stage in stages:
        expected_date = stage.get('expected_date')
        if expected_date and stage.get('status') not in ['DONE', 'BLOCKED']:
            if isinstance(expected_date, str):
                expected_date = datetime.fromisoformat(expected_date).date()
            if expected_date < today:
                overdue.append({
                    'project_id': project.get('id'),
                    'project_name': project.get('name'),
                    'stage_id': stage.get('id'),
                    'stage_name': stage.get('name'),
                    'expected_date': expected_date,
                    'days_overdue': (today - expected_date).days,
                    'status': stage.get('status')
                })
    return overdue