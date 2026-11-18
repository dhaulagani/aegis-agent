import unittest
import json
from aegis.mcp import process_message, TOOLS_MANIFEST


class TestMCPServer(unittest.TestCase):
    def test_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        res = process_message(req)
        self.assertEqual(res["jsonrpc"], "2.0")
        self.assertEqual(res["id"], 1)
        self.assertIn("serverInfo", res["result"])
        self.assertEqual(res["result"]["serverInfo"]["name"], "aegis-mcp")

    def test_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res = process_message(req)
        self.assertEqual(res["id"], 2)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("aegis_audit_command", tool_names)
        self.assertIn("aegis_analyze_diff", tool_names)
        self.assertIn("aegis_scan_deps", tool_names)
        self.assertIn("aegis_audit_topology", tool_names)

    def test_tools_call_audit_command(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "aegis_audit_command",
                "arguments": {"command": "rm -rf /"}
            }
        }
        res = process_message(req)
        self.assertEqual(res["id"], 3)
        content_text = res["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertEqual(payload["status"], "BLOCKED")
        self.assertEqual(payload["risk_score"], 100)

    def test_tools_call_unknown(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        res = process_message(req)
        self.assertTrue(res["result"].get("isError"))


if __name__ == "__main__":
    unittest.main()
