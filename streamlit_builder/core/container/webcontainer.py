from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ...utils.logger import logger
from .filesystem import FileSystem
from .terminal import Terminal
from .process import ProcessManager

@dataclass
class ContainerConfig:
    """Configuration for WebContainer"""
    work_dir: Path
    env_dir: Path

class WebContainer:
    """Container for web development environment"""
    
    def __init__(self, config: ContainerConfig):
        self.config = config
        self.fs = FileSystem(config.work_dir)
        self.terminal = Terminal(config.work_dir)
        self.process = ProcessManager()
        
    async def setup(self):
        """Set up container environment"""
        try:
            # Create directories if they don't exist
            self.config.work_dir.mkdir(parents=True, exist_ok=True)
            self.config.env_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Container environment setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup container: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up container resources"""
        try:
            await self.process.cleanup()
            logger.info("Container cleanup complete")
        except Exception as e:
            logger.error(f"Error during container cleanup: {str(e)}")
            raise 