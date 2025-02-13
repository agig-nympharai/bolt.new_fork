import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, ANY

from streamlit_builder.project.manager import ProjectManager
from streamlit_builder.core.container.webcontainer import WebContainer

@pytest.fixture
def mock_container():
    container = Mock(spec=WebContainer)
    container.fs = AsyncMock()
    container.terminal = AsyncMock()
    return container

@pytest.fixture
def project_manager(mock_container):
    return ProjectManager(mock_container)

@pytest.mark.asyncio
class TestProjectManager:
    async def test_create_project_basic_template(self, project_manager, mock_container):
        # Test creating a project with the basic template
        await project_manager.create_project("test_app")
        
        # Check if files were created
        expected_files = [
            "app.py",
            "utils.py",
            "config.py",
            "pyproject.toml"
        ]
        
        # Verify each file was created
        for file in expected_files:
            mock_container.fs.write_file.assert_any_call(
                file,
                ANY  # Use ANY to match any content
            )
        
        # Verify pyproject.toml content structure
        pyproject_calls = [
            call for call in mock_container.fs.write_file.call_args_list 
            if call[0][0] == "pyproject.toml"
        ]
        assert len(pyproject_calls) == 1
        pyproject_content = pyproject_calls[0][0][1]
        assert "test_app" in pyproject_content
        assert "streamlit" in pyproject_content
        
        # Check if UV was initialized
        mock_container.terminal.execute.assert_called_once_with(
            ["uv", "pip", "install", "-e", "."],
            "install_deps"
        )
    
    async def test_create_project_invalid_template(self, project_manager):
        with pytest.raises(ValueError, match="Template invalid_template not found"):
            await project_manager.create_project("test_app", template_name="invalid_template") 