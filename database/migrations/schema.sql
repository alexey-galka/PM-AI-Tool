-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Basic
    name TEXT NOT NULL,
    status TEXT DEFAULT 'PLANNING',
    
    -- Goals and results
    goals TEXT,
    key_results TEXT,
    
    -- Dates
    start_date TEXT,
    end_date TEXT,
    actual_end_date TEXT,
    
    -- Participants
    stakeholders TEXT,
    
    -- Links
    related_projects TEXT,
    replaning TEXT,
    
    -- Problem description
    problem TEXT,
    hypothesis TEXT,
    success_criteria TEXT,
    
    -- Project scope
    must_have TEXT,
    nice_to_have TEXT,
    not_in_scope TEXT,
    
    -- Additional
    created_at TEXT,
    updated_at TEXT
);

-- Risks
CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    impact TEXT,
    description TEXT,
    impact_on_result TEXT,
    impact_on_timeline TEXT,
    mitigation_plan TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Stages
CREATE TABLE IF NOT EXISTS stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT,
    description TEXT,
    risk_id INTEGER,
    risk_text TEXT,
    risk_realization_date TEXT,
    expected_date TEXT,
    actual_date TEXT,
    status TEXT DEFAULT 'PLANNED',
    comment TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (risk_id) REFERENCES risks (id)
);

-- RACI Matrix
CREATE TABLE IF NOT EXISTS raci_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    artifact_name TEXT,
    role_name TEXT,
    raci_code TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Additional materials (articles)
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT,
    url TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'TODO',
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Project team
CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    contact TEXT,
    email TEXT,
    telegram TEXT,
    responsibilities TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Project team
CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT,
    role TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Communications
CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT,
    frequency TEXT,
    time TEXT,
    duration INTEGER,
    description TEXT,
    location TEXT,
    link TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Table for storing meeting audio recordings
CREATE TABLE IF NOT EXISTS audio_recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    duration REAL,
    file_size INTEGER,
    recorded_date TEXT,
    transcript TEXT,
    transcript_status TEXT DEFAULT 'pending',
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

-- Table for storing extracted data from transcription
CREATE TABLE IF NOT EXISTS meeting_minutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL,
    meeting_name TEXT,           -- Meeting name
    decisions TEXT,              -- Decisions made
    action_items TEXT,           -- Actions and tasks
    participants TEXT,           -- Participants (JSON array)
    topics TEXT,                 -- Topics discussed
    next_meeting_date TEXT,
    summary TEXT,                -- Brief summary
    raw_extraction TEXT,
    created_at TEXT,
    FOREIGN KEY (recording_id) REFERENCES audio_recordings (id) ON DELETE CASCADE
);