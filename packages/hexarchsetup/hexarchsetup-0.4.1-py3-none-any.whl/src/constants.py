"""
Constants specific to that module, such as error codes
"""

# Error codes
INVALID_NAME_PROJECT = "Invalid name project"
PROJECT_ALREADY_EXISTS = "A directory with this project name already exists."
INVALID_NAME_MODULE = "Invalid module name: {module}"

# Directories
SOURCE_DIR = "src"
TESTS_DIR = "tests"
TEMPLATES_DIR = "templates"

# Files
ROOT_STRUCTURE_JSON = "root_structure.json"
BASE_STRUCTURE_JSON = "base_structure.json"
MODULE_STRUCTURE_JSON = "module_structure.json"
INIT_FILE = "__init__.py"

# Replacements
MODULE_NAME_REPLACEMENT = "{module_name}"

# Formats
DESCRIPTION_FORMAT = '"""\n{value}\n"""'
PREFIX_TEST_MODULE = "test_"
