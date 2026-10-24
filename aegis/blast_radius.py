"""
Git Diff Blast Radius & Structural Risk Engine.
Calculates risk scores (0-100) and detects destructive operations in AI-generated code patches.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Finding:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    file: str
    line: Optional[int]
    description: str
    snippet: str = ""


@dataclass
class BlastRadiusReport:
    score: int  # 0 to 100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    files_touched: List[str]
    additions: int
    deletions: int
    findings: List[Finding] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "risk_level": self.risk_level,
            "files_touched": self.files_touched,
            "additions": self.additions,
            "deletions": self.deletions,
            "findings_count": len(self.findings),
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "file": f.file,
                    "line": f.line,
                    "description": f.description,
                    "snippet": f.snippet
                }
                for f in self.findings
            ],
            "mitigations": self.mitigations
        }


CRITICAL_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|PGP) PRIVATE KEY-----", re.I), "Private key exposure", "SECURITY_SECRET"),
    (re.compile(r"(?:rm\s+-(?:rf|fr)\s+[/~*]|shutil\.rmtree\(['\"/]\)|rmdir\s+/s\s+/q)", re.I), "Destructive file deletion command", "DESTRUCTIVE_FS"),
    (re.compile(r"DROP\s+(?:DATABASE|TABLE|SCHEMA)|TRUNCATE\s+(?:TABLE)?", re.I), "Destructive SQL operation (DROP/TRUNCATE)", "DESTRUCTIVE_SQL"),
    (re.compile(r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0['\"]?", re.I), "TLS certificate verification disabled", "SECURITY_BYPASS"),
    (re.compile(r"verify\s*=\s*False", re.I), "SSL verification explicitly disabled in HTTP client", "SECURITY_BYPASS"),
    (re.compile(r"(?:eval|exec)\s*\(\s*(?:request|input|sys\.argv|os\.environ)", re.I), "Remote code execution via dynamic eval/exec", "RCE_VECTOR"),
]

HIGH_PATTERNS = [
    (re.compile(r"chmod\s+777|chmod\s+-R\s+777", re.I), "Permissive file permissions (chmod 777)", "SECURITY_PERMS"),
    (re.compile(r"(?:ghp_[A-Za-z0-9_]{36}|AKIA[0-9A-Z]{16})"), "Hardcoded cloud credential or API token", "SECURITY_SECRET"),
    (re.compile(r"subprocess\.(?:run|call|Popen)\([^)]*shell\s*=\s*True[^)]*\)"), "Shell execution with shell=True enabled", "SUBPROCESS_SHELL"),
]

MEDIUM_PATTERNS = [
    (re.compile(r"curl\s+[^|\n]+\|\s*(?:bash|sh|zsh)"), "Direct curl-to-shell pipe detected", "SUSPICIOUS_SCRIPT"),
    (re.compile(r"#\s*type:\s*ignore\[all\]|flake8:\s*noqa|eslint-disable", re.I), "Broad linter/type safety suppression", "QUALITY_BYPASS"),
]

SENSITIVE_FILES_RE = re.compile(
    r"(?:\.env|\.github/workflows/|auth|payment|crypto|credentials|settings\.py|database\.py|secret|config/master\.key)",
    re.I
)


def analyze_diff(diff_text: str) -> BlastRadiusReport:
    """
    Parse a unified diff string and compute blast radius risk score and findings.
    """
    files_touched: List[str] = []
    current_file = "unknown"
    additions = 0
    deletions = 0
    findings: List[Finding] = []

    lines = diff_text.splitlines()
    line_num = 0

    for raw_line in lines:
        if raw_line.startswith("diff --git"):
            parts = raw_line.split()
            if len(parts) >= 4:
                filepath = parts[3].lstrip("b/")
                current_file = filepath
                if filepath not in files_touched:
                    files_touched.append(filepath)
            line_num = 0
            continue
        elif raw_line.startswith("+++ b/"):
            filepath = raw_line[6:]
            current_file = filepath
            if filepath not in files_touched and filepath != "/dev/null":
                files_touched.append(filepath)
            line_num = 0
            continue
        elif raw_line.startswith("@@"):
            line_num = 1
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            additions += 1
            line_num += 1
            added_content = raw_line[1:].strip()

            for pattern, desc, category in CRITICAL_PATTERNS:
                if pattern.search(added_content):
                    findings.append(Finding(
                        severity="CRITICAL",
                        category=category,
                        file=current_file,
                        line=line_num,
                        description=desc,
                        snippet=added_content[:100]
                    ))

            for pattern, desc, category in HIGH_PATTERNS:
                if pattern.search(added_content):
                    findings.append(Finding(
                        severity="HIGH",
                        category=category,
                        file=current_file,
                        line=line_num,
                        description=desc,
                        snippet=added_content[:100]
                    ))

            for pattern, desc, category in MEDIUM_PATTERNS:
                if pattern.search(added_content):
                    findings.append(Finding(
                        severity="MEDIUM",
                        category=category,
                        file=current_file,
                        line=line_num,
                        description=desc,
                        snippet=added_content[:100]
                    ))

        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            deletions += 1

    sensitive_count = 0
    for f in files_touched:
        if SENSITIVE_FILES_RE.search(f):
            sensitive_count += 1
            findings.append(Finding(
                severity="HIGH",
                category="SENSITIVE_FILE_TOUCH",
                file=f,
                line=None,
                description=f"Patch modifies mission-critical surface: {f}",
                snippet=""
            ))

    score = 0
    has_critical = False
    has_high = False

    for f in findings:
        if f.severity == "CRITICAL":
            score += 50
            has_critical = True
        elif f.severity == "HIGH":
            score += 25
            has_high = True
        elif f.severity == "MEDIUM":
            score += 10

    score += (sensitive_count * 10)
    churn = additions + deletions
    churn_score = min(20, churn // 40)
    score += churn_score
    score = min(100, max(0, score))

    if has_critical or score >= 60:
        risk_level = "CRITICAL"
    elif has_high or score >= 40:
        risk_level = "HIGH"
    elif score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    mitigations = []
    if any(f.category == "SECURITY_SECRET" for f in findings):
        mitigations.append("Remove hardcoded credentials immediately. Use environment variables or KMS.")
    if any(f.category.startswith("DESTRUCTIVE") for f in findings):
        mitigations.append("Block automated merge. Review filesystem/database purge logic under human supervision.")
    if any(f.category == "SECURITY_BYPASS" for f in findings):
        mitigations.append("Restore SSL/TLS certificate verification. Never deploy verify=False to production.")
    if sensitive_count > 0:
        mitigations.append(f"Require 2-person security review for changes to sensitive files ({sensitive_count} files).")
    if not mitigations and score < 20:
        mitigations.append("Patch blast radius is minimal. Safe for standard automated CI pipeline.")

    return BlastRadiusReport(
        score=score,
        risk_level=risk_level,
        files_touched=files_touched,
        additions=additions,
        deletions=deletions,
        findings=findings,
        mitigations=mitigations
    )
