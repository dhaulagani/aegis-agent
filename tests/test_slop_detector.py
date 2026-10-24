import unittest
from aegis.slop_detector import scan_dependencies


SAMPLE_CLEAN_REQS = """
requests>=2.28.0
numpy==1.24.3
pydantic>=2.0.0
pytest
"""

SAMPLE_TYPOSQUAT_REQS = """
reqeusts>=2.28.0
boto4
openai-python-client
"""


class TestSlopDetector(unittest.TestCase):
    def test_clean_requirements(self):
        report = scan_dependencies(SAMPLE_CLEAN_REQS)
        self.assertEqual(report.suspicious_count, 0)
        self.assertEqual(len(report.alerts), 0)

    def test_detect_typosquat_and_hallucination(self):
        report = scan_dependencies(SAMPLE_TYPOSQUAT_REQS)
        self.assertGreaterEqual(report.suspicious_count, 2)
        pkgs = [a.package for a in report.alerts]
        self.assertIn("reqeusts", pkgs)
        self.assertTrue(any("boto4" in p or "openai" in p for p in pkgs))


if __name__ == "__main__":
    unittest.main()
