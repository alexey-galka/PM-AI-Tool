from datetime import datetime
from database.connection import get_connection


def add_risk(project_id, impact, description, impact_on_result, impact_on_timeline, mitigation_plan):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO risks (project_id, impact, description, impact_on_result, impact_on_timeline, mitigation_plan, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, impact, description, impact_on_result, impact_on_timeline, mitigation_plan, datetime.now().isoformat()))
        conn.commit()


def update_risk(risk_id, data):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE risks 
            SET impact=?, description=?, impact_on_result=?, impact_on_timeline=?, mitigation_plan=?
            WHERE id=?
        ''', (data.get('impact'), data.get('description'), data.get('impact_on_result'),
              data.get('impact_on_timeline'), data.get('mitigation_plan'), risk_id))
        conn.commit()


def delete_risk(risk_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM risks WHERE id=?', (risk_id,))
        conn.commit()
