import argparse
import json
from pathlib import Path

from sector_common import (
    bollinger_position,
    clamp,
    latest_macd_state,
    latest_volume_ratio,
    load_json,
    moving_average,
    percentile_rank,
    safe_divide,
)
from sector_leaders import identify_sector_leaders


def breadth_metrics(sector):
    constituents = sector.get("constituents", [])
    valid = len(constituents) or 1
    above_ma20 = sum(1 for stock in constituents if stock.get("above_ma20"))
    above_ma60 = sum(1 for stock in constituents if stock.get("above_ma60"))
    up_count = sum(1 for stock in constituents if stock.get("return_1d", 0.0) > 0)
    new_high_count = sum(1 for stock in constituents if stock.get("new_20d_high"))
    contributions = sorted(
        [abs(float(stock.get("contribution_to_sector_return", 0.0))) for stock in constituents],
        reverse=True,
    )
    contribution_mass = sum(contributions) or 1.0
    top3_contribution = sum(contributions[:3])
    return {
        "breadth_above_ma20": above_ma20 / valid,
        "breadth_above_ma60": above_ma60 / valid,
        "up_stock_ratio": up_count / valid,
        "new_20d_high_ratio": new_high_count / valid,
        "top3_return_contribution": top3_contribution / contribution_mass,
    }


def classify_state(sector, benchmark, metrics):
    if sector["return_5d"] < 0 or (
        metrics["flow_intensity_1d"] < 0 and sector["return_5d"] < benchmark["return_5d"]
    ):
        return "fading"
    if (
        sector["return_20d"] > benchmark["return_20d"]
        and metrics["flow_intensity_1d"] > 0
        and metrics["breadth_above_ma20"] >= 0.6
        and metrics["top3_return_contribution"] < 0.6
    ):
        return "strengthening"
    if (
        sector["return_5d"] > benchmark["return_5d"]
        and metrics["flow_intensity_1d"] > 0
        and metrics["breadth_above_ma20"] >= 0.4
    ):
        return "launch"
    if (
        sector["return_5d"] > 0
        and metrics["top3_return_contribution"] >= 0.6
        and metrics["breadth_above_ma20"] < 0.6
    ):
        return "divergence"
    if sector["return_20d"] <= 0 and metrics["breadth_above_ma20"] >= 0.4:
        return "bottoming"
    return "range-bound"


