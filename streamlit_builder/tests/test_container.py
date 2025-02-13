import pytest
import pytest_asyncio
from pathlib import Path
from streamlit_builder.core.container.webcontainer import WebContainer, ContainerConfig

@pytest_asyncio.fixture
async def container(tmp_path):
    config = ContainerConfig(work_dir=tmp_path)
    container = WebContainer(config)
    await container.setup()
    yield container
    await container.cleanup()

@pytest.mark.asyncio
async def test_container_initialization(container):
    # Check if work directory exists
    assert container.config.work_dir.exists()
    assert container.config.env_dir.exists()

@pytest.mark.asyncio
async def test_file_operations(container):
    # Test file writing
    test_content = "print('Hello, World!')"
    await container.fs.write_file("test.py", test_content)
    
    # Test file reading
    content = await container.fs.read_file("test.py")
    assert content == test_content
    
    # Test file listing
    files = await container.fs.list_files()
    assert len(files) > 0
    assert Path("test.py") in files
    
    # Test file deletion
    await container.fs.delete_file("test.py")
    files = await container.fs.list_files()
    assert len(files) == 0 