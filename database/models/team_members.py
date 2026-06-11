from datetime import datetime
from database.connection import get_connection


def add_team_member(project_id, name, role):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO team (project_id, name, role, created_at)
            VALUES (?, ?, ?, ?)
        ''', (project_id, name, role, datetime.now().isoformat()))
        conn.commit()


def delete_team_member(member_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM team WHERE id=?', (member_id,))
        conn.commit()
