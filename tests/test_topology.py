import unittest
from aegis.topology import analyze_reasoning_topology, BondType


SAMPLE_STABLE_COT = """
Step 1: First, we need to inspect the input parameters. What if the user supplies a negative integer? Alternatively, it could be empty.
Step 2: Therefore, we validate that the input is a positive integer before proceeding.
Step 3: Calculating the factorial iteratively gives a runtime of O(N) and memory of O(1).
Step 4: Wait, let's double check if 0! is handled correctly according to the mathematical definition.
Step 5: Reviewing the premise, 0! equals 1, so our base case satisfies this condition.
Step 6: Thus, we conclude with the iterative implementation returning 1 for n=0.
"""

SAMPLE_EXPLORATION_DRIFT = """
Step 1: Maybe we could use a neural network for this.
Step 2: Or alternatively, what if we use a genetic algorithm?
Step 3: Another angle is perhaps quantum computing simulation.
Step 4: Hypothetically, could it be solved with an evolutionary strategy?
"""

SAMPLE_RIGID_COT = """
Step 1: Therefore we execute line 1.
Step 2: Thus we compute line 2.
Step 3: Consequently we write line 3.
Step 4: Hence we finish execution.
"""

SAMPLE_NEUROTIC_COT = """
Step 1: Wait, let me check.
Step 2: Hold on, is this right?
Step 3: Re-evaluating the previous thought.
Step 4: Wait, could this be an error?
"""


class TestReasoningTopology(unittest.TestCase):
    def test_stable_convergent_trace(self):
        report = analyze_reasoning_topology(SAMPLE_STABLE_COT)
        self.assertEqual(report.isomer_state, "STABLE_CONVERGENT")
        self.assertGreater(report.covalent_ratio, 0.3)
        self.assertGreater(report.hydrogen_ratio, 0.1)
        self.assertGreater(report.vdw_ratio, 0.05)
        self.assertIn(report.entropy_trend, ["MONOTONIC_DECREASING", "OSCILLATING"])
        self.assertGreaterEqual(len(report.recommendations), 1)

    def test_excessive_exploration_detection(self):
        report = analyze_reasoning_topology(SAMPLE_EXPLORATION_DRIFT)
        self.assertEqual(report.isomer_state, "UNSTABLE_EXPLORATION")
        self.assertGreater(report.vdw_ratio, 0.35)
        self.assertTrue(any("Van der Waals" in a for a in report.anomalies))

    def test_rigid_deduction_detection(self):
        report = analyze_reasoning_topology(SAMPLE_RIGID_COT)
        self.assertEqual(report.isomer_state, "RIGID_DEDUCTION")
        self.assertEqual(report.hydrogen_ratio, 0.0)
        self.assertTrue(any("Hydrogen" in a for a in report.anomalies))

    def test_neurotic_reflection_detection(self):
        report = analyze_reasoning_topology(SAMPLE_NEUROTIC_COT)
        self.assertEqual(report.isomer_state, "NEUROTIC_REFLECTION")
        self.assertGreater(report.hydrogen_ratio, 0.35)

    def test_empty_trace_handling(self):
        report = analyze_reasoning_topology("")
        self.assertEqual(report.total_steps, 0)
        self.assertEqual(report.isomer_state, "EMPTY")


if __name__ == "__main__":
    unittest.main()
