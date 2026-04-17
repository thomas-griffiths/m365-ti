import sys
from pathlib import Path

# Ensure src directory is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from utils import contains_any, summarize_hits, _html_escape


def test_contains_any_matches_exact_domain():
    assert contains_any("domain.com", ["domain.com"]) is True


def test_contains_any_ignores_similar_domains():
    needles = ["domain.com"]
    assert contains_any("sub.domain.com", needles) is False
    assert contains_any("domain.com.bad", needles) is False
    assert contains_any("notdomain.com", needles) is False


def test_contains_any_matches_ip():
    assert contains_any("contact 1.2.3.4 now", ["1.2.3.4"]) is True


def test_contains_any_ignores_ip_substring():
    # 1.2.3.4 should not match 1.2.3.45
    assert contains_any("1.2.3.45", ["1.2.3.4"]) is False


def test_contains_any_empty_inputs():
    assert contains_any("", ["domain.com"]) is False
    assert contains_any("some text", []) is False
    assert contains_any("", []) is False


def test_contains_any_short_needles_skipped():
    # needles shorter than 3 chars are ignored
    assert contains_any("ab text", ["ab"]) is False


# --- summarize_hits ---

def test_summarize_hits_returns_html_list():
    hits = [{"id": "abc", "subject": "Test", "receivedDateTime": "2024-01-01"}]
    html = summarize_hits(hits)
    assert html.startswith("<ul>")
    assert html.endswith("</ul>")
    assert "<li>" in html


def test_summarize_hits_empty_returns_no_matches():
    html = summarize_hits([])
    assert "No matches" in html


def test_summarize_hits_escapes_subject():
    hits = [{"id": "x", "subject": "<script>alert(1)</script>", "receivedDateTime": ""}]
    html = summarize_hits(hits)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


# --- _html_escape ---

def test_html_escape_ampersand():
    assert _html_escape("a & b") == "a &amp; b"


def test_html_escape_tags():
    assert _html_escape("<b>bold</b>") == "&lt;b&gt;bold&lt;/b&gt;"


def test_html_escape_quotes():
    assert _html_escape('"quoted"') == "&quot;quoted&quot;"


def test_html_escape_empty():
    assert _html_escape("") == ""
    assert _html_escape(None) == ""
