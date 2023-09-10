"""
This module contains the functions for creating the folder and file structure.
"""

import os

import src.constants as constants


def create_structure(structure: dict, parent_folder: str = "") -> None:
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
