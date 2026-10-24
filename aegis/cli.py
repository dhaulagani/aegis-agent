"""
AegisAgent Command Line Interface (CLI).
Zero external dependencies.
"""

import sys
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
from .reporter import (
    render_blast_radius,
    render_slop_report,
    render_command_audit,
    print_banner,
    CYAN, GREEN, RED, BOLD, RESET
)


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


if __name__ == "__main__":
    main()
