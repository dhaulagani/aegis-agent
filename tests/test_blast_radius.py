import unittest
from aegis.blast_radius import analyze_diff


SAMPLE_SAFE_DIFF = """
diff --git a/src/utils.py b/src/utils.py
--- a/src/utils.py
+++ b/src/utils.py
@@ -10,3 +10,5 @@ def add(a, b):
+def multiply(a, b):
+    return a * b
"""

SAMPLE_DANGEROUS_DIFF = """
diff --git a/deploy.sh b/deploy.sh
--- a/deploy.sh
+++ b/deploy.sh
@@ -1,3 +1,5 @@
+rm -rf /var/log/*
+chmod 777 /etc/app_secrets.json
"""

SAMPLE_CRITICAL_SECRET_DIFF = """
diff --git a/config/auth.py b/config/auth.py
--- a/config/auth.py
+++ b/config/auth.py
@@ -1,2 +1,4 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEowIBAAKCAQEA0Y...
"""


class TestBlastRadius(unittest.TestCase):
    def test_safe_diff(self):
        report = analyze_diff(SAMPLE_SAFE_DIFF)
        self.assertEqual(report.risk_level, "LOW")
        self.assertLess(report.score, 25)
        self.assertEqual(len(report.findings), 0)

    def test_destructive_patterns(self):
        report = analyze_diff(SAMPLE_DANGEROUS_DIFF)
        self.assertIn(report.risk_level, ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(report.score, 45)
        categories = [f.category for f in report.findings]
        self.assertTrue(any("DESTRUCTIVE_FS" in c or "SECURITY_PERMS" in c for c in categories))

    def test_private_key_leak(self):
        report = analyze_diff(SAMPLE_CRITICAL_SECRET_DIFF)
        self.assertEqual(report.risk_level, "CRITICAL")
        self.assertGreaterEqual(report.score, 50)
        categories = [f.category for f in report.findings]
        self.assertIn("SECURITY_SECRET", categories)
        self.assertIn("SENSITIVE_FILE_TOUCH", categories)


if __name__ == "__main__":
    unittest.main()
