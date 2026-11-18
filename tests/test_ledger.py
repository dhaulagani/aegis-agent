import unittest
import tempfile
import os
from aegis.ledger import record_incident, record_action, get_agent_reputation, get_recent_incidents


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_ledger.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_record_action_and_reputation(self):
        record_action("agent_01", "COMMAND_AUDIT", "CLEAN", db_path=self.db_path)
        record_action("agent_01", "DIFF_AUDIT", "CLEAN", db_path=self.db_path)

        rep = get_agent_reputation("agent_01", db_path=self.db_path)
        self.assertEqual(rep["trust_score"], 100)
        self.assertEqual(rep["total_actions"], 2)
        self.assertEqual(rep["total_violations"], 0)

    def test_record_incident_and_score_deduction(self):
        record_incident("agent_bad", "COMMAND_BLOCKED", "CRITICAL", 100, target="rm -rf /", details="destructive wipe", db_path=self.db_path)
        record_incident("agent_bad", "TYPOSQUAT_PKG", "HIGH", 60, target="reqeusts", details="typosquat", db_path=self.db_path)

        rep = get_agent_reputation("agent_bad", db_path=self.db_path)
        # 100 - (1*25 + 1*10) = 65
        self.assertEqual(rep["trust_score"], 65)
        self.assertEqual(rep["breakdown"]["CRITICAL"], 1)
        self.assertEqual(rep["breakdown"]["HIGH"], 1)

        incidents = get_recent_incidents(10, db_path=self.db_path)
        self.assertEqual(len(incidents), 2)
        self.assertEqual(incidents[0]["agent_id"], "agent_bad")


if __name__ == "__main__":
    unittest.main()
