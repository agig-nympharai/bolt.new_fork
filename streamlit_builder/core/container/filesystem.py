from pathlib import Path
from typing import Union, List, Dict, Optional
import os

from ...utils.logger import logger

class FileSystem:
    """File system operations within the container"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
    
    async def write_file(self, path: Union[str, Path], content: str):
        """Write content to a file"""
        full_path = self.root_dir / Path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            full_path.write_text(content)
            logger.debug(f"File written: {path}")
        except Exception as e:
            logger.error(f"Failed to write file {path}: {str(e)}")
            raise
    
    async def create_dir(self, path: str):
        """Create a directory and its parents"""
        try:
            full_path = self.root_dir / path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {path}")
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {str(e)}")
            raise
    
    async def read_file(self, path: Union[str, Path]) -> str:
        """Read content from a file"""
        full_path = self.root_dir / Path(path)
        
        try:
            content = full_path.read_text()
            logger.debug(f"File read: {path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {path}: {str(e)}")
            raise
    
    async def list_files(self, directory: Union[str, Path] = ".") -> List[Path]:
        """List all files in a directory"""
        full_path = self.root_dir / Path(directory)
        
        try:
            # Exclude .venv directory and get relative paths
            files = [
                p.relative_to(self.root_dir) 
                for p in full_path.rglob("*")
                if not any(part.startswith(".venv") for part in p.relative_to(self.root_dir).parts)
            ]
            return files
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {str(e)}")
            raise
    
    async def delete_file(self, path: Union[str, Path]):
        """Delete a file"""
        full_path = self.root_dir / Path(path)
        
        try:
            if full_path.is_file():
                full_path.unlink()
                logger.debug(f"File deleted: {path}")
            elif full_path.is_dir():
                full_path.rmdir()
                logger.debug(f"Directory deleted: {path}")
        except Exception as e:
            logger.error(f"Failed to delete {path}: {str(e)}")
            raise 