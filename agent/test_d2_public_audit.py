import copy
from pathlib import Path
import unittest
from agent.d2_public_audit import open_archive,regrade

class PublicAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c,cls.ab,cls.aa=open_archive(Path("d2-raw.zip"))

    def test_regrade(self):
        _,_,r=regrade(self.ab,self.aa)
        self.assertEqual(r["raw_calls"],120)
        self.assertEqual(r["public_matches"],{"verbose":11,"compact":20})
        self.assertEqual(r["new_public_errors"],0)

    def test_bad_label(self):
        ab=copy.deepcopy(self.ab)
        x=ab["rows"][0]["observations"][0]
        x["exact_public_answer_match"]=not x["exact_public_answer_match"]
        with self.assertRaises(ValueError): regrade(ab,self.aa)

    def test_false_summary(self):
        ab=copy.deepcopy(self.ab)
        ab["summary"]["public_exact_matches"]["compact"]=30
        with self.assertRaises(ValueError): regrade(ab,self.aa)

    def test_false_model(self):
        ab=copy.deepcopy(self.ab)
        ab["weight_files"][0]["sha256"]="0"*64
        with self.assertRaises(ValueError): regrade(ab,self.aa)

    def test_wrong_task(self):
        aa=copy.deepcopy(self.aa)
        aa["rows"][0]["expected"]="0"
        with self.assertRaises(ValueError): regrade(self.ab,aa)
