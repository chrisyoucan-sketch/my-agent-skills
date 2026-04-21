import argparse
from pathlib import Path

from sector_common import load_json
from sector_leaders import run as run_leaders
from sector_rotation import analyze_rotation
from sector_score import score_sectors


def pct(value):
    return f"{value * 100:.1f}%"


def build_note(payload):
    scored = score_sectors(payload)
    leaders = run_leaders(payload)["leaders_by_sector"]
    rotation = analyze_rotation(
        {
            "date": payload["date"],
            "sectors": [
                {
                    "sector_name": sector["sector_name"],
                    "daily_returns_history": sector["daily_returns_history"],
                }
                for sector in payload["sectors"]
            ],
        }
    )
    leader_map = {item["sector_code"]: item for item in leaders}

    lines = []
    lines.append(f"# Daily A-Share Sector Snapshot ({payload['date']})")
    lines.append("")
    lines.append(
        f"Benchmark `{scored['benchmark']['name']}` moved {pct(scored['benchmark']['return_1d'])}. "
        "The note ranks Wind industry and concept sectors using main-force inflow, trend, breadth, and leader confirmation."
    )
    lines.append("")
    lines.append("## Top Sectors")
    lines.append("")
    lines.append("| Rank | Sector | Taxonomy | Total | State | 1D | 5D | 20D | Confidence |")
    lines.append("|---|---|---|---:|---|---:|---:|---:|---:|")
    for sector in scored["sectors"]:
        lines.append(
            f"| {sector['rank']} | {sector['sector_name']} | {sector['taxonomy']} | {sector['total_score']:.1f} | "
            f"{sector['sector_state']} | {pct(sector['return_1d'])} | {pct(sector['return_5d'])} | "
            f"{pct(sector['return_20d'])} | {sector['confidence']:.2f} |"
        )

    lines.append("")
    lines.append("## Flow And Breadth")
    lines.append("")
    for sector in scored["sectors"]:
        metrics = sector["metrics"]
        lines.append(
            f"- {sector['sector_name']}: flow intensity {metrics['flow_intensity_1d']:.3f}, "
            f"breadth above MA20 {metrics['breadth_above_ma20']:.0%}, top-3 contribution {metrics['top3_return_contribution']:.0%}."
        )

    lines.append("")
    lines.append("## Leaders")
    lines.append("")
    lines.append("| Sector | Primary Leader | Score | 1D | 5D | Comment |")
    lines.append("|---|---|---:|---:|---:|---|")
    for sector in scored["sectors"]:
        leader = leader_map[sector["sector_code"]]
        primary = leader["primary_leader"]
        lines.append(
            f"| {sector['sector_name']} | {primary['name']} | {primary['score']:.1f} | {pct(primary['return_1d'])} | "
            f"{pct(primary['return_5d'])} | {leader['comment']} |"
        )

    lines.append("")
    lines.append("## Correlation")
    lines.append("")
    for pair in rotation["correlation_pairs"]:
        lines.append(
            f"- {pair['left_sector']} vs {pair['right_sector']}: correlation {pair['correlation']:.2f}, {pair['cluster']}."
        )

    lines.append("")
    lines.append("## Risk Flags")
    lines.append("")
    for sector in scored["sectors"]:
        flags = ", ".join(sector["risk_flags"]) if sector["risk_flags"] else "none"
        lines.append(f"- {sector['sector_name']}: {flags}.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build a daily A-share sector markdown note.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", help="Optional output markdown path.")
    args = parser.parse_args()

    payload = load_json(args.input)
    note = build_note(payload)
    if args.output:
        Path(args.output).write_text(note, encoding="utf-8")
    print(note)


if __name__ == "__main__":
    main()
