import unittest
from aegis.gate import check_ast_complexity, check_canary_leakage, run_ship_gates
from aegis.honeytoken import generate_canary, CanaryType


SAMPLE_CLEAN_CODE = """
def simple_function(x):
    if x > 0:
        return x * 2
    return 0
"""

SAMPLE_COMPLEX_CODE = """
def overly_complex(a, b, c, d, e, f, g, h, i, j):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    if i:
                                        if j:
                                            return 1
    return 0
"""


class TestShipGates(unittest.TestCase):
    def test_ast_complexity_pass(self):
        check = check_ast_complexity(SAMPLE_CLEAN_CODE, max_complexity=15)
        self.assertTrue(check.passed)

    def test_ast_complexity_fail(self):
        check = check_ast_complexity(SAMPLE_COMPLEX_CODE, max_complexity=5)
        self.assertFalse(check.passed)
        self.assertIn("Exceeded complexity limit", check.details)

    def test_canary_leakage_detection(self):
        canary = generate_canary(token_type=CanaryType.GENERIC, identifier="secret_trap")
        diff_with_canary = f"""
diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,1 +1,2 @@
+API_KEY = "{canary['token']}"
"""
        check = check_canary_leakage(diff_with_canary)
        self.assertFalse(check.passed)
        self.assertIn("Detected leaked canary", check.details)

    def test_run_ship_gates_clean(self):
        clean_diff = """
diff --git a/src/app.py b/src/app.py
--- a/src/app.py
+++ b/src/app.py
@@ -1,2 +1,3 @@
 def run():
+    print("ok")
"""
        report = run_ship_gates(clean_diff)
        self.assertEqual(report.status, "PASSED")
        self.assertEqual(report.gate_score, 100)


if __name__ == "__main__":
    unittest.main()
