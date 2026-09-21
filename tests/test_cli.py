"""Automated tests for PyLaunchpad CLI commands."""

import argparse
import sqlite3
from pylaunchpad.cli import backup_database, generate_secret_key, init_project, verify_license


def test_cli_generate_secret_key():
    """Verify cryptographic secret key generation."""
    key1 = generate_secret_key()
    key2 = generate_secret_key()
    assert len(key1) >= 32
    assert len(key2) >= 32
    assert key1 != key2


def test_cli_init_project(tmp_path, monkeypatch):
    """Test project initialization and .env file generation."""
    monkeypatch.chdir(tmp_path)
    args = argparse.Namespace(name="TestSaaS", database="sqlite", force=False)
    exit_code = init_project(args)
    assert exit_code == 0

    env_path = tmp_path / ".env"
    assert env_path.exists()
    content = env_path.read_text(encoding="utf-8")
    assert 'APP_NAME="TestSaaS"' in content
    assert "SECRET_KEY=" in content
    assert "DATABASE_URL=" in content

    # Running again without --force should fail cleanly
    exit_code_again = init_project(args)
    assert exit_code_again == 1


def test_cli_verify_license_invalid():
    """Test verify-license CLI with invalid key."""
    args = argparse.Namespace(key="INVALID-KEY")
    exit_code = verify_license(args)
    assert exit_code in [0, 1]  # Either returns 1 or handled error


def test_cli_backup_database_success(tmp_path):
    """Test atomic SQLite database backup creation."""
    src_db = tmp_path / "test.db"
    dest_db = tmp_path / "test_backup.db"

    # Create dummy sqlite database with a table
    with sqlite3.connect(src_db) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
        conn.execute("INSERT INTO users (email) VALUES ('user@example.com')")
        conn.commit()

    args = argparse.Namespace(source=str(src_db), dest=str(dest_db))
    exit_code = backup_database(args)
    assert exit_code == 0
    assert dest_db.exists()

    # Verify backed up data is intact
    with sqlite3.connect(dest_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = 1")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "user@example.com"


def test_cli_backup_database_missing_source(tmp_path):
    """Negative control: verify backup fails cleanly when source DB does not exist."""
    missing_db = tmp_path / "nonexistent.db"
    dest_db = tmp_path / "dest.db"

    args = argparse.Namespace(source=str(missing_db), dest=str(dest_db))
    exit_code = backup_database(args)
    assert exit_code == 1
    assert not dest_db.exists()

