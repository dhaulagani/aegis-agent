"""
Honeytoken & Canary Trap Generator.
Produces authentic-looking credentials embedded with an offline verifiable cryptographic signature.
"""

import hmac
import hashlib
import secrets
import string
from enum import Enum
from typing import Dict, Any, Optional


class CanaryType(str, Enum):
    AWS = "aws"
    GITHUB = "github"
    OPENAI = "openai"
    GENERIC = "generic"


DEFAULT_CANARY_SALT = "aegis_agent_canary_v1"


def _generate_signature(data: str, secret: str) -> str:
    """Generate a truncated HMAC signature (8 chars) used as embedded checksum."""
    h = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256)
    return h.hexdigest()[:8]


def generate_canary(
    token_type: CanaryType = CanaryType.GENERIC,
    identifier: str = "prod_trap",
    secret: str = DEFAULT_CANARY_SALT
) -> Dict[str, Any]:
    """
    Generate an authentic-looking canary token embedded with cryptographic HMAC checksum.
    """
    nonce = secrets.token_hex(4)  # 8 hex chars
    payload = f"{identifier}_{nonce}"
    sig = _generate_signature(payload, secret)

    if token_type == CanaryType.AWS:
        # AWS Access Key ID format: AKIA + 16 uppercase alphanumeric chars
        raw = f"{nonce.upper()}{sig.upper()}"
        padding = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16 - len(raw)))
        token = f"AKIA{raw[:16]}"
    elif token_type == CanaryType.GITHUB:
        # GitHub Personal Access Token format: ghp_ + 36 alphanumeric
        token = f"ghp_{nonce}{sig}{secrets.token_hex(10)}"
    elif token_type == CanaryType.OPENAI:
        # OpenAI style: sk-proj-...
        token = f"sk-proj-{nonce}-{sig}-{secrets.token_urlsafe(24)}"
    else:
        # Generic Aegis Canary
        token = f"aegis_canary_{payload}_{sig}"

    return {
        "type": token_type.value,
        "identifier": identifier,
        "token": token,
        "nonce": nonce,
        "signature": sig,
        "hint": "Plant this token in fake configs, test fixtures, or docs to catch unauthorized agent exfiltration."
    }


def verify_canary(token: str, secret: str = DEFAULT_CANARY_SALT) -> Dict[str, Any]:
    """
    Verify if a given credential string is an Aegis Canary token.
    Returns details if verified, or is_canary=False otherwise.
    """
    if not token or not isinstance(token, str):
        return {"is_canary": False, "reason": "Empty or invalid token format"}

    # Generic format: aegis_canary_<identifier>_<nonce>_<sig>
    if token.startswith("aegis_canary_"):
        parts = token[len("aegis_canary_"):].split("_")
        if len(parts) >= 3:
            sig = parts[-1]
            nonce = parts[-2]
            identifier = "_".join(parts[:-2])
            payload = f"{identifier}_{nonce}"
            expected_sig = _generate_signature(payload, secret)
            if hmac.compare_digest(sig, expected_sig):
                return {
                    "is_canary": True,
                    "type": "generic",
                    "identifier": identifier,
                    "nonce": nonce
                }

    # GitHub format: ghp_<nonce:8><sig:8><random:20>
    if token.startswith("ghp_") and len(token) >= 20:
        body = token[4:]
        nonce = body[:8]
        sig = body[8:16]
        # In github mode, payload identifier is default 'prod_trap' unless custom
        # Check standard identifiers
        for test_id in ["prod_trap", "dev_trap", "agent_trap"]:
            payload = f"{test_id}_{nonce}"
            if hmac.compare_digest(sig, _generate_signature(payload, secret)):
                return {
                    "is_canary": True,
                    "type": "github",
                    "identifier": test_id,
                    "nonce": nonce
                }

    # OpenAI format: sk-proj-<nonce>-<sig>-<rest>
    if token.startswith("sk-proj-"):
        parts = token.split("-")
        if len(parts) >= 4:
            nonce = parts[2]
            sig = parts[3]
            for test_id in ["prod_trap", "dev_trap", "agent_trap"]:
                payload = f"{test_id}_{nonce}"
                if hmac.compare_digest(sig, _generate_signature(payload, secret)):
                    return {
                        "is_canary": True,
                        "type": "openai",
                        "identifier": test_id,
                        "nonce": nonce
                    }

    return {"is_canary": False, "reason": "Checksum mismatch or unknown canary format"}
