"""Command-line interface (CLI) for PyLaunchpad starter kit scaffolding."""

import argparse
import secrets
import sys
from pathlib import Path


BANNER = r"""
  ____        _                              _                 _ 
 |  _ \ _   _| |    __ _ _   _ _ __   ___| |__  _ __   __ _| |
 | |_) | | | | |   / _` | | | | '_ \ / __| '_ \| '_ \ / _` | |
 |  __/| |_| | |__| (_| | |_| | | | | (__| | | | |_) | (_| |_|
 |_|    \__, |_____\__,_|\__,_|_| |_|\___|_| |_| .__/ \__,_(_)
        |___/                                  |_|            
"""


def generate_secret_key() -> str:
    """Generate a cryptographically secure 32-byte URL-safe secret key."""
    return secrets.token_urlsafe(32)


def init_project(args: argparse.Namespace) -> int:
    """Initialize environment and database configurations for a new PyLaunchpad project."""
    project_dir = Path.cwd()
    env_file = project_dir / ".env"

    print(BANNER)
    print("Welcome to PyLaunchpad Pro - Production FastAPI Micro-SaaS Starter Kit")
    print("-" * 70)

    if env_file.exists() and not args.force:
        print(f"[!] Warning: {env_file} already exists. Use --force to overwrite.")
        return 1

    secret_key = generate_secret_key()
    app_name = args.name or "MyMicroSaaS"
    db_choice = args.database or "sqlite"

    if db_choice == "postgres":
        db_url = "postgresql+asyncpg://user:password@localhost:5432/myapp_db"
    else:
        db_url = "sqlite:///./pylaunchpad.db"

    env_content = f"""# PyLaunchpad Application Configuration
ENVIRONMENT=development
DEBUG=True
APP_NAME="{app_name}"
APP_VERSION="1.0.1"
HOST="0.0.0.0"
PORT=8000

# Security (Cryptographically generated)
SECRET_KEY="{secret_key}"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database
DATABASE_URL="{db_url}"

# Polar.sh Merchant of Record Billing
# Get your credentials at https://polar.sh/
POLAR_ACCESS_TOKEN=""
POLAR_ORGANIZATION_ID=""
POLAR_WEBHOOK_SECRET=""
POLAR_ENVIRONMENT="sandbox"

# Rate Limiting
DEFAULT_RATE_LIMIT_PER_MINUTE=60
"""

    env_file.write_text(env_content, encoding="utf-8")
    print(f"[+] Created environment configuration: {env_file}")
    print(f"[+] Secret key generated: {secret_key[:8]}...")
    print(f"[+] Database target: {db_url}")
    print("-" * 70)
    print("Next steps:")
    print("  1. Run migrations / tests:  python -m pytest")
    print("  2. Start local server:      uvicorn pylaunchpad.app:app --reload")
    print("  3. View interactive API:    http://localhost:8000/api/docs")
    print("  4. View live dashboard:     http://localhost:8000/dashboard")
    print("-" * 70)
    print("Need the production commercial licence or turnkey Polar billing?")
    print("Get PyLaunchpad Pro: https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk")
    print("(Use promo code LAUNCH20 for 20% off)")
    return 0


def verify_license(args: argparse.Namespace) -> int:
    """Verify customer license key against Polar.sh API."""
    key = args.key.strip()
    if not key:
        print("Error: License key cannot be empty.")
        return 1

    print(f"Verifying PyLaunchpad Pro license key: {key}...")
    import httpx
    try:
        r = httpx.post(
            "https://api.polar.sh/v1/license-keys/validate",
            json={"key": key, "organization_id": "3a277a0f-0b25-43e0-af89-0eb74ccf069d"},
            timeout=10.0,
        )
        if r.status_code == 200 and r.json().get("status") == "granted":
            print("[+] Licence valid and active! Thank you for supporting PyLaunchpad.")
            return 0
        print(f"[-] Validation failed: Status {r.status_code}. Response: {r.text}")
        return 1
    except Exception as exc:
        print(f"[-] Error connecting to Polar API: {exc}")
        return 1


def main() -> int:
    """CLI entry point for PyLaunchpad command-line runner."""
    parser = argparse.ArgumentParser(description="PyLaunchpad Starter Kit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init subcommand
    init_parser = subparsers.add_parser("init", help="Initialize a new project environment")
    init_parser.add_argument("--name", default="MyMicroSaaS", help="Application name")
    init_parser.add_argument("--database", choices=["sqlite", "postgres"], default="sqlite", help="Target database")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing .env file")

    # verify-license subcommand
    license_parser = subparsers.add_parser("verify-license", help="Verify a Polar.sh license key")
    license_parser.add_argument("key", help="Customer license key (e.g. PYLP-XXXX-XXXX-XXXX)")

    args = parser.parse_args()

    if args.command == "init":
        return init_project(args)
    if args.command == "verify-license":
        return verify_license(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
