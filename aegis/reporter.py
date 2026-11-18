"""
Terminal Visual Reporter & JSON Formatter.
Zero external dependency: utilizes native ANSI color sequences and Unicode glyphs.
"""

import sys
import json
from typing import Dict, Any

# Ensure robust UTF-8 output across Windows cp1252 / legacy consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .blast_radius import BlastRadiusReport
from .slop_detector import SlopScanReport
from .command_shield import CommandAuditResult
from .topology import TopologyReport, BondType
from .quarantine import QuarantineResult
from .gate import ShipGateReport

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


def render_topology_report(report: TopologyReport, json_output: bool = False):
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}🧬 MOLECULAR CoT REASONING TOPOLOGY & ENTROPY AUDITOR{RESET}")
    print(f"{DIM}   Based on arXiv:2601.06002 (The Molecular Structure of Thought){RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    # Isomer Badge
    if report.isomer_state == "STABLE_CONVERGENT":
        badge = f"{GREEN}{BOLD}[STABLE ISOMER / CONVERGENT]{RESET}"
    elif report.isomer_state == "UNSTABLE_EXPLORATION":
        badge = f"{RED}{BOLD}[UNSTABLE / EXCESSIVE DRIFT]{RESET}"
    elif report.isomer_state == "RIGID_DEDUCTION":
        badge = f"{YELLOW}{BOLD}[RIGID / UNVERIFIED BACKBONE]{RESET}"
    else:
        badge = f"{YELLOW}{BOLD}[NEUROTIC REFLECTION LOOP]{RESET}"

    print(f"Total Steps     : {BOLD}{report.total_steps}{RESET} reasoning nodes")
    print(f"Isomer State    : {badge}")
    print(f"Entropy Trend   : {CYAN}{BOLD}{report.entropy_trend}{RESET}")
    print()
    print(f"{BOLD}Bond Distribution Ratio:{RESET}")
    print(f"  • Covalent (Deep-Reasoning)  : {GREEN}{int(report.covalent_ratio * 100)}%{RESET} (Target: 60-75%)")
    print(f"  • Hydrogen (Self-Reflection) : {CYAN}{int(report.hydrogen_ratio * 100)}%{RESET} (Target: 15-25%)")
    print(f"  • Van der Waals (Exploration): {MAGENTA}{int(report.vdw_ratio * 100)}%{RESET} (Target: 10-20%)")
    print()

    if report.anomalies:
        print(f"{BOLD}⚠️  TOPOLOGICAL ANOMALIES DETECTED:{RESET}")
        for a in report.anomalies:
            print(f"  {RED}✗{RESET} {a}")
        print()

    if report.recommendations:
        print(f"{BOLD}💡 STRUCTURAL OPTIMIZATIONS:{RESET}")
        for r in report.recommendations:
            print(f"  {CYAN}▸{RESET} {r}")
        print()

    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def render_quarantine_report(result: QuarantineResult, json_output: bool = False):
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}🛡️  PROMPT INJECTION & INGESTION QUARANTINE SHIELD{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    if result.is_clean:
        status_badge = f"{GREEN}{BOLD}[CLEAN / VERIFIED]{RESET}"
    elif result.threat_level == "HIGH_THREAT":
        status_badge = f"{BG_RED}{WHITE}{BOLD} HIGH THREAT BLOCKED {RESET}"
    else:
        status_badge = f"{YELLOW}{BOLD}[SUSPICIOUS INSTRUCTION]{RESET}"

    print(f"Threat Status   : {status_badge}")
    print(f"Threat Count    : {BOLD}{result.threat_count}{RESET} flagged items")
    print(f"Sanitized Size  : {len(result.sanitized_text)} characters")

    if result.detected_threats:
        print()
        print(f"{BOLD}⚠️  DETECTED INJECTION VECTORS:{RESET}")
        for t in result.detected_threats:
            print(f"  {RED}•{RESET} {t}")

    print()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def render_ledger_report(rep: Dict[str, Any], incidents: list, json_output: bool = False):
    if json_output:
        print(json.dumps({"reputation": rep, "recent_incidents": incidents}, indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}📊 AGENT REPUTATION & INCIDENT LEDGER{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    score = rep["trust_score"]
    if score >= 85:
        badge = f"{GREEN}{BOLD}{score}/100 [HIGHLY TRUSTED]{RESET}"
    elif score >= 60:
        badge = f"{YELLOW}{BOLD}{score}/100 [NEEDS SUPERVISION]{RESET}"
    else:
        badge = f"{RED}{BOLD}{score}/100 [UNTRUSTED / HIGH RISK]{RESET}"

    print(f"Agent Target    : {CYAN}{BOLD}{rep['agent_id']}{RESET}")
    print(f"Trust Score     : {badge}")
    print(f"Total Audits    : {BOLD}{rep['total_actions']}{RESET} | Clean: {GREEN}{rep['clean_actions']}{RESET} | Violations: {RED}{rep['total_violations']}{RESET}")
    print(f"Violation Breakdown: CRITICAL={RED}{rep['breakdown']['CRITICAL']}{RESET}, HIGH={YELLOW}{rep['breakdown']['HIGH']}{RESET}, MED={rep['breakdown']['MEDIUM']}, LOW={rep['breakdown']['LOW']}")

    if incidents:
        print()
        print(f"{BOLD}Recent Security Incidents ({len(incidents)}):{RESET}")
        for inc in incidents[:5]:
            sev_color = RED if inc["severity"] in ["CRITICAL", "HIGH"] else YELLOW
            print(f"  {sev_color}[{inc['severity']}]{RESET} {BOLD}{inc['event_type']}{RESET} - {inc.get('details', '')[:80]}")
            if inc.get("target"):
                print(f"      {DIM}Target: {inc['target'][:70]}{RESET}")

    print()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def render_gate_report(report: ShipGateReport, json_output: bool = False):
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print_banner()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}🚢 ADVERSARIAL PRE-SHIP VERIFICATION GATES{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    if report.status == "PASSED":
        badge = f"{GREEN}{BOLD}[SHIP GATES PASSED (Score: {report.gate_score}/100)]{RESET}"
    elif report.status == "WARNING":
        badge = f"{YELLOW}{BOLD}[SHIP WARNINGS DETECTED (Score: {report.gate_score}/100)]{RESET}"
    else:
        badge = f"{BG_RED}{WHITE}{BOLD} GATES FAILED (Score: {report.gate_score}/100) {RESET}"

    print(f"Ship Verdict    : {badge}")
    print(f"Checks Cleared  : {BOLD}{report.to_dict()['passed_checks']}/{report.to_dict()['total_checks']}{RESET}")
    print()
    print(f"{BOLD}Verification Checkpoints:{RESET}")
    for c in report.checks:
        icon = f"{GREEN}✓{RESET}" if c.passed else f"{RED}✗{RESET}"
        print(f"  {icon} {BOLD}{c.name}{RESET}: {DIM}{c.details}{RESET}")

    if report.violations:
        print()
        print(f"{BOLD}🚨 Violations Blocking Ship:{RESET}")
        for v in report.violations:
            print(f"  {RED}•{RESET} {v}")

    if report.remediations:
        print()
        print(f"{BOLD}🛡️  Required Remediations:{RESET}")
        for r in report.remediations:
            print(f"  {CYAN}▸{RESET} {r}")

    print()
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


