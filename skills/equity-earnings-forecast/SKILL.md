---
name: equity-earnings-forecast
description: Build auditable quarterly/annual earnings forecasts for listed companies (A-share, H-share, US equities) using three baselines (consensus, guidance midpoint, historical trend), driver-based modeling, scenario analysis, and rolling backtests. Use when asked to estimate revenue, margins, net profit, EPS, or FCF; reconcile forecast deltas; validate assumptions against history; or produce investment-banking-style forecast notes with explicit evidence chains.
---

# Equity Earnings Forecast

## Overview

Deliver repeatable, explainable earnings forecasts with explicit formulas, source traceability, and historical validation.
Run a baseline-first workflow, then apply driver assumptions and scenario stress tests before publishing outputs.

## Workflow

1. Define target and output grain.
- Confirm market (`A/H/US`), ticker, forecast horizon (`quarterly` or `annual`), and segment granularity.
- Set required outputs: `Revenue`, `Gross Margin`, `Operating Profit`, `Net Profit`, `Diluted EPS`, `FCF`.

2. Collect and normalize data.
- Read [data-contracts.md](references/data-contracts.md) and map provider fields into the unified schema.
- Ingest: company filings/guidance, consensus snapshots, market/industry indicators, and historical financials.
- Preserve timestamped source metadata for each field.

3. Generate three baselines.
- Build `consensus baseline` from the latest broker-consensus snapshot.
- Build `guidance midpoint baseline` from company ranges (`(low + high) / 2`).
- Build `historical trend baseline` from seasonality + rolling trend.
- Apply fallback order when missing data: `consensus -> guidance -> historical trend`.

4. Build driver model and core forecast.
- Use volume-price decomposition by segment and cost/expense elasticities.
- Compute `Revenue -> Gross Profit -> Operating Profit -> Net Profit -> Diluted EPS -> FCF`.
- Isolate one-off items and FX impacts before finalizing normalized earnings.

5. Run scenarios.
- Build `Base`, `Bull`, `Bear` with explicit parameter deltas.
- Recalculate all outputs for each scenario.
- Report sensitivity to critical levers (price, volume, gross margin, opex ratio, tax rate).

6. Backtest and validate.
- Run rolling out-of-sample backtest over at least 8-12 historical quarters.
- Report `MAPE`, `RMSE`, direction accuracy, and interval coverage.
- Flag unstable parameters and revise assumptions only with evidence.

7. Publish auditable output.
- Return forecast table, assumptions table, variance bridge, and evidence chain.
- Include a non-advisory disclaimer: analytical research use only, not investment advice.

## Quality Gates

- Reject outputs lacking source timestamp, formula, or assumption rationale.
- Reject outputs where normalized earnings still contain one-off events.
- Reject outputs if scenario definitions are inconsistent across metrics.
- Reject outputs if backtest sample is below 8 quarters unless user explicitly waives it.

## Script Usage

Generate one-quarter forecast:

```bash
python scripts/forecast_quarter.py --input references/example_forecast_input.json --scenario base
```

Run rolling backtest:

```bash
python scripts/backtest_forecast.py --input references/example_backtest_input.json --lookback 8
```

Generate 3-year FY forecast with growth-logic narrative:

```bash
python scripts/forecast_fy3.py --input references/example_fy3_input_zjxc.json --scenario base
```

## References

- [methodology.md](references/methodology.md): Baselines, formula stack, and validation logic.
- [data-contracts.md](references/data-contracts.md): Unified schemas and provider field mapping template.
- [model-assumptions.md](references/model-assumptions.md): Scenario knobs, evidence-chain schema, and analyst checklist.
- [example_forecast_input.json](references/example_forecast_input.json): Example single-quarter input.
- [example_backtest_input.json](references/example_backtest_input.json): Example rolling-backtest input.
- [example_fy3_input_zjxc.json](references/example_fy3_input_zjxc.json): 3-year FY example input (ZJXC demo).
- [sample_output.md](references/sample_output.md): Example output table, assumptions, and sensitivity section.

## Output Standard

Return these sections in order:
1. Forecast table by metric and scenario.
2. Key assumptions with change-vs-prior snapshot.
3. Baseline selection and fallback notes.
4. Sensitivity summary.
5. Evidence chain rows (`metric`, `value`, `formula`, `source`, `timestamp`).
