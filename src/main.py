"""Entrypoint script for the threat feed to M365 integration."""

from m365_client import M365Client
from threat_feed import ThreatFeed
from utils import load_config


def main() -> None:
    config = load_config("config.json")
    client = M365Client(config)
    feed = ThreatFeed()
    indicators = feed.fetch_indicators()
    for indicator in indicators:
        client.lookup_indicator(indicator)


if __name__ == "__main__":
    main()
