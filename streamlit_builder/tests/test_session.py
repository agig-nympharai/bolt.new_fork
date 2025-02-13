import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from watchfiles import Change

from streamlit_builder.runtime.session_manager import DevelopmentSession
from streamlit_builder.core.container.webcontainer import WebContainer

@pytest.fixture
def mock_container():
    container = Mock(spec=WebContainer)
    container.terminal = AsyncMock()
    return container

@pytest.fixture
def session(mock_container, tmp_path):
    return DevelopmentSession(mock_container, tmp_path)

@pytest.mark.asyncio
class TestDevelopmentSession:
    async def test_session_start(self, session):
        with patch.object(session.streamlit, 'start', AsyncMock()) as mock_start, \
             patch.object(session.file_watcher, 'start', AsyncMock()) as mock_watch, \
             patch.object(session.uv, 'create_venv', AsyncMock()) as mock_venv:
            
            await session.start()
            
            mock_venv.assert_called_once()
            mock_watch.assert_called_once()
            mock_start.assert_called_once()
    
    async def test_session_stop(self, session):
        with patch.object(session.streamlit, 'stop', AsyncMock()) as mock_stop, \
             patch.object(session.file_watcher, 'stop', AsyncMock()) as mock_watch:
            
            await session.stop()
            
            mock_stop.assert_called_once()
            mock_watch.assert_called_once()
    
    async def test_file_change_handlers(self, session):
        with patch.object(session.streamlit, 'restart', AsyncMock()) as mock_restart:
            # Test Python file modification
            await session._on_file_modified(Path('test.py'))
            mock_restart.assert_called_once()
            
            mock_restart.reset_mock()
            
            # Test requirements.txt modification
            with patch.object(session.uv, 'install_requirements', AsyncMock()) as mock_install:
                await session._on_file_modified(Path('requirements.txt'))
                mock_install.assert_called_once()
                mock_restart.assert_called_once()