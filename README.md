


# M365 Threat Feed Integration

This project demonstrates how to integrate an **open-source threat feed** with **Microsoft 365 (Outlook Email)** using the Microsoft Graph API.  
The goal is to fetch indicators from a public threat feed and use them to check and act upon emails inside an M365 environment.  

---

## 🚀 Features
- Connects to Microsoft 365 using OAuth2 and Microsoft Graph API.  
- Retrieves indicators (IPs, domains, URLs, hashes) from a threat feed.  
- Cross-checks indicators against Outlook email metadata (senders, URLs, attachments).  
- Supports enrichment workflows for SOC or demo purposes.  
- Provides a baseline for POCs (Proof of Concepts) in threat intelligence and API integrations.  

---

## 🛠 Prerequisites
- Microsoft 365 tenant with **Outlook Email (Defender for Office 365)**.  
- An **Azure App Registration** with the following API permissions:  
  - `Mail.Read`  
  - `Mail.ReadWrite`  
  - `Mail.ReadBasic`  
- `client_id`, `client_secret`, and `tenant_id` for authentication.  
- Python 3.9+  
- `pip` for dependency management  

---

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/m365-threat-feed.git
   cd m365-threat-feed


2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   export TENANT_ID="<your-tenant-id>"
   export CLIENT_ID="<your-client-id>"
   export CLIENT_SECRET="<your-client-secret>"
   ```

---

## ⚡ Usage

### 1. Authenticate and get an access token:

```bash
python auth.py
```

### 2. Fetch threat feed indicators:

```bash
python fetch_feed.py
```

### 3. Scan M365 Outlook emails against the threat feed:

```bash
python scan_emails.py
```

---



---

## 🔗 References

* [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview)
* [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
* [Open Threat Intelligence Feeds](https://otx.alienvault.com/)

---

## 📜 License

MIT License – feel free to use, modify, and share.

