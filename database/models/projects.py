import sqlite3
import json
from datetime import datetime
from database.connection import get_connection


def get_all_projects():
    """Get all projects for dashboard"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, goals, end_date, status, created_at 
            FROM projects ORDER BY created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]


def get_all_projects_short():
    """For sidebar: id, name"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name FROM projects ORDER BY created_at DESC")
        return cursor.fetchall()


def get_project_full(project_id):
    """Get full project information with all related data"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Main project
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = cursor.fetchone()

        if not project:
            return None

        result = dict(project)

        # Parse JSON fields
        for field in ['stakeholders', 'related_projects', 'must_have', 'nice_to_have', 'not_in_scope']:
            if result.get(field):
                try:
                    result[field] = json.loads(result[field])
                except:
                    result[field] = []
            else:
                result[field] = []

        # Risks
        cursor.execute(
            'SELECT * FROM risks WHERE project_id = ?', (project_id,))
        result['risks'] = [dict(row) for row in cursor.fetchall()]

        # Stages with risk data
        cursor.execute('''
            SELECT 
                s.*, 
                r.description as risk_description, 
                r.impact as risk_impact
            FROM stages s
            LEFT JOIN risks r ON s.risk_id = r.id
            WHERE s.project_id = ?
            ORDER BY s.expected_date
        ''', (project_id,))
        result['stages'] = [dict(row) for row in cursor.fetchall()]

        # Add risk_text if missing (for backward compatibility)
        for stage in result['stages']:
            if 'risk_text' not in stage or not stage['risk_text']:
                # If risk_description exists, use it as risk_text
                if stage.get('risk_description'):
                    stage['risk_text'] = stage['risk_description']

        # RACI
        cursor.execute(
            'SELECT * FROM raci_matrix WHERE project_id = ?', (project_id,))
        result['raci'] = [dict(row) for row in cursor.fetchall()]

        # Articles
        cursor.execute(
            'SELECT * FROM articles WHERE project_id = ?', (project_id,))
        result['articles'] = [dict(row) for row in cursor.fetchall()]

        # Tasks
        cursor.execute(
            'SELECT * FROM tasks WHERE project_id = ?', (project_id,))
        result['tasks'] = [dict(row) for row in cursor.fetchall()]

        # Team
        cursor.execute(
            'SELECT * FROM team WHERE project_id = ?', (project_id,))
        result['team'] = [dict(row) for row in cursor.fetchall()]

        # Communications
        cursor.execute(
            'SELECT * FROM communications WHERE project_id = ?', (project_id,))
        result['communications'] = [dict(row) for row in cursor.fetchall()]

        # Meeting audio recordings
        cursor.execute(
            'SELECT * FROM audio_recordings WHERE project_id = ?', (project_id,))
        result['audio_recordings'] = [dict(row) for row in cursor.fetchall()]

        return result


def create_project(data):
    """Create project with all fields, including related tables"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Insert main project
        cursor.execute('''
            INSERT INTO projects (
                name, status, goals, key_results, start_date, end_date, actual_end_date,
                stakeholders, related_projects, replaning, problem, hypothesis,
                success_criteria, must_have, nice_to_have, not_in_scope, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('status', 'PLANNING'),
            data.get('goals'),
            data.get('key_results'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('actual_end_date'),
            json.dumps(data.get('stakeholders', []), ensure_ascii=False),
            json.dumps(data.get('related_projects', []), ensure_ascii=False),
            data.get('replaning'),
            data.get('problem'),
            data.get('hypothesis'),
            data.get('success_criteria'),
            json.dumps(data.get('must_have', []), ensure_ascii=False),
            json.dumps(data.get('nice_to_have', []), ensure_ascii=False),
            json.dumps(data.get('not_in_scope', []), ensure_ascii=False),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        project_id = cursor.lastrowid

        # ========== 1. SAVE RISKS ==========
        risk_id_map = {}
        for idx, risk in enumerate(data.get('risks', [])):
            if risk.get('description'):
                cursor.execute('''
                    INSERT INTO risks (project_id, impact, description, impact_on_result, impact_on_timeline, mitigation_plan, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, risk.get('impact'), risk.get('description'),
                      risk.get('impact_on_result'), risk.get(
                          'impact_on_timeline'),
                      risk.get('mitigation_plan'), datetime.now().isoformat()))
                risk_id_map[idx] = cursor.lastrowid

        # ========== 2. SAVE STAGES ==========
        for stage in data.get('stages', []):
            if stage.get('name'):
                print(
                    f"  - Saving stage: {stage.get('name')}, risk_text='{stage.get('risk_text', '')}'")

        for stage in data.get('stages', []):
            if stage.get('name'):
                expected_date = stage.get('expected_date')
                if hasattr(expected_date, 'isoformat'):
                    expected_date = expected_date.isoformat()

                risk_realization_date = stage.get('risk_realization_date')
                if risk_realization_date and hasattr(risk_realization_date, 'isoformat'):
                    risk_realization_date = risk_realization_date.isoformat()

                actual_date = stage.get('actual_date')
                if actual_date and hasattr(actual_date, 'isoformat'):
                    actual_date = actual_date.isoformat()

                # Get risk ID if exists
                risk_id = None
                temp_risk_id = stage.get('risk_id')
                if temp_risk_id is not None and temp_risk_id in risk_id_map:
                    risk_id = risk_id_map[temp_risk_id]

                cursor.execute('''
                    INSERT INTO stages (project_id, name, description, expected_date, status, comment, created_at, risk_text, risk_realization_date, actual_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (project_id,
                      stage.get('name'),
                      stage.get('description'),
                      expected_date,
                      stage.get('status', 'PLANNED'),
                      stage.get('comment'),
                      datetime.now().isoformat(),
                      stage.get('risk_text', ''),  # Save risk text
                      risk_realization_date,
                      actual_date))

        # ========== 3. SAVE OTHER DATA ==========
        # RACI
        for raci in data.get('raci', []):
            if raci.get('artifact_name') and raci.get('role_name'):
                cursor.execute('''
                    INSERT INTO raci_matrix (project_id, artifact_name, role_name, raci_code, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, raci.get('artifact_name'), raci.get('role_name'),
                      raci.get('raci_code'), datetime.now().isoformat()))

        # Articles
        for article in data.get('articles', []):
            if article.get('title'):
                cursor.execute('''
                    INSERT INTO articles (project_id, title, url, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, article.get('title'), article.get('url'), datetime.now().isoformat()))

        # Tasks
        for task in data.get('tasks', []):
            if task.get('title'):
                cursor.execute('''
                    INSERT INTO tasks (project_id, title, description, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, task.get('title'), task.get('description'), 'TODO', datetime.now().isoformat()))

        # Team
        for member in data.get('team', []):
            if member.get('name'):
                cursor.execute('''
                    INSERT INTO team (project_id, name, role, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, member.get('name'), member.get('role'), datetime.now().isoformat()))

        # Communications
        for comm in data.get('communications', []):
            if comm.get('name'):
                cursor.execute('''
                    INSERT INTO communications (project_id, name, frequency, time, duration, description, location, link, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, comm.get('name'), comm.get('frequency'),
                      comm.get('time'), comm.get(
                          'duration'), comm.get('description'),
                      comm.get('location'), comm.get('link'), datetime.now().isoformat()))

        conn.commit()
        return project_id


