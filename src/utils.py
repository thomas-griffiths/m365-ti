import re
from functools import lru_cache
from typing import Dict, Iterable, List


def normalize_text(s: str) -> str:
    """Normalize text for comparison."""
    return (s or "").lower()


@lru_cache(maxsize=4)
def _compile_patterns(needles: frozenset) -> List[re.Pattern]:
    """Pre-compile regex patterns for a frozen set of IoC needles."""
    patterns = []
    for needle in needles:
        needle = (needle or "").lower().strip()
        if not needle or len(needle) < 3:
            continue
        if _looks_like_ip(needle):
            patterns.append(re.compile(rf"\b{re.escape(needle)}\b"))
        else:
            patterns.append(re.compile(rf"(?<![\w.-]){re.escape(needle)}(?![\w.-])"))
    return patterns


def contains_any(text: str, needles: Iterable[str]) -> bool:
    """
    Check if text contains any of the IoCs with improved matching.
    Uses negative lookarounds for domains and exact matching for IPs to reduce false
    positives. Patterns are compiled once per unique needle set.
    """
    if not text or not needles:
        return False

    t = normalize_text(text)
    for pattern in _compile_patterns(frozenset(needles)):
        if pattern.search(t):
            return True
    return False


def _looks_like_ip(s: str) -> bool:
    """Quick check if string looks like an IP address."""
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", s))


def summarize_hits(hits: Iterable[Dict]) -> str:
    """Generate HTML summary of hits with proper escaping."""
    rows = []
    for h in hits:
        subject = _html_escape(h.get("subject", "(no subject)"))
        received_time = _html_escape(h.get("receivedDateTime", ""))
        msg_id = _html_escape(h.get("id", ""))
        rows.append(
            f"<li><b>{subject}</b> – {received_time} – <code>{msg_id}</code></li>"
        )
    return "<ul>" + "".join(rows or ["<li>No matches</li>"]) + "</ul>"


def _html_escape(text: str) -> str:
    """Basic HTML escaping to prevent XSS."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
