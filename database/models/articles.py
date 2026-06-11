from datetime import datetime
from database.connection import get_connection


def add_article(project_id, title, url):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (project_id, title, url, created_at)
            VALUES (?, ?, ?, ?)
        ''', (project_id, title, url, datetime.now().isoformat()))
        conn.commit()


def delete_article(article_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles WHERE id=?', (article_id,))
        conn.commit()
