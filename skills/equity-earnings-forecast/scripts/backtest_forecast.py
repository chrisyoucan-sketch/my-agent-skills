import argparse
import json
import math
from statistics import mean

from forecast_core import forecast_from_data, mape


def rmse(actuals, preds):
    if not actuals:
        return None
    mse = mean([(a - p) ** 2 for a, p in zip(actuals, preds)])
    return math.sqrt(mse)


def direction_accuracy(actuals, preds):
    if len(actuals) < 2:
        return None
    hits = 0
    total = 0
    for i in range(1, len(actuals)):
        da = actuals[i] - actuals[i - 1]
        dp = preds[i] - preds[i - 1]
        if da == 0:
            continue
        total += 1
        if (da > 0 and dp > 0) or (da < 0 and dp < 0):
            hits += 1
    return (hits / total) if total else None


def interval_coverage(actuals, preds, band=0.1):
    if not actuals:
        return None
    hits = 0
    for a, p in zip(actuals, preds):
        low, high = p * (1 - band), p * (1 + band)
        if low <= a <= high:
            hits += 1
    return hits / len(actuals)


def run_backtest(payload, lookback):
    rows = payload.get("quarters") or []
    if len(rows) < lookback + 1:
        raise ValueError(f"Need at least {lookback + 1} quarters for rolling backtest.")

    actuals = []
    preds = []
    details = []
    start = len(rows) - lookback

    for i in range(start, len(rows)):
        history = []
        for j in range(0, i):
            history.append(
                {
                    "period": rows[j]["period"],
                    "revenue": rows[j]["actuals"]["revenue"],
                    "net_profit": rows[j]["actuals"]["net_profit"],
                    "eps": rows[j]["actuals"]["eps_diluted"],
                }
            )

        obs = rows[i]
        data = {
            "company": payload.get("company", {}),
            "target_period": obs["period"],
            "segments": obs.get("segments", []),
            "opex": obs.get("opex", {}),
            "non_operating": obs.get("non_operating", {"amount": 0.0}),
            "tax_rate": obs.get("tax_rate", 0.2),
            "shares_diluted": obs.get("shares_diluted", 1.0),
            "cfo": obs.get("cfo", 0.0),
            "capex": obs.get("capex", 0.0),
            "consensus": obs.get("consensus"),
            "guidance": obs.get("guidance"),
            "history": history,
        }

        pred = forecast_from_data(data, scenario="base")["forecast"]["revenue"]
        act = obs["actuals"]["revenue"]
        actuals.append(act)
        preds.append(pred)
        details.append({"period": obs["period"], "actual_revenue": act, "pred_revenue": pred})

    mapes = [mape(a, p) for a, p in zip(actuals, preds) if mape(a, p) is not None]
    return {
        "company": payload.get("company", {}),
        "lookback_quarters": lookback,
        "metrics": {
            "mape": round(mean(mapes), 6) if mapes else None,
            "rmse": round(rmse(actuals, preds), 6) if actuals else None,
            "direction_accuracy": round(direction_accuracy(actuals, preds), 6)
            if direction_accuracy(actuals, preds) is not None
            else None,
            "interval_coverage_10pct": round(interval_coverage(actuals, preds, band=0.1), 6),
        },
        "details": details,
        "disclaimer": "For research analysis only. Not investment advice.",
    }


def main():
    parser = argparse.ArgumentParser(description="Run rolling earnings forecast backtest.")
    parser.add_argument("--input", required=True, help="Path to backtest JSON.")
    parser.add_argument("--lookback", type=int, default=8, help="Number of target quarters.")
    parser.add_argument("--output", help="Optional output path.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    result = run_backtest(payload, args.lookback)
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
