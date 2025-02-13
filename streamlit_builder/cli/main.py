import click
import asyncio
from pathlib import Path
from typing import Optional

from .commands import runner
from ..utils.logger import logger

@click.group()
def cli():
    """Streamlit Builder CLI"""
    pass

@cli.command()
@click.argument("name")
@click.option("--template", default="basic", help="Project template to use")
def new(name: str, template: str):
    """Create a new Streamlit project"""
    project_path = Path.cwd() / name
    
    try:
        asyncio.run(runner.execute("new", project_path, template=template))
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise click.Abort()

@cli.command()
@click.option("--port", default=8501, help="Port to run Streamlit server on")
def run(port: int):
    """Run Streamlit project"""
    project_path = Path.cwd()
    
    try:
        asyncio.run(runner.execute("run", project_path, port=port))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Failed to run project: {str(e)}")
        raise click.Abort()
    finally:
        asyncio.run(runner.cleanup())

@cli.command()
@click.argument("package")
def install(package: str):
    """Install a package"""
    project_path = Path.cwd()
    
    try:
        asyncio.run(runner.execute("install", project_path, package=package))
    except Exception as e:
        logger.error(f"Failed to install package: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument("prompt", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Start interactive chat mode")
def chat(prompt: Optional[str], interactive: bool):
    """Start interactive chat or process single prompt"""
    try:
        if interactive and prompt:
            logger.warning("Prompt is ignored in interactive mode")
        asyncio.run(runner.execute("chat", Path.cwd(), prompt=prompt, interactive=interactive))
    except KeyboardInterrupt:
        logger.info("\nChat session ended")
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise click.Abort()

def main():
    """CLI entry point"""
    try:
        cli()
    except Exception as e:
        logger.error(f"CLI error: {str(e)}")
        raise click.Abort()

if __name__ == "__main__":
    main() 