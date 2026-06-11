import sqlite3
from datetime import datetime
from database.connection import get_connection


def get_next_milestone(project_id):
    """Get the nearest incomplete stage"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, expected_date, status 
            FROM stages 
            WHERE project_id = ? AND status != 'DONE'
            ORDER BY expected_date 
            LIMIT 1
        ''', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_stage(project_id, name, description, expected_date, status, comment):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stages (project_id, name, description, expected_date, status, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, name, description, expected_date.isoformat(), status, comment, datetime.now().isoformat()))
        conn.commit()


def update_stage_status(stage_id, status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE stages SET status = ? WHERE id = ?', (status, stage_id))
        conn.commit()


def update_stage(stage_id, data):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE stages 
            SET name=?, description=?, expected_date=?, status=?, comment=?
            WHERE id=?
        ''', (data.get('name'), data.get('description'), data.get('expected_date'),
              data.get('status'), data.get('comment'), stage_id))
        conn.commit()


def delete_stage(stage_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM stages WHERE id=?', (stage_id,))
        conn.commit()