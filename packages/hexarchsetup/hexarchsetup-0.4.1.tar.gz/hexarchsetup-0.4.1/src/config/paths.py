"""
This module contains the paths to the project directories.
"""

from pathlib import Path

import src.constants as constants


_PARENTS = 2  # Number of levels from this file to the root directory of the project


PROJECT_ROOT = Path(__file__).resolve().parents[_PARENTS]

TEMPLATES_PATH = PROJECT_ROOT / constants.TEMPLATES_DIR
SRC_PATH = PROJECT_ROOT / constants.SOURCE_DIR
