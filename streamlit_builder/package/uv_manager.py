from pathlib import Path
from typing import List, Optional, Dict
import tomli
import tomli_w

from ..utils.logger import logger
from ..core.container.terminal import Terminal

class UVManager:
    """Manages UV virtual environments and package installation"""
    
    def __init__(self, terminal: Terminal, project_root: Path):
        self.terminal = terminal
        self.project_root = project_root
        self.venv_path = project_root / ".venv"
    
    async def create_venv(self):
        """Create a new virtual environment"""
        try:
            if not self.venv_path.exists():
                await self.terminal.execute(
                    ["uv", "venv", str(self.venv_path)],
                    "create_venv"
                )
                logger.info("Created virtual environment")
        except Exception as e:
            logger.error(f"Failed to create virtual environment: {str(e)}")
            raise
    
    async def install_requirements(self, requirements: Dict[str, str]):
        """Install packages from requirements dictionary"""
        try:
            # Create requirements.txt
            requirements_content = "\n".join(
                f"{pkg}=={ver}" if ver.startswith("==") else f"{pkg}{ver}"
                for pkg, ver in requirements.items()
            )
            requirements_path = self.project_root / "requirements.txt"
            requirements_path.write_text(requirements_content)
            
            # Install requirements
            await self.terminal.execute(
                ["uv", "pip", "install", "-r", str(requirements_path)],
                "install_requirements"
            )
            logger.info("Installed requirements")
            
        except Exception as e:
            logger.error(f"Failed to install requirements: {str(e)}")
            raise
    
    async def install_package(self, package: str, version: Optional[str] = None):
        """Install a single package"""
        try:
            cmd = ["uv", "pip", "install", package]
            if version:
                cmd[-1] = f"{package}=={version}"
            
            await self.terminal.execute(cmd, f"install_{package}")
            logger.info(f"Installed package: {package}")
            
        except Exception as e:
            logger.error(f"Failed to install {package}: {str(e)}")
            raise
    
    async def uninstall_package(self, package: str):
        """Uninstall a package"""
        try:
            await self.terminal.execute(
                ["uv", "pip", "uninstall", "-y", package],
                f"uninstall_{package}"
            )
            logger.info(f"Uninstalled package: {package}")
            
        except Exception as e:
            logger.error(f"Failed to uninstall {package}: {str(e)}")
            raise 