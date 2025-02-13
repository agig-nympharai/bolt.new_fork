from pathlib import Path
import asyncio
from typing import Optional, Dict
import signal
import aiohttp

from ..utils.logger import logger
from ..core.container.terminal import Terminal

class StreamlitRunner:
    """Manages Streamlit server instances"""
    
    def __init__(self, terminal: Terminal, project_root: Path):
        self.terminal = terminal
        self.project_root = project_root
        self._process: Optional[asyncio.subprocess.Process] = None
        self._port: int = 8501  # Default port
        
    async def start(self, app_path: str = "app.py", port: Optional[int] = None):
        """Start Streamlit server"""
        if self._process:
            logger.warning("Streamlit server already running")
            return
            
        try:
            if port is not None:
                self._port = port
                
            cmd = ["streamlit", "run", app_path, "--server.port", str(self._port)]
            
            # Start streamlit process
            self._process = await self.terminal.execute(
                cmd,
                "streamlit_server",
                wait=False  # Don't wait for completion
            )
            
            # Wait for server to start
            await self._wait_for_server()
            logger.info(f"Streamlit server started on port {self._port}")
            
        except Exception as e:
            logger.error(f"Failed to start Streamlit server: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop Streamlit server"""
        if self._process:
            try:
                self._process.send_signal(signal.SIGTERM)
                await self._process.wait()
                logger.info("Streamlit server stopped")
            except Exception as e:
                logger.error(f"Error stopping Streamlit server: {str(e)}")
            finally:
                self._process = None
    
    async def restart(self):
        """Restart Streamlit server"""
        current_port = self._port
        await self.stop()
        await self.start(port=current_port)  # Always restart with same port
    
    async def _wait_for_server(self, timeout: int = 10):
        """Wait for Streamlit server to start"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{self._port}", timeout=1.0) as resp:
                        if resp.status == 200:
                            return
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError(f"Streamlit server failed to start: {str(e)}")
                await asyncio.sleep(0.5) 