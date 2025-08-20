# M365 Threat Feed Integration

This project demonstrates how to integrate an **open-source threat feed** with **Microsoft 365 (Outlook Email)** using the Microsoft Graph API.  
The goal is to fetch indicators from a public threat feed and use them to check and act upon emails inside an M365 environment.  

---

##  Features
- Connects to Microsoft 365 using OAuth2 and Microsoft Graph API.  
- Retrieves indicators (IPs, domains, URLs, hashes) from a threat feed.  
- Cross-checks indicators against Outlook email metadata (senders, URLs, attachments).  
- Supports enrichment workflows for SOC or demo purposes.  
- Provides a baseline for POCs (Proof of Concepts) in threat intelligence and API integrations.  

---

##  Prerequisites
- Microsoft 365 tenant with **Outlook Email (Defender for Office 365)**.  
- An **Azure App Registration** with the following API permissions:  
  - `Mail.Read`  
  - `Mail.ReadWrite`  
  - `Mail.ReadBasic`  
- `client_id`, `client_secret`, and `tenant_id` for authentication.  
- Python 3.9+  
- `pip` for dependency management  

---

##  Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/thomas-griffiths/m365-ti.git
   cd m365-ti
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure authentication by copying the example config:
   ```bash
   cp config.json.example config.json
   ```
   
   Then edit `config.json` with your Azure app credentials:
   ```json
   {
     "tenant_id": "your-tenant-id",
     "client_id": "your-client-id", 
     "client_secret": "your-client-secret",
     "scope": "https://graph.microsoft.com/.default",
     "graph_base": "https://graph.microsoft.com/v1.0"
   }
   ```

---

##  Usage

### Run the threat intelligence scanner:

```bash
python src/main.py --user user@tenant.onmicrosoft.com
```

### Common options:

```bash
# Scan last 100 messages and ensure category exists
python src/main.py --user user@tenant.onmicrosoft.com --top 100 --ensure-category

# Send summary email after scanning
python src/main.py --user user@tenant.onmicrosoft.com --summary-to admin@company.com

# Use custom category name
python src/main.py --user user@tenant.onmicrosoft.com --category "Malicious-Content"
```

---

## 🔗 References

* [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview)
* [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
* [Open Threat Intelligence Feeds](https://otx.alienvault.com/)

---

## License

MIT License – feel free to use, modify, and share.

