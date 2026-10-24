"""
AI Package Hallucination & Slopsquatting Detector.
Guards against AI agents generating non-existent or typosquatted dependency names.
Uses Damerau-Levenshtein distance to detect character swaps, insertions, and omissions.
"""

import os
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


# Reference list of top PyPI and NPM canonical packages for typosquatting check
CANONICAL_PACKAGES = [
    "requests", "urllib3", "cryptography", "pandas", "numpy", "pytest",
    "flask", "django", "fastapi", "pydantic", "boto3", "botocore",
    "torch", "torchvision", "tensorflow", "scipy", "scikit-learn",
    "transformers", "openai", "anthropic", "langchain", "celery",
    "redis", "sqlalchemy", "psycopg2", "wheel", "setuptools", "click",
    "rich", "typer", "httpx", "aiohttp", "pillow", "matplotlib",
    "express", "lodash", "react", "vue", "axios", "next", "tailwindcss"
]

SUSPICIOUS_SUFFIXES = [
    "-python", "-py", "-official", "-sdk", "-api", "-client",
    "-official-sdk", "-python-client", "-core-v2", "-v2"
]


def _damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute optimal string alignment / Damerau-Levenshtein distance
    supporting insertions, deletions, substitutions, and adjacent transpositions.
    """
    d = {}
    len1 = len(s1)
    len2 = len(s2)

    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,        # deletion
                d[(i, j - 1)] + 1,        # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 1)  # transposition

    return d[(len1 - 1, len2 - 1)]


@dataclass
class SlopAlert:
    package: str
    risk_type: str  # TYPOSQUAT, HALLUCINATION_PATTERN, UNPINNED_REMOTE
    severity: str  # HIGH, MEDIUM
    details: str
    suggested_alternative: str = ""


@dataclass
class SlopScanReport:
    total_dependencies: int
    suspicious_count: int
    alerts: List[SlopAlert] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_dependencies": self.total_dependencies,
            "suspicious_count": self.suspicious_count,
            "alerts": [
                {
                    "package": a.package,
                    "risk_type": a.risk_type,
                    "severity": a.severity,
                    "details": a.details,
                    "suggested_alternative": a.suggested_alternative
                }
                for a in self.alerts
            ]
        }


def _extract_packages_from_text(content: str, filename: str) -> List[str]:
    """Extract package names from requirements.txt, pyproject.toml, or package.json."""
    packages = []
    fname = os.path.basename(filename).lower()

    if fname == "package.json":
        try:
            data = json.loads(content)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            packages.extend(list(deps.keys()))
            packages.extend(list(dev_deps.keys()))
        except Exception:
            pass
        return packages

    # Requirements or general file
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#")[0].strip()
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)", line)
        if match:
            pkg = match.group(1).lower()
            packages.append(pkg)

    return list(set(packages))


def scan_dependencies(content_or_path: str, is_path: bool = False) -> SlopScanReport:
    """
    Scan a requirements list or file path for hallucinated / typosquatted AI package names.
    """
    if is_path:
        filename = content_or_path
        with open(content_or_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    else:
        filename = "requirements.txt"
        content = content_or_path

    packages = _extract_packages_from_text(content, filename)
    alerts: List[SlopAlert] = []

    for pkg in packages:
        pkg_clean = pkg.lower()

        # 1. Check exact match in canonical list (safe)
        if pkg_clean in CANONICAL_PACKAGES:
            continue

        # 2. Typosquatting check (Damerau-Levenshtein distance <= 1)
        typo_match = None
        for canonical in CANONICAL_PACKAGES:
            dist = _damerau_levenshtein_distance(pkg_clean, canonical)
            if dist == 1 and len(canonical) >= 5:
                typo_match = canonical
                break

        if typo_match:
            alerts.append(SlopAlert(
                package=pkg,
                risk_type="TYPOSQUAT",
                severity="HIGH",
                details=f"Package '{pkg}' is 1 edit/swap distance from canonical '{typo_match}'. Likely hallucination or typosquatting trap.",
                suggested_alternative=typo_match
            ))
            continue

        # 3. Check suspicious hallucination patterns
        found_hallucination = False
        for canonical in CANONICAL_PACKAGES:
            for suffix in SUSPICIOUS_SUFFIXES:
                hallucinated_cand = f"{canonical}{suffix}"
                prefix_cand = f"python-{canonical}"
                if pkg_clean == hallucinated_cand or pkg_clean == prefix_cand:
                    alerts.append(SlopAlert(
                        package=pkg,
                        risk_type="HALLUCINATION_PATTERN",
                        severity="HIGH",
                        details=f"Compound name pattern '{pkg}' matches common LLM hallucination for official package '{canonical}'.",
                        suggested_alternative=canonical
                    ))
                    found_hallucination = True
                    break
            if found_hallucination:
                break

        if found_hallucination:
            continue

        # 4. Check version suffix hallucination (e.g., boto4, pydantic2, beautifulsoup5)
        m = re.match(r"^([a-zA-Z_\-]+)(\d+)$", pkg_clean)
        if m:
            base, num = m.groups()
            if base in CANONICAL_PACKAGES and num != "3":
                alerts.append(SlopAlert(
                    package=pkg,
                    risk_type="HALLUCINATION_PATTERN",
                    severity="MEDIUM",
                    details=f"Suspicious synthetic major version increment '{pkg}' based on '{base}'.",
                    suggested_alternative=base
                ))

    return SlopScanReport(
        total_dependencies=len(packages),
        suspicious_count=len(alerts),
        alerts=alerts
    )
