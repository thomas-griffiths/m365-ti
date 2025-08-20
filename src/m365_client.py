import time
from typing import Dict, List, Optional
import requests
import msal


class M365Client:
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        scope: str = "https://graph.microsoft.com/.default",
        graph_base: str = "https://graph.microsoft.com/v1.0",
    ):
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = [scope]
        self.graph = graph_base.rstrip("/")
        self._session = requests.Session()
        self._cca = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=self.authority,
        )
        self._token: Optional[Dict] = None
        self._token_exp = 0

    def _get_token(self) -> str:
        now = int(time.time())
        if self._token and now < self._token_exp - 60:
            return self._token["access_token"]
        token = self._cca.acquire_token_for_client(scopes=self.scope)
        if "access_token" not in token:
            raise RuntimeError(f"Token error: {token}")
        self._token = token
        # expires_in is seconds from now
        self._token_exp = now + int(token.get("expires_in", 3599))
        return token["access_token"]

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._get_token()}"}

    # ------------ Mail ------------
    def list_messages(
        self,
        user_upn: str,
        top: int = 50,
        select: str = "id,subject,receivedDateTime,bodyPreview,categories",
    ) -> List[Dict]:
        """List messages with improved error handling."""
        url = f"{self.graph}/users/{user_upn}/messages"
        params = {
            "$top": str(min(top, 1000)),
            "$select": select,
        }  # Limit to reasonable max

        try:
            resp = self._session.get(
                url, headers=self._headers(), params=params, timeout=30
            )
            resp.raise_for_status()
            return resp.json().get("value", [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to list messages for {user_upn}: {e}")

    def ensure_category(self, user_upn: str, category: str) -> None:
        """Create master category if missing with improved error handling."""
        # Validate category name
        if not category or len(category.strip()) == 0:
            raise ValueError("Category name cannot be empty")

        url = f"{self.graph}/users/{user_upn}/outlook/masterCategories"

        try:
            # Check list first (avoid noisy errors)
            r = self._session.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            names = {x.get("displayName") for x in r.json().get("value", [])}
            if category in names:
                return

            payload = {"displayName": category, "color": "preset0"}
            resp = self._session.post(
                url,
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if resp.status_code not in (200, 201, 409):
                resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(
                f"Failed to ensure category '{category}' for {user_upn}: {e}"
            )

    def tag_message(self, user_upn: str, message_id: str, category: str) -> None:
        """Tag message with improved error handling."""
        if not message_id or not category:
            raise ValueError("Message ID and category are required")

        url = f"{self.graph}/users/{user_upn}/messages/{message_id}"
        payload = {"categories": [category]}

        try:
            resp = self._session.patch(
                url,
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to tag message {message_id}: {e}")

    def send_mail(self, user_upn: str, to: str, subject: str, body_html: str) -> None:
        """Send mail with improved error handling."""
        if not to or not subject:
            raise ValueError("Recipient and subject are required")

        url = f"{self.graph}/users/{user_upn}/sendMail"
        payload = {
            "message": {
                "subject": subject[:255],  # Limit subject length
                "body": {"contentType": "HTML", "content": body_html},
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
            "saveToSentItems": True,
        }

        try:
            resp = self._session.post(
                url,
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if resp.status_code not in (200, 202):
                resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to send mail to {to}: {e}")
