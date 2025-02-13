from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable, Awaitable
from pathlib import Path
import asyncio
import click
import os
from datetime import datetime

from ..utils.logger import logger
from ..core.container.webcontainer import WebContainer, ContainerConfig
from ..runtime.session_manager import DevelopmentSession
from .display import Display
from ..core.llm.chat import ChatSession
from ..core.llm.model import ClaudeModel
from ..core.constants import ENV_DIR

@dataclass
class CommandContext:
    """Context for command execution"""
    display: Display
    container: WebContainer
    project_path: Path
    config: Dict[str, Any]

class CommandRunner:
    """Manages CLI command execution"""
    
    def __init__(self):
        self.display = Display()
        self._commands: Dict[str, Callable[[CommandContext], Awaitable[None]]] = {}
        self._container: Optional[WebContainer] = None
        self._session: Optional[DevelopmentSession] = None
    
    def command(self, name: str):
        """Decorator to register commands"""
        def decorator(func: Callable[[CommandContext], Awaitable[None]]):
            self._commands[name] = func
            return func
        return decorator
    
    async def execute(self, command: str, project_path: Path, **kwargs):
        """Execute a CLI command"""
        if command == "chat":
            await self._handle_chat(project_path, **kwargs)
        elif command == "new":
            await self._create_project(project_path, **kwargs)
        elif command == "run":
            await self._run_project(project_path, **kwargs)
        elif command == "install":
            await self._install_package(project_path, **kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    async def _handle_chat(self, project_path: Path, prompt: Optional[str] = None, interactive: bool = False):
        """Handle chat command"""
        try:
            # Create workspace directory
            workspace_dir = project_path / "workspaces" / datetime.now().strftime("%Y%m%d_%H%M%S")
            workspace_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(workspace_dir)  # Change to workspace directory
            
            # Get API key from environment
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self.display.error("ANTHROPIC_API_KEY environment variable not set")
                raise click.Abort()
            
            # Create container config
            config = ContainerConfig(
                work_dir=workspace_dir,
                env_dir=workspace_dir / ENV_DIR
            )
            
            # Initialize chat session
            model = ClaudeModel(api_key=api_key)
            container = WebContainer(config)
            await container.setup()
            
            chat_session = ChatSession(container, model)
            
            try:
                if interactive:
                    self.display.info(f"\nWorking directory: {workspace_dir}")
                    await self._run_interactive_chat(chat_session)
                elif prompt:
                    await self._process_single_prompt(chat_session, prompt)
                else:
                    self.display.error("Either provide a prompt or use --interactive mode")
            finally:
                await container.cleanup()
                
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            raise
            
    async def _run_interactive_chat(self, chat_session: ChatSession):
        """Run interactive chat session"""
        self.display.info("Starting interactive chat session (Ctrl+C to exit)")
        
        while True:
            try:
                # Get user input
                prompt = input("\nYou: ").strip()
                if not prompt:
                    continue
                    
                # Process prompt and stream response
                self.display.info("\nAssistant: ")
                async for chunk in chat_session.process_prompt(prompt):
                    print(chunk, end="", flush=True)
                print()  # New line after response
                
            except KeyboardInterrupt:
                print()  # New line after Ctrl+C
                break
                
    async def _process_single_prompt(self, chat_session: ChatSession, prompt: str):
        """Process a single prompt"""
        self.display.info("Processing prompt...")
        async for chunk in chat_session.process_prompt(prompt):
            print(chunk, end="", flush=True)
        print()
    
    async def _create_project(self, project_path: Path, **kwargs):
        """Create a new Streamlit project"""
        with self.display.progress("Creating project...") as progress:
            task = progress.add_task("Initializing...", total=None)
            
            # Create project using container
            await self._container.fs.create_dir(project_path)
            
            # Initialize development session
            self._session = DevelopmentSession(self._container, project_path)
            await self._session.start()
            
            progress.update(task, completed=True)
        
        self.display.success(f"Project created at {project_path}")
    
    async def _run_project(self, project_path: Path, **kwargs):
        """Run Streamlit project"""
        port = kwargs.get("port", 8501)
        
        with self.display.progress("Starting Streamlit server...") as progress:
            task = progress.add_task("Initializing...", total=None)
            
            # Initialize development session
            self._session = DevelopmentSession(self._container, project_path)
            await self._session.start(port=port)
            
            progress.update(task, completed=True)
        
        self.display.success(f"Streamlit server running at http://localhost:{port}")
        
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.display.info("Shutting down...")
            await self._session.stop()
    
    async def _install_package(self, project_path: Path, **kwargs):
        """Install a package"""
        package = kwargs.get("package")
        if not package:
            raise ValueError("Package name required")
        
        with self.display.progress(f"Installing {package}...") as progress:
            task = progress.add_task("Installing...", total=None)
            
            await self._container.terminal.execute(
                ["uv", "pip", "install", package],
                f"install_{package}"
            )
            
            progress.update(task, completed=True)
        
        self.display.success(f"Package {package} installed")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.stop()
        if self._container:
            await self._container.cleanup()

# Create global command runner
runner = CommandRunner()

@runner.command("new")
async def create_project(ctx: CommandContext):
    """Create a new Streamlit project"""
    with ctx.display.progress("Creating project...") as progress:
        task = progress.add_task("Initializing...", total=None)
        
        # Create project using container
        await ctx.container.fs.create_dir(ctx.project_path)
        
        # Initialize development session
        ctx._session = DevelopmentSession(ctx.container, ctx.project_path)
        await ctx._session.start()
        
        progress.update(task, completed=True)
    
    ctx.display.success(f"Project created at {ctx.project_path}")

@runner.command("run")
async def run_project(ctx: CommandContext):
    """Run Streamlit project"""
    port = ctx.config.get("port", 8501)
    
    with ctx.display.progress("Starting Streamlit server...") as progress:
        task = progress.add_task("Initializing...", total=None)
        
        # Initialize development session
        ctx._session = DevelopmentSession(ctx.container, ctx.project_path)
        await ctx._session.start(port=port)
        
        progress.update(task, completed=True)
    
    ctx.display.success(f"Streamlit server running at http://localhost:{port}")
    
    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        ctx.display.info("Shutting down...")
        await ctx._session.stop()

@runner.command("install")
async def install_package(ctx: CommandContext):
    """Install a package"""
    package = ctx.config.get("package")
    if not package:
        raise ValueError("Package name required")
    
    with ctx.display.progress(f"Installing {package}...") as progress:
        task = progress.add_task("Installing...", total=None)
        
        await ctx.container.terminal.execute(
            ["uv", "pip", "install", package],
            f"install_{package}"
        )
        
        progress.update(task, completed=True)
    
    ctx.display.success(f"Package {package} installed") 