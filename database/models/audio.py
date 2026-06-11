import sqlite3
from datetime import datetime
from database.connection import get_connection


def add_audio_recording(project_id, filename, file_path, file_size, duration, transcript, recording_date=None):
    """Add meeting audio recording"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_recordings (project_id, filename, file_path, file_size, duration, transcript, recording_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, filename, file_path, file_size, duration, transcript, recording_date or datetime.now().isoformat(),
              datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid


def get_audio_recordings(project_id):
    """Get all audio recordings of the project"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM audio_recordings 
            WHERE project_id = ? 
            ORDER BY recording_date DESC
        ''', (project_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_audio_recording(recording_id):
    """Get audio recording by ID"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM audio_recordings WHERE id = ?', (recording_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_audio_recording(recording_id, data):
    """Update audio recording (transcript, summary, etc.)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE audio_recordings 
            SET transcript = ?, summary = ?, decisions = ?, action_items = ?, updated_at = ?
            WHERE id = ?
        ''', (data.get('transcript'), data.get('summary'), data.get('decisions'),
              data.get('action_items'), datetime.now().isoformat(), recording_id))
        conn.commit()


def delete_audio_recording(recording_id):
    """Delete audio recording"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM audio_recordings WHERE id = ?', (recording_id,))
        conn.commit()


def add_action_item(recording_id, description, assignee=None, due_date=None):
    """Add action item from meeting"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO action_items (recording_id, description, assignee, due_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recording_id, description, assignee, due_date, 'pending', datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid


def get_action_items(recording_id):
    """Get all action items for a recording"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM action_items WHERE recording_id = ? ORDER BY due_date', (recording_id,))
        return [dict(row) for row in cursor.fetchall()]


def update_action_item_status(item_id, status):
    """Update action item status"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE action_items SET status = ? WHERE id = ?', (status, item_id))
        conn.commit()