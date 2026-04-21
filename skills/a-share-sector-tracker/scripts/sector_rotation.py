import argparse
import json
from itertools import combinations
from pathlib import Path

from sector_common import best_lead_lag, correlation, load_json


def cluster_label(corr_value):
    if corr_value >= 0.8:
        return "tight_cluster"
    if corr_value >= 0.6:
        return "high_correlation"
    if corr_value >= 0.4:
        return "moderate_correlation"
    return "low_correlation"


def analyze_rotation(payload):
    sectors = payload.get("sectors", [])
    matrix = []
    lead_lag = []
    for left, right in combinations(sectors, 2):
        left_series = left.get("daily_returns_history", [])
        right_series = right.get("daily_returns_history", [])
        corr_value = correlation(left_series, right_series)
        lag_info = best_lead_lag(left_series, right_series, max_lag=5)
        matrix.append(
            {
                "left_sector": left["sector_name"],
                "right_sector": right["sector_name"],
                "correlation": round(corr_value, 4),
                "cluster": cluster_label(corr_value),
            }
        )
        lead_lag.append(
            {
                "pair": f"{left['sector_name']} vs {right['sector_name']}",
                "leader_candidate": left["sector_name"] if lag_info["lag"] > 0 else right["sector_name"] if lag_info["lag"] < 0 else "none",
                "follower_candidate": right["sector_name"] if lag_info["lag"] > 0 else left["sector_name"] if lag_info["lag"] < 0 else "none",
                "lag_days": lag_info["lag"],
                "correlation": round(lag_info["correlation"], 4),
            }
        )
    return {"date": payload["date"], "correlation_pairs": matrix, "lead_lag_pairs": lead_lag}


def main():
    parser = argparse.ArgumentParser(description="Run sector correlation and lead-lag analysis.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = load_json(args.input)
    result = analyze_rotation(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
