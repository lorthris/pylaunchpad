# Maintenance & Reliability Plan

Quarterly maintenance, dependency upgrade protocol, and security monitoring procedures for PyLaunchpad.

---

## 1. Maintenance Cadence

To maintain operational reliability with near-zero ongoing effort:

| Frequency | Action | Verification |
| :--- | :--- | :--- |
| **Quarterly** | Audit dependency versions and security advisories | `pip-audit` and `pytest -v tests/` |
| **Quarterly** | Re-run distribution packaging build | `python distribution/build_release.py` |
| **Biannual** | Test clean container build on newest Python base image | `docker compose build --no-cache` |
| **As Needed** | Patch upstream security advisories within 48 hours | Release patch update via Polar |

---

## 2. Dependency Audit Procedure

1. Scan active dependencies for reported vulnerabilities:
   ```bash
   pip install pip-audit
   pip-audit
   ```
2. Check for outdated core packages (FastAPI, Pydantic, SQLAlchemy, Uvicorn):
   ```bash
   pip list --outdated
   ```
3. Update version pins in `pyproject.toml` and re-run test suite:
   ```bash
   pytest -v tests/
   ```

---

## 3. Release Versioning Policy

PyLaunchpad follows **Semantic Versioning (SemVer 2.0)**:
- **Major (`X.0.0`):** Breaking architectural changes or backwards-incompatible database schema revisions.
- **Minor (`1.X.0`):** New feature modules (e.g. adding OAuth providers, extra ORM templates).
- **Patch (`1.0.X`):** Security patches, dependency updates, and bug fixes.

---

## 4. Disaster Recovery & Rollback

- **Code Rollback:** Every customer release is tracked in git tags (`v1.0.0`, `v1.0.1`, `v1.0.2`). If an upstream library regression occurs, revert to the previous release tag in git.
- **Customer Deliverable Backups:** Release archives are saved in `dist/` with accompanying `.sha256` checksums and manifest files.
