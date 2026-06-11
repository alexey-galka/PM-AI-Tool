from datetime import datetime
from database.connection import get_connection


def add_raci(project_id, artifact_name, role_name, raci_code):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO raci_matrix (project_id, artifact_name, role_name, raci_code, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, artifact_name, role_name, raci_code, datetime.now().isoformat()))
        conn.commit()


def update_raci(raci_id, data):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE raci_matrix 
            SET artifact_name=?, role_name=?, raci_code=?
            WHERE id=?
        ''', (data.get('artifact_name'), data.get('role_name'), data.get('raci_code'), raci_id))
        conn.commit()


def delete_raci(raci_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM raci_matrix WHERE id=?', (raci_id,))
        conn.commit()
