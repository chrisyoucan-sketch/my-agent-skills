import argparse
import json
from pathlib import Path

from sector_common import load_json, percentile_rank


LEADER_WEIGHTS = {
    "turnover_value": 0.20,
    "return_1d": 0.10,
    "return_5d": 0.20,
    "return_20d": 0.20,
    "main_force_net_inflow_1d": 0.15,
    "volume_ratio": 0.05,
    "is_limit_up": 0.05,
    "contribution_to_sector_return": 0.05,
}


def identify_sector_leaders(sector):
    constituents = sector.get("constituents", [])
    if not constituents:
        return {
            "sector_code": sector.get("sector_code"),
            "sector_name": sector.get("sector_name"),
            "leaders": [],
            "primary_leader": None,
            "comment": "no valid constituents"
        }

    metrics = {}
    for field in LEADER_WEIGHTS:
        if field == "is_limit_up":
            metrics[field] = [1.0 if stock.get(field) else 0.0 for stock in constituents]
        else:
            metrics[field] = [float(stock.get(field, 0.0)) for stock in constituents]

    scored = []
    for stock in constituents:
        total_score = 0.0
        for field, weight in LEADER_WEIGHTS.items():
            raw_value = 1.0 if stock.get(field) is True else float(stock.get(field, 0.0))
            total_score += weight * percentile_rank(metrics[field], raw_value)
        scored.append(
            {
                "ticker": stock.get("ticker"),
                "name": stock.get("name"),
                "score": round(total_score, 2),
                "return_1d": stock.get("return_1d", 0.0),
                "return_5d": stock.get("return_5d", 0.0),
                "return_20d": stock.get("return_20d", 0.0),
                "main_force_net_inflow_1d": stock.get("main_force_net_inflow_1d", 0.0),
                "turnover_value": stock.get("turnover_value", 0.0),
                "is_limit_up": stock.get("is_limit_up", False),
                "contribution_to_sector_return": stock.get("contribution_to_sector_return", 0.0),
            }
        )

    leaders = sorted(scored, key=lambda item: item["score"], reverse=True)
    primary = leaders[0]
    comment = "sector following primary leader"
    if len(leaders) > 1 and primary["score"] - leaders[1]["score"] > 15:
        comment = "leadership highly concentrated"
    elif len(leaders) > 1 and leaders[1]["score"] > 70:
        comment = "multiple leaders confirm the move"

    return {
        "sector_code": sector.get("sector_code"),
        "sector_name": sector.get("sector_name"),
        "leaders": leaders[:3],
        "primary_leader": primary,
        "comment": comment,
    }


def run(payload):
    return {"leaders_by_sector": [identify_sector_leaders(sector) for sector in payload.get("sectors", [])]}


def main():
    parser = argparse.ArgumentParser(description="Identify sector leaders from a sector input payload.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = load_json(args.input)
    result = run(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
