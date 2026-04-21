import math
from statistics import mean


def midpoint(low, high):
    if low is None and high is None:
        return None
    if low is None:
        return high
    if high is None:
        return low
    return (low + high) / 2.0


def historical_revenue_baseline(history):
    if not history:
        return None
    revs = [row["revenue"] for row in history if row.get("revenue") is not None]
    if not revs:
        return None
    if len(revs) == 1:
        return revs[-1]
    trend = mean(revs[-min(4, len(revs)):])
    seasonality = revs[-1]
    return 0.6 * seasonality + 0.4 * trend


def select_baseline(data):
    consensus = (data.get("consensus") or {}).get("revenue")
    guidance = data.get("guidance") or {}
    guidance_mid = midpoint(guidance.get("revenue_low"), guidance.get("revenue_high"))
    hist = historical_revenue_baseline(data.get("history") or [])

    if consensus is not None:
        return "consensus", consensus
    if guidance_mid is not None:
        return "guidance_midpoint", guidance_mid
    if hist is not None:
        return "historical_trend", hist
    raise ValueError("No baseline available: consensus/guidance/history all missing.")


def compute_driver_revenue(segments):
    if not segments:
        raise ValueError("segments are required for driver model.")
    rev = 0.0
    for seg in segments:
        volume = float(seg.get("volume", 0.0))
        price = float(seg.get("price", 0.0))
        rev += volume * price
    return rev


def scenario_multipliers(scenario):
    default = {
        "base": {"volume": 1.00, "price": 1.00, "cogs_ratio_delta": 0.0, "opex_ratio_delta": 0.0},
        "bull": {"volume": 1.05, "price": 1.02, "cogs_ratio_delta": -0.01, "opex_ratio_delta": -0.005},
        "bear": {"volume": 0.95, "price": 0.98, "cogs_ratio_delta": 0.01, "opex_ratio_delta": 0.005},
    }
    if scenario not in default:
        raise ValueError(f"Unsupported scenario: {scenario}")
    return default[scenario]


def forecast_from_data(data, scenario="base"):
    segments = data.get("segments") or []
    opex = data.get("opex") or {}
    non_op = (data.get("non_operating") or {}).get("amount", 0.0)
    tax_rate = float(data.get("tax_rate", 0.2))
    shares = float(data.get("shares_diluted", 1.0))
    cfo = float(data.get("cfo", 0.0))
    capex = float(data.get("capex", 0.0))

    baseline_source, baseline_revenue = select_baseline(data)
    mult = scenario_multipliers(scenario)

    adj_segments = []
    for seg in segments:
        c = dict(seg)
        c["volume"] = float(c.get("volume", 0.0)) * mult["volume"]
        c["price"] = float(c.get("price", 0.0)) * mult["price"]
        c["cogs_ratio"] = float(c.get("cogs_ratio", 0.0)) + mult["cogs_ratio_delta"]
        adj_segments.append(c)

    driver_revenue = compute_driver_revenue(adj_segments)
    revenue = 0.5 * baseline_revenue + 0.5 * driver_revenue

    weighted_cogs_ratio = mean([max(0.0, min(1.0, s.get("cogs_ratio", 0.0))) for s in adj_segments]) if adj_segments else 0.0
    cogs = revenue * weighted_cogs_ratio
    gross_profit = revenue - cogs

    sga_ratio = float(opex.get("sga_ratio", 0.0)) + mult["opex_ratio_delta"]
    rnd_ratio = float(opex.get("rnd_ratio", 0.0))
    other_ratio = float(opex.get("other_opex_ratio", 0.0))
    sga = revenue * max(0.0, sga_ratio)
    rnd = revenue * max(0.0, rnd_ratio)
    other_opex = revenue * max(0.0, other_ratio)

    operating_profit = gross_profit - sga - rnd - other_opex
    pre_tax_profit = operating_profit + float(non_op)
    tax = max(0.0, pre_tax_profit * tax_rate)
    net_profit = pre_tax_profit - tax
    eps = net_profit / shares if shares else math.nan
    fcf = cfo - capex

    evidence_chain = [
        {
            "metric": "revenue",
            "value": round(revenue, 4),
            "formula": "0.5*baseline_revenue + 0.5*sum(volume*price)",
            "source": baseline_source + " + segment_driver",
            "timestamp": (data.get("consensus") or {}).get("timestamp")
            or (data.get("guidance") or {}).get("timestamp")
            or "n/a",
        },
        {
            "metric": "net_profit",
            "value": round(net_profit, 4),
            "formula": "(revenue-cogs-sga-rnd-other_opex+non_operating)-tax",
            "source": "computed",
            "timestamp": "computed",
        },
        {
            "metric": "eps_diluted",
            "value": round(eps, 6),
            "formula": "net_profit / shares_diluted",
            "source": "computed",
            "timestamp": "computed",
        },
    ]

    return {
        "company": data.get("company", {}),
        "target_period": data.get("target_period"),
        "scenario": scenario,
        "baseline_source": baseline_source,
        "baseline_revenue": round(baseline_revenue, 4),
        "forecast": {
            "revenue": round(revenue, 4),
            "gross_profit": round(gross_profit, 4),
            "operating_profit": round(operating_profit, 4),
            "net_profit": round(net_profit, 4),
            "eps_diluted": round(eps, 6),
            "fcf": round(fcf, 4),
        },
        "assumptions": {
            "scenario_multipliers": mult,
            "tax_rate": tax_rate,
            "shares_diluted": shares,
        },
        "evidence_chain": evidence_chain,
        "disclaimer": "For research analysis only. Not investment advice.",
    }


def mape(actual, pred):
    if actual == 0:
        return None
    return abs((actual - pred) / actual)
