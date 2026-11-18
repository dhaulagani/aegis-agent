# Native Model Context Protocol (MCP) Server (`aegis mcp`)

AegisAgent ships with a native, zero-dependency **Model Context Protocol (MCP)** server compliant with the standard JSON-RPC 2.0 specification over stdio.

---

## 🛠️ Exposed MCP Tools

When launched, the Aegis MCP server exposes the following tools directly to client agents:

| Tool Name | Parameters | Purpose |
|---|---|---|
| `aegis_audit_command` | `command: string` | Pre-flight check before executing a shell command. |
| `aegis_analyze_diff` | `diff: string` | Blast-radius assessment of proposed code patches. |
| `aegis_scan_deps` | `manifest_content: string` | Slopsquatting audit for dependency manifests. |
| `aegis_audit_topology` | `trace: string` | CoT reasoning molecular topology & entropy check. |
| `aegis_canary_generate` | `type: string, identifier: string` | Generate verifiable canary trap tokens. |
| `aegis_canary_verify` | `token: string` | Verify suspicious credential strings locally. |

---

## ⚙️ Client Configurations

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "aegis": {
      "command": "aegis",
      "args": ["mcp"]
    }
  }
}
```

### Antigravity / Cursor (`mcpSettings.json`)
```json
{
  "mcpServers": {
    "aegis-agent": {
      "command": "python",
      "args": ["-m", "aegis", "mcp"]
    }
  }
}
```

### Test Stdio Communication
```bash
python -m aegis mcp
# Send: {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
# Receive: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", ...}}
```
