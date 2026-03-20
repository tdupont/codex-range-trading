"""Import bootstrap helpers for Streamlit script execution."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_root_on_path(from_file: str) -> None:
    project_root = Path(from_file).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
