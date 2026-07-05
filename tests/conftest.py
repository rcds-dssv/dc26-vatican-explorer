"""Pytest configuration file.

This file configures pytest to properly find modules in the src directory.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path so imports work correctly
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Some scraper modules still use legacy top-level imports such as ``config``.
package_path = src_path / "dc26_vatican_explorer"
sys.path.insert(0, str(package_path))
