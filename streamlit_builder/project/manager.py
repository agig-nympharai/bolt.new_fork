from pathlib import Path
from typing import Optional, Dict, Any
import tomli_w

from ..utils.logger import logger
from ..core.container.webcontainer import WebContainer
from .templates import Template, BasicTemplate

class ProjectManager:
    """Manages project creation and configuration"""
    
    def __init__(self, container: WebContainer):
        self.container = container
        self.templates: Dict[str, Template] = {
            "basic": BasicTemplate()
        }
    
    async def create_project(
        self,
        name: str,
        template_name: str = "basic",
        config: Optional[Dict[str, Any]] = None
    ):
        """Create a new project from a template"""
        try:
            template = self.templates.get(template_name)
            if not template:
                raise ValueError(f"Template {template_name} not found")
            
            logger.info(f"Creating project {name} using template {template_name}")
            
            # Create project files
            for file_path, content in template.get_files().items():
                await self.container.fs.write_file(file_path, content)
            
            # Create pyproject.toml
            await self._create_pyproject(name, template)
            
            # Initialize UV environment
            await self._setup_environment()
            
            logger.info(f"Project {name} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise
    
    async def _create_pyproject(self, name: str, template: Template):
        """Create pyproject.toml with project configuration"""
        pyproject = {
            "project": {
                "name": name,
                "version": "0.1.0",
                "dependencies": template.get_dependencies()
            },
            "build-system": {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build"
            }
        }
        
        await self.container.fs.write_file(
            "pyproject.toml",
            tomli_w.dumps(pyproject)
        )
    
    async def _setup_environment(self):
        """Set up UV environment and install dependencies"""
        await self.container.terminal.execute(
            ["uv", "pip", "install", "-e", "."],
            "install_deps"
        ) 