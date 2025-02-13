from pathlib import Path
from typing import Optional, Dict, Any
import asyncio

from watchfiles import Change

from ..utils.logger import logger
from ..core.container.webcontainer import WebContainer
from ..server.streamlit_runner import StreamlitRunner
from ..core.files.watcher import FileWatcher
from ..package.uv_manager import UVManager

class DevelopmentSession:
    """Manages a development session for a Streamlit project"""
    
    def __init__(self, container: WebContainer, project_path: Path):
        self.container = container
        self.project_path = project_path
        self.streamlit = StreamlitRunner(container.terminal, project_path)
        self.file_watcher = FileWatcher(project_path)
        self.uv = UVManager(container.terminal, project_path)
        
        # Set up file change handlers
        self.file_watcher.on_change(Change.modified, self._on_file_modified)
        self.file_watcher.on_change(Change.added, self._on_file_added)
        self.file_watcher.on_change(Change.deleted, self._on_file_deleted)
    
    async def start(self, port: int = 8501):
        """Start development session"""
        try:
            # Initialize environment
            await self.uv.create_venv()
            
            # Start file watcher
            await self.file_watcher.start()
            
            # Start Streamlit server
            await self.streamlit.start(port=port)
            
            logger.info(f"Development session started for {self.project_path}")
            
        except Exception as e:
            logger.error(f"Failed to start development session: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop development session"""
        try:
            await self.streamlit.stop()
            await self.file_watcher.stop()
            logger.info("Development session stopped")
        except Exception as e:
            logger.error(f"Error stopping development session: {str(e)}")
            raise
    
    async def _on_file_modified(self, path: Path):
        """Handle file modifications"""
        try:
            if path.suffix == '.py':
                await self.streamlit.restart()
            elif path.name == 'requirements.txt':
                await self.uv.install_requirements()
                await self.streamlit.restart()
        except Exception as e:
            logger.error(f"Error handling file modification: {str(e)}")
    
    async def _on_file_added(self, path: Path):
        """Handle new files"""
        await self._on_file_modified(path)
    
    async def _on_file_deleted(self, path: Path):
        """Handle deleted files"""
        if path.suffix == '.py':
            await self.streamlit.restart() 