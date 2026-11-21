"""Fenrir contract and conservative critique tests."""
import copy
import unittest

from cerberus.gate import evaluate
from fenrir.reviewer import critique


class FenrirTests(unittest.TestCase):
    def setUp(self):
        self.o = {
            "cycle_id": "cycle-01",
            "candidate_sha256": "a" * 64,
            "source_commit": "b" * 40,
            "producer": {
                "agent_id": "OUROBOROS",
                "execution_id": "o-worker-1",
                "evidence_url": "https://github.com/example/o/actions/runs/1",
            },
        }

    def run_critic(self):
        return critique(self.o, execution_id="fenrir-worker-2",
                        evidence_url="https://github.com/example/c/actions/runs/2")

    def test_creates_bound_fenrir_report(self):
        report = self.run_critic()
        self.assertEqual(report["producer"]["agent_id"], "FENRIR")
        self.assertEqual(report["candidate_sha256"], self.o["candidate_sha256"])
        self.assertTrue(report["findings"])
        self.assertEqual(report["review_mode"], "RULE_BASED_PROTOTYPE_NOT_INDEPENDENT_LLM")

    def test_cerberus_does_not_call_report_pass(self):
        self.assertEqual(evaluate(self.o, self.run_critic())["status"], "INCONCLUSIVE")

    def test_missing_artifact_digest_rejected(self):
        self.o.pop("candidate_sha256")
        with self.assertRaises(ValueError):
            self.run_critic()

    def test_bad_source_commit_rejected(self):
        self.o["source_commit"] = "broken"
        with self.assertRaises(ValueError):
            self.run_critic()

    def test_fenrir_sharing_o_execution_id_rejected(self):
        with self.assertRaises(ValueError):
            critique(self.o, execution_id="o-worker-1", evidence_url="https://example.com/e")

    def test_missing_evidence_url_rejected(self):
        with self.assertRaises(ValueError):
            critique(self.o, execution_id="different", evidence_url="")

    def test_benchmark_reuse_flagged_as_risk_not_confirmed_defect(self):
        self.o["evaluation"] = {"benchmark_reused": True}
        report = self.run_critic()
        finding = next(f for f in report["findings"] if f["id"] == "F-LEAKAGE-01")
        self.assertEqual(finding["classification"], "hypothesis")

    def test_complete_self_report_still_not_proof(self):
        self.o["evaluation"] = {
            "holdout_id": "asserted",
            "holdout_protected": True,
            "independent_replay_url": "https://github.com/example/o/actions/runs/3",
            "baseline_score": 0.5,
            "candidate_score": 0.6,
        }
        report = self.run_critic()
        self.assertEqual(report["findings"][0]["id"], "F-SCOPE-01")
        self.assertEqual(evaluate(self.o, report)["status"], "INCONCLUSIVE")

    def test_different_candidate_blocked_by_cerberus(self):
        report = self.run_critic()
        report["candidate_sha256"] = "c" * 64
        self.assertEqual(evaluate(self.o, report)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
