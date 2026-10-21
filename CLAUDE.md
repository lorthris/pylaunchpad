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
- Never write credentials or hardcoded secret keys in code or `.env`.
- Keep credentials in Vaultwarden collection `mylaunchpad`.
- Write pure logic where practical; keep side effects isolated to route handlers and task workers.
- Run `python -m pytest -v tests/` before committing code changes.

## Commands

- Start development server with Vaultwarden secrets: `pwsh scripts/pylaunchpad_vault.ps1 uvicorn pylaunchpad.app:app --reload --port 8000`
- Run automated tests: `python -m pytest -v tests/`
- Build distribution package: `python distribution/build_release.py`

## Project navigation

Use `docs/project_map/INDEX.md` or open `docs/project_map/index.html` before broad searches.
The authored source is `docs/project_map/project_map_source.json`.

Run `python scripts/project_map.py q <path-or-words>` for ownership and related context.
Use `impact`, `tests` and `brief` with the same target before a change.
After an included file or component changes, update the source and run
`python scripts/project_map.py build` and `python scripts/project_map.py check`.
The launcher uses the shared engine under `~/.claude/tools/project-map`;
set `PROJECT_MAP_ENGINE` to its `project_map.py` file for a separate installation.
Keep credentials, local state, caches and generated packages out of the map inventory.
