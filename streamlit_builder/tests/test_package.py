import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from streamlit_builder.package.uv_manager import UVManager
from streamlit_builder.core.container.terminal import Terminal

@pytest.fixture
def mock_terminal():
    return AsyncMock(spec=Terminal)

@pytest.fixture
def uv_manager(mock_terminal, tmp_path):
    return UVManager(mock_terminal, tmp_path)

@pytest.mark.asyncio
class TestUVManager:
    async def test_create_venv(self, uv_manager, mock_terminal):
        await uv_manager.create_venv()
        mock_terminal.execute.assert_called_once_with(
            ["uv", "venv", str(uv_manager.venv_path)],
            "create_venv"
        )
    
    async def test_install_requirements(self, uv_manager, mock_terminal):
        requirements = {
            "streamlit": ">=1.32.0",
            "pandas": "==2.2.0"
        }
        
        await uv_manager.install_requirements(requirements)
        
        # Check if requirements.txt was created
        requirements_path = uv_manager.project_root / "requirements.txt"
        assert requirements_path.exists()
        
        # Check if uv install was called
        mock_terminal.execute.assert_called_once_with(
            ["uv", "pip", "install", "-r", str(requirements_path)],
            "install_requirements"
        ) 