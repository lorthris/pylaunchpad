"""Marketing automation and SEO auditing utilities for PyLaunchpad."""

import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse


def generate_utm_link(base_url: str, source: str, medium: str, campaign: str = "launch") -> str:
    """Generate a trackable UTM-tagged URL."""
    parsed = urlparse(base_url)
    query_params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    encoded = urlencode(query_params)
    return urlunparse(parsed._replace(query=encoded))


def audit_html_file(file_path: Path) -> dict:
    """Audit an HTML file for search engine optimization best practices."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    results = {
        "file": file_path.name,
        "has_title": bool(re.search(r"<title>.*?</title>", content, re.IGNORECASE | re.DOTALL)),
        "has_description": bool(re.search(r'<meta\s+name=["\']description["\']', content, re.IGNORECASE)),
        "has_canonical": bool(re.search(r'<link\s+rel=["\']canonical["\']', content, re.IGNORECASE)),
        "has_og": bool(re.search(r'<meta\s+property=["\']og:title["\']', content, re.IGNORECASE)),
        "has_twitter": bool(re.search(r'<meta\s+name=["\']twitter:card["\']', content, re.IGNORECASE)),
        "json_ld_count": len(re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', content, re.IGNORECASE | re.DOTALL)),
        "json_ld_valid": True,
    }

    # Verify JSON-LD schemas parse correctly
    for match in re.finditer(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', content, re.IGNORECASE | re.DOTALL):
        snippet = match.group(1).strip()
        try:
            json.loads(snippet)
        except Exception:
            results["json_ld_valid"] = False

    return results


def audit_docs_directory(docs_dir: Path) -> list[dict]:
    """Audit all HTML files within the documentation directory."""
    audits = []
    for p in sorted(docs_dir.glob("*.html")):
        audits.append(audit_html_file(p))
    return audits
