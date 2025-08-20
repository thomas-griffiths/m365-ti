"""
Simple IoC collectors from public sources:
- URLHaus (recent URLs) -> domains
- Feodo Tracker ipblocklist -> IPv4s

Swap/extend `collect_iocs` to take Dataminr payloads later.
"""

import re
from typing import Dict, Set
import requests


DOMAIN_RE = re.compile(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
IPV4_RE = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")


def _urlhaus_domains() -> Set[str]:
    """Fetch domains from URLhaus threat feed with error handling."""
    url = "https://urlhaus.abuse.ch/downloads/csv_recent/"
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch URLhaus data: {e}")
        return set()

    domains: Set[str] = set()
    for line in r.text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        # CSV: <,,, URL ,,,>
        parts = line.split(",")
        if len(parts) < 4:
            continue
        raw_url = parts[2]
        # strip scheme and path
        host = raw_url.split("//")[-1].split("/")[0].lstrip("*.").lower()
        if DOMAIN_RE.match(host):
            domains.add(host)
    return domains


def _feodo_ips() -> Set[str]:
    """Fetch IPs from Feodo Tracker with error handling."""
    url = "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch Feodo data: {e}")
        return set()

    ips = set(
        IPV4_RE.findall(
            "\n".join([ln for ln in r.text.splitlines() if not ln.startswith("#")])
        )
    )
    return ips


def collect_iocs() -> Dict[str, Set[str]]:
    """Collect IoCs from all sources with deduplication."""
    domains = _urlhaus_domains()
    ips = _feodo_ips()

    # Remove duplicates and invalid entries
    domains = {d for d in domains if d and len(d) > 3}
    ips = {ip for ip in ips if ip and _validate_ip(ip)}

    print(f"[feed] Collected {len(domains)} domains, {len(ips)} IPs")
    return {"domains": domains, "ipv4": ips}


def _validate_ip(ip: str) -> bool:
    """Basic IP validation to avoid obvious false positives."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False
