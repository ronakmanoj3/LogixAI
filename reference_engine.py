"""Deterministic teaching-case calculator. This is NOT a live LLM agent.

Run: python3 reference_engine.py
     python3 reference_engine.py --no-transfer
     python3 reference_engine.py --no-transfer --express-day 5
All receipts arrive before that day's demand. Demand is lost, not backordered.
"""
import argparse
import json
import math
from pathlib import Path


def number(value, label, integer=False, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: numeric value required")
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"{label}: invalid value")
    if integer and int(value) != value:
        raise ValueError(f"{label}: integer required")


def validate(case):
    for key in ("on_hand", "daily_demand", "horizon_days", "transfer_available"):
        number(case[key], key, integer=True, minimum=1 if key == "horizon_days" else 0)
    for key in ("contribution_per_unit", "standard_unit_cost", "response_budget"):
        number(case[key], key)
    for receipt in case["regular_receipts"]:
        number(receipt["day"], "receipt day", integer=True, minimum=1)
        number(receipt["quantity"], "receipt quantity", integer=True)
    if not case["actions"] or len({a["name"] for a in case["actions"]}) != len(case["actions"]):
        raise ValueError("Unique, nonempty action list required")
    for action in case["actions"]:
        if action["kind"] not in {"none", "transfer", "purchase"}:
            raise ValueError("Unknown action kind")
        for key in ("day", "quantity"):
            number(action[key], key, integer=True, minimum=1 if key == "day" else 0)
        for key in ("unit_premium", "fixed_fee"):
            number(action[key], key)
        if action["kind"] == "none" and any(action[k] != 0 for k in ("quantity", "unit_premium", "fixed_fee")):
            raise ValueError("No-action option must have zero quantity and costs")
    if not any(a["kind"] == "none" for a in case["actions"]):
        raise ValueError("No-action baseline required")


def simulate(case, action=None):
    stock = case["on_hand"]
    trace = []
    for day in range(1, case["horizon_days"] + 1):
        receipts = sum(r["quantity"] for r in case["regular_receipts"] if r["day"] == day)
        if action is not None and action["day"] == day:
            receipts += action["quantity"]
        stock += receipts
        fulfilled = min(stock, case["daily_demand"])
        stock -= fulfilled
        trace.append({"day": day, "receipts": receipts, "fulfilled": fulfilled,
                      "lost_units": case["daily_demand"] - fulfilled, "closing_stock": stock})
    return trace


def evaluate(case):
    validate(case)
    baseline = simulate(case)
    baseline_lost = sum(d["lost_units"] for d in baseline)
    options = []
    for action in case["actions"]:
        incremental_cost = action["quantity"] * action["unit_premium"] + action["fixed_fee"]
        cash = incremental_cost
        if action["kind"] == "purchase":
            cash += action["quantity"] * case["standard_unit_cost"]
        reasons = []
        if action["kind"] == "transfer" and action["quantity"] > case["transfer_available"]:
            reasons.append("Insufficient transferable donor stock")
        if cash > case["response_budget"]:
            reasons.append("Exceeds response cash budget")
        trace = simulate(case, action)
        lost = sum(d["lost_units"] for d in trace)
        gain = (baseline_lost - lost) * case["contribution_per_unit"] - incremental_cost
        options.append({"action": action["name"], "feasible": not reasons,
                        "rejection_reasons": reasons, "lost_units": lost,
                        "incremental_response_cost": incremental_cost,
                        "cash_required": cash, "net_contribution_gain_vs_no_action": gain,
                        "daily_trace": trace})
    feasible = [o for o in options if o["feasible"]]
    best = max(feasible, key=lambda o: (o["net_contribution_gain_vs_no_action"], -o["cash_required"]))
    return {"status": "REFERENCE CALCULATION ONLY; human review required",
            "dataset_label": case["dataset_label"], "sku": case["sku"], "currency": case["currency"],
            "baseline_lost_units": baseline_lost, "baseline_daily_trace": baseline,
            "recommended_action": best["action"], "options": options}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=Path(__file__).with_name("scenario.json"))
    parser.add_argument("--no-transfer", action="store_true")
    parser.add_argument("--express-day", type=int)
    parser.add_argument("--budget", type=float)
    args = parser.parse_args()
    try:
        case = json.loads(args.scenario.read_text())
        if args.no_transfer:
            case["transfer_available"] = 0
        if args.budget is not None:
            case["response_budget"] = args.budget
        if args.express_day is not None:
            for action in case["actions"]:
                if action["kind"] == "purchase":
                    action["day"] = args.express_day
        print(json.dumps(evaluate(case), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"INPUT ERROR: {error}\n")
