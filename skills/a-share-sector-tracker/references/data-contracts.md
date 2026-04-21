# Data Contracts

## Top-Level Input Schema

```json
{
  "date": "2026-03-06",
  "provider": "Wind",
  "benchmark": {
    "name": "All A",
    "return_1d": 0.012,
    "return_5d": 0.031,
    "return_20d": 0.084
  },
  "sectors": []
}
```

## Required Top-Level Fields

| Field | Type | Notes |
|---|---|---|
| `date` | string | ISO date |
| `provider` | string | v1 expects `Wind` |
| `benchmark.name` | string | use `All A` by default |
| `benchmark.return_1d` | number | decimal return |
| `benchmark.return_5d` | number | decimal return |
| `benchmark.return_20d` | number | decimal return |
| `sectors` | array | one row per board |

## Required Sector Fields

| Field | Type | Notes |
|---|---|---|
| `sector_code` | string | provider or internal code |
| `sector_name` | string | display name |
| `taxonomy` | string | `industry` or `concept` |
| `board_source` | string | source taxonomy identifier |
| `return_1d` | number | decimal return |
| `return_5d` | number | decimal return |
| `return_20d` | number | decimal return |
| `turnover_value` | number | daily turnover value |
| `main_force_net_inflow_1d` | number | daily main-force net inflow |
| `main_force_net_inflow_5d` | number | rolling 5-day main-force net inflow |
| `main_force_net_inflow_20d` | number | rolling 20-day main-force net inflow |
| `close_history` | array[number] | at least 20 daily closes |
| `volume_history` | array[number] | aligned with close history |
| `daily_returns_history` | array[number] | at least 20 daily returns |
| `constituents` | array | at least 3 valid stocks for leader analysis |

## Optional Sector Fields

| Field | Type | Notes |
|---|---|---|
| `catalysts` | array | optional event tags |
| `risk_flags` | array[string] | optional pre-tagged risks |
| `sector_level_flow_source` | string | disclose if aggregated from stocks |
| `turnover_share_of_market` | number | decimal share |

## Required Constituent Fields

| Field | Type | Notes |
|---|---|---|
| `ticker` | string | stock identifier |
| `name` | string | stock name |
| `return_1d` | number | decimal return |
| `return_5d` | number | decimal return |
| `return_20d` | number | decimal return |
| `turnover_value` | number | daily turnover value |
| `main_force_net_inflow_1d` | number | daily main-force net inflow |
| `volume_ratio` | number | daily volume divided by 5-day average |
| `is_limit_up` | boolean | limit-up flag |
| `above_ma20` | boolean | breadth input |
| `above_ma60` | boolean | breadth input |
| `new_20d_high` | boolean | breadth input |
| `contribution_to_sector_return` | number | additive contribution proxy |

## Units

- returns use decimals, not percentages
- turnover and flow use the same currency units within one run
- ratios use decimals unless the field explicitly says percentile or score

## Fallback Disclosure

If a field is missing and derived from a fallback:

- keep the derived value
- add a note in `flow_source` or `risk_flags`
- lower `confidence`
