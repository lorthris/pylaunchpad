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


def build_indexnow_payload(host: str, key: str, key_location: str, url_list: list[str]) -> dict:
    """Build standard JSON payload for IndexNow search engine submission."""
    return {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_list,
    }


def submit_indexnow(
    host: str = "lorthris.github.io",
    key: str = "d4e5f61a7b8c9d0e1f2a3b4c5d6e7f80",
    key_location: str = "https://lorthris.github.io/pylaunchpad/d4e5f61a7b8c9d0e1f2a3b4c5d6e7f80.txt",
    url_list: list[str] | None = None,
) -> dict:
    """Submit URLs to IndexNow search engine protocol (Bing, Yandex, Seznam, Naver)."""
    import httpx

    if url_list is None:
        url_list = [
            "https://lorthris.github.io/pylaunchpad/",
            "https://lorthris.github.io/pylaunchpad/docs.html",
            "https://lorthris.github.io/pylaunchpad/demo.html",
            "https://lorthris.github.io/pylaunchpad/vs-nextjs.html",
            "https://lorthris.github.io/pylaunchpad/fastapi-polar-guide.html",
            "https://lorthris.github.io/pylaunchpad/ai-micro-saas-guide.html",
            "https://lorthris.github.io/pylaunchpad/terms.html",
        ]

    payload = build_indexnow_payload(host, key, key_location, url_list)
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
    ]
    results = {}
    for ep in endpoints:
        try:
            r = httpx.post(ep, json=payload, timeout=10.0)
            results[ep] = {
                "status_code": r.status_code,
                "success": r.status_code in [200, 202],
            }
        except Exception as exc:
            results[ep] = {
                "status_code": 0,
                "success": False,
                "error": str(exc),
            }
    return results


def audit_internal_links(docs_dir: Path) -> dict:
    """Audit internal hyperlinks and assets across all HTML documentation files."""
    checked = 0
    broken = []

    for html_file in docs_dir.glob("*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        # Match href="..." and src="..."
        links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', content)
        for link in links:
            # Skip external links, mailto, javascript, and pure in-page fragments
            if link.startswith(("http://", "https://", "mailto:", "javascript:", "#")):
                continue
            # Strip fragment for file resolution
            target_rel = link.split("#")[0]
            if not target_rel:
                continue

            checked += 1
            target_path = docs_dir / target_rel
            if not target_path.exists():
                broken.append({
                    "source": html_file.name,
                    "target": link,
                })

    return {
        "checked": checked,
        "broken": broken,
        "all_valid": len(broken) == 0,
    }

