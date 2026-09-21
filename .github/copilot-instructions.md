# GitHub Copilot Instructions for PyLaunchpad

When suggesting code for PyLaunchpad:
- Follow FastAPI 0.110+ and SQLAlchemy 2.0 idioms.
- Validate request payloads with Pydantic v2 BaseModel schemas.
- Do not add heavy external dependencies when Python standard library functions suffice.
- Respect dark-mode only styling in HTML and CSS.
