"""
This file is used to build your package. It is used by the command
`python setup.py install` or `python setup.py develop`.
"""

from setuptools import setup, find_packages


setup(
    name='microservice_setup',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        # Your dependencies here
    ],
    python_requires='>=3.9',
    package_data={
        'src': ['templates/*.json'],
    },
    entry_points={
        'console_scripts': [
            # This allows you to run your main function from the command line.
            'ms-init=src.main:main',
        ],
    },
    author='Éric Dominguez Morales',
    author_email='ericdominguezm@gmail.com',
    description='Automatically generate a hexagonal architecture project structure for microservices in Python. \
        Easily customizable to include user-defined modules.',
)
