import argparse
import json
from pathlib import Path
from typing import List, Dict

from m365_client import M365Client
from threat_feed import collect_iocs
from utils import contains_any, summarize_hits

def load_config(path: Path) -> Dict:
    with path.open() as f:
        return json.load(f)

def scan_and_tag(client: M365Client, user: str, top: int, category: str, ensure_category: bool, summary_to: str | None):
    # 1) Pull IoCs
    iocs = collect_iocs()
    domains = sorted(iocs["domains"])
    ips = sorted(iocs["ipv4"])
    print(f"[feed] domains={len(domains)} ips={len(ips)}")

    # 2) List recent messages
    msgs = client.list_messages(user, top=top)
    print(f"[graph] fetched {len(msgs)} messages")

    # 3) Find hits
    needles = set(domains) | set(ips)
    hits: List[Dict] = []
    for m in msgs:
        text = f"{m.get('subject','')} {m.get('bodyPreview','')}"
        if contains_any(text, needles):
            hits.append({"id": m["id"], "subject": m.get("subject", ""), "receivedDateTime": m.get("receivedDateTime","")})

    print(f"[scan] hits={len(hits)}")

    # 4) Tag
    if hits:
        if ensure_category:
            client.ensure_category(user, category)
        for h in hits:
            client.tag_message(user, h["id"], category)
        print(f"[tag] applied category '{category}' to {len(hits)} messages")

    # 5) Optional summary email
    if summary_to:
        html = summarize_hits(hits)
        client.send_mail(user, summary_to, f"[PoC] Mail scan results ({len(hits)} hit{'s' if len(hits)!=1 else ''})", html)
        print(f"[mail] summary sent to {summary_to}")

def main():
    ap = argparse.ArgumentParser(description="Threat feed → M365 email tagger (PoC)")
    ap.add_argument("--config", default="config.json", help="Path to config.json")
    ap.add_argument("--user", required=True, help="Mailbox UPN to scan, e.g. user@tenant.onmicrosoft.com")
    ap.add_argument("--top", type=int, default=50, help="How many recent messages to scan")
    ap.add_argument("--category", default="Suspect-IOC", help="Mailbox category to apply on hits")
    ap.add_argument("--ensure-category", action="store_true", help="Create category if missing (needs MailboxSettings.ReadWrite)")
    ap.add_argument("--summary-to", default=None, help="Send HTML summary email to this address (optional)")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    client = M365Client(
        tenant_id=cfg["tenant_id"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scope=cfg.get("scope", "https://graph.microsoft.com/.default"),
        graph_base=cfg.get("graph_base", "https://graph.microsoft.com/v1.0"),
    )

    scan_and_tag(
        client=client,
        user=args.user,
        top=args.top,
        category=args.category,
        ensure_category=args.ensure_category,
        summary_to=args.summary_to,
    )

if __name__ == "__main__":
    main()