def update_project_status(project_id, status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE projects SET status = ? WHERE id = ?', (status, project_id))
        conn.commit()


def update_project(project_id, data):
    """Update main project fields"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE projects 
            SET name=?, status=?, goals=?, key_results=?, 
                start_date=?, end_date=?, actual_end_date=?,
                stakeholders=?, problem=?, hypothesis=?, success_criteria=?,
                must_have=?, nice_to_have=?, not_in_scope=?, updated_at=?
            WHERE id=?
        ''', (
            data.get('name'),
            data.get('status'),
            data.get('goals'),
            data.get('key_results'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('actual_end_date'),
            json.dumps(data.get('stakeholders', []), ensure_ascii=False),
            data.get('problem'),
            data.get('hypothesis'),
            data.get('success_criteria'),
            json.dumps(data.get('must_have', []), ensure_ascii=False),
            json.dumps(data.get('nice_to_have', []), ensure_ascii=False),
            json.dumps(data.get('not_in_scope', []), ensure_ascii=False),
            datetime.now().isoformat(),
            project_id
        ))
        conn.commit()


def update_project_full(project_id, data):
    """Full update of project with all related data"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Update main project
        cursor.execute('''
            UPDATE projects 
            SET name=?, status=?, goals=?, key_results=?, 
                start_date=?, end_date=?, actual_end_date=?,
                stakeholders=?, related_projects=?, replaning=?,
                problem=?, hypothesis=?, success_criteria=?,
                must_have=?, nice_to_have=?, not_in_scope=?, updated_at=?
            WHERE id=?
        ''', (
            data.get('name'),
            data.get('status'),
            data.get('goals'),
            data.get('key_results'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('actual_end_date'),
            json.dumps(data.get('stakeholders', []), ensure_ascii=False),
            json.dumps(data.get('related_projects', []), ensure_ascii=False),
            data.get('replaning'),
            data.get('problem'),
            data.get('hypothesis'),
            data.get('success_criteria'),
            json.dumps(data.get('must_have', []), ensure_ascii=False),
            json.dumps(data.get('nice_to_have', []), ensure_ascii=False),
            json.dumps(data.get('not_in_scope', []), ensure_ascii=False),
            datetime.now().isoformat(),
            project_id
        ))

        # Delete old related data
        cursor.execute('DELETE FROM risks WHERE project_id = ?', (project_id,))
        cursor.execute(
            'DELETE FROM stages WHERE project_id = ?', (project_id,))
        cursor.execute(
            'DELETE FROM raci_matrix WHERE project_id = ?', (project_id,))
        cursor.execute(
            'DELETE FROM articles WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM team WHERE project_id = ?', (project_id,))
        cursor.execute(
            'DELETE FROM communications WHERE project_id = ?', (project_id,))

        # Insert new risks
        for risk in data.get('risks', []):
            if risk.get('description'):
                cursor.execute('''
                    INSERT INTO risks (project_id, impact, description, impact_on_result, impact_on_timeline, mitigation_plan, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, risk.get('impact'), risk.get('description'),
                      risk.get('impact_on_result'), risk.get(
                          'impact_on_timeline'),
                      risk.get('mitigation_plan'), datetime.now().isoformat()))

        # Insert new stages
        for stage in data.get('stages', []):
            if stage.get('name'):
                cursor.execute('''
                    INSERT INTO stages (project_id, name, description, expected_date, status, comment, created_at, risk_text, risk_realization_date, actual_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (project_id,
                      stage.get('name'),
                      stage.get('description'),
                      stage.get('expected_date'),
                      stage.get('status'),
                      stage.get('comment'),
                      datetime.now().isoformat(),
                      stage.get('risk_text', ''),
                      stage.get('risk_realization_date'),
                      stage.get('actual_date')))

        # Insert RACI
        for raci in data.get('raci', []):
            if raci.get('artifact_name') and raci.get('role_name'):
                cursor.execute('''
                    INSERT INTO raci_matrix (project_id, artifact_name, role_name, raci_code, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, raci.get('artifact_name'), raci.get('role_name'),
                      raci.get('raci_code'), datetime.now().isoformat()))

        # Insert articles
        for article in data.get('articles', []):
            if article.get('title'):
                cursor.execute('''
                    INSERT INTO articles (project_id, title, url, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, article.get('title'), article.get('url'), datetime.now().isoformat()))

        # Insert tasks
        for task in data.get('tasks', []):
            if task.get('title'):
                cursor.execute('''
                    INSERT INTO tasks (project_id, title, description, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, task.get('title'), task.get('description'),
                      task.get('status', 'TODO'), datetime.now().isoformat()))

        # Insert team
        for member in data.get('team', []):
            if member.get('name'):
                cursor.execute('''
                    INSERT INTO team (project_id, name, role, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, member.get('name'), member.get('role'), datetime.now().isoformat()))

        # Insert communications
        for comm in data.get('communications', []):
            if comm.get('name'):
                cursor.execute('''
                    INSERT INTO communications (project_id, name, frequency, time, duration, description, location, link, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, comm.get('name'), comm.get('frequency'),
                      comm.get('time'), comm.get(
                          'duration'), comm.get('description'),
                      comm.get('location'), comm.get('link'), datetime.now().isoformat()))

        conn.commit()


def get_project_short(project_id):
    """Get brief project information (name only)"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_project(project_id):
    """Full deletion of project and all related data"""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'DELETE FROM risks WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM stages WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM raci_matrix WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM articles WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM tasks WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM team WHERE project_id = ?', (project_id,))
            cursor.execute(
                'DELETE FROM communications WHERE project_id = ?', (project_id,))
            # Delete audio recordings and related data
            cursor.execute(
                'DELETE FROM meeting_minutes WHERE recording_id IN (SELECT id FROM audio_recordings WHERE project_id = ?)', (project_id,))
            cursor.execute(
                'DELETE FROM audio_recordings WHERE project_id = ?', (project_id,))
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting project: {e}")
            conn.rollback()
            return False