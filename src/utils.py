import re
from typing import Dict, Iterable


def normalize_text(s: str) -> str:
    """Normalize text for comparison."""
    return (s or "").lower()


def contains_any(text: str, needles: Iterable[str]) -> bool:
    """
    Check if text contains any of the IoCs with improved matching.
    Uses word boundaries for domains and exact matching for IPs to reduce false positives.
    """
    if not text or not needles:
        return False

    t = normalize_text(text)
    for needle in needles:
        needle = (needle or "").lower().strip()
        if not needle or len(needle) < 3:  # Skip very short needles
            continue

        # For IP addresses, use exact matching with word boundaries
        if _looks_like_ip(needle):
            if re.search(rf"\b{re.escape(needle)}\b", t):
                return True
        # For domains, use word boundaries but allow subdomain matching
        else:
            # Match domain.com or subdomain.domain.com
            pattern = rf"\b{re.escape(needle)}\b"
            if re.search(pattern, t):
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
