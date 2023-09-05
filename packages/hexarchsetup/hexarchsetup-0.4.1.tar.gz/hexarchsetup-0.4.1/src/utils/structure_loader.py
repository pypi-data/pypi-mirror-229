"""
This module contains the structure loader.
"""

import json

from src.config.paths import TEMPLATES_PATH


def load_structure_from_json(file_name: str) -> dict:
    """
    Load the structure from a JSON file located in the templates directory.
    """
    template_path = TEMPLATES_PATH / file_name

    with open(template_path, 'r', encoding='utf-8') as _f:
        return json.load(_f)
