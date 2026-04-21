# GitHub SDK Sandbox

A FastAPI-based application designed to interact with the GitHub API, providing a structured way to manage repository data and storage operations.

### Overview

This project serves as a bridge between your local environment and GitHub. It uses a clean, layered architecture to handle API requests, business logic, and data persistence.

### Key Features:

- GitHub Client: Robust integration with the GitHub API for fetching repository details.

- Layered Architecture: Separation of concerns between API routes, services, and external clients.

- Flexible Storage: An abstract storage layer with an initial In-Memory implementation.

- Schema Validation: Strict data typing using Pydantic models.

## 

1. Clone this repository to your local machine.

    ```bash
    git clone https://github.com/Andrii-Bezkrovnyi/service_app.git
    ```

2. Navigate to the project directory:

    ```bash
    cd service_app
    ```

3. Create virtual environment:

   ```bash
    python -m venv venv
   ```
4. Enter in virtual environment in Linux:

   ```bash
    source venv/bin/activate
   ```
   - in Windows
   ```bash
    venv\Scripts\activate
   ```
5. Install the main dependencies:
    ```bash
    pip install .
    ```
6. Install the development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```
7. Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
8. Set `GITHUB_TOKEN` in the `.env`.
9. Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```
   - or
    ```bash
    py -m app.main
    ```
10. Open your browser and navigate to `http://127.0.0.1:8000/docs` 
to access the interactive API documentation in Swagger UI.

### Example endpoints

- `GET /health`
- `GET /github/users/{username}`
- `GET /github/repos/{owner}/{repo}`
- `GET /github/users/{username}/repos`
- `GET /storage`
- `GET /storage/{key}`
- `POST /storage/{key}`
- `PUT /storage/{key}`
- `DELETE /storage/{key}`

### Data for create and update operations:
```bash
{
  "login": "Andrii-Bezkrovnyi",
  "id": 72101233,
  "name": "Andrei Bezkrovnyi",
  "public_repos": 2
}
```

## Architecture of the project
    service_app/
    ├── app/
    │   ├── api/                # FastAPI Layer: Route handlers and controllers
    │   │   ├── __init__.py
    │   │   ├── github_routes.py
    │   │   └── storage_routes.py
    │   ├── clients/            # Integration Layer: GitHub API SDK and HTTP clients 
    │   │   ├── __init__.py
    │   │   └── github_client.py
    │   ├── core/               # Core Layer: Shared config, exceptions, and utilities
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── exceptions.py
    │   │   ├── json_utils.py
    │   │   └── types.py
    │   ├── schemas/            # Data Layer: Pydantic models (DTOs) and validation 
    │   │   ├── __init__.py
            ├── repo_schemas.py
    │   ├── services/           # Service Layer: Core business logic 
    │   │   ├── __init__.py
    │   │   └── github_service.py
    │   ├── storage/            # Persistence Layer: In-memory and abstract storage 
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── in_memory.py
    │   ├── __init__.py
    │   ├── dependencies.py     # FastAPI dependency injection helpers
    │   └── main.py             # Application entry point
    ├── tests/                  # Test Suite: Pytest implementation
    │   ├── __init__.py 
    │   ├── conftest.py
    │   ├── test_repos.py
    │   ├── test_storage.py
    │   └── test_users.py
    ├── .env.example            # Environment variables template
    ├── .env                    # Environment variables
    ├── .gitignore              # Git exclusion rules
    ├── pyproject.toml          # Project metadata and dependencies
    ├── pytest.ini              # Pytest configuration
    ├── README.md               # Project documentation
    └── setup.cfg               # Tooling configuration
