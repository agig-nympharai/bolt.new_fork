import asyncio
import os
from pathlib import Path
from typing import Callable, Dict, List, Set
from watchfiles import awatch, Change

from ...utils.logger import logger

class FileWatcher:
    """Watch for file changes in a directory"""
    
    def __init__(self, path: Path):
        self.path = path.absolute()  # Use absolute path
        self.handlers: Dict[Change, List[Callable]] = {
            change: [] for change in Change
        }
        self._task: asyncio.Task | None = None
        self._running = False
        
        # Create directory if it doesn't exist
        os.makedirs(str(self.path), exist_ok=True)
    
    def on_change(self, change_type: Change, handler: Callable):
        """Register a handler for a specific change type"""
        self.handlers[change_type].append(handler)
    
    async def start(self):
        """Start watching for changes"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch())
        # Wait for watcher to actually start
        await asyncio.sleep(0.2)  # Increased wait time
        logger.info(f"Started watching {self.path}")
    
    async def stop(self):
        """Stop watching for changes"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Stopped file watcher")
    
    async def _watch(self):
        """Watch for file changes"""
        try:
            watch_gen = awatch(
                self.path,
                debounce=100,  # Increased debounce time
                recursive=True,
                yield_on_timeout=True,
                watch_filter=None  # Watch all files
            )
            
            async for changes in watch_gen:
                if not self._running:
                    break
                
                if not changes:  # Skip empty changes (from timeout)
                    continue
                    
                for change_type, file_path in changes:
                    try:
                        abs_path = Path(file_path).absolute()
                        handlers = self.handlers.get(change_type, [])
                        
                        for handler in handlers:
                            try:
                                await handler(abs_path)
                                logger.debug(f"Handler called for {change_type} on {abs_path}")
                            except Exception as e:
                                logger.error(f"Handler error: {str(e)}")
                                
                    except Exception as e:
                        logger.error(f"Error processing change {change_type} for {file_path}: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Error in file watcher: {str(e)}")
            if self._running:
                raise 