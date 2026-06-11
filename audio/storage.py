import os
from config.settings import AUDIO_STORAGE_DIR


def ensure_audio_dir():
    """Creates audio storage directory if it doesn't exist"""
    AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_audio_file(uploaded_file, project_id, filename):
    """Saves uploaded audio file"""
    ensure_audio_dir()

    # Create subdirectory for the project
    project_dir = AUDIO_STORAGE_DIR / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    file_path = project_dir / filename
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def get_audio_file_path(project_id, filename):
    """Gets path to audio file"""
    project_dir = AUDIO_STORAGE_DIR / str(project_id)
    file_path = project_dir / filename
    return str(file_path) if file_path.exists() else None


def delete_audio_file(project_id, filename):
    """Deletes audio file"""
    file_path = get_audio_file_path(project_id, filename)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False