"""
Federated Outbreak Detection System - Entry Point for Streamlit Cloud
Execute the federated_health_triage/app.py directly
"""

import sys
from pathlib import Path

# Setup path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "federated_health_triage"))

# Read and execute the actual app file in the current namespace
with open(project_root / "federated_health_triage" / "app.py") as f:
    app_code = f.read()
    
# Execute in current globals so Streamlit sees everything
exec(app_code, globals())






