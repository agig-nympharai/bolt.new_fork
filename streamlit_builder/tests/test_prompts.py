import pytest
from pathlib import Path

from streamlit_builder.core.constants import (
    WORK_DIR_NAME,
    MODEL_NAME,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    MessageRole
)
from streamlit_builder.core.llm.prompts import (
    SYSTEM_PROMPT,
    get_system_prompt,
    get_project_creation_prompt
)

def test_system_prompt():
    """Test that system prompt contains required sections"""
    prompt = get_system_prompt()
    
    # Test prompt sections
    assert "<system_constraints>" in prompt
    assert "<code_formatting>" in prompt
    assert "<streamlit_guidelines>" in prompt
    assert "<response_format>" in prompt
    assert WORK_DIR_NAME in prompt

def test_project_creation_prompt():
    """Test project creation prompt generation"""
    project_name = "test_app"
    prompt = get_project_creation_prompt(project_name)
    
    # Test prompt content
    assert project_name in prompt
    assert "app.py" in prompt
    assert "requirements.txt" in prompt
    assert "utils.py" in prompt
    assert "config.py" in prompt 