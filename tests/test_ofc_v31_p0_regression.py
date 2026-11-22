import unittest
from agent import cycle_registry as r
SOURCE = "b" * 40

class CerberusReceiptRegression(unittest.TestCase):
    def active(self):
        return dict(schema=1, agent=r.AGENT, cycle="cycle-c", source=SOURCE,
                    phase="open", owner="run-c", generation=5, expires=200,
                    checkpoint=None, pending=None, results={})

    def test_unreserved_receipt_rejected(self):
        with self.assertRaises(r.Blocked):
            r.transition(self.active(), "record", "run-c", 5, SOURCE, "fake=proof", 100, 60)

    def test_mismatched_receipt_rejected_and_pending_retained(self):
        state, _ = r.transition(self.active(), "reserve", "run-c", 5, SOURCE, "key-1", 100, 60)
        with self.assertRaises(r.Blocked):
            r.transition(state, "record", "run-c", 5, SOURCE, "key-2=proof", 101, 60)
        self.assertEqual(state["pending"], "key-1")

    def test_duplicate_receipt_not_new_success(self):
        state, _ = r.transition(self.active(), "reserve", "run-c", 5, SOURCE, "key-1", 100, 60)
        state, _ = r.transition(state, "record", "run-c", 5, SOURCE, "key-1=receipt", 101, 60)
        with self.assertRaises(r.Blocked):
            r.transition(state, "reserve", "run-c", 5, SOURCE, "key-1", 102, 60)
        self.assertEqual(state["results"], {"key-1": "receipt"})

    def test_wrong_owner_generation_and_source_rejected(self):
        for owner, gen, source in [("attacker", 5, SOURCE), ("run-c", 4, SOURCE), ("run-c", 5, "c"*40)]:
            with self.subTest(owner=owner, gen=gen, source=source):
                with self.assertRaises(r.Blocked):
                    r.transition(self.active(), "checkpoint", owner, gen, source, "pass", 100, 60)

    def test_no_cryptographic_signature_verification_in_registry(self):
        # Explicit limitation: record stores opaque evidence, not a signed proof.
        state, _ = r.transition(self.active(), "reserve", "run-c", 5, SOURCE, "key", 100, 60)
        state, _ = r.transition(state, "record", "run-c", 5, SOURCE, "key=UNSIGNED", 101, 60)
        self.assertEqual(state["results"]["key"], "UNSIGNED")
if __name__ == "__main__":
    unittest.main()
