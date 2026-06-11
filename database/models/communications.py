from datetime import datetime
from database.connection import get_connection


def add_communication(project_id, name, frequency, time, duration, description, location, link):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO communications (project_id, name, frequency, time, duration, description, location, link, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, name, frequency, time, duration, description, location, link, datetime.now().isoformat()))
        conn.commit()


def delete_communication(comm_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM communications WHERE id=?', (comm_id,))
        conn.commit()
