import re
from typing import Dict, Iterable

def normalize_text(s: str) -> str:
    return (s or "").lower()

def contains_any(text: str, needles: Iterable[str]) -> bool:
    t = normalize_text(text)
    for n in needles:
        n = (n or "").lower().strip()
        if not n:
            continue
        # Fast path: substring; for domains/IPs this is okay for a demo.
        if n in t:
            return True
    return False

def summarize_hits(hits: Iterable[Dict]) -> str:
    rows = []
    for h in hits:
        rows.append(f"<li><b>{h.get('subject','(no subject)')}</b> – {h.get('receivedDateTime','')} – <code>{h.get('id','')}</code></li>")
    return "<ul>" + "".join(rows or ["<li>No matches</li>"]) + "</ul>"
