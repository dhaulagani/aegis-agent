"""
AegisAgent - Autonomous AI Coding Agent Safety, Blast-Radius Auditor & Honeytoken Engine.
Zero external dependencies. Pure standard library.
"""

__version__ = "1.2.0"
__author__ = "dhaulagani"
__license__ = "MIT"

from .blast_radius import analyze_diff, BlastRadiusReport
from .slop_detector import scan_dependencies, SlopScanReport
from .honeytoken import generate_canary, verify_canary, CanaryType
from .command_shield import audit_command, CommandAuditResult
from .topology import analyze_reasoning_topology, TopologyReport, BondType
from .quarantine import sanitize_input, QuarantineResult
from .ledger import record_incident, record_action, get_agent_reputation, get_recent_incidents
from .gate import run_ship_gates, ShipGateReport, check_ast_complexity, check_canary_leakage
from .mcp import run_mcp_server

__all__ = [
    "analyze_diff",
    "BlastRadiusReport",
    "scan_dependencies",
    "SlopScanReport",
    "generate_canary",
    "verify_canary",
    "CanaryType",
    "audit_command",
    "CommandAuditResult",
    "analyze_reasoning_topology",
    "TopologyReport",
    "BondType",
    "sanitize_input",
    "QuarantineResult",
    "record_incident",
    "record_action",
    "get_agent_reputation",
    "get_recent_incidents",
    "run_ship_gates",
    "ShipGateReport",
    "check_ast_complexity",
    "check_canary_leakage",
    "run_mcp_server",
]
