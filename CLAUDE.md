# PyLaunchpad Coding Agent Rules

Guidelines for AI coding assistants working in this repository.

## Architecture Boundaries

- `pylaunchpad/app.py`: Application factory, middleware, and route mounting.
- `pylaunchpad/config.py`: Central configuration using Pydantic Settings. Do not hardcode secrets or ports.
- `pylaunchpad/database.py`: SQLAlchemy session generator. Always use `get_db` dependency in FastAPI endpoints.
- `pylaunchpad/models/`: Database entities. Inherit from `pylaunchpad.models.base.BaseModel`.
- `pylaunchpad/schemas/`: Pydantic request and response models. Separate database models from API schemas.
- `pylaunchpad/auth/`: Security logic. Use PBKDF2 password hashing and JWT token signing.
- `pylaunchpad/billing/`: Polar.sh API interactions and Standard Webhook verification.
- `pylaunchpad/tasks/`: In-process asynchronous task queue.
- `pylaunchpad/api/v1/`: Versioned REST API endpoints.

## Coding Standards

- Use Python 3.10+ type hints for all function signatures.
- Prefer explicit error handling over generic exceptions.
- Never write credentials or hardcoded secret keys in code.
- Write pure logic where practical; keep side effects isolated to route handlers and task workers.
- Run `pytest -v tests/` before committing code changes.

## Commands

- Start development server: `uvicorn pylaunchpad.app:app --reload --port 8000`
- Run automated tests: `pytest -v tests/`
- Build distribution package: `python distribution/build_release.py`
