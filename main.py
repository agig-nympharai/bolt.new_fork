#!/usr/bin/env python3
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables from .env
load_dotenv(project_root / ".env")

from streamlit_builder.cli.main import main
from streamlit_builder.utils.logger import logger


def run_cli():
    """Run the Streamlit Builder CLI"""
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
