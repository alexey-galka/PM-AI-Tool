import sqlite3
import json
from datetime import datetime
from database.connection import get_connection


def save_recording_metadata(project_id, filename, file_path, duration, file_size, recorded_date=None):
    """Saves audio recording metadata"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_recordings (project_id, filename, file_path, duration, file_size, recorded_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, filename, file_path, duration, file_size, recorded_date or datetime.now().isoformat(),
              datetime.now().isoformat(), datetime.now().isoformat()))
        return cursor.lastrowid


def get_recordings_by_project(project_id):
    """Get all audio recordings by project"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM audio_recordings 
            WHERE project_id = ? 
            ORDER BY recorded_date DESC
        ''', (project_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_recording(recording_id):
    """Get audio recording by ID"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM audio_recordings WHERE id = ?', (recording_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_transcript(recording_id, transcript, status='completed'):
    """Update transcription"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE audio_recordings 
            SET transcript = ?, transcript_status = ?, updated_at = ?
            WHERE id = ?
        ''', (transcript, status, datetime.now().isoformat(), recording_id))
        conn.commit()


def save_meeting_minutes(recording_id, decisions, action_items, participants, topics, next_meeting_date, meeting_name, raw_extraction, summary=""):
    """Save extracted meeting data"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meeting_minutes (recording_id, meeting_name, decisions, action_items, participants, topics, next_meeting_date, summary, raw_extraction, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (recording_id, meeting_name, decisions, action_items, json.dumps(participants, ensure_ascii=False),
              topics, next_meeting_date, summary, raw_extraction, datetime.now().isoformat()))
        return cursor.lastrowid


def get_meeting_minutes(recording_id):
    """Get extracted meeting data"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM meeting_minutes WHERE recording_id = ?', (recording_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get('participants'):
                try:
                    result['participants'] = json.loads(result['participants'])
                except:
                    result['participants'] = []
            return result
        return None


def update_meeting_minutes(recording_id, meeting_name, decisions, action_items, participants, topics, next_meeting_date, summary):
    """Updates meeting minutes"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE meeting_minutes 
            SET meeting_name = ?, decisions = ?, action_items = ?, participants = ?, 
                topics = ?, next_meeting_date = ?, summary = ?, created_at = ?
            WHERE recording_id = ?
        ''', (meeting_name, decisions, action_items, json.dumps(participants, ensure_ascii=False),
              topics, next_meeting_date, summary, datetime.now().isoformat(), recording_id))
        conn.commit()


def update_audio_status(recording_id, status):
    """Update audio processing status"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE audio_recordings 
            SET transcript_status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), recording_id))
        conn.commit()


def delete_recording(recording_id):
    """Deletes audio recording from database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM meeting_minutes WHERE recording_id = ?', (recording_id,))
        cursor.execute(
            'DELETE FROM audio_recordings WHERE id = ?', (recording_id,))
        conn.commit()
        return True


def delete_audio_recording(recording_id):
    """Deletes audio recording from database (alias)"""
    return delete_recording(recording_id)
