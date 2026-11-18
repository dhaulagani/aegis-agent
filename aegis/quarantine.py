"""
Ingestion Sanitizer & Prompt Injection Quarantine Engine.
Strips indirect prompt injection, hidden HTML comments, zero-width steganography,
and exfiltration hooks before untrusted content enters agent context.
Zero external dependencies. Pure standard library.
"""

import re
import base64
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


INJECTION_PATTERNS = [
    (re.compile(r"(?:ignore|disregard|forget|override)\s+(?:all\s+)?(?:previous|prior|system)\s+(?:instructions?|directives?|prompts?|rules?)", re.I), "INDIRECT_PROMPT_INJECTION", "Instruction override attempt detected"),
    (re.compile(r"\b(?:you\s+are\s+now(?:\s+in)?|act\s+as)\s+(?:DAN(?:\s+mode)?|unrestricted|jailbroken|an\s+unfiltered\s+AI|root\s+user)\b|\b(?:DAN\s+mode|jailbreak\s+mode|developer\s+mode)\b", re.I), "JAILBREAK_ATTEMPT", "Persona hijacking or jailbreak vector detected"),
    (re.compile(r"\b(?:system\s+prompt|developer\s+mode)\s*(?::|\s+enabled|\s+override)", re.I), "PROMPT_LEAK_PROBE", "System prompt extraction probe detected"),
    (re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.I | re.DOTALL), "MALICIOUS_SCRIPT_TAG", "Embedded HTML script tag stripped"),
    (re.compile(r"<!--[\s\S]*?(?:ignore|execute|curl|rm|eval|token|secret|system|hack)[\s\S]*?-->", re.I), "HIDDEN_HTML_DIRECTIVE", "Hidden HTML comment directive stripped"),
    (re.compile(r"!\[[^\]]*\]\(https?://[^\s)]+(?:\?|&)(?:token|secret|key|cookie|env)=[^\s)]*\)", re.I), "EXFILTRATION_MARKDOWN", "Markdown image exfiltration pixel hook stripped"),
]

INVISIBLE_UNICODE_CHARS = [
    '\u200b',  # zero-width space
    '\u200c',  # zero-width non-joiner
    '\u200d',  # zero-width joiner
    '\u2060',  # word joiner
    '\ufeff',  # zero-width no-break space / BOM
    '\u202e',  # right-to-left override
    '\u202a',  # left-to-right embedding
    '\u202b',  # right-to-left embedding
]


@dataclass
class QuarantineResult:
    is_clean: bool
    threat_level: str  # CLEAN, SUSPICIOUS, HIGH_THREAT
    threat_count: int
    detected_threats: List[str] = field(default_factory=list)
    sanitized_text: str = ""
    stripped_tokens_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_clean": self.is_clean,
            "threat_level": self.threat_level,
            "threat_count": self.threat_count,
            "detected_threats": self.detected_threats,
            "stripped_tokens_count": self.stripped_tokens_count,
            "sanitized_length": len(self.sanitized_text)
        }


def sanitize_input(text: str) -> QuarantineResult:
    """
    Sanitize untrusted text from GitHub issues, web pages, or PR descriptions
    before passing into an AI agent's prompt context.
    """
    if not text:
        return QuarantineResult(is_clean=True, threat_level="CLEAN", threat_count=0, sanitized_text="")

    detected_threats: List[str] = []
    sanitized = text

    # 1. Detect and strip invisible unicode characters (steganography)
    unicode_stripped = 0
    clean_chars = []
    for char in sanitized:
        if char in INVISIBLE_UNICODE_CHARS:
            unicode_stripped += 1
        else:
            clean_chars.append(char)

    if unicode_stripped > 0:
        detected_threats.append(f"Stripped {unicode_stripped} invisible/zero-width unicode characters (steganography vector)")
        sanitized = "".join(clean_chars)

    # 2. Check and neutralize prompt injection regex patterns
    for pattern, category, description in INJECTION_PATTERNS:
        matches = list(pattern.finditer(sanitized))
        if matches:
            detected_threats.append(f"[{category}] {description} ({len(matches)} instance(s))")
            # Replace malicious block with safe sanitization placeholder
            sanitized = pattern.sub("[AEGIS:SANITIZED_UNTRUSTED_INSTRUCTION]", sanitized)

    # 3. Check for suspicious base64 code execution payload
    b64_matches = re.findall(r"(?:eval|exec)\s*\(\s*base64\.b64decode\(['\"]([A-Za-z0-9+/=]{20,})['\"]\)", sanitized)
    if b64_matches:
        detected_threats.append("[BASE64_EXEC_PAYLOAD] Obfuscated base64 code execution detected")
        sanitized = re.sub(r"(?:eval|exec)\s*\(\s*base64\.b64decode\(['\"][A-Za-z0-9+/=]+['\"]\)\s*\)", "[AEGIS:BLOCKED_EXEC_PAYLOAD]", sanitized)

    threat_count = len(detected_threats)
    if threat_count >= 2 or any("INDIRECT_PROMPT_INJECTION" in t or "BASE64" in t for t in detected_threats):
        threat_level = "HIGH_THREAT"
        is_clean = False
    elif threat_count == 1:
        threat_level = "SUSPICIOUS"
        is_clean = False
    else:
        threat_level = "CLEAN"
        is_clean = True

    return QuarantineResult(
        is_clean=is_clean,
        threat_level=threat_level,
        threat_count=threat_count,
        detected_threats=detected_threats,
        sanitized_text=sanitized,
        stripped_tokens_count=unicode_stripped
    )
