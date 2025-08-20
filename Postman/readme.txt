Import the M365-Demo collection for Postman
Create a new Environment with the following variables

# Core Vars (always needed for Graph auth + user context)

```tenant_id → your Entra ID tenant (GUID)
client_id → app registration ID
client_secret → secret from app registration
access_token → gets set dynamically by the Get Token request
graph → usually https://graph.microsoft.com/v1.0
user_upn → mailbox you’re testing with 
summary_to → where the demo summary email gets sent
```
# IOC / Threat Feed Vars (for abuse.ch pulls)

```urlhaus_key → your abuse.ch API key
ioc_hosts → list of IOCs pulled (JSON array of IPs/URLs)
ioc_hosts_text → pretty-printed IOC list for email body
ioc_count → number of IOCs pulled
hits_json → list of matching messages in M365
hits_count → number of hits in mailbox
hits_text → pretty-printed hits for email
```
