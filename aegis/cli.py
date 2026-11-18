"""
AegisAgent Command Line Interface (CLI).
Zero external dependencies.
"""

import sys
import os
import argparse
import json

# Ensure robust UTF-8 output across Windows cp1252 / legacy consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .blast_radius import analyze_diff
from .slop_detector import scan_dependencies
from .honeytoken import generate_canary, verify_canary, CanaryType
from .command_shield import audit_command
from .topology import analyze_reasoning_topology
from .quarantine import sanitize_input
from .ledger import record_incident, record_action, get_agent_reputation, get_recent_incidents
from .gate import run_ship_gates
from .mcp import run_mcp_server
from .reporter import (
    render_blast_radius,
    render_slop_report,
    render_command_audit,
    render_topology_report,
    render_quarantine_report,
    render_ledger_report,
    render_gate_report,
    print_banner,
    CYAN, GREEN, RED, BOLD, RESET
)


def cmd_topology(args):
    """Analyze an AI agent's Chain-of-Thought (CoT) reasoning topology and entropy convergence."""
    if args.file == "-" or not args.file:
        trace_text = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            trace_text = f.read()

    report = analyze_reasoning_topology(trace_text)
    render_topology_report(report, json_output=args.json)

    if args.strict and report.isomer_state != "STABLE_CONVERGENT":
        sys.exit(1)


def cmd_quarantine(args):
    """Sanitize untrusted input from prompt injection vectors."""
    if args.file == "-" or not args.file:
        input_text = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            input_text = f.read()

    result = sanitize_input(input_text)
    if not result.is_clean:
        record_incident("agent_input", "PROMPT_INJECTION", result.threat_level, 75 if result.threat_level == "HIGH_THREAT" else 40, target=input_text[:50], details="; ".join(result.detected_threats))
    else:
        record_action("agent_input", "QUARANTINE_CHECK", "CLEAN")

    render_quarantine_report(result, json_output=args.json)

    if args.strict and not result.is_clean:
        sys.exit(1)


def cmd_ledger(args):
    """Inspect agent reputation score and incident audit trail."""
    rep = get_agent_reputation(agent_id=args.agent)
    incidents = get_recent_incidents(limit=args.limit)
    render_ledger_report(rep, incidents, json_output=args.json)


def cmd_gate(args):
    """Run adversarial pre-ship verification gates before commit/PR."""
    if args.diff == "-" or not args.diff:
        diff_text = sys.stdin.read()
    elif os.path.exists(args.diff):
        with open(args.diff, "r", encoding="utf-8", errors="ignore") as f:
            diff_text = f.read()
    else:
        diff_text = args.diff

    report = run_ship_gates(diff_text=diff_text, file_paths=args.files or [])
    render_gate_report(report, json_output=args.json)

    if args.strict and report.status != "PASSED":
        sys.exit(1)


def cmd_mcp(args):
    """Launch the AegisAgent native Model Context Protocol (MCP) server."""
    run_mcp_server()


def cmd_diff(args):
    """Analyze a git diff from file or standard input."""
    if args.file == "-" or not args.file:
        diff_text = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            diff_text = f.read()

    report = analyze_diff(diff_text)
    render_blast_radius(report, json_output=args.json)

    # Return exit code 1 if critical/high risk and strict mode is on
    if args.strict and report.score >= 50:
        sys.exit(1)


def cmd_deps(args):
    """Scan dependency manifests for hallucinations or typosquatting."""
    report = scan_dependencies(args.file, is_path=True)
    render_slop_report(report, json_output=args.json)

    if args.strict and report.suspicious_count > 0:
        sys.exit(1)


def cmd_shield(args):
    """Audit a command string before agent execution."""
    result = audit_command(args.command)
    render_command_audit(result, json_output=args.json)

    if result.status == "BLOCKED":
        sys.exit(2)
    elif result.status == "WARNING" and args.strict:
        sys.exit(1)


def cmd_canary(args):
    """Generate or verify cryptographic honeytokens."""
    if args.action == "generate":
        ctype = CanaryType(args.type)
        res = generate_canary(token_type=ctype, identifier=args.id, secret=args.secret)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print_banner()
            print(f"{BOLD}🍯 GENERATED VERIFIABLE CANARY TOKEN:{RESET}")
            print(f"Type       : {CYAN}{res['type'].upper()}{RESET}")
            print(f"Identifier : {BOLD}{res['identifier']}{RESET}")
            print(f"Token      : {GREEN}{BOLD}{res['token']}{RESET}")
            print(f"Signature  : {res['signature']}")
            print(f"Notice     : {res['hint']}")
    elif args.action == "verify":
        res = verify_canary(args.token, secret=args.secret)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print_banner()
            print(f"{BOLD}🔍 CANARY TOKEN ATTESTATION VERIFICATION:{RESET}")
            if res.get("is_canary"):
                print(f"Result     : {GREEN}{BOLD}✓ AUTHENTIC AEGIS CANARY HONEYTOKEN{RESET}")
                print(f"Canary Type: {res.get('type')}")
                print(f"Identifier : {res.get('identifier')}")
                print(f"Nonce      : {res.get('nonce')}")
            else:
                print(f"Result     : {RED}{BOLD}✗ NOT AN AEGIS CANARY TOKEN{RESET}")
                print(f"Reason     : {res.get('reason')}")


