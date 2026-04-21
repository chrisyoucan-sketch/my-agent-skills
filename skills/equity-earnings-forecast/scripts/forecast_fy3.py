import argparse
import json
from pathlib import Path


def scenario_adjustment(scenario):
    default = {
        "base": {
            "growth_delta": 0.0,
            "gross_margin_delta": 0.0,
            "opex_ratio_delta": 0.0,
            "tax_rate_delta": 0.0,
        },
        "bull": {
            "growth_delta": 0.02,
            "gross_margin_delta": 0.01,
            "opex_ratio_delta": -0.005,
            "tax_rate_delta": -0.005,
        },
        "bear": {
            "growth_delta": -0.02,
            "gross_margin_delta": -0.01,
            "opex_ratio_delta": 0.005,
            "tax_rate_delta": 0.005,
        },
    }
    if scenario not in default:
        raise ValueError(f"Unsupported scenario: {scenario}")
    return default[scenario]


def fmt_pct(x):
    return f"{x * 100:.1f}%"


def build_growth_narrative(company_name, years, scenario):
    y1, y2, y3 = years
    text = []
    text.append(
        f"{company_name} 3-year FY forecast ({scenario}) assumes revenue growth of "
        f"{fmt_pct(y1['growth'])}/{fmt_pct(y2['growth'])}/{fmt_pct(y3['growth'])} in FY+1/FY+2/FY+3."
    )
    text.append(
        "Growth logic: FY+1 reflects near-term demand visibility and capacity release; "
        "FY+2 assumes normalization under a higher base; FY+3 converges toward mid-cycle growth."
    )
    text.append(
        "Key assumptions include volume growth, ASP trend, market-share/new-business contribution, "
        "cost curve and product-mix impact on gross margin, opex discipline, tax rate stability, and diluted shares."
    )
    return " ".join(text)


def compute_one_year(prev_revenue, year_assumption, adj):
    components = year_assumption.get("growth_components", {})
    volume = float(components.get("volume_growth", 0.0))
    price = float(components.get("price_growth", 0.0))
    share_newbiz = float(components.get("share_newbiz_contribution", 0.0))
    churn_headwind = float(components.get("churn_headwind", 0.0))
    growth = volume + price + share_newbiz - churn_headwind + adj["growth_delta"]

    revenue = prev_revenue * (1.0 + growth)

    gross_margin = float(year_assumption.get("gross_margin", 0.30)) + adj["gross_margin_delta"]
    gross_margin = max(0.0, min(0.95, gross_margin))

    sga_ratio = float(year_assumption.get("sga_ratio", 0.08))
    rnd_ratio = float(year_assumption.get("rnd_ratio", 0.08))
    other_opex_ratio = float(year_assumption.get("other_opex_ratio", 0.01))
    opex_ratio = sga_ratio + rnd_ratio + other_opex_ratio + adj["opex_ratio_delta"]
    opex_ratio = max(0.0, min(0.9, opex_ratio))

    gross_profit = revenue * gross_margin
    operating_profit = revenue * (gross_margin - opex_ratio)
    non_operating = float(year_assumption.get("non_operating", 0.0))
    pre_tax = operating_profit + non_operating

    tax_rate = float(year_assumption.get("tax_rate", 0.20)) + adj["tax_rate_delta"]
    tax_rate = max(0.0, min(0.5, tax_rate))
    tax = max(0.0, pre_tax * tax_rate)
    net_profit = pre_tax - tax

    shares = float(year_assumption.get("shares_diluted", 1.0))
    eps = net_profit / shares if shares else None

    cfo_margin = float(year_assumption.get("cfo_margin", 0.2))
    capex_ratio = float(year_assumption.get("capex_ratio", 0.08))
    fcf = revenue * cfo_margin - revenue * capex_ratio

    key_assumptions = {
        "growth_components": {
            "volume_growth": volume,
            "price_growth": price,
            "share_newbiz_contribution": share_newbiz,
            "churn_headwind": churn_headwind,
            "scenario_growth_delta": adj["growth_delta"],
        },
        "gross_margin": gross_margin,
        "opex_ratio": opex_ratio,
        "tax_rate": tax_rate,
        "shares_diluted": shares,
    }

    return {
        "growth": growth,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "operating_profit": operating_profit,
        "net_profit": net_profit,
        "eps_diluted": eps,
        "fcf": fcf,
        "key_assumptions": key_assumptions,
    }


def forecast_fy3(payload, scenario):
    company = payload.get("company", {})
    base = payload.get("base_year", {})
    base_revenue = float(base.get("revenue"))
    assumptions = payload.get("assumptions_by_year", [])

    if len(assumptions) != 3:
        raise ValueError("assumptions_by_year must contain exactly 3 years (FY+1/FY+2/FY+3).")

    adj = scenario_adjustment(scenario)
    results = []
    prev_revenue = base_revenue
    for row in assumptions:
        out = compute_one_year(prev_revenue, row, adj)
        results.append(
            {
                "year": row["year"],
                "growth": round(out["growth"], 6),
                "revenue": round(out["revenue"], 4),
                "gross_profit": round(out["gross_profit"], 4),
                "operating_profit": round(out["operating_profit"], 4),
                "net_profit": round(out["net_profit"], 4),
                "eps_diluted": round(out["eps_diluted"], 6) if out["eps_diluted"] is not None else None,
                "fcf": round(out["fcf"], 4),
                "key_assumptions": out["key_assumptions"],
            }
        )
        prev_revenue = out["revenue"]

    narrative = build_growth_narrative(company.get("name", "Company"), results, scenario)

    return {
        "company": company,
        "base_year": base,
        "scenario": scenario,
        "fy_forecast": results,
        "growth_logic_narrative": narrative,
        "note": payload.get("note", ""),
        "disclaimer": "For research analysis only. Not investment advice.",
    }


def main():
    parser = argparse.ArgumentParser(description="Build 3-year FY forecast and growth-logic narrative.")
    parser.add_argument("--input", required=True, help="Path to FY3 input JSON.")
    parser.add_argument("--scenario", default="base", choices=["base", "bull", "bear"])
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    result = forecast_fy3(payload, args.scenario)
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
