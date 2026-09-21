"""Release packaging script to generate production customer distribution archives."""

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
VERSION = "1.0.0"
PACKAGE_NAME = f"pylaunchpad-pro-v{VERSION}"
ZIP_FILENAME = f"{PACKAGE_NAME}.zip"

EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build",
    "*.egg-info",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    "pylaunchpad.db",
    "pylaunchpad.sqlite3",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
}


def build_release_package() -> Path:
    """Pack project files into clean customer release ZIP archive with SHA-256 manifest."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / ZIP_FILENAME

    file_count = 0
    total_bytes = 0

    print(f"Building PyLaunchpad Pro release: {ZIP_FILENAME}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith(".egg-info")]

            rel_root = Path(root).relative_to(ROOT_DIR)

            # Skip dist directory
            if str(rel_root).startswith("dist"):
                continue

            for file in files:
                if file in EXCLUDE_FILES or file.endswith(".pyc"):
                    continue

                full_path = Path(root) / file
                archive_path = Path(PACKAGE_NAME) / rel_root / file

                zipf.write(full_path, str(archive_path).replace("\\", "/"))
                file_count += 1
                total_bytes += full_path.stat().st_size

    # Compute SHA-256 digest
    sha256 = hashlib.sha256()
    with open(zip_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    digest = sha256.hexdigest()

    # Write checksum file
    checksum_path = DIST_DIR / f"{ZIP_FILENAME}.sha256"
    checksum_path.write_text(f"{digest} *{ZIP_FILENAME}\n", encoding="utf-8")

    # Write manifest
    manifest = {
        "package_name": PACKAGE_NAME,
        "version": VERSION,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "files_included": file_count,
        "uncompressed_bytes": total_bytes,
        "compressed_bytes": zip_path.stat().st_size,
        "sha256": digest,
    }
    manifest_path = DIST_DIR / f"{PACKAGE_NAME}-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Build complete:")
    print(f"  Archive:  {zip_path} ({manifest['compressed_bytes']:,} bytes)")
    print(f"  Files:    {file_count} files included")
    print(f"  SHA-256:  {digest}")
    print(f"  Manifest: {manifest_path}")

    return zip_path


if __name__ == "__main__":
    build_release_package()
