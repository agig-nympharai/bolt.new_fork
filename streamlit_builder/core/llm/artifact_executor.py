import asyncio
from pathlib import Path
from typing import List
import re

from ...utils.logger import logger
from ..container.webcontainer import WebContainer
from .artifact_parser import Artifact, ArtifactType

class ArtifactExecutor:
    """Execute artifacts in a safe environment"""
    
    def __init__(self, container: WebContainer):
        self.container = container
        
    async def execute_artifacts(self, artifacts: List[Artifact]):
        """Execute a list of artifacts in order"""
        for artifact in artifacts:
            try:
                await self._execute_artifact(artifact)
            except Exception as e:
                logger.error(f"Failed to execute artifact {artifact.id}: {str(e)}")
                raise
    
    async def _execute_artifact(self, artifact: Artifact):
        """Execute a single artifact"""
        logger.info(f"Executing: {artifact.title}")
        
        try:
            if artifact.type == ArtifactType.FILE:
                await self._handle_file_artifact(artifact)
            elif artifact.type == ArtifactType.COMMAND:
                await self._handle_command_artifact(artifact)
            elif artifact.type == ArtifactType.MESSAGE:
                logger.info(artifact.content)
        except Exception as e:
            logger.error(f"Error executing {artifact.type.value}: {str(e)}")
            raise
    
    async def _handle_file_artifact(self, artifact: Artifact):
        """Handle file creation/modification"""
        # Extract file path and content from code block
        code_block_match = re.search(r'```\w+:([^\n]+)\n(.*?)```', artifact.content, re.DOTALL)
        if not code_block_match:
            raise ValueError("Invalid file artifact format")
            
        file_path = code_block_match.group(1)
        content = code_block_match.group(2).strip()
        
        # Create parent directories if needed
        file_path = Path(file_path)
        if file_path.parent != Path('.'):
            await self.container.fs.create_dir(str(file_path.parent))
        
        # Write file
        await self.container.fs.write_file(str(file_path), content)
        logger.info(f"Created file: {file_path}")
    
    async def _handle_command_artifact(self, artifact: Artifact):
        """Handle command execution"""
        # Extract command from content (remove $ prefix)
        command = artifact.content.strip().lstrip('$ ').split()
        
        # Execute command
        await self.container.terminal.execute(command, f"command_{artifact.id}")
        logger.info(f"Executed command: {' '.join(command)}") 