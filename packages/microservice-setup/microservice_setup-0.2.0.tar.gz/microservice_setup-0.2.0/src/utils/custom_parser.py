"""
Custom parser for command line arguments.
"""

import argparse

import src.constants as constants


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate a hexagonal architecture project structure for microservices in Python."
    )
    parser.add_argument(constants.SERVICE_NAMES, type=str, nargs='*', help="The names of the services.")
    return parser.parse_args()

def get_service_names() -> list:
    """
    Get the service names.
    """
    return getattr(parse_args(), constants.SERVICE_NAMES, None)
