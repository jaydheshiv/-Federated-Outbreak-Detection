"""
Federated Outbreak Detection System - Entry Point for Streamlit Cloud
This file serves as the entry point for Streamlit Cloud deployment
"""

import sys
from pathlib import Path

# Add federated_health_triage to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "federated_health_triage"))

# Import and run the main app
from app import *  # noqa: F401, F403

if __name__ == "__main__":
    pass  # Streamlit runs the app automatically
