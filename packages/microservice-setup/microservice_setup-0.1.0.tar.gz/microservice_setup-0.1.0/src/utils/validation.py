"""
Validation functions.
"""

import os
import re

import src.exceptions as exceptions

def is_valid_name(name: str):
    """
    Validate project name.
    """
    return re.match(r'^\w+$', name) is not None


def check_project_name(name: str):
    """
    Check if the project name is valid.
    """
    if not is_valid_name(name):
        raise exceptions.InvalidNameProjectException()

    if os.path.exists(name):
        raise exceptions.ProjectAlreadyExistsException()
