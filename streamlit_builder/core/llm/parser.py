import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..constants import ActionType
from ...utils.logger import logger

@dataclass
class Action:
    type: ActionType
    file_path: Optional[str] = None
    content: Optional[str] = None
    package_name: Optional[str] = None
    command: Optional[List[str]] = None

class MessageParser:
    """Parse LLM messages to extract actions"""
    
    ACTION_PATTERNS = {
        ActionType.CREATE_FILE: r"```(?:[\w-]+)?(?:\:(?P<file_path>[^\n]+))?\n(?P<content>.*?)```",
        ActionType.INSTALL_PACKAGE: r"pip install (?P<package_name>[^\s]+)",
        ActionType.RUN_COMMAND: r"\$\s*(?P<command>[^\n]+)",
    }
    
    @classmethod
    def parse_actions(cls, message: str) -> List[Action]:
        """Parse a message and extract all actions"""
        actions: List[Action] = []
        
        # Parse file creations/modifications
        for match in re.finditer(cls.ACTION_PATTERNS[ActionType.CREATE_FILE], message, re.DOTALL):
            file_path = match.group("file_path")
            content = match.group("content")
            
            if file_path and content:
                actions.append(Action(
                    type=ActionType.CREATE_FILE,
                    file_path=file_path.strip(),
                    content=content.strip()
                ))
        
        # Parse package installations
        for match in re.finditer(cls.ACTION_PATTERNS[ActionType.INSTALL_PACKAGE], message):
            package_name = match.group("package_name")
            if package_name:
                actions.append(Action(
                    type=ActionType.INSTALL_PACKAGE,
                    package_name=package_name.strip()
                ))
        
        # Parse command executions
        for match in re.finditer(cls.ACTION_PATTERNS[ActionType.RUN_COMMAND], message):
            command = match.group("command")
            if command:
                actions.append(Action(
                    type=ActionType.RUN_COMMAND,
                    command=command.strip().split()
                ))
        
        return actions 