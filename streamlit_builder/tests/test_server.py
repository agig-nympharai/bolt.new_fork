import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
import signal
import aiohttp
from types import SimpleNamespace

from streamlit_builder.server.streamlit_runner import StreamlitRunner
from streamlit_builder.core.container.terminal import Terminal

@pytest.fixture
def mock_terminal():
    return AsyncMock(spec=Terminal)

@pytest.fixture
def mock_process():
    """Create a mock process with correct sync/async methods"""
    process = AsyncMock()
    # Make send_signal synchronous
    process.send_signal = Mock()
    return process

@pytest.fixture
def streamlit_runner(mock_terminal, tmp_path):
    return StreamlitRunner(mock_terminal, tmp_path)

class MockResponse:
    """Mock aiohttp response"""
    def __init__(self, status):
        self.status = status
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockGet:
    """Mock for the get request"""
    def __init__(self, response):
        self.response = response
    
    async def __aenter__(self):
        return self.response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockClientSession:
    """Mock aiohttp client session"""
    def __init__(self, response):
        self.response = response
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def get(self, url, **kwargs):
        """Return a context manager for the get request"""
        return MockGet(self.response)

@pytest.mark.asyncio
class TestStreamlitRunner:
    async def test_start_server(self, streamlit_runner):
        # Setup mock response with proper async context managers
        mock_response = MockResponse(status=200)
        mock_session = MockClientSession(mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await streamlit_runner.start()
            
            assert streamlit_runner._process is not None
            assert streamlit_runner._port == 8501
    
    async def test_stop_server(self, streamlit_runner, mock_process):
        # Use the fixture with correct sync/async methods
        streamlit_runner._process = mock_process
        
        await streamlit_runner.stop()
        
        mock_process.send_signal.assert_called_once_with(signal.SIGTERM)
        mock_process.wait.assert_awaited_once()  # wait is still async
        assert streamlit_runner._process is None
    
    async def test_restart_server(self, streamlit_runner):
        with patch.object(streamlit_runner, 'start', AsyncMock()) as mock_start, \
             patch.object(streamlit_runner, 'stop', AsyncMock()) as mock_stop:
            
            # Set initial port
            streamlit_runner._port = 8501
            
            await streamlit_runner.restart()
            
            mock_stop.assert_called_once()
            mock_start.assert_called_once_with(port=8501) 