from datetime import datetime
from database.connection import get_connection


def add_task(project_id, title, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (project_id, title, description, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, title, description, 'TODO', datetime.now().isoformat()))
        conn.commit()


def update_task(task_id, data):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status=? WHERE id=?',
                       (data.get('status'), task_id))
        conn.commit()


def delete_task(task_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        conn.commit()
