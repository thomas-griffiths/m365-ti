"""
Simple IoC collectors from public sources:
- URLHaus (recent URLs) -> domains
- Feodo Tracker ipblocklist -> IPv4s

Swap/extend `collect_iocs` to take Dataminr payloads later.
"""
from typing import Dict, Set, Tuple
import re
import requests

DOMAIN_RE = re.compile(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
IPV4_RE = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")

def _urlhaus_domains() -> Set[str]:
    url = "https://urlhaus.abuse.ch/downloads/csv_recent/"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
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
    url = "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    ips = set(IPV4_RE.findall("\n".join([ln for ln in r.text.splitlines() if not ln.startswith("#")])))
    return ips

def collect_iocs() -> Dict[str, Set[str]]:
    domains = _urlhaus_domains()
    ips = _feodo_ips()
    return {"domains": domains, "ipv4": ips}
