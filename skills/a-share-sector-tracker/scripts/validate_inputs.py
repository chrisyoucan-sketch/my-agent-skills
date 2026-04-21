import argparse
import json
import sys

from sector_common import load_json


def validate_payload(payload):
    errors = []
    warnings = []

    if payload.get("provider") != "Wind":
        warnings.append("Provider is not Wind; v1 is optimized for Wind mappings.")

    benchmark = payload.get("benchmark", {})
    if benchmark.get("name") != "All A":
        warnings.append("Benchmark is not All A.")

    for field in ("return_1d", "return_5d", "return_20d"):
        if field not in benchmark:
            errors.append(f"Missing benchmark field: {field}")

    sectors = payload.get("sectors")
    if not isinstance(sectors, list) or not sectors:
        errors.append("Input must include a non-empty sectors array.")
        return errors, warnings

    required_sector_fields = [
        "sector_code",
        "sector_name",
        "taxonomy",
        "board_source",
        "return_1d",
        "return_5d",
        "return_20d",
        "turnover_value",
        "main_force_net_inflow_1d",
        "main_force_net_inflow_5d",
        "main_force_net_inflow_20d",
        "close_history",
        "volume_history",
        "daily_returns_history",
        "constituents",
    ]
    required_constituent_fields = [
        "ticker",
        "name",
        "return_1d",
        "return_5d",
        "return_20d",
        "turnover_value",
        "main_force_net_inflow_1d",
        "volume_ratio",
        "is_limit_up",
        "above_ma20",
        "above_ma60",
        "new_20d_high",
        "contribution_to_sector_return",
    ]

    for sector in sectors:
        label = sector.get("sector_name", "<unknown>")
        for field in required_sector_fields:
            if field not in sector:
                errors.append(f"{label}: missing sector field {field}")
        if len(sector.get("close_history", [])) < 20:
            errors.append(f"{label}: close_history must have at least 20 points")
        if len(sector.get("volume_history", [])) < 20:
            errors.append(f"{label}: volume_history must have at least 20 points")
        if len(sector.get("daily_returns_history", [])) < 20:
            errors.append(f"{label}: daily_returns_history must have at least 20 points")
        constituents = sector.get("constituents", [])
        if len(constituents) < 3:
            errors.append(f"{label}: need at least 3 constituents for leader analysis")
        elif len(constituents) < 5:
            warnings.append(f"{label}: fewer than 5 constituents, confidence will be lower")
        for constituent in constituents:
            stock_label = constituent.get("name", "<unknown>")
            for field in required_constituent_fields:
                if field not in constituent:
                    errors.append(f"{label}/{stock_label}: missing constituent field {field}")
        if sector.get("sector_level_flow_source") == "constituent_aggregate":
            warnings.append(f"{label}: sector flow is aggregated from constituents")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate an A-share sector tracker input payload.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = load_json(args.input)
    errors, warnings = validate_payload(payload)
    result = {
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    print(text)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
