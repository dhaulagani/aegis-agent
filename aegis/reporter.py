"""
Terminal Visual Reporter & JSON Formatter.
Zero external dependency: utilizes native ANSI color sequences and Unicode glyphs.
"""

import sys
import json
from typing import Dict, Any
from .blast_radius import BlastRadiusReport
from .slop_detector import SlopScanReport
from .command_shield import CommandAuditResult

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"


def print_banner():
    banner = rf"""
{CYAN}{BOLD}   ___    ___ ____ ___ ____     _    ____ _____ _   _ _____ 
  / _ \  | __/ ___|_ _/ ___|   / \  / ___| ____| \ | |_   _|
 / /_\ \ | _|\___ \ | |\___ \  / _ \| |  _|  _| |  \| | | |  
/_/   \_\|___|____/|___|____/ /_/ \_\_|\__|_____|_| \_| |_|  {RESET}
{DIM}  Autonomous AI Coding Agent Safety & Blast-Radius Engine v1.0.0{RESET}
{DIM}  Hermetic • Zero-Disk-Bloat • Zero-Dependency Standard{RESET}
"""
    print(banner)


def render_blast_radius(report: BlastRadiusReport, json_output: bool = False):
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}🔍 BLAST RADIUS & RISK ANALYSIS{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    # Risk badge
    if report.risk_level == "CRITICAL":
        badge = f"{BG_RED}{WHITE}{BOLD} CRITICAL {RESET}"
    elif report.risk_level == "HIGH":
        badge = f"{RED}{BOLD}[HIGH RISK]{RESET}"
    elif report.risk_level == "MEDIUM":
        badge = f"{YELLOW}{BOLD}[MEDIUM RISK]{RESET}"
    else:
        badge = f"{GREEN}{BOLD}[LOW RISK / SAFE]{RESET}"

    print(f"Risk Assessment : {badge} (Score: {BOLD}{report.score}/100{RESET})")
    print(f"Files Modified  : {CYAN}{len(report.files_touched)}{RESET} files")
    print(f"Code Churn      : {GREEN}+{report.additions}{RESET} / {RED}-{report.deletions}{RESET} lines")
    print()

    if report.findings:
        print(f"{BOLD}⚠️  DETECTIONS & VIOLATIONS ({len(report.findings)}):{RESET}")
        for i, f in enumerate(report.findings, 1):
            sev_color = RED if f.severity in ["CRITICAL", "HIGH"] else YELLOW
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"  {DIM}{i:02d}.{RESET} {sev_color}[{f.severity}]{RESET} {BOLD}{f.description}{RESET}")
            print(f"      {DIM}Location: {loc}{RESET}")
            if f.snippet:
                print(f"      {DIM}Snippet: {f.snippet}{RESET}")
        print()

    if report.mitigations:
        print(f"{BOLD}🛡️  REQUIRED MITIGATIONS:{RESET}")
        for m in report.mitigations:
            print(f"  {CYAN}▸{RESET} {m}")
        print()

    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def render_slop_report(report: SlopScanReport, json_output: bool = False):
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}📦 AI PACKAGE HALLUCINATION & SQUATTING SHIELD{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"Total Scanned   : {BOLD}{report.total_dependencies}{RESET} packages")
    
    if report.suspicious_count == 0:
        print(f"Integrity Status: {GREEN}{BOLD}✓ ALL PACKAGES VERIFIED CLEAN{RESET}")
    else:
        print(f"Integrity Status: {RED}{BOLD}✗ {report.suspicious_count} SUSPICIOUS PACKAGES DETECTED{RESET}")
        print()
        print(f"{BOLD}🚨 SUSPICIOUS OR HALLUCINATED DEPENDENCIES:{RESET}")
        for alert in report.alerts:
            sev_color = RED if alert.severity == "HIGH" else YELLOW
            print(f"  {sev_color}• [{alert.risk_type}] {alert.package}{RESET}")
            print(f"    {DIM}Details: {alert.details}{RESET}")
            if alert.suggested_alternative:
                print(f"    {GREEN}Suggested Canonical: {alert.suggested_alternative}{RESET}")
    print()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def render_command_audit(result: CommandAuditResult, json_output: bool = False):
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}⚡ AGENT COMMAND PRE-FLIGHT AUDIT{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"Command : {CYAN}{result.command}{RESET}")

    if result.status == "BLOCKED":
        status_badge = f"{BG_RED}{WHITE}{BOLD} BLOCKED {RESET}"
    elif result.status == "WARNING":
        status_badge = f"{YELLOW}{BOLD}[WARNING / REQUIRES CONFIRMATION]{RESET}"
    else:
        status_badge = f"{GREEN}{BOLD}[SAFE TO EXECUTE]{RESET}"

    print(f"Verdict : {status_badge} (Risk: {result.risk_score}/100)")

    if result.violations:
        print()
        print(f"{BOLD}Violations Flagged:{RESET}")
        for v in result.violations:
            color = RED if "[BLOCKED]" in v else YELLOW
            print(f"  {color}{v}{RESET}")

    print()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
