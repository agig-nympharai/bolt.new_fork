from typing import Optional, AsyncGenerator
from pathlib import Path

from ..constants import ActionType
from .model import ClaudeModel
from .parser import MessageParser, Action
from .prompts import get_system_prompt
from ...utils.logger import logger
from ..container.webcontainer import WebContainer
from .artifact_parser import ArtifactParser, ArtifactType
from .artifact_executor import ArtifactExecutor

class ChatSession:
    """Manages an AI chat session for Streamlit development"""
    
    def __init__(self, container: WebContainer, model: ClaudeModel):
        self.container = container
        self.model = model
        self.system_prompt = get_system_prompt()
        self.messages = []
        self.artifact_executor = ArtifactExecutor(container)
        self.current_response = []  # Store current response chunks
    
    async def process_prompt(self, prompt: str) -> AsyncGenerator[str, None]:
        """Process a single prompt and stream the response"""
        try:
            # Add user message
            self.messages.append({"role": "user", "content": prompt})
            self.current_response = []
            
            # Get streaming response
            async for chunk in self.model.stream_chat(
                messages=self.messages,
                system_prompt=self.system_prompt
            ):
                self.current_response.append(chunk)
                # Don't yield chunks - we'll display only message artifacts
            
            # Parse and execute artifacts
            response = "".join(self.current_response)
            artifacts = ArtifactParser.parse_artifacts(response)
            
            # Execute artifacts and display messages
            for artifact in artifacts:
                await self.artifact_executor.execute_artifacts([artifact])
                if artifact.type == ArtifactType.MESSAGE:
                    yield f"\n{artifact.content}\n"
            
            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": response})
                
        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}")
            raise
    
    async def _execute_action(self, action: Action):
        """Execute a single action from the LLM response"""
        try:
            if action.type == ActionType.CREATE_FILE:
                if action.file_path and action.content:
                    await self.container.fs.write_file(action.file_path, action.content)
                    logger.info(f"Created/modified file: {action.file_path}")
                    
            elif action.type == ActionType.INSTALL_PACKAGE:
                if action.package_name:
                    await self.container.terminal.execute(
                        ["uv", "pip", "install", action.package_name],
                        f"install_{action.package_name}"
                    )
                    logger.info(f"Installed package: {action.package_name}")
                    
            elif action.type == ActionType.RUN_COMMAND:
                if action.command:
                    await self.container.terminal.execute(
                        action.command,
                        "run_command"
                    )
                    logger.info(f"Executed command: {' '.join(action.command)}")
                    
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            raise 