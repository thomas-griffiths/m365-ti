"""Microsoft Graph API client helper."""

from typing import Any

import msal
import requests


class M365Client:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        # TODO: Initialize MSAL confidential client

    def lookup_indicator(self, indicator: str) -> None:
        """Lookup an indicator in M365 mailboxes.

        Args:
            indicator: Indicator of compromise to search for.
        """
        raise NotImplementedError("Graph API lookup not implemented")
