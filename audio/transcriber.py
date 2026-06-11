import os
import json
import re
from services.ai_service import call_ollama
from datetime import datetime
from config.settings import MODELS_DIR, TRANSCRIPTS_DIR, ensure_dirs, WHISPER_MODEL


def transcribe_audio(file_path, model_name=WHISPER_MODEL):
    if not os.path.exists(file_path):
        return f"Error: Audio file not found {file_path}"

    ensure_dirs()

    try:
        import whisper
        model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
        result = model.transcribe(file_path, fp16=False)
        return result["text"]
    except ImportError:
        return "Error: openai-whisper is not installed"
    except Exception as e:
        return f"Transcription error: {str(e)}"


def fix_json_string(json_str):
    """Fixes common JSON errors more aggressively"""
    if not json_str:
        return "{}"

    # Remove any non-JSON text before the first { and after the last }
    first_brace = json_str.find('{')
    last_brace = json_str.rfind('}')
    if first_brace != -1 and last_brace != -1:
        json_str = json_str[first_brace:last_brace + 1]

    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    # Add missing quotes around keys
    json_str = re.sub(
        r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)

    # Fix unescaped quotes inside strings
    json_str = re.sub(r'(?<!\\)"', '\\"', json_str)
    # But restore the quotes we just added around keys
    json_str = re.sub(r'\\"([a-zA-Z_][a-zA-Z0-9_]*)\\":', r'"\1":', json_str)
    # Restore quotes around string values that were escaped
    json_str = re.sub(r':\\"', r':"', json_str)
    json_str = re.sub(r'\\"([^"]*)\\",', r'"\1",', json_str)
    json_str = re.sub(r'\\"([^"]*)\\""', r'"\1"', json_str)

    # Remove trailing commas again (in case they were created)
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    # Fix missing commas between array items
    json_str = re.sub(r'"\s+"', '", "', json_str)

    return json_str


def extract_project_info(transcript):
    """Extracts information from transcription to fill project passport"""

    if len(transcript) < 50:
        print("Transcription is too short")
        return None

#     prompt = f"""Analyze the text and fill in the project passport. Fill in ALL fields.

# Text:
# {transcript}

# Return ONLY valid JSON. ALL fields MUST be filled in. ALL 9 fields must be included:
# - name: project name (string)
# - goals: project goals (string)
# - key_results: key results (string)
# - problem: problem the project solves (string)
# - hypothesis: project hypothesis (string)
# - success_criteria: success criteria (string)
# - must_have: mandatory requirements (array of strings)
# - nice_to_have: desirable requirements (array of strings)
# - not_in_scope: what is not included in the project (array of strings)

# If there is no information in the text, write "Not specified" for strings and [] for arrays.

# Example response:
# {{
#      "name": "Project name",
#      "goals": "Project goals",
#      "key_results": "Key results",
#      "problem": "Project problem",
#      "hypothesis": "Project hypothesis",
#      "success_criteria": "Success criteria",
#      "must_have": ["Requirement1", "Requirement2"],
#      "nice_to_have": ["Requirement1", "Requirement2"],
#      "not_in_scope": ["Requirement1", "Requirement2"]
# }}

