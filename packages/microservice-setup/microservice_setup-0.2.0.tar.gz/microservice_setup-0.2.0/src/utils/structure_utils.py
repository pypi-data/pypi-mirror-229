"""
Structure utilities.
"""

import src.constants as constants

def replace_service_name(structure: dict, service_name: str) -> None:
    """
    Replace the service name in the structure.
    """
    for key, value in structure.copy().items():
        if isinstance(value, dict):
            replace_service_name(value, service_name)
        else:
            formatted_key = key.replace(constants.SERVICE_NAME_REPLACEMENT, service_name)
            structure[formatted_key] = structure.pop(key, value)


def add_init_files_to_structure(structure: dict) -> None:
    """
    Add the __init__.py files to the structure.
    """
    for value in structure.values():
        if isinstance(value, dict):
            add_init_files_to_structure(value)
    structure[constants.INIT_FILE] = ""