def main():
    parser = argparse.ArgumentParser(
        prog="aegis",
        description="AegisAgent: Autonomous AI Coding Agent Safety & Blast-Radius Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: diff
    p_diff = subparsers.add_parser("diff", help="Analyze git diff blast radius and security risks")
    p_diff.add_argument("file", nargs="?", default="-", help="Path to diff file or '-' for stdin")
    p_diff.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    p_diff.add_argument("--strict", action="store_true", help="Exit with non-zero code on HIGH or CRITICAL score")

    # Subcommand: deps
    p_deps = subparsers.add_parser("deps", help="Check requirements / package.json for AI slopsquatting")
    p_deps.add_argument("file", help="Path to requirements.txt, pyproject.toml, or package.json")
    p_deps.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    p_deps.add_argument("--strict", action="store_true", help="Exit with code 1 if any suspicious package found")

    # Subcommand: shield
    p_shield = subparsers.add_parser("shield", help="Pre-flight audit an agent shell command")
    p_shield.add_argument("command", help="Command string to audit")
    p_shield.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    p_shield.add_argument("--strict", action="store_true", help="Fail on WARNING status as well as BLOCKED")

    # Subcommand: canary
    p_canary = subparsers.add_parser("canary", help="Generate or verify honeytoken traps")
    p_canary.add_argument("action", choices=["generate", "verify"], help="Action to execute")
    p_canary.add_argument("--type", choices=["aws", "github", "openai", "generic"], default="generic", help="Canary token style")
    p_canary.add_argument("--id", default="prod_trap", help="Identifier tag for the canary token")
    p_canary.add_argument("--token", help="Token to verify (for 'verify' action)")
    p_canary.add_argument("--secret", default="aegis_agent_canary_v1", help="HMAC secret salt")
    p_canary.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: topology
    p_top = subparsers.add_parser("topology", help="Audit AI Chain-of-Thought molecular topology & entropy convergence (arXiv:2601.06002)")
    p_top.add_argument("file", nargs="?", default="-", help="Path to CoT trace file or '-' for stdin")
    p_top.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    p_top.add_argument("--strict", action="store_true", help="Exit with non-zero code if isomer state is UNSTABLE or RIGID")

    # Subcommand: quarantine
    p_quar = subparsers.add_parser("quarantine", help="Sanitize untrusted text from prompt injections and steganography")
    p_quar.add_argument("file", nargs="?", default="-", help="Path to file or '-' for stdin")
    p_quar.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    p_quar.add_argument("--strict", action="store_true", help="Exit with code 1 if threat is detected")

    # Subcommand: ledger
    p_led = subparsers.add_parser("ledger", help="View agent reputation score and incident audit trail")
    p_led.add_argument("--agent", default=None, help="Specific agent ID to filter reputation")
    p_led.add_argument("--limit", type=int, default=10, help="Number of recent incidents to show")
    p_led.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")

    # Subcommand: gate
    p_gate = subparsers.add_parser("gate", help="Run adversarial pre-ship verification gates before commit/PR")
    p_gate.add_argument("diff", nargs="?", default="-", help="Path to diff or '-' for stdin")
    p_gate.add_argument("--files", nargs="*", help="Optional file paths to check AST complexity")
    p_gate.add_argument("--strict", action="store_true", help="Exit with code 1 if gates do not pass 100%")
    p_gate.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")

    # Subcommand: mcp
    p_mcp = subparsers.add_parser("mcp", help="Launch native Model Context Protocol (MCP) JSON-RPC server over stdio")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "diff":
        cmd_diff(args)
    elif args.command == "deps":
        cmd_deps(args)
    elif args.command == "shield":
        cmd_shield(args)
    elif args.command == "canary":
        cmd_canary(args)
    elif args.command == "topology":
        cmd_topology(args)
    elif args.command == "quarantine":
        cmd_quarantine(args)
    elif args.command == "ledger":
        cmd_ledger(args)
    elif args.command == "gate":
        cmd_gate(args)
    elif args.command == "mcp":
        cmd_mcp(args)


if __name__ == "__main__":
    main()
