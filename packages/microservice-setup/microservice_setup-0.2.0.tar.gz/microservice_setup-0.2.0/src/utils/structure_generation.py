"""
Structure generation module.
"""

from copy import deepcopy

import src.constants as constants
from src.utils.structure_loader import load_structure_from_json
from src.utils.structure_utils import replace_service_name, add_init_files_to_structure
from src.utils.structure_migration import migrate_to_test_structure


def generate_template_structure() -> dict:
    """
    Generate the template structure.
    """
    # Load the root structure
    root_structure: dict = load_structure_from_json(constants.ROOT_STRUCTURE_JSON)

    # Load the base structure
    base_structure: dict = load_structure_from_json(constants.BASE_STRUCTURE_JSON)
    test_base_structure: dict = migrate_to_test_structure(deepcopy(base_structure))
    add_init_files_to_structure(base_structure)

    # Add the base structure to the root structure
    root_structure[constants.SOURCE_PATH] = base_structure
    root_structure[constants.TESTS_PATH] = test_base_structure

    return root_structure


def generate_hexagonal_structure(service_names: str) -> dict:
    """
    Generate the hexagonal structure.
    """
    root_structure: dict = generate_template_structure()
    hexagonal_structure: dict = {}

    for service_name in service_names:
        # Prompt for project name and module names
        project_name: str = service_name + constants.SUFIX_SERVICE

        # Hexagonal modular architecture
        hexagonal_structure[project_name] = deepcopy(root_structure)

        replace_service_name(hexagonal_structure[project_name], project_name)

    return hexagonal_structure
