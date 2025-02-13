import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from streamlit_builder.core.llm.parser import MessageParser, Action, ActionType
from streamlit_builder.core.llm.model import ClaudeModel
from streamlit_builder.core.llm.action_runner import ActionRunner
from streamlit_builder.core.container.webcontainer import WebContainer, ContainerConfig
from streamlit_builder.core.llm.constants import MODEL_NAME, DEFAULT_TEMPERATURE, MAX_TOKENS
from streamlit_builder.core.llm.prompts import SYSTEM_PROMPT, get_system_prompt

@pytest.fixture
def sample_message():
    return """
Let's create a simple Streamlit app.

```python:app.py
import streamlit as st

st.title("Hello World")
```

```txt:requirements.txt
streamlit>=1.32.0
```

$ uv pip install -r requirements.txt
$ streamlit run app.py
"""

@pytest.fixture
def mock_container():
    container = Mock(spec=WebContainer)
    container.fs = Mock()
    container.fs.write_file = AsyncMock()
    container.terminal = Mock()
    container.terminal.execute = AsyncMock()
    return container

class TestMessageParser:
    def test_parse_file_creation(self, sample_message):
        actions = MessageParser.parse_actions(sample_message)
        file_actions = [a for a in actions if a.type == ActionType.CREATE_FILE]
        
        assert len(file_actions) == 2
        assert file_actions[0].file_path == "app.py"
        assert "import streamlit as st" in file_actions[0].content
        assert file_actions[1].file_path == "requirements.txt"
    
    def test_parse_commands(self, sample_message):
        actions = MessageParser.parse_actions(sample_message)
        command_actions = [a for a in actions if a.type == ActionType.RUN_COMMAND]
        
        assert len(command_actions) == 2
        assert command_actions[0].command == ["uv", "pip", "install", "-r", "requirements.txt"]
        assert command_actions[1].command == ["streamlit", "run", "app.py"]

@pytest.mark.asyncio
class TestActionRunner:
    async def test_execute_file_action(self, mock_container):
        runner = ActionRunner(mock_container)
        action = Action(
            type=ActionType.CREATE_FILE,
            file_path="test.py",
            content="print('hello')"
        )
        
        await runner.execute_actions([action])
        mock_container.fs.write_file.assert_called_once_with("test.py", "print('hello')")
    
    async def test_execute_package_action(self, mock_container):
        runner = ActionRunner(mock_container)
        action = Action(
            type=ActionType.INSTALL_PACKAGE,
            package_name="streamlit"
        )
        
        await runner.execute_actions([action])
        mock_container.terminal.execute.assert_called_once_with(
            ["uv", "pip", "install", "streamlit"],
            "install_streamlit"
        )

@pytest.mark.asyncio
class TestClaudeModel:
    @pytest.fixture
    def mock_anthropic(self):
        with patch("anthropic.AsyncAnthropic") as mock:
            client = Mock()
            client.messages = Mock()
            client.messages.create = AsyncMock()
            mock.return_value = client
            yield mock

    async def test_stream_chat(self, mock_anthropic):
        model = ClaudeModel("fake-key")
        messages = [{"role": "user", "content": "Hello"}]
        
        # Create a proper async iterator class
        class AsyncStreamMock:
            async def __aiter__(self):
                yield Mock(type="content_block_delta", delta=Mock(text="Hello"))
                yield Mock(type="content_block_delta", delta=Mock(text=" World"))
        
        mock_stream = AsyncStreamMock()
        mock_anthropic.return_value.messages.create.return_value = mock_stream
        
        chunks = []
        async for chunk in model.stream_chat(messages):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " World"]
        
        # Verify the API call
        mock_anthropic.return_value.messages.create.assert_called_once_with(
            model=MODEL_NAME,
            messages=model._format_messages(messages),
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )

@pytest.mark.asyncio
@pytest.mark.integration
class TestClaudeModelIntegration:
    async def test_stream_chat_real_api(self):
        # TODO: Update model version when new versions are released
        # See streamlit_builder/core/llm/constants.py
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")
            
        model = ClaudeModel(api_key)
        messages = [{
            "role": "user",
            "content": "Say 'Hello, World!' concisely"
        }]
        
        chunks = []
        async for chunk in model.stream_chat(messages):
            chunks.append(chunk)
        
        full_response = "".join(chunks).strip()
        assert "Hello, World!" in full_response
        assert len(full_response.split()) < 10 