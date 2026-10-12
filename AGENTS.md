# PyLaunchpad Agent Rules

Universal rules for autonomous agents working in this repository.

## Component Map

- Database models in `pylaunchpad/models/` inherit from `BaseModel`.
- API endpoints in `pylaunchpad/api/v1/` use explicit response models from `pylaunchpad/schemas/`.
- All password hashes use `hash_password` in `pylaunchpad/auth/security.py`.
- Polar.sh webhooks verify Standard Webhooks HMAC-SHA256 signatures with timestamp checks.

## Secrets and Vaultwarden Integration

- Store all project credentials in Vaultwarden collection `mylaunchpad` at `https://vault.yaboylorthy.com:8443`.
- Items: `app-security` (`secret_key`), `polar-billing` (`organization_id`, `environment`, `access_token`, `webhook_secret`), `database-app` (`database_url`).
- Never commit credentials to git or store plaintext secrets in `.env` files.
- Inject secrets into child processes using `scripts/pylaunchpad_vault.ps1` or `vw-run --account mylaunchpad`.

## Shared Brain Scope

- Repository maps to the `pylaunchpad` Brain project scope in `C:/Drive/Brain`.
- Search project and global memory with `python -B C:/Drive/Brain/tools/brain.py find <words>`.
- Store durable project facts that the repository does not hold in `projects/pylaunchpad/`.

## Verification Gate

Every change must pass the automated test suite before completion:

```bash
python -m pytest -v tests/
```
