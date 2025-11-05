"""
Pytest configuration file.

This file configures pytest to properly find modules in the src directory.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path so imports work correctly
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
