import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict

from m365_client import M365Client
from threat_feed import collect_iocs
from utils import contains_any, summarize_hits

# Email validation regex
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> bool:
    """Validate email address format."""
    return bool(EMAIL_RE.match(email.strip())) if email else False


def load_config(path: Path) -> Dict:
    """Load and validate configuration file."""
    try:
        with path.open() as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{path}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")

    # Validate required configuration keys
    required_keys = ["tenant_id", "client_id", "client_secret"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    return config


def scan_and_tag(
    client: M365Client,
    user: str,
    top: int,
    category: str,
    ensure_category: bool,
    summary_to: str | None,
):
    """Main scanning and tagging logic with improved error handling."""
    # Validate user email
    if not validate_email(user):
        raise ValueError(f"Invalid user email format: {user}")

    # Validate summary email if provided
    if summary_to and not validate_email(summary_to):
        raise ValueError(f"Invalid summary email format: {summary_to}")

    # 1) Pull IoCs
    try:
        iocs = collect_iocs()
        domains = sorted(iocs["domains"])
        ips = sorted(iocs["ipv4"])

        if not domains and not ips:
            print("Warning: No IoCs collected from threat feeds")
            return

        print(f"[feed] domains={len(domains)} ips={len(ips)}")
    except Exception as e:
        raise RuntimeError(f"Error collecting IoCs: {e}") from e

    # 2) List recent messages
    try:
        msgs = client.list_messages(user, top=top)
        print(f"[graph] fetched {len(msgs)} messages")
    except Exception as e:
        raise RuntimeError(f"Error fetching messages: {e}") from e

    # 3) Find hits
    needles = set(domains) | set(ips)
    hits: List[Dict] = []
    for m in msgs:
        text = f"{m.get('subject', '')} {m.get('bodyPreview', '')}"
        if contains_any(text, needles):
            hits.append(
                {
                    "id": m["id"],
                    "subject": m.get("subject", ""),
                    "receivedDateTime": m.get("receivedDateTime", ""),
                }
            )

    print(f"[scan] hits={len(hits)}")

    # 4) Tag
    if hits:
        try:
            if ensure_category:
                client.ensure_category(user, category)
            for h in hits:
                client.tag_message(user, h["id"], category)
            print(f"[tag] applied category '{category}' to {len(hits)} messages")
        except Exception as e:
            print(f"Error tagging messages: {e}")
            return

    # 5) Optional summary email
    if summary_to and hits:
        try:
            html = summarize_hits(hits)
            client.send_mail(
                user,
                summary_to,
                f"[PoC] Mail scan results ({len(hits)} hit{'s' if len(hits) != 1 else ''})",
                html,
            )
            print(f"[mail] summary sent to {summary_to}")
        except Exception as e:
            print(f"Error sending summary email: {e}")


def main():
    ap = argparse.ArgumentParser(description="Threat feed → M365 email tagger (PoC)")
    ap.add_argument("--config", default="config.json", help="Path to config.json")
    ap.add_argument(
        "--user",
        required=True,
        help="Mailbox UPN to scan, e.g. user@tenant.onmicrosoft.com",
    )
    ap.add_argument(
        "--top",
        type=int,
        default=50,
        help="How many recent messages to scan (max 1000)",
    )
    ap.add_argument(
        "--category", default="Suspect-IOC", help="Mailbox category to apply on hits"
    )
    ap.add_argument(
        "--ensure-category",
        action="store_true",
        help="Create category if missing (needs MailboxSettings.ReadWrite)",
    )
    ap.add_argument(
        "--summary-to",
        default=None,
        help="Send HTML summary email to this address (optional)",
    )
    args = ap.parse_args()

    # Validate arguments
    if args.top <= 0 or args.top > 1000:
        print("Error: --top must be between 1 and 1000")
        sys.exit(1)

    if not args.category.strip():
        print("Error: --category cannot be empty")
        sys.exit(1)

    try:
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
            category=args.category.strip(),
            ensure_category=args.ensure_category,
            summary_to=args.summary_to,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
