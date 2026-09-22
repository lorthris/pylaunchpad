"""Automated tests for search engine optimization and marketing utilities."""

import argparse
from pathlib import Path
from unittest.mock import patch

from pylaunchpad.cli import audit_seo, generate_utm, run_indexnow, run_link_check
from pylaunchpad.marketing import (
    audit_docs_directory,
    audit_html_file,
    audit_internal_links,
    build_indexnow_payload,
    generate_utm_link,
    submit_indexnow,
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


def test_build_indexnow_payload():
    """Verify IndexNow payload format matches protocol specification."""
    payload = build_indexnow_payload(
        host="example.com",
        key="test-key-123",
        key_location="https://example.com/test-key-123.txt",
        url_list=["https://example.com/page1", "https://example.com/page2"],
    )
    assert payload["host"] == "example.com"
    assert payload["key"] == "test-key-123"
    assert payload["keyLocation"] == "https://example.com/test-key-123.txt"
    assert len(payload["urlList"]) == 2


def test_audit_internal_links_live_docs():
    """Verify zero broken internal links across live docs directory."""
    docs_dir = Path("docs")
    res = audit_internal_links(docs_dir)
    assert res["all_valid"] is True
    assert len(res["broken"]) == 0
    assert res["checked"] >= 50


def test_audit_internal_links_broken_detection(tmp_path):
    """Negative control: verify audit flags missing target files."""
    html = '<a href="nonexistent.html">Broken Link</a><img src="missing.png">'
    (tmp_path / "index.html").write_text(html, encoding="utf-8")
    res = audit_internal_links(tmp_path)
    assert res["all_valid"] is False
    assert len(res["broken"]) == 2


def test_cli_seo_audit_command(capsys):
    """Test CLI seo-audit subcommand execution."""
    args = argparse.Namespace(dir="docs")
    exit_code = audit_seo(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "SEO Audit Results" in captured.out
    assert "All pages pass search engine optimization criteria" in captured.out


def test_cli_link_check_command(capsys):
    """Test CLI link-check subcommand execution."""
    args = argparse.Namespace(dir="docs")
    exit_code = run_link_check(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "All internal links and assets resolve successfully" in captured.out


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


def test_submit_indexnow_mock():
    """Verify submit_indexnow handles HTTP responses gracefully."""
    with patch("httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        res = submit_indexnow(
            host="lorthris.github.io",
            key="testkey",
            key_location="https://lorthris.github.io/pylaunchpad/testkey.txt",
            url_list=["https://lorthris.github.io/pylaunchpad/"],
        )
        assert len(res) == 2
        for ep, item in res.items():
            assert item["success"] is True
            assert item["status_code"] == 200


def test_cli_indexnow_command(capsys):
    """Test CLI indexnow subcommand with mock response."""
    with patch("pylaunchpad.marketing.submit_indexnow") as mock_submit:
        mock_submit.return_value = {
            "https://api.indexnow.org/indexnow": {"status_code": 200, "success": True},
            "https://www.bing.com/indexnow": {"status_code": 200, "success": True},
        }
        args = argparse.Namespace(host="lorthris.github.io", key="testkey")
        exit_code = run_indexnow(args)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Submitted successfully" in captured.out
