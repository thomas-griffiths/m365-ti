# Threat Feed → M365 Email Integration (PoC)

This project demonstrates integrating a public/open threat intelligence feed with Microsoft 365 (Outlook/Exchange Online) using the **Microsoft Graph API**.

The PoC workflow:
1. Ingest indicators from a threat feed (domains, IPs, hashes).
2. Query M365 mailboxes via Graph API for potential matches.
3. Export results or raise alerts (e.g., tickets, logs, or SIEM integration).

---

## Quick Start

### 1. Clone repo
```bash
git clone https://github.com/thomas-griffiths/m365-ti.git
cd threatfeed-m365-poc
