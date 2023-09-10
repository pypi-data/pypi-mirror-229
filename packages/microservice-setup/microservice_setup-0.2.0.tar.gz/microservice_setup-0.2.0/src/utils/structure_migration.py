"""
This module contains the functions to migrate the structure to the test structure.
"""

import src.constants as constants


def migrate_to_test_structure(structure: dict) -> dict:
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
