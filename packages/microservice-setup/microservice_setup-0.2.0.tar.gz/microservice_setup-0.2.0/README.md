# Microservice Setup

## Overview

Microservice Setup is a Python-based Command-Line Interface (CLI) tool aimed to auto-generate a domain-driven, scalable, and maintainable microservices directory structure based on hexagonal architecture. 

## Features

- Auto-generates a clean and scalable microservices project skeleton
- Built around hexagonal architecture principles
- Allows for easy customization to include user-defined modules
- Works with Python 3.9 or later

## Installation

### Via pip

```bash
pip install microservice_setup
```

### Clone Repository

Clone this repository and navigate into the directory:

```bash
git clone https://github.com/DoMo-98/microservice_setup.git
cd microservice_setup
```

## Usage

After installation, you can initialize your microservices project in one of two ways:

1. Via pip installation:

    ```bash
    ms-init example
    ```

2. Via Python module:

    ```bash
    python -m src.main example
    ```

Follow the prompts to set up your project.

## Generated Structure

When you run `microservice_setup`, the following directory structure will be generated:

```plaintext
example_service/
├── app/
│   ├── adapters/
│   │   ├── controllers/
│   │   └── serializers/
│   ├── application/
│   │   ├── services/
│   │   └── use_cases/
│   ├── common/
│   │   └── constants/
│   └── domain/
│       ├── entities/
│       ├── exceptions/
│       └── interfaces/
├── config/
├── constants/
├── main.py
├── requirements/
├── templates/
└── tests/
    ├── adapters/
    │   ├── controllers/
    │   └── serializers/
    ├── application/
    │   ├── services/
    │   └── use_cases/
    ├── common/
    │   └── constants/
    └── domain/
        ├── entities/
        ├── exceptions/
        └── interfaces/
```

This structure adheres to the principles of hexagonal architecture and DDD, providing a clear and maintainable outline for your microservice.

## Requirements

- Python 3.9 or later

## Dependencies

To be added based on your project's needs.

## Author

- Éric Dominguez Morales - *Initial Work* - [Email](mailto:ericdominguezm@gmail.com)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
