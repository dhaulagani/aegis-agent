"""
AegisAgent - Autonomous AI Coding Agent Safety, Blast-Radius Auditor & Honeytoken Engine.
Zero external dependencies. Pure standard library.
"""

__version__ = "1.0.0"
__author__ = "dhaulagani"
__license__ = "MIT"

from .blast_radius import analyze_diff, BlastRadiusReport
from .slop_detector import scan_dependencies, SlopScanReport
from .honeytoken import generate_canary, verify_canary, CanaryType
from .command_shield import audit_command, CommandAuditResult

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
]
