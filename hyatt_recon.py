#!/usr/bin/env python3

import subprocess
import requests
import os
from datetime import datetime

OUTPUT_DIR = "hyatt_output"
DOMAIN = "hyatt.com"

def setup_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_amass():
    print(f"\n[+] Running Amass (passive) for {DOMAIN}...")
    out_path = os.path.join(OUTPUT_DIR, "amass.txt")
    subprocess.run(["amass", "enum", "-passive", "-d", DOMAIN, "-o", out_path], check=False)
    print("[+] Amass complete.")
    return out_path

def check_live_hosts(subdomain_file):
    print("\n[+] Checking which subdomains are live...")
    live_hosts = []
    output_path = os.path.join(OUTPUT_DIR, "live_hosts.txt")

    with open(subdomain_file, "r") as file:
        for subdomain in file:
            subdomain = subdomain.strip()
            try:
                response = requests.get(f"https://{subdomain}", timeout=5, verify=False)
                if response.status_code < 400:
                    print(f"[+] Live: {subdomain}")
                    live_hosts.append(subdomain)
            except requests.RequestException:
                pass

    with open(output_path, "w") as f:
        for host in live_hosts:
            f.write(f"{host}\n")

    print(f"[+] Live hosts saved to {output_path}")
    return live_hosts

def run_nmap_scan(live_hosts):
    print("\n[+] Running Nmap scan on live hosts...")
    for host in live_hosts:
        print(f"\n[*] Scanning {host}...")
        subprocess.run(["nmap", "-T4", "-F", host])

def generate_report(subdomains, live_hosts):
    print("\n[+] Generating report...")
    report_path = os.path.join(OUTPUT_DIR, "hyatt_recon_report.md")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    with open(report_path, "w") as f:
        f.write(f"# 🕵️ Hyatt Reconnaissance Report\n")
        f.write(f"**Date:** {now}\n\n")
        f.write(f"## 🔍 Target\n")
        f.write(f"- Domain: `{DOMAIN}`\n")
        f.write(f"- Scope: `*.hyatt.com`\n\n")

        f.write(f"## 📊 Subdomain Enumeration\n")
        f.write(f"Total unique subdomains found: **{len(subdomains)}**\n\n")
        f.write("### Sample:\n")
        for sub in subdomains[:10]:
            f.write(f"- {sub}\n")
        if len(subdomains) > 10:
            f.write("- ...\n")

        f.write(f"\n## 🌐 Live Hosts\n")
        f.write(f"Total live subdomains: **{len(live_hosts)}**\n\n")
        for host in live_hosts:
            f.write(f"- {host}\n")

        f.write(f"\n## ⚠️ Notes & Observations\n")
        f.write("- Passive recon only using Amass.\n")
        f.write("- Live hosts checked with HTTPS requests.\n")
        f.write("- Nmap fast scans performed (top 100 ports).\n\n")

        f.write("## 🛠 Tools Used\n")
        f.write("- Amass (passive mode)\n")
        f.write("- Python `requests`\n")
        f.write("- Nmap\n")

    print(f"[+] Report saved to {report_path}")

def main():
    requests.packages.urllib3.disable_warnings()
    setup_output_dir()
    amass_path = run_amass()

    with open(amass_path, "r") as f:
        subdomains = [line.strip() for line in f if line.strip()]

    live_hosts = check_live_hosts(amass_path)
    run_nmap_scan(live_hosts)
    generate_report(subdomains, live_hosts)

if __name__ == "__main__":
    main()
