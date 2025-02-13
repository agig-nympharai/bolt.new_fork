from pathlib import Path
from typing import Dict, Any

class Template:
    """Base class for project templates"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_files(self) -> Dict[str, str]:
        """Return a dictionary of file paths and their contents"""
        raise NotImplementedError
    
    def get_dependencies(self) -> Dict[str, str]:
        """Return a dictionary of package names and their versions"""
        raise NotImplementedError

class BasicTemplate(Template):
    """Basic Streamlit application template"""
    def __init__(self):
        super().__init__(
            name="basic",
            description="Basic Streamlit application with standard structure"
        )
    
    def get_files(self) -> Dict[str, str]:
        return {
            "app.py": self._get_app_content(),
            "utils.py": self._get_utils_content(),
            "config.py": self._get_config_content(),
        }
    
    def get_dependencies(self) -> Dict[str, str]:
        return {
            "streamlit": ">=1.32.0",
            "pandas": ">=2.2.0",
            "plotly": ">=5.18.0",
        }
    
    def _get_app_content(self) -> str:
        return '''
import streamlit as st
from config import settings
from utils import load_data

st.set_page_config(**settings.page_config)

def main():
    st.title(settings.app_title)
    
    # Load and display data
    data = load_data()
    if data is not None:
        st.dataframe(data)

if __name__ == "__main__":
    main()
'''.strip()

    def _get_utils_content(self) -> str:
        return '''
import pandas as pd
from pathlib import Path
import streamlit as st

@st.cache_data
def load_data(filepath: Path | str | None = None):
    """Load and cache data"""
    try:
        if filepath is None:
            # Generate sample data if no file provided
            return pd.DataFrame({
                'x': range(10),
                'y': range(10)
            })
        return pd.read_csv(filepath)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None
'''.strip()

    def _get_config_content(self) -> str:
        return '''
from dataclasses import dataclass

@dataclass
class Settings:
    """Application settings"""
    app_title: str = "Streamlit App"
    page_config: dict = None
    
    def __post_init__(self):
        if self.page_config is None:
            self.page_config = {
                "page_title": self.app_title,
                "layout": "wide",
                "initial_sidebar_state": "expanded"
            }

settings = Settings()
'''.strip() 