import asyncio
import signal
from typing import Optional, Dict, List
from pathlib import Path

from ...utils.logger import logger

class ProcessManager:
    """Manages running processes"""
    
    def __init__(self, cwd: Optional[Path] = None):
        self._processes: Dict[str, asyncio.subprocess.Process] = {}
        self.cwd = cwd
    
    def add_process(self, name: str, process: asyncio.subprocess.Process):
        """Add a process to manage"""
        self._processes[name] = process
    
    def remove_process(self, name: str):
        """Remove a process from management"""
        if name in self._processes:
            del self._processes[name]
    
    async def cleanup(self):
        """Clean up all managed processes"""
        for name, process in list(self._processes.items()):
            try:
                process.send_signal(signal.SIGTERM)
                await process.wait()
                logger.debug(f"Process {name} terminated")
            except Exception as e:
                logger.error(f"Error terminating process {name}: {str(e)}")
            finally:
                self.remove_process(name)

    async def run(
        self,
        command: List[str],
        process_name: str,
        env: Optional[Dict[str, str]] = None,
        shell: bool = False,
    ) -> asyncio.subprocess.Process:
        """Run a command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.cwd) if self.cwd else None,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.add_process(process_name, process)
            logger.debug(f"Started process {process_name}: {' '.join(command)}")
            
            return process
            
        except Exception as e:
            logger.error(f"Failed to run command {' '.join(command)}: {str(e)}")
            raise
    
    async def stop(self, process_name: str):
        """Stop a running process"""
        process = self._processes.get(process_name)
        if process:
            try:
                process.send_signal(signal.SIGTERM)
                await process.wait()
                logger.debug(f"Stopped process: {process_name}")
            except Exception as e:
                logger.error(f"Failed to stop process {process_name}: {str(e)}")
            finally:
                self.remove_process(process_name)
    
    async def stop_all(self):
        """Stop all running processes"""
        for process_name in list(self._processes.keys()):
            await self.stop(process_name)
    
    async def is_running(self, process_name: str) -> bool:
        """Check if a process is running"""
        process = self._processes.get(process_name)
        if not process:
            return False
        return process.returncode is None 