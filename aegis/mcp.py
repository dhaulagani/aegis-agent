"""
Native Model Context Protocol (MCP) Server for AegisAgent.
Complies with MCP JSON-RPC 2.0 specification over stdio.
Zero external dependencies. Pure standard library.
"""

from __future__ import annotations

import sys
import json
import traceback
from typing import Dict, Any, List, Optional

from .blast_radius import analyze_diff
from .slop_detector import scan_dependencies
from .command_shield import audit_command
from .topology import analyze_reasoning_topology
from .honeytoken import generate_canary, verify_canary, CanaryType

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "aegis-mcp"
SERVER_VERSION = "1.1.0"

TOOLS_MANIFEST = [
    {
        "name": "aegis_audit_command",
        "description": "Pre-flight audit a shell command for destructive operations (rm -rf, format, reverse shells, force-push).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command string to audit"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "aegis_analyze_diff",
        "description": "Calculate git diff blast-radius risk score (0-100), sensitive file touches, and security violations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "diff": {"type": "string", "description": "Unified git diff string"}
            },
            "required": ["diff"]
        }
    },
    {
        "name": "aegis_scan_deps",
        "description": "Scan requirements or package.json content for hallucinated packages and typosquatting attacks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "manifest_content": {"type": "string", "description": "Raw contents of requirements.txt or package.json"}
            },
            "required": ["manifest_content"]
        }
    },
    {
        "name": "aegis_audit_topology",
        "description": "Audit an AI agent's Chain-of-Thought (CoT) trace for molecular reasoning topology and entropy convergence (arXiv:2601.06002).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trace": {"type": "string", "description": "Full Chain-of-Thought reasoning text"}
            },
            "required": ["trace"]
        }
    },
    {
        "name": "aegis_canary_generate",
        "description": "Generate an authentic-looking canary honeytoken with embedded HMAC cryptographic signature.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["aws", "github", "openai", "generic"], "default": "generic"},
                "identifier": {"type": "string", "default": "trap_fixture"}
            }
        }
    },
    {
        "name": "aegis_canary_verify",
        "description": "Verify if a suspicious credential string is an authentic Aegis canary honeytoken.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "Candidate token string to verify"}
            },
            "required": ["token"]
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the requested Aegis tool and return MCP formatted content."""
    try:
        if name == "aegis_audit_command":
            cmd = arguments.get("command", "")
            res = audit_command(cmd)
            return {"content": [{"type": "text", "text": json.dumps(res.to_dict(), indent=2)}]}

        elif name == "aegis_analyze_diff":
            diff_text = arguments.get("diff", "")
            report = analyze_diff(diff_text)
            return {"content": [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]}

        elif name == "aegis_scan_deps":
            content = arguments.get("manifest_content", "")
            report = scan_dependencies(content, is_path=False)
            return {"content": [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]}

        elif name == "aegis_audit_topology":
            trace = arguments.get("trace", "")
            report = analyze_reasoning_topology(trace)
            return {"content": [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]}

        elif name == "aegis_canary_generate":
            ctype = CanaryType(arguments.get("type", "generic"))
            ident = arguments.get("identifier", "trap_fixture")
            canary = generate_canary(token_type=ctype, identifier=ident)
            return {"content": [{"type": "text", "text": json.dumps(canary, indent=2)}]}

        elif name == "aegis_canary_verify":
            token = arguments.get("token", "")
            res = verify_canary(token)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        else:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
            }
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Tool execution failed: {str(e)}\n{traceback.format_exc()}"}]
        }


def process_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single incoming JSON-RPC 2.0 message."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_MANIFEST
            }
        }

    elif method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        res = handle_tool_call(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": res
        }

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        return None


def run_mcp_server():
    """Run JSON-RPC 2.0 loop reading from stdin and writing to stdout."""
    # Ensure UTF-8 stdio
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            msg = json.loads(line)
            response = process_message(msg)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error or internal exception: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