# IMPORTANT: Return ONLY the JSON object, no other text before or after. 
# """

    prompt = f"""You are a project manager assistant. Extract project information from the following meeting transcript or lecture.

TRANSCRIPT:
{transcript}

Based on this transcript, create a project passport. If the transcript is a lecture or training material, create a project around applying those skills.

Return ONLY valid JSON with these 9 fields:

1. name: A project name derived from the main topic (string)
2. goals: What this project aims to achieve (string)
3. key_results: Measurable outcomes (string) 
4. problem: The problem this project solves (string)
5. hypothesis: What we believe will happen if we solve the problem (string)
6. success_criteria: How we measure success (string)
7. must_have: List of essential requirements for this project (array of strings)
8. nice_to_have: List of nice-to-have features (array of strings)
9. not_in_scope: What is explicitly excluded (array of strings)

RULES:
- If the transcript is a lecture/training, create a project about IMPLEMENTING those skills
- Extract at least 3 must-have requirements from the content
- For the example above (public speaking lecture), must_have should include: ["Public speaking techniques", "Pacing strategies", "Visual aids usage"]
- For strings with no info, use "Learn and apply main topic skills"
- For arrays with no info, extract 2-3 items from the transcript content
- NEVER leave arrays empty - extract at least 2 items from the text

EXAMPLE RESPONSE for a public speaking lecture:
{{
    "name": "Public Speaking Skills Development Project",
    "goals": "Master effective public speaking techniques including proper pacing, pause usage, and audience engagement",
    "key_results": "Deliver 3 successful presentations with positive feedback, reduce speaking speed by 25%",
    "problem": "Speakers often rush through presentations without allowing pauses, losing audience attention",
    "hypothesis": "Learning proper pacing and pause techniques will improve audience engagement",
    "success_criteria": "Audience feedback score of 4.5+, natural use of pauses in presentations",
    "must_have": ["Pacing and pause control techniques", "Strong presentation openings", "Visual aids integration", "Note-taking strategies"],
    "nice_to_have": ["Advanced storytelling techniques", "Handling Q&A sessions", "Managing presentation anxiety"],
    "not_in_scope": ["One-on-one coaching", "Writing presentation scripts"]
}}

Return ONLY the JSON object, no other text.
"""
    
    response = call_ollama(prompt)

    # Clean response from control characters
    response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response)
    response = re.sub(r'[\x00-\x1f\x7f]', '', response)

    print(f"Raw response (first 500 chars): {response[:500]}")

    # Try to extract JSON with multiple strategies
    result = None

    # Strategy 1: Direct JSON parsing with fixing
    try:
        json_str = fix_json_string(response)
        result = json.loads(json_str)
        print("Strategy 1 succeeded")
    except json.JSONDecodeError as e:
        print(f"Strategy 1 failed: {e}")

        # Strategy 2: Try to find JSON with regex and fix
        try:
            json_match = re.search(
                r'\{[^{}]*\{.*\}[^{}]*\}', response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                json_str = fix_json_string(json_str)
                result = json.loads(json_str)
                print("Strategy 2 succeeded")
        except json.JSONDecodeError as e2:
            print(f"Strategy 2 failed: {e2}")

            # Strategy 3: Build JSON manually by extracting key-value pairs
            try:
                result = {}

                # Extract name
                name_match = re.search(
                    r'"name"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if name_match:
                    result['name'] = name_match.group(1)

                # Extract goals
                goals_match = re.search(
                    r'"goals"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if goals_match:
                    result['goals'] = goals_match.group(1)

                # Extract key_results
                kr_match = re.search(
                    r'"key_results"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if kr_match:
                    result['key_results'] = kr_match.group(1)

                # Extract problem
                problem_match = re.search(
                    r'"problem"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if problem_match:
                    result['problem'] = problem_match.group(1)

                # Extract hypothesis
                hypothesis_match = re.search(
                    r'"hypothesis"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if hypothesis_match:
                    result['hypothesis'] = hypothesis_match.group(1)

                # Extract success_criteria
                sc_match = re.search(
                    r'"success_criteria"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
                if sc_match:
                    result['success_criteria'] = sc_match.group(1)

                # Extract arrays
                must_have_match = re.search(
                    r'"must_have"\s*:\s*\[(.*?)\]', response, re.IGNORECASE | re.DOTALL)
                if must_have_match:
                    items = re.findall(r'"([^"]+)"', must_have_match.group(1))
                    result['must_have'] = items

                nice_to_have_match = re.search(
                    r'"nice_to_have"\s*:\s*\[(.*?)\]', response, re.IGNORECASE | re.DOTALL)
                if nice_to_have_match:
                    items = re.findall(
                        r'"([^"]+)"', nice_to_have_match.group(1))
                    result['nice_to_have'] = items

                not_in_scope_match = re.search(
                    r'"not_in_scope"\s*:\s*\[(.*?)\]', response, re.IGNORECASE | re.DOTALL)
                if not_in_scope_match:
                    items = re.findall(
                        r'"([^"]+)"', not_in_scope_match.group(1))
                    result['not_in_scope'] = items

                if result:
                    print("Strategy 3 succeeded")
            except Exception as e3:
                print(f"Strategy 3 failed: {e3}")

    # Fill in default values for missing fields
    default_fields = {
        "name": "Not specified",
        "goals": "Not specified",
        "key_results": "Not specified",
        "problem": "Not specified",
        "hypothesis": "Not specified",
        "success_criteria": "Not specified",
        "must_have": [],
        "nice_to_have": [],
        "not_in_scope": []
    }

    if result:
        for key in default_fields:
            if key not in result or result[key] is None or result[key] == "":
                result[key] = default_fields[key]
            # Ensure arrays are actually arrays
            if key in ['must_have', 'nice_to_have', 'not_in_scope'] and not isinstance(result[key], list):
                if isinstance(result[key], str) and result[key]:
                    result[key] = [result[key]]
                else:
                    result[key] = []
        return result

    print("All parsing strategies failed")
    return None


def trim_ai_response(text):
    """Remove thinking/reasoning prefix from model response"""
    if not text:
        return text

    # Find ...done thinking. and return everything after it
    match = re.search(r'\.\.\.done thinking\.?\s*', text, re.IGNORECASE)
    if match:
        return text[match.end():].strip()

    # Find first occurrence of DECISIONS: or TOPICS: or SUMMARY:
    patterns = [r'DECISIONS:', r'TASKS:', r'TOPICS:', r'SUMMARY:']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text[match.start():]

    return text


def extract_field(text, field_name):
    """Extract field value from response"""
    if not text:
        return ""

    # Find the field
    pattern = rf'{field_name}\s*(.*?)(?=DECISIONS:|TASKS:|TOPICS:|SUMMARY:|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        value = match.group(1).strip()
        # Remove any leftover brackets or placeholders
        value = re.sub(r'\[.*?\]', '', value)
        # Clean up multiple spaces
        value = ' '.join(value.split())
        return value

    return ""


def clean_field_value(value, default):
    """Clean field value and ensure it's not empty"""
    if not value or value == "" or value.lower() in ['no information', 'none', 'n/a']:
        return default
    return value


def extract_topics_from_transcript(transcript):
    """Extract main topics from transcript using simple keyword extraction"""
    if not transcript:
        return "General discussion"

    # Common keywords to look for
    topic_keywords = [
        "speaking", "presentation", "confidence", "public speaking",
        "strategy", "technique", "planning", "development",
        "requirements", "design", "testing", "deployment",
        "risk", "budget", "timeline", "resource", "stakeholder"
    ]

    found_topics = []
    transcript_lower = transcript.lower()

    for keyword in topic_keywords:
        if keyword in transcript_lower and keyword not in found_topics:
            found_topics.append(keyword.capitalize())

    if found_topics:
        return ", ".join(found_topics[:5])  # Limit to 5 topics
    return "Project discussion"


def extract_meeting_info(transcript, meeting_name=""):
    """Extracts meeting information from transcription"""

    text_for_analysis = transcript

    if len(text_for_analysis) < 50:
        return {
            "decisions": "",
            "action_items": "",
            "topics": "",
            "next_meeting_date": None,
            "summary": "Transcription is too short"
        }

    # Save transcription to file for history
    if meeting_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in meeting_name if c.isalnum()
                            or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_{timestamp}.txt"
        file_path = TRANSCRIPTS_DIR / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_for_analysis)

    prompt = f"""You are a meeting secretary. Analyze the transcript and write a brief minutes.

Transcript:
{text_for_analysis[:3000]}

Write the minutes EXACTLY in this format (each field on a new line). Replace placeholders with actual content from the transcript:

DECISIONS: [Write actual decisions made, or "No decisions made" if none]
TASKS: [Write actual tasks with responsible persons, or "No tasks assigned" if none]
TOPICS: [Write actual topics discussed]
SUMMARY: [Write one sentence summarizing the meeting]

CRITICAL RULES:
1. Do NOT keep the brackets []. Write actual content.
2. Do NOT write placeholder text like "list decisions made briefly". Write real content.
3. If there is no information for a field, write "None" or "No decisions made".
4. Each field must have content, not empty.
5. Return ONLY these 4 lines, nothing else.

Example of correct response:
DECISIONS: Team agreed to use Agile methodology; Sprint duration set to 2 weeks
TASKS: Create project plan - John; Setup development environment - Mary
TOPICS: Project methodology, Timeline planning, Resource allocation
SUMMARY: Team finalized project approach and assigned initial tasks
"""

    response = call_ollama(prompt)
    response = trim_ai_response(response)  # Clean thinking prefix if present

    # Parse response with better extraction
    decisions = extract_field(response, 'DECISIONS:')
    action_items = extract_field(response, 'TASKS:')
    topics = extract_field(response, 'TOPICS:')
    summary = extract_field(response, 'SUMMARY:')

    # Post-process to ensure no empty values
    decisions = clean_field_value(decisions, "No decisions made")
    action_items = clean_field_value(action_items, "No tasks assigned")
    topics = clean_field_value(
        topics, extract_topics_from_transcript(transcript))
    # summary = clean_field_value(summary)

    return {
        "decisions": decisions,
        "action_items": action_items,
        "topics": topics,
        "next_meeting_date": None,
        "summary": summary
    }
