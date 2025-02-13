import asyncio
from typing import Optional, Dict, Callable, List
from pathlib import Path

from ...utils.logger import logger
from .process import ProcessManager

class Terminal:
    """Terminal emulation for command execution"""
    
    def __init__(self, cwd: Path):
        self.cwd = cwd
        self.process_manager = ProcessManager(cwd)
        self._output_handlers: Dict[str, List[Callable[[str], None]]] = {}
    
    def add_output_handler(self, process_name: str, handler: Callable[[str], None]):
        """Add handler for process output"""
        if process_name not in self._output_handlers:
            self._output_handlers[process_name] = []
        self._output_handlers[process_name].append(handler)
    
    async def execute(
        self,
        command: List[str],
        process_name: str,
        env: Optional[Dict[str, str]] = None,
    ):
        """Execute a command and handle its output"""
        process = await self.process_manager.run(command, process_name, env)
        
        async def handle_output(stream: asyncio.StreamReader, prefix: str):
            while True:
                line = await stream.readline()
                if not line:
                    break
                    
                decoded = line.decode().rstrip()
                logger.debug(f"{prefix} {decoded}")
                
                # Notify handlers
                handlers = self._output_handlers.get(process_name, [])
                for handler in handlers:
                    handler(decoded)
        
        # Handle both stdout and stderr
        await asyncio.gather(
            handle_output(process.stdout, "[stdout]"),
            handle_output(process.stderr, "[stderr]")
        )
        
        return await process.wait()
    
    async def cleanup(self):
        """Clean up all running processes"""
        await self.process_manager.stop_all() 