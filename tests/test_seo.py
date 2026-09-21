"""Automated tests for search engine optimization and marketing utilities."""

import argparse
from pathlib import Path

from pylaunchpad.cli import audit_seo, generate_utm
from pylaunchpad.marketing import (
    audit_docs_directory,
    audit_html_file,
    generate_utm_link,
)


def test_generate_utm_link():
    """Verify UTM tracking parameter generation."""
    url = generate_utm_link(
        base_url="https://lorthris.github.io/pylaunchpad/",
        source="reddit",
        medium="social",
        campaign="launch",
    )
    assert "utm_source=reddit" in url
    assert "utm_medium=social" in url
    assert "utm_campaign=launch" in url
    assert url.startswith("https://lorthris.github.io/pylaunchpad/?")


def test_audit_html_file_valid(tmp_path):
    """Verify audit passes for a fully compliant HTML file."""
    valid_html = """<!DOCTYPE html>
<html>
<head>
  <title>Sample Page</title>
  <meta name="description" content="This is a test description.">
  <link rel="canonical" href="https://example.com/page">
  <meta property="og:title" content="Sample Page">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">
  {"@context": "https://schema.org", "@type": "WebPage", "name": "Sample"}
  </script>
</head>
<body><h1>Hello</h1></body>
</html>"""
    test_file = tmp_path / "valid.html"
    test_file.write_text(valid_html, encoding="utf-8")

    res = audit_html_file(test_file)
    assert res["has_title"] is True
    assert res["has_description"] is True
    assert res["has_canonical"] is True
    assert res["has_og"] is True
    assert res["has_twitter"] is True
    assert res["json_ld_count"] == 1
    assert res["json_ld_valid"] is True


def test_audit_html_file_invalid(tmp_path):
    """Verify audit flags missing tags and malformed JSON-LD."""
    invalid_html = """<!DOCTYPE html>
<html>
<head>
  <script type="application/ld+json">
  { malformed json ld content }
  </script>
</head>
<body><h1>Hello</h1></body>
</html>"""
    test_file = tmp_path / "invalid.html"
    test_file.write_text(invalid_html, encoding="utf-8")

    res = audit_html_file(test_file)
    assert res["has_title"] is False
    assert res["has_description"] is False
    assert res["has_canonical"] is False
    assert res["has_og"] is False
    assert res["json_ld_count"] == 1
    assert res["json_ld_valid"] is False


def test_docs_directory_seo_compliance():
    """Verify all published documentation pages meet SEO standards."""
    docs_dir = Path("docs")
    assert docs_dir.exists()

    audits = audit_docs_directory(docs_dir)
    assert len(audits) >= 7

    files_found = {a["file"] for a in audits}
    expected_files = {
        "index.html",
        "docs.html",
        "demo.html",
        "terms.html",
        "vs-nextjs.html",
        "fastapi-polar-guide.html",
        "ai-micro-saas-guide.html",
    }
    assert expected_files.issubset(files_found)

    for a in audits:
        assert a["has_title"] is True, f"{a['file']} is missing title"
        assert a["has_description"] is True, f"{a['file']} is missing meta description"
        assert a["has_canonical"] is True, f"{a['file']} is missing canonical tag"
        assert a["has_og"] is True, f"{a['file']} is missing og:title"
        assert a["json_ld_valid"] is True, f"{a['file']} has invalid JSON-LD schema"


def test_cli_seo_audit_command(capsys):
    """Test CLI seo-audit subcommand execution."""
    args = argparse.Namespace(dir="docs")
    exit_code = audit_seo(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "SEO Audit Results" in captured.out
    assert "All pages pass search engine optimization criteria" in captured.out


def test_cli_utm_command(capsys):
    """Test CLI utm subcommand execution."""
    args = argparse.Namespace(
        url="https://lorthris.github.io/pylaunchpad/",
        source="twitter",
        medium="social",
        campaign="launch",
    )
    exit_code = generate_utm(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "utm_source=twitter" in captured.out
