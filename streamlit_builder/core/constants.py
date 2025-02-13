"""
Core constants for the streamlit-builder project.
All constants should be defined here to maintain a single source of truth.
"""
from pathlib import Path
from enum import Enum, auto

# Project Structure
PROJECT_ROOT = Path(__file__).parent.parent
WORK_DIR_NAME = "project"
TEMPLATES_DIR = PROJECT_ROOT / WORK_DIR_NAME / "templates"

# Environment
DEFAULT_PYTHON_VERSION = "3.12"
DEFAULT_UV_VERSION = "0.5.3"
ENV_DIR = ".venv"
REQUIREMENTS_FILE = "requirements.txt"

# Server Configuration
DEFAULT_PORT = 8501  # Default Streamlit port

# Claude API Configuration
MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
CLAUDE_MODEL_VERSION = "claude-3-5-sonnet-20241022"
MODEL_NAME = CLAUDE_MODEL_VERSION

# Message Roles
class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

# Action Types
class ActionType(Enum):
    CREATE_FILE = auto()
    INSTALL_PACKAGE = auto()
    RUN_COMMAND = auto()

