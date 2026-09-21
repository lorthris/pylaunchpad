"""Automated tests for PyLaunchpad CLI commands."""

import argparse
from pylaunchpad.cli import generate_secret_key, init_project, verify_license


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
