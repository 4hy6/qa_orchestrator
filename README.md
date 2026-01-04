# QA Orchestrator

Automated testing framework designed for the Restful-Booker API.
This project implements a scalable architecture using Python 3.12, Pytest, and Pydantic with strict type enforcement.

## Features

*   **API Client:** Modular wrapper around `requests` with automatic retries, logging, and session management.
*   **Data Validation:** Strict Pydantic models for request/response contracts.
*   **Type Safety:** Fully typed codebase verified by `mypy` in strict mode.
*   **Infrastructure:** Docker-ready and configured for CI/CD pipelines.

## Requirements

*   Python 3.12+
*   uv (Dependency manager)
*   Make (Optional, for build automation)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd qa_orchestrator
    ```

2.  **Install dependencies:**
    ```bash
    make install
    # Or manually: uv sync
    ```

3.  **Environment Setup:**
    Copy the example configuration file and adjust settings if necessary.
    ```bash
    cp .env.example .env
    ```

## Usage

### Running Tests

To run the test suite using Pytest:

```bash
make test
```

For verbose output:
```bash
make test-v
```

### Static Analysis & Code Quality

The project enforces strict code quality standards using Ruff and Mypy.

```bash
# Run linting
make lint

# Run type checking
make type-check

# Run full quality gate (Format + Lint + Type + Test)
make check
```

## Configuration

Configuration is managed via environment variables (supported by `.env` file).

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment (dev/test/prod) | `dev` |
| `BASE_URL` | Target API URL | `https://restful-booker.herokuapp.com` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `BOOKER_USERNAME` | Username for API Auth | - |
| `BOOKER_PASSWORD` | Password for API Auth | - |

## Project Structure

*   `app/clients` - API interaction layer (HTTP clients).
*   `app/schemas` - Pydantic data models.
*   `tests` - Test suite and fixtures.
*   `config` - Configuration loaders and logging setup.
