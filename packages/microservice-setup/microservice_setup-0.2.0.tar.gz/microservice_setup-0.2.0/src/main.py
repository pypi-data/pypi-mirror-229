"""
Automatically generate a hexagonal architecture project structure for microservices in Python.
Easily customizable to include user-defined modules.
"""

from src.utils.structure_creation import create_structure
from src.utils.structure_generation import generate_hexagonal_structure
from src.utils.custom_parser import get_service_names


def main():
    """
    Main function for the script.
    """

    # Get the service names
    service_names: list = get_service_names()

    # Generate the hexagonal structure
    hexagonal_structure: dict = generate_hexagonal_structure(service_names)

    # Create the folder and file structure
    create_structure(hexagonal_structure)


if __name__ == "__main__":
    main()
