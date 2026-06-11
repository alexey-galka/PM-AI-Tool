import subprocess
import requests
import logging
import re
from typing import Optional
from config import OLLAMA_MODEL, OLLAMA_HOST, OLLAMA_TIMEOUT, DEBUG
import os

# ==================== SETTINGS ====================
# Logging setup
if DEBUG:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # logging.FileHandler('ollama_calls.log'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)


# ==================== MAIN FUNCTIONS ====================
def clean_response(text):
    """Cleans response from control characters and terminal emulation"""
    if not text:
        return text

    # Remove ANSI escape sequences ([...)
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)

    # Remove other control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

    # Remove specific cursor movement sequences
    text = re.sub(r'\x1b\[\d+[ABCD]', '', text)  # cursor movements
    text = re.sub(r'\x1b\[\d+[~]', '', text)     # special codes
    text = re.sub(r'\x1b\[[0-9;]*[JK]', '', text)  # screen clearing

    # Remove extra spaces and line breaks
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def call_ollama_via_cli(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call Ollama via CLI (local mode)"""
    cmd = ['ollama', 'run', model, prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=OLLAMA_TIMEOUT,
            env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '1',
                 'CLICOLOR': '0'}  # Disable terminal emulation
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            # Clean from control characters
            output = clean_response(output)
            return output
        else:
            raise Exception(f"CLI error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception(f"Timeout {OLLAMA_TIMEOUT} sec")
    except Exception as e:
        raise Exception(f"CLI error: {str(e)}")


def call_ollama(prompt: str, model: Optional[str] = None, host: Optional[str] = None) -> str:
    """
    Call Ollama with given prompt (auto-select method)

    Args:
        prompt: query text
        model: model name (if None, taken from settings)
        host: Ollama address (if None, taken from settings)

    Returns:
        model response or error message
    """
    if model is None:
        model = OLLAMA_MODEL
    if host is None:
        host = OLLAMA_HOST

    try:
        # Check if this is a local or remote call
        is_local = host in ["http://localhost:11434", "http://127.0.0.1:11434"]

        if is_local:
            # Local call via CLI
            result = call_ollama_via_cli(prompt, model)

        return result

    except subprocess.TimeoutExpired:
        error_msg = f"Error: timeout exceeded ({OLLAMA_TIMEOUT} sec)"
        logger.error(error_msg)
        return error_msg

    except requests.exceptions.Timeout:
        error_msg = f"Error: API timeout exceeded ({OLLAMA_TIMEOUT} sec)"
        logger.error(error_msg)
        return error_msg

    except requests.exceptions.ConnectionError:
        error_msg = f"Error: failed to connect to Ollama at {host}"
        logger.error(error_msg)
        return error_msg

    except Exception as e:
        error_msg = f"Error calling Ollama: {str(e)}"
        logger.error(error_msg)
        return error_msg


def trim_ai_response(text):
    """Trim AI response - keep only content after ...done thinking."""
    if not text:
        return text

    # Find ...done thinking. and return everything after it
    match = re.search(r'\.\.\.done thinking\.?\s*', text, re.IGNORECASE)
    if match:
        return text[match.end():].strip()

    return text