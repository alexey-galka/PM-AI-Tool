# PM AI Tool - Project Management System
A comprehensive project management tool built with Streamlit, featuring AI-powered assistance for project planning, risk management, meeting transcription, and intelligent Q&A.

## Key Features Explained
### AI Risk Generation
Automatically generates 4-5 relevant risks based on project problem, hypothesis, and success criteria. Each risk includes impact level, description, impact analysis, and mitigation plan.

### AI Stages Generation
Creates 4-7 logical project stages with:
- Stage names and descriptions
- Duration estimates (1-30 days)
- Automatic date calculation
- Risk linking based on keywords

### AI RACI and Tasks
- Generates a reference for RACI based on your project team, so you can use it as a template or just apply it
- Creates a stack of tasks to do during a project to make sure that project results will be delivered

### Health Check System
Calculates health score based on:
- Number of HIGH/MEDIUM risks (-10 points per HIGH risk)
- Blocked stages (-15 points each)
- Overdue stages (-10 points each)
- Missing required fields (-15 points each)
- No stages defined (-20 points)

Provides AI-powered assessment, problem identification, and recommendations.

### RAG Q&A System
- Indexes all project data in ChromaDB vector database
- Uses multilingual embeddings
- Returns answers with source attribution (e.g., "Meeting transcript from 2024-01-15", "Project passport - Goals")
- Supports natural language queries like:
  - "What are the main risks of this project?"
  - "Show me the project goals"
  - "What decisions were made in the last meeting?"
  - "Who is responsible for testing?"

## Features
### 1. Project Management
- **Create new projects** with detailed information including goals, problem statements, hypotheses, and success criteria
- **Edit existing projects** with full data management
- **Project dashboard** with status overview, statistics, and filtering
- **Project scope definition** (Must have, Nice to have, Not in scope)
- **Stakeholder management**

### 2. Risk Management
- **AI-powered risk generation** based on project description
- Manual risk addition with impact levels (HIGH/MEDIUM/LOW)
- Risk mitigation planning
- Risk impact analysis on results and timeline

### 3. Stage Planning
- **AI-generated project stages** based on project information
- Stage duration calculation (1-30 days)
- Automatic date calculation based on stage duration
- Stage status tracking (PLANNED, IN_PROGRESS, DONE, BLOCKED)
- Link stages to risks

### 4. RACI Matrix
- Define roles and responsibilities
- RACI codes: Responsible, Accountable, Consulted, Informed
- Artifact and role mapping
- Matrix preview in table format

### 5. Team Management
- Team member registration with roles
- Contact information storage

### 6. Communication Plan
- Meeting scheduling with frequency (Daily/Weekly/Monthly/On demand)
- Meeting duration and location tracking
- Video conferencing links

### 7. Audio Transcription & Meeting Minutes
- **Upload audio recordings** (MP3, WAV, M4A, OGG, FLAC)
- **Automatic transcription** using Whisper AI
- **AI-powered meeting minutes extraction** including:
  - Decisions made
  - Action items with assignees
  - Discussion topics
  - Meeting summaries
- Edit meeting minutes manually
- Persistent storage of transcripts and minutes

### 8. Health Check
- **Automatic project health scoring** (0-100%)
- Risk and stage statistics
- Missing fields detection
- **AI-powered analysis** with:
  - Project assessment
  - Problem identification (3 problems)
  - Actionable recommendations (5 recommendations)
- Exportable health check reports

### 9. Weekly Digest
- **AI-generated weekly project summaries**
- Progress tracking
- Completed and upcoming stages
- Risk highlights
- Recommendations for next steps
- Export to Markdown format

### 10. RAG (Retrieval-Augmented Generation) Q&A
- **Ask questions about your project** in natural language
- Intelligent search across:
  - Project passport information
  - Risk descriptions
  - Stage plans
  - RACI matrix
  - Team information
  - Meeting transcripts
  - Tasks and articles
- **Source-attributed answers** (shows where information comes from)
- Persistent chat history
- Project reindexing capability

## Technology Stack
- **Frontend**: Streamlit
- **Database**: SQLite
- **Vector Database**: ChromaDB (for RAG)
- **AI Models**:
  - Ollama (LLM for text generation)
  - LFM 2.5:8b
  - Whisper (audio transcription)
  - Multilingual embedding model for RAG
- **Audio Processing**: Whisper AI

## Installation
### Prerequisites
- Python 3.11+
- Ollama installed locally
- Whisper model (auto-downloads on first use)

### Setup
1. Clone the repository
> git clone https://github.com/alexey-galka/PM-AI-Tool
cd PM-AI-Tool

2. Create virtual environment
> python -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
> pip install -r requirements.txt

4. Install Ollama and pull models
> ollama pull llama3.2:3b
> ollama pull jeffh/intfloat-multilingual-e5-large:f16

5. Run the application
> streamlit run app.py

## Usage Workflow
### Creating a New Project
1. Click "New Project" in sidebar
2. Fill basic information (name, goals, dates, stakeholders)
3. Define problem, hypothesis, and success criteria
4. Set project scope (must have, nice to have, not in scope)
5. Generate risks automatically or add manually
6. Generate stages automatically or add manually
7. Define RACI matrix
8. Add team members
9. Set up communication plan
10. Add articles and tasks
11. Submit the form

### Working with an Existing Project
1. Select project from dashboard
2. View project passport with all information
3. Navigate through tabs:
   - **Passport** - Project overview and statistics
   - **Risks** - Risk register with detailed view
   - **Stages** - Timeline with stage status
   - **RACI** - Responsibility matrix
   - **Materials** - Articles and tasks
   - **Health Check** - Run health analysis
   - **Team** - Team members list
   - **Communications** - Meeting schedule
   - **Meetings** - Upload and manage meeting recordings
   - **Digest** - Generate weekly summary
   - **Q&A** - Ask questions about the project

### Meeting Management
1. Go to "Meetings" tab
2. Upload audio file (MP3, WAV, M4A, OGG, FLAC)
3. Enter meeting name and participants
4. System automatically:
   - Transcribes audio using Whisper
   - Extracts decisions, action items, topics
   - Generates meeting summary
5. Edit minutes manually if needed
6. View all past meetings in the list

## Troubleshooting
### Common Issues
**JSON parsing errors in AI responses**
- The system includes fallback parsers that extract JSON even from malformed responses
- Default values are provided when extraction fails

**Model returns thinking/reasoning text**
- The system automatically trims responses to remove prefixes like "Thinking..."
- Extracts content after "...done thinking." markers

**Audio transcription fails**
- Ensure audio file format is supported (MP3, WAV, M4A, OGG, FLAC)
- Check Whisper model is properly installed
- Verify file is not corrupted

**RAG Q&A not working**
- Click "Reindex project" to rebuild the vector index
- Ensure project has sufficient data (passport, risks, stages, etc.)
- Check Ollama embedding model is running

## License
MIT License