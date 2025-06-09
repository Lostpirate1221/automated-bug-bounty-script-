# Hyatt Recon

## Overview

**Hyatt Recon** is a custom reconnaissance framework built specifically for identifying assets, subdomains, and potential vulnerabilities in the Hyatt Hotels Corporation infrastructure. This recon phase is part of a broader bug bounty strategy, focused on discovering public-facing assets, mapping the attack surface, and filtering targets for further exploitation (e.g., XSS, SQLi, Auth Bypass).

## Objectives

- Enumerate Hyatt-owned subdomains.
- Resolve and filter live hosts.
- Perform port scanning and service detection.
- Identify potential endpoints vulnerable to common web-based exploits.
- Organize findings for prioritized manual testing.

---

## Recon Stack / Tools Used

| Tool        | Purpose                                      |
|-------------|----------------------------------------------|
| `amass`     | Subdomain enumeration                        |
| `subfinder` | Fast passive subdomain discovery             |
| `httpx`     | Probing for live hosts, status codes, and TLS |
| `nmap`      | Port scanning, banner grabbing               |
| `gf`        | Filtering for specific vulnerability patterns |
| `waybackurls` | Gathering historical URLs for fuzzing     |
| `ffuf`      | Content discovery and fuzzing                |
| `dnsx`      | DNS resolution                               |
| `katana`    | Crawler for JS endpoints and hidden params   |

---

## Recon Workflow

```bash
# 1. Subdomain Enumeration
amass enum -d hyatt.com -o hyatt_amass.txt
subfinder -d hyatt.com -silent -o hyatt_subfinder.txt

# 2. Consolidate and Resolve
cat hyatt_*.txt | sort -u > hyatt_all_subs.txt
dnsx -l hyatt_all_subs.txt -silent -o hyatt_resolved.txt

# 3. Probing for Live Hosts
httpx -l hyatt_resolved.txt -silent -status-code -title -tech-detect -o hyatt_live_hosts.txt

# 4. Port Scanning and Service Discovery
nmap -iL hyatt_resolved.txt -T4 -sV -oN hyatt_nmap.txt

# 5. Wayback and Archive Mining
cat hyatt_live_hosts.txt | waybackurls | tee hyatt_wayback.txt

# 6. Vulnerability Pattern Search (XSS, LFI, SSRF, etc.)
cat hyatt_wayback.txt | gf xss > hyatt_xss_candidates.txt
cat hyatt_wayback.txt | gf ssrf > hyatt_ssrf_candidates.txt

# 7. JS Endpoint Discovery
katana -list hyatt_live_hosts.txt -jsl hyatt_js_endpoints.txt

# 8. Optional Fuzzing
ffuf -u https://target.HOST/FUZZ -w wordlists/common.txt -mc 200
