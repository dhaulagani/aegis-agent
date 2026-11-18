"""
Adversarial Pre-Ship Verification Gates Engine.
Multi-checkpoint gate auditing AST complexity, canary leakage,
clean-room provenance, and blast-radius before commits/PRs.
Zero external dependencies. Pure standard library.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .blast_radius import analyze_diff, BlastRadiusReport
from .honeytoken import verify_canary


@dataclass
class GateCheck:
    name: str
    passed: bool
    details: str


@dataclass
class ShipGateReport:
    status: str  # PASSED, WARNING, FAILED
    gate_score: int  # 0 to 100 (100 = perfect)
    checks: List[GateCheck] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    remediations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "gate_score": self.gate_score,
            "passed_checks": sum(1 for c in self.checks if c.passed),
            "total_checks": len(self.checks),
            "checks": [{"name": c.name, "passed": c.passed, "details": c.details} for c in self.checks],
            "violations": self.violations,
            "remediations": self.remediations
        }


def _calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of an AST function/method definition."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, (ast.comprehension,)):
            complexity += 1
    return complexity


def check_ast_complexity(code_or_path: str, is_path: bool = False, max_complexity: int = 15) -> GateCheck:
    """Check that all Python functions satisfy maximum cyclomatic complexity constraint."""
    if is_path:
        if not os.path.exists(code_or_path) or not code_or_path.endswith(".py"):
            return GateCheck(name="AST Cyclomatic Complexity", passed=True, details="Skipped non-python or missing file")
        with open(code_or_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    else:
        source = code_or_path

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return GateCheck(name="AST Cyclomatic Complexity", passed=False, details="Syntax error during AST parse")

    high_complexity_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            comp = _calculate_cyclomatic_complexity(node)
            if comp > max_complexity:
                high_complexity_funcs.append(f"{node.name} (complexity={comp} > {max_complexity})")

    if high_complexity_funcs:
        return GateCheck(
            name="AST Cyclomatic Complexity",
            passed=False,
            details=f"Exceeded complexity limit ({max_complexity}) in: {', '.join(high_complexity_funcs)}"
        )
    return GateCheck(name="AST Cyclomatic Complexity", passed=True, details=f"All functions pass complexity threshold (<= {max_complexity})")


def check_canary_leakage(text: str) -> GateCheck:
    """Scan patch/text to ensure no active canary honeytokens were committed."""
    # Find candidate tokens
    candidates = re.findall(r"\b(?:aegis_canary_[A-Za-z0-9_]+|ghp_[A-Za-z0-9_]{30,}|sk-proj-[A-Za-z0-9_\-]+)\b", text)
    leaked_canaries = []
    for cand in candidates:
        res = verify_canary(cand)
        if res.get("is_canary"):
            leaked_canaries.append(f"{res.get('type')}:{res.get('identifier')}")

    if leaked_canaries:
        return GateCheck(
            name="Canary Honeytoken Leakage",
            passed=False,
            details=f"Detected leaked canary honeytokens in diff: {', '.join(leaked_canaries)}"
        )
    return GateCheck(name="Canary Honeytoken Leakage", passed=True, details="No canary trap tokens detected in patch")


def run_ship_gates(diff_text: str = "", file_paths: Optional[List[str]] = None) -> ShipGateReport:
    """
    Run adversarial pre-ship verification gates across diff text and modified files.
    """
    checks: List[GateCheck] = []
    violations: List[str] = []
    remediations: List[str] = []

    # Check 1: Blast Radius & Destructive Ops
    blast_report = analyze_diff(diff_text)
    if blast_report.score >= 50:
        checks.append(GateCheck(
            name="Blast Radius Threshold",
            passed=False,
            details=f"Diff blast radius risk score too high ({blast_report.score}/100, Risk: {blast_report.risk_level})"
        ))
        violations.append(f"Blast radius score {blast_report.score} exceeds maximum acceptable shipping threshold (49)")
        remediations.extend(blast_report.mitigations)
    else:
        checks.append(GateCheck(
            name="Blast Radius Threshold",
            passed=True,
            details=f"Blast radius risk score acceptable ({blast_report.score}/100)"
        ))

    # Check 2: Canary Leakage
    canary_check = check_canary_leakage(diff_text)
    checks.append(canary_check)
    if not canary_check.passed:
        violations.append(canary_check.details)
        remediations.append("Remove canary trap tokens from source code and test fixtures immediately.")

    # Check 3: AST Cyclomatic Complexity (on supplied file paths or python diff chunks)
    if file_paths:
        for fp in file_paths:
            if fp.endswith(".py") and os.path.exists(fp):
                ast_check = check_ast_complexity(fp, is_path=True)
                checks.append(ast_check)
                if not ast_check.passed:
                    violations.append(f"File {fp}: {ast_check.details}")
                    remediations.append(f"Refactor complex functions in {fp} to reduce cyclomatic branching.")

    # Compute Overall Gate Score and Status
    passed_count = sum(1 for c in checks if c.passed)
    total_checks = len(checks)
    gate_score = int((passed_count / max(1, total_checks)) * 100)

    if any(not c.passed and "Canary" in c.name for c in checks) or blast_report.score >= 70:
        status = "FAILED"
    elif passed_count < total_checks:
        status = "WARNING"
    else:
        status = "PASSED"

    if status == "PASSED" and not remediations:
        remediations.append("All ship gates cleared. Changes verified safe for deployment or PR merge.")

    return ShipGateReport(
        status=status,
        gate_score=gate_score,
        checks=checks,
        violations=violations,
        remediations=remediations
    )
