# PyLaunchpad Agent Rules

Universal rules for autonomous agents working in this repository.

## Component Map

- Database models in `pylaunchpad/models/` inherit from `BaseModel`.
- API endpoints in `pylaunchpad/api/v1/` use explicit response models from `pylaunchpad/schemas/`.
- All password hashes use `hash_password` in `pylaunchpad/auth/security.py`.
- Polar.sh webhooks verify Standard Webhooks HMAC-SHA256 signatures with timestamp checks.

## Verification Gate

Every change must pass the automated test suite before completion:

```bash
pytest -v tests/
```
