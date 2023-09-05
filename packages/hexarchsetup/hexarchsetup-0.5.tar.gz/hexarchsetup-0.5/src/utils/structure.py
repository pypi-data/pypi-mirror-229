"""
This module contains the functions for creating the folder and file structure.
"""

import os
from copy import deepcopy

import src.constants as constants
from src.utils.structure_loader import load_structure_from_json


def create_structure(structure: dict, parent_folder: str = ""):
    """
    Creates the folder and file structure based on the given dictionary.
    """
    for key, value in structure.items():
        if isinstance(value, dict):
            new_folder = os.path.join(parent_folder, key)
            os.makedirs(new_folder, exist_ok=True)
            create_structure(value, new_folder)
        else:
            new_file = os.path.join(parent_folder, key)
            with open(new_file, "w", encoding="utf-8") as _f:
                description = constants.DESCRIPTION_FORMAT.format(value=value) if value else ""
                _f.write(description)


def add_module_to_base_structure(base_structure: dict, module_structure: dict, module_name: str):
    """
    Add the module to the base structure.
    """
    for key, value in module_structure.items():
        if isinstance(value, dict):
            add_module_to_base_structure(
                base_structure.setdefault(key.replace(constants.MODULE_NAME_REPLACEMENT, module_name), {}),
                value,
                module_name,
            )
        else:
            formatted_key = key.replace(constants.MODULE_NAME_REPLACEMENT, module_name)
            base_structure[formatted_key] = value


def migrate_to_test_structure(structure: dict):
    """
    Migrate the structure to the test structure.
    """
    for key, value in structure.copy().items():
        if isinstance(value, dict):
            migrate_to_test_structure(value)
        else:
            structure[constants.PREFIX_TEST_MODULE + key] = ""
            del structure[key]

    return structure


def add_init_files_to_structure(structure: dict):
    """
    Add the __init__.py files to the structure.
    """
    for value in structure.values():
        if isinstance(value, dict):
            add_init_files_to_structure(value)
    structure[constants.INIT_FILE] = ""


def add_modules_to_root_structure(structure: dict, module_names: list[str]):
    """
    Add the module names to the structure.
    """
    module_structure = load_structure_from_json(constants.MODULE_STRUCTURE_JSON)
    test_module_structure = migrate_to_test_structure(deepcopy(module_structure))
    for module_name in module_names:
        add_module_to_base_structure(structure[constants.SOURCE_PATH], module_structure, module_name)
        add_module_to_base_structure(structure[constants.TESTS_PATH], test_module_structure, module_name)
    add_init_files_to_structure(structure[constants.SOURCE_PATH])
