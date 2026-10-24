import unittest
from aegis.honeytoken import generate_canary, verify_canary, CanaryType


class TestHoneytoken(unittest.TestCase):
    def test_generic_canary_lifecycle(self):
        canary = generate_canary(token_type=CanaryType.GENERIC, identifier="test_trap")
        token = canary["token"]
        self.assertTrue(token.startswith("aegis_canary_test_trap_"))

        verification = verify_canary(token)
        self.assertTrue(verification["is_canary"])
        self.assertEqual(verification["identifier"], "test_trap")

    def test_github_canary_lifecycle(self):
        canary = generate_canary(token_type=CanaryType.GITHUB, identifier="prod_trap")
        token = canary["token"]
        self.assertTrue(token.startswith("ghp_"))

        verification = verify_canary(token)
        self.assertTrue(verification["is_canary"])
        self.assertEqual(verification["type"], "github")

    def test_openai_canary_lifecycle(self):
        canary = generate_canary(token_type=CanaryType.OPENAI, identifier="prod_trap")
        token = canary["token"]
        self.assertTrue(token.startswith("sk-proj-"))

        verification = verify_canary(token)
        self.assertTrue(verification["is_canary"])
        self.assertEqual(verification["type"], "openai")

    def test_invalid_canary(self):
        verification = verify_canary("ghp_randomfaketoken12345678901234567890")
        self.assertFalse(verification["is_canary"])


if __name__ == "__main__":
    unittest.main()
