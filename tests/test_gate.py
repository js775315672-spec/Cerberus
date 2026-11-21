"""Offline tests: no network, no credentials and no external dependencies."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from cerberus.gate import evaluate, load_document


class GateTests(unittest.TestCase):
    def setUp(self):
        self.o = {
            "cycle_id": "cycle-001",
            "candidate_sha256": "a" * 64,
            "source_commit": "b" * 40,
            "producer": {"agent_id": "OUROBOROS", "execution_id": "o-100",
                         "evidence_url": "https://github.com/example/O/actions/runs/10"},
        }
        self.f = {
            "cycle_id": "cycle-001",
            "candidate_sha256": "a" * 64,
            "producer": {"agent_id": "FENRIR", "execution_id": "f-101",
                         "evidence_url": "https://github.com/example/F/issues/1"},
            "findings": [{"id": "F-01", "severity": "P2",
                          "classification": "hypothesis", "summary": "Possible leak",
                          "reproduction": "Replay with a new holdout split",
                          "evidence_url": "https://github.com/example/F/issues/1"}],
        }

    def test_valid_metadata_still_cannot_prove_independence(self):
        result = evaluate(self.o, self.f)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertFalse(result["eligible_for_merge"])
        self.assertFalse(result["independence_verified"])

    def test_sha_mismatch_blocks(self):
        self.f["candidate_sha256"] = "c" * 64
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_cycle_mismatch_blocks(self):
        self.f["cycle_id"] = "other"
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_wrong_fenrir_identity_blocks(self):
        self.f["producer"]["agent_id"] = "OUROBOROS"
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_same_execution_id_blocks(self):
        self.f["producer"]["execution_id"] = "o-100"
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_confirmed_p0_blocks(self):
        item = self.f["findings"][0]
        item["severity"] = "P0"
        item["classification"] = "confirmed"
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_hypothetical_p0_does_not_claim_pass(self):
        self.f["findings"][0]["severity"] = "P0"
        self.assertEqual(evaluate(self.o, self.f)["status"], "INCONCLUSIVE")

    def test_absent_findings_blocks(self):
        self.f["findings"] = []
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_duplicate_finding_id_blocks(self):
        self.f["findings"].append(copy.deepcopy(self.f["findings"][0]))
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_invalid_finding_blocks(self):
        self.f["findings"][0]["classification"] = "proof"
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_malformed_severity_type_blocks_instead_of_crashing(self):
        self.f["findings"][0]["severity"] = ["P0"]
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_malformed_classification_type_blocks(self):
        self.f["findings"][0]["classification"] = {"x": 1}
        self.assertEqual(evaluate(self.o, self.f)["status"], "BLOCKED")

    def test_non_object_blocks(self):
        self.assertEqual(evaluate([], self.f)["status"], "BLOCKED")

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "dup.json"
            path.write_text('{"x": 1, "x": 2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_document(path)

    def test_oversized_json_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "large.json"
            path.write_text(json.dumps({"x": "A" * 1_000_001}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_document(path)


if __name__ == "__main__":
    unittest.main()
