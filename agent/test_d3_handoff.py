import json
import unittest
from agent.d3_handoff import independent_grade
class D3HandoffTests(unittest.TestCase):
    def test_wrong_math_and_novelty(self):
        case=dict(id="x",a=35,b=3,observed="4")
        x=dict(risk="possible_digit_integer_conflict",test_a=81,test_b=9,rationale="The digit and integer instructions may conflict.",expected="38",observed="4",mismatch=True,test_expected="90")
        r=dict(mode="direct",raw=json.dumps(x))
        self.assertTrue(independent_grade(r,case)["pass_"])
        for bad in (dict(expected="7"),dict(risk="no_mismatch_in_this_case"),dict(test_a=11,test_b=2,test_expected="13")):
            self.assertFalse(independent_grade(dict(r,raw=json.dumps(dict(x,**bad))),case)["pass_"])
    def test_hybrid_ground_truth(self):
        case=dict(id="x",a=35,b=3,observed="4")
        x=dict(risk="possible_digit_integer_conflict",test_a=81,test_b=9,rationale="The digit and integer instructions may conflict.")
        self.assertEqual(independent_grade(dict(mode="hybrid",raw=json.dumps(x)),case)["expected"],"38")
        self.assertFalse(independent_grade(dict(mode="hybrid",raw=json.dumps(x)+ "{}"),case)["pass_"])
