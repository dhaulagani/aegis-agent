"""
Agent Command Execution Shield.
Pre-execution static analysis and sandbox guard for autonomous terminal commands.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CommandAuditResult:
    command: str
    status: str  # SAFE, WARNING, BLOCKED
    risk_score: int  # 0 to 100
    violations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "status": self.status,
            "risk_score": self.risk_score,
            "violations": self.violations
        }


BLOCKED_RULES = [
    (re.compile(r"rm\s+-(?:rf|fr)\s+[/~*]", re.I), "Root/home destructive wipe (rm -rf / or ~)"),
    (re.compile(r"(?:format\s+[a-zA-Z]:|mkfs)", re.I), "Storage filesystem format attempt"),
    (re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", re.I), "POSIX fork bomb detected"),
    (re.compile(r"nc(?:\.traditional)?\s+-[el]", re.I), "Netcat reverse shell listener invocation"),
    (re.compile(r"/dev/tcp/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", re.I), "Raw bash TCP socket exfiltration"),
    (re.compile(r"git\s+push\s+(?:--force|-f)\s+(?:origin\s+)?(?:main|master)", re.I), "Destructive force-push to production master/main branch"),
    (re.compile(r"dd\s+if=/dev/(?:zero|urandom)\s+of=/dev/", re.I), "Raw disk overwrite attempt via dd"),
]

WARNING_RULES = [
    (re.compile(r"(?:curl|wget)\s+[^|\n]+\|\s*(?:bash|sh|zsh|python)", re.I), "Direct download pipe to shell execution"),
    (re.compile(r"chmod\s+(?:-R\s+)?777", re.I), "Broad world-writable permission granting (chmod 777)"),
    (re.compile(r"npm\s+publish\s+--access\s+public", re.I), "Publishing public NPM package"),
    (re.compile(r"pip\s+install\s+--pre", re.I), "Installation of pre-release unverified dependencies"),
    (re.compile(r"export\s+[A-Za-z0-9_]*TOKEN|set\s+[A-Za-z0-9_]*KEY", re.I), "Plaintext credential export in command line history"),
]


def audit_command(command_str: str) -> CommandAuditResult:
    """
    Audit a raw shell command string before an AI agent executes it.
    """
    cmd = command_str.strip()
    violations: List[str] = []
    is_blocked = False

    for pattern, reason in BLOCKED_RULES:
        if pattern.search(cmd):
            violations.append(f"[BLOCKED] {reason}")
            is_blocked = True

    for pattern, reason in WARNING_RULES:
        if pattern.search(cmd):
            violations.append(f"[WARNING] {reason}")

    if is_blocked:
        status = "BLOCKED"
        score = 100
    elif violations:
        status = "WARNING"
        score = 50 + (len(violations) * 10)
        score = min(90, score)
    else:
        status = "SAFE"
        score = 0

    return CommandAuditResult(
        command=cmd,
        status=status,
        risk_score=score,
        violations=violations
    )
