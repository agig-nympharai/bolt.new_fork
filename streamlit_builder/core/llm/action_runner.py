from typing import List
from pathlib import Path

from .parser import Action, ActionType
from ..container.webcontainer import WebContainer
from ...utils.logger import logger

class ActionRunner:
    """Execute actions parsed from LLM messages"""
    
    def __init__(self, container: WebContainer):
        self.container = container
    
    async def execute_actions(self, actions: List[Action]):
        """Execute a list of actions in order"""
        for action in actions:
            try:
                await self._execute_action(action)
            except Exception as e:
                logger.error(f"Failed to execute action: {str(e)}")
                raise
    
    async def _execute_action(self, action: Action):
        """Execute a single action"""
        if action.type == ActionType.CREATE_FILE:
            await self._handle_file_action(action)
        elif action.type == ActionType.INSTALL_PACKAGE:
            await self._handle_package_action(action)
        elif action.type == ActionType.RUN_COMMAND:
            await self._handle_command_action(action)
    
    async def _handle_file_action(self, action: Action):
        """Handle file creation/modification"""
        if not action.file_path or not action.content:
            raise ValueError("File action missing path or content")
        
        await self.container.fs.write_file(action.file_path, action.content)
        logger.info(f"Created/modified file: {action.file_path}")
    
    async def _handle_package_action(self, action: Action):
        """Handle package installation"""
        if not action.package_name:
            raise ValueError("Package action missing package name")
        
        await self.container.terminal.execute(
            ["uv", "pip", "install", action.package_name],
            f"install_{action.package_name}"
        )
        logger.info(f"Installed package: {action.package_name}")
    
    async def _handle_command_action(self, action: Action):
        """Handle command execution"""
        if not action.command:
            raise ValueError("Command action missing command")
        
        await self.container.terminal.execute(
            action.command,
            f"run_{'_'.join(action.command)}"
        )
        logger.info(f"Executed command: {' '.join(action.command)}") 