import pytest
import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock
from watchfiles import Change

from streamlit_builder.core.files.watcher import FileWatcher
from streamlit_builder.utils.logger import logger

@pytest.fixture
async def tmp_dir(tmp_path):
    """Create a temporary directory for testing"""
    path = tmp_path.absolute()  # Use absolute path
    await asyncio.sleep(0.1)
    return path

@pytest.fixture
def watcher(tmp_dir):
    """Create a FileWatcher instance"""
    return FileWatcher(tmp_dir)

@pytest.mark.asyncio
class TestFileWatcher:
    async def test_handler_registration(self, watcher):
        handler = AsyncMock()
        watcher.on_change(Change.modified, handler)
        assert handler in watcher.handlers[Change.modified]
    
    async def test_start_stop(self, watcher):
        await watcher.start()
        assert watcher._running
        assert watcher._task is not None
        
        await watcher.stop()
        assert not watcher._running
        assert watcher._task is None
    
    async def test_file_change_detection(self, watcher, tmp_dir):
        # Register handlers for both added and modified events
        handler = AsyncMock()
        watcher.on_change(Change.added, handler)
        watcher.on_change(Change.modified, handler)
        
        # Start watching before creating the file
        await watcher.start()
        
        # Create and modify file with proper flushing
        test_file = tmp_dir / "test.txt"
        
        # Initial write
        with open(test_file, 'w') as f:
            f.write("initial")
            f.flush()
            os.fsync(f.fileno())
        
        await asyncio.sleep(0.3)  # Wait longer for file system events
        
        # Modify
        with open(test_file, 'w') as f:
            f.write("modified")
            f.flush()
            os.fsync(f.fileno())
        
        # Wait for handler with timeout and better logging
        start_time = asyncio.get_event_loop().time()
        while handler.call_count < 1:  # We expect at least one call
            await asyncio.sleep(0.1)
            if asyncio.get_event_loop().time() - start_time > 2.0:
                logger.warning(f"Timeout waiting for handler. Call count: {handler.call_count}")
                break
        
        await watcher.stop()
        
        # Verify handler was called at least once
        assert handler.call_count >= 1, "Handler was not called"
        
        # Verify the path matches (using str to handle path differences)
        for call in handler.call_args_list:
            called_path = Path(call[0][0])
            # Get the actual file path from the event
            event_file = called_path / test_file.name if called_path.is_dir() else called_path
            assert str(test_file.resolve()) == str(event_file.resolve()) 