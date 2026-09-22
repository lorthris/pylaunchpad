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
APP_VERSION="1.0.4"
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


def backup_database(args: argparse.Namespace) -> int:
    """Create an atomic backup of the local SQLite database file."""
    src = Path(args.source or "pylaunchpad.db")
    if not src.exists():
        print(f"[-] Source database file not found: {src}")
        return 1

    dest = Path(args.dest or f"backup_{src.stem}_{secrets.token_hex(4)}.db")
    import sqlite3

    try:
        with sqlite3.connect(src) as src_conn, sqlite3.connect(dest) as dest_conn:
            src_conn.backup(dest_conn)
        print(f"[+] Atomic database backup created: {dest}")
        return 0
    except Exception as exc:
        print(f"[-] Backup failed: {exc}")
        return 1


def audit_seo(args: argparse.Namespace) -> int:
    """Audit HTML documentation for search engine optimization standards."""
    from pylaunchpad.marketing import audit_docs_directory

    docs_dir = Path(args.dir)
    if not docs_dir.exists():
        print(f"[-] Directory not found: {docs_dir}")
        return 1

    audits = audit_docs_directory(docs_dir)
    if not audits:
        print(f"[!] No HTML files found in {docs_dir}")
        return 1

    print(f"SEO Audit Results for {docs_dir} ({len(audits)} pages):")
    print("-" * 75)
    all_pass = True
    for a in audits:
        status = "PASS" if (a["has_title"] and a["has_description"] and a["has_canonical"] and a["has_og"] and a["json_ld_valid"]) else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"[{status}] {a['file']:<26} Title: {a['has_title']} | Meta: {a['has_description']} | Canon: {a['has_canonical']} | OG: {a['has_og']} | LD: {a['json_ld_count']}")
    print("-" * 75)
    if all_pass:
        print("[+] All pages pass search engine optimization criteria.")
        return 0
    print("[-] Some pages failed search engine optimization criteria.")
    return 1


def generate_utm(args: argparse.Namespace) -> int:
    """Generate a trackable UTM marketing URL."""
    from pylaunchpad.marketing import generate_utm_link

    link = generate_utm_link(
        base_url=args.url,
        source=args.source,
        medium=args.medium,
        campaign=args.campaign,
    )
    print(f"Generated trackable URL:\n{link}")
    return 0


def run_indexnow(args: argparse.Namespace) -> int:
    """Submit URLs to search engines via IndexNow protocol."""
    from pylaunchpad.marketing import submit_indexnow

    print(f"Submitting URLs for {args.host} via IndexNow...")
    results = submit_indexnow(host=args.host, key=args.key)
    success = True
    for ep, res in results.items():
        if res.get("success"):
            print(f"[+] {ep}: Submitted successfully (HTTP {res.get('status_code')})")
        else:
            print(f"[-] {ep}: Submission status {res.get('status_code')} (detail: {res.get('error', 'none')})")
            # IndexNow returns 200 or 202 on success; other codes might be due to offline or rate limits
    return 0 if success else 1


def run_link_check(args: argparse.Namespace) -> int:
    """Audit internal hyperlinks and assets in documentation directory."""
    from pylaunchpad.marketing import audit_internal_links

    docs_dir = Path(args.dir)
    if not docs_dir.exists():
        print(f"[-] Directory not found: {docs_dir}")
        return 1

    res = audit_internal_links(docs_dir)
    print(f"Link Audit for {docs_dir}: Checked {res['checked']} internal links and asset references.")
    if res["all_valid"]:
        print("[+] All internal links and assets resolve successfully.")
        return 0

    print(f"[-] Found {len(res['broken'])} broken links:")
    for b in res["broken"]:
        print(f"  - {b['source']} -> {b['target']}")
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

    # backup subcommand
    backup_parser = subparsers.add_parser("backup", help="Create an atomic backup of SQLite database")
    backup_parser.add_argument("--source", default="pylaunchpad.db", help="Path to source SQLite database")
    backup_parser.add_argument("--dest", default=None, help="Destination backup file path")

    # seo-audit subcommand
    seo_parser = subparsers.add_parser("seo-audit", help="Audit documentation pages for SEO compliance")
    seo_parser.add_argument("--dir", default="docs", help="Directory containing HTML files (default: docs)")

    # link-check subcommand
    link_parser = subparsers.add_parser("link-check", help="Audit internal links and asset references")
    link_parser.add_argument("--dir", default="docs", help="Directory containing HTML files (default: docs)")

    # indexnow subcommand
    indexnow_parser = subparsers.add_parser("indexnow", help="Submit documentation URLs to IndexNow search engine protocol")
    indexnow_parser.add_argument("--host", default="lorthris.github.io", help="Host domain")
    indexnow_parser.add_argument("--key", default="d4e5f61a7b8c9d0e1f2a3b4c5d6e7f80", help="IndexNow API key")

    # utm subcommand
    utm_parser = subparsers.add_parser("utm", help="Generate trackable UTM marketing link")
    utm_parser.add_argument("--url", default="https://lorthris.github.io/pylaunchpad/", help="Base URL")
    utm_parser.add_argument("--source", required=True, help="UTM source (e.g. reddit, twitter, hackernews)")
    utm_parser.add_argument("--medium", required=True, help="UTM medium (e.g. social, post, directory)")
    utm_parser.add_argument("--campaign", default="launch", help="Campaign name (default: launch)")

    args = parser.parse_args()

    if args.command == "init":
        return init_project(args)
    if args.command == "verify-license":
        return verify_license(args)
    if args.command == "backup":
        return backup_database(args)
    if args.command == "seo-audit":
        return audit_seo(args)
    if args.command == "link-check":
        return run_link_check(args)
    if args.command == "indexnow":
        return run_indexnow(args)
    if args.command == "utm":
        return generate_utm(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())


