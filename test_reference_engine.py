"""Numerical acceptance tests for the reference calculator, not the proposed agent."""
import copy
import json
from pathlib import Path
import unittest
from reference_engine import evaluate


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads(Path(__file__).with_name("scenario.json").read_text())

    def test_baseline_and_transfer(self):
        result = evaluate(self.case)
        self.assertEqual(result["baseline_lost_units"], 80)
        self.assertEqual([d["day"] for d in result["baseline_daily_trace"] if d["lost_units"]], [4, 5])
        self.assertEqual(result["recommended_action"], "Warehouse transfer")
        transfer = result["options"][1]
        self.assertEqual((transfer["lost_units"], transfer["cash_required"], transfer["net_contribution_gain_vs_no_action"]), (0, 400, 1600))

    def test_transfer_unavailable(self):
        self.case["transfer_available"] = 0
        result = evaluate(self.case)
        self.assertEqual(result["recommended_action"], "Expedited purchase")
        purchase = result["options"][2]
        self.assertEqual((purchase["lost_units"], purchase["cash_required"], purchase["incremental_response_cost"], purchase["net_contribution_gain_vs_no_action"]), (0, 9160, 1160, 840))

    def test_late_receipt_not_retroactive(self):
        self.case["transfer_available"] = 0
        self.case["actions"][2]["day"] = 5
        result = evaluate(self.case)
        self.assertEqual(result["recommended_action"], "No action")
        self.assertEqual(result["options"][2]["lost_units"], 40)
        self.assertEqual(result["options"][2]["net_contribution_gain_vs_no_action"], -160)

    def test_cash_budget_is_not_incremental_cost(self):
        self.case["transfer_available"] = 0
        self.case["response_budget"] = 2000
        result = evaluate(self.case)
        self.assertEqual(result["recommended_action"], "No action")
        self.assertFalse(result["options"][2]["feasible"])

    def test_sufficient_inventory(self):
        self.case["on_hand"] = 400
        self.assertEqual(evaluate(self.case)["recommended_action"], "No action")

    def test_bad_values_rejected(self):
        for bad in (-1, float("nan"), "unknown", True):
            with self.subTest(bad=bad):
                case = copy.deepcopy(self.case)
                case["on_hand"] = bad
                with self.assertRaises(ValueError):
                    evaluate(case)

    def test_missing_data_rejected(self):
        del self.case["daily_demand"]
        with self.assertRaises(KeyError):
            evaluate(self.case)

    def test_stock_flow_conservation(self):
        result = evaluate(self.case)
        for option in result["options"]:
            trace = option["daily_trace"]
            self.assertEqual(self.case["on_hand"] + sum(d["receipts"] for d in trace),
                             sum(d["fulfilled"] for d in trace) + trace[-1]["closing_stock"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