def score_sectors(payload):
    benchmark = payload["benchmark"]
    sectors = payload.get("sectors", [])
    flow_intensities = [
        safe_divide(sector.get("main_force_net_inflow_1d", 0.0), sector.get("turnover_value", 0.0))
        for sector in sectors
    ]

    enriched = []
    trend_values = []
    breadth_values = []
    leader_values = []
    for sector in sectors:
        breadth = breadth_metrics(sector)
        close_history = sector["close_history"]
        volume_history = sector["volume_history"]
        latest_close = close_history[-1]
        ma20 = moving_average(close_history, 20)
        ma60 = moving_average(close_history, 60)
        trend_value = (
            35.0 * (1.0 if latest_close > ma20 else 0.0)
            + 20.0 * (1.0 if latest_close > ma60 else 0.0)
            + 20.0 * max(0.0, latest_volume_ratio(volume_history) - 0.8)
            + 25.0 * (1.0 if latest_macd_state(close_history) == "bullish" else 0.3)
        )
        breadth_value = (
            40.0 * breadth["breadth_above_ma20"]
            + 25.0 * breadth["breadth_above_ma60"]
            + 20.0 * breadth["up_stock_ratio"]
            + 15.0 * breadth["new_20d_high_ratio"]
        )
        leader_result = identify_sector_leaders(sector)
        leader_value = leader_result["primary_leader"]["score"] if leader_result["primary_leader"] else 0.0
        trend_values.append(trend_value)
        breadth_values.append(breadth_value)
        leader_values.append(leader_value)
        enriched.append(
            {
                "sector": sector,
                "breadth": breadth,
                "trend_value": trend_value,
                "breadth_value": breadth_value,
                "leader_result": leader_result,
                "leader_value": leader_value,
            }
        )

    ranked = []
    for item, flow_value in zip(enriched, flow_intensities):
        sector = item["sector"]
        breadth = item["breadth"]
        flow_score = percentile_rank(flow_intensities, flow_value)
        trend_score = percentile_rank(trend_values, item["trend_value"])
        breadth_score = percentile_rank(breadth_values, item["breadth_value"])
        leader_score = percentile_rank(leader_values, item["leader_value"])
        catalyst_score = 60.0 if sector.get("catalysts") else 20.0
        total_score = (
            0.30 * flow_score
            + 0.25 * trend_score
            + 0.20 * breadth_score
            + 0.15 * leader_score
            + 0.10 * catalyst_score
        )

        confidence = 1.0
        if sector.get("sector_level_flow_source") == "constituent_aggregate":
            confidence -= 0.15
        if len(sector.get("constituents", [])) < 5:
            confidence -= 0.10
        if not sector.get("catalysts"):
            confidence -= 0.10

        metrics = {
            "excess_return_vs_all_a_1d": sector["return_1d"] - benchmark["return_1d"],
            "excess_return_vs_all_a_5d": sector["return_5d"] - benchmark["return_5d"],
            "excess_return_vs_all_a_20d": sector["return_20d"] - benchmark["return_20d"],
            "flow_intensity_1d": flow_value,
            "volume_ratio": latest_volume_ratio(sector["volume_history"]),
            "macd_state": latest_macd_state(sector["close_history"]),
            "bollinger_position": bollinger_position(sector["close_history"]),
            "breadth_above_ma20": breadth["breadth_above_ma20"],
            "breadth_above_ma60": breadth["breadth_above_ma60"],
            "up_stock_ratio": breadth["up_stock_ratio"],
            "new_20d_high_ratio": breadth["new_20d_high_ratio"],
            "top3_return_contribution": breadth["top3_return_contribution"],
        }
        sector_state = classify_state(sector, benchmark, metrics)
        risk_flags = list(sector.get("risk_flags", []))
        if metrics["top3_return_contribution"] >= 0.6:
            risk_flags.append("leader_concentration_high")
        if metrics["flow_intensity_1d"] < 0 and sector["return_1d"] > 0:
            risk_flags.append("price_up_flow_down")

        ranked.append(
            {
                "date": payload["date"],
                "provider": payload["provider"],
                "taxonomy": sector["taxonomy"],
                "sector_code": sector["sector_code"],
                "sector_name": sector["sector_name"],
                "board_source": sector["board_source"],
                "return_1d": sector["return_1d"],
                "return_5d": sector["return_5d"],
                "return_20d": sector["return_20d"],
                "total_score": round(total_score, 2),
                "capital_flow_score": round(flow_score, 2),
                "trend_score": round(trend_score, 2),
                "breadth_score": round(breadth_score, 2),
                "leader_score_component": round(leader_score, 2),
                "catalyst_score": round(catalyst_score, 2),
                "confidence": round(clamp(confidence), 2),
                "sector_state": sector_state,
                "leader_name": item["leader_result"]["primary_leader"]["name"],
                "leader_score": round(item["leader_value"], 2),
                "metrics": metrics,
                "risk_flags": sorted(set(risk_flags)),
                "flow_source": sector.get("sector_level_flow_source", "sector"),
                "evidence": [
                    {
                        "metric": "return_5d",
                        "value": sector["return_5d"],
                        "basis": "All A benchmark comparison",
                        "rule": "sector_return_5d - benchmark_return_5d",
                        "source": payload["provider"],
                        "timestamp": payload["date"],
                    },
                    {
                        "metric": "main_force_net_inflow_1d",
                        "value": sector["main_force_net_inflow_1d"],
                        "basis": "daily sector flow",
                        "rule": "main_force_net_inflow_1d / turnover_value",
                        "source": payload["provider"],
                        "timestamp": payload["date"],
                    },
                ],
            }
        )

    ranked.sort(key=lambda row: row["total_score"], reverse=True)
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return {"date": payload["date"], "benchmark": benchmark, "sectors": ranked}


def main():
    parser = argparse.ArgumentParser(description="Score A-share sectors from a Wind-style payload.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = load_json(args.input)
    result = score_sectors(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
