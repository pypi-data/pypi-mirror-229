"""
This module contains the functions for creating the folder and file structure.
"""

import os

import src.constants as constants


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


def replace_service_name(structure: dict, service_name: str):
    """
    Replace the service name in the structure.
    """
    for key, value in structure.copy().items():
        if isinstance(value, dict):
            replace_service_name(value, service_name)
        else:
            formatted_key = key.replace(constants.SERVICE_NAME_REPLACEMENT, service_name)
            structure[formatted_key] = structure.pop(key, value)


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
