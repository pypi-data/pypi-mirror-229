"""
Automatically generate a hexagonal architecture project structure for microservices in Python.
Easily customizable to include user-defined modules.
"""

import argparse
from copy import deepcopy

import src.constants as constants
from src.utils.validation import check_project_name
from src.utils.structure import (
    create_structure,
    migrate_to_test_structure,
    replace_service_name,
    add_init_files_to_structure,
)
from src.utils.structure_loader import load_structure_from_json


def main():
    """
    Main function for the script.
    """

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Generate a hexagonal architecture project structure for microservices in Python."
    )
    parser.add_argument("service_name", type=str, help="The name of the service.")
    args = parser.parse_args()

    # Prompt for project name and module names
    project_name: str = args.service_name + constants.SUFIX_SERVICE
    check_project_name(project_name)

    # Load the root structure
    root_structure: dict = load_structure_from_json(constants.ROOT_STRUCTURE_JSON)

    # Load the base structure
    base_structure: dict = load_structure_from_json(constants.BASE_STRUCTURE_JSON)
    test_base_structure: dict = migrate_to_test_structure(deepcopy(base_structure))
    add_init_files_to_structure(base_structure)

    # Add the base structure to the root structure
    root_structure[constants.SOURCE_PATH] = base_structure
    root_structure[constants.TESTS_PATH] = test_base_structure

    # Hexagonal modular architecture
    hexagonal_structure: dict = {
        project_name: root_structure,
    }

    replace_service_name(hexagonal_structure, project_name)

    # Create the folder and file structure
    create_structure(hexagonal_structure)


if __name__ == "__main__":
    main()
