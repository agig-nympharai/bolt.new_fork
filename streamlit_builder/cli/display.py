from typing import Optional
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install

from ..utils.logger import logger

# Install rich traceback handler
install(show_locals=True)

class Display:
    """Rich console display manager"""
    
    def __init__(self):
        self.theme = Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green",
            "command": "blue",
            "path": "magenta"
        })
        
        self.console = Console(theme=self.theme)
        self._progress: Optional[Progress] = None
    
    def info(self, message: str):
        """Display info message"""
        self.console.print(f"[info]ℹ {message}[/]")
    
    def success(self, message: str):
        """Display success message"""
        self.console.print(f"[success]✓ {message}[/]")
    
    def warning(self, message: str):
        """Display warning message"""
        self.console.print(f"[warning]⚠ {message}[/]")
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Display error message with optional exception"""
        self.console.print(f"[error]✗ {message}[/]")
        if exception:
            self.console.print_exception(show_locals=True)
    
    def command(self, cmd: str):
        """Display command being executed"""
        self.console.print(f"[command]$ {cmd}[/]")
    
    def code(self, code: str, language: str = "python"):
        """Display syntax-highlighted code"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)
    
    def panel(self, content: str, title: Optional[str] = None):
        """Display content in a panel"""
        self.console.print(Panel(content, title=title))
    
    def progress(self, message: str) -> Progress:
        """Create and return a progress context"""
        if self._progress:
            self._progress.stop()
            
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        return self._progress
    
    def clear(self):
        """Clear the console"""
        self.console.clear() 