# Earnings Forecast Methodology

## Baseline Framework

Build three baseline estimates for the target quarter:

1. Consensus baseline
- Source latest consensus snapshot.
- Use provider timestamp and estimate count.

2. Guidance midpoint baseline
- For each guided metric: midpoint = `(low + high) / 2`.
- If only one bound exists, use the bound and mark confidence as reduced.

3. Historical trend baseline
- Build quarterly seasonality ratio from prior same-quarter values.
- Build rolling trend from latest 4 quarters where available.
- Blend seasonality and trend at `60/40` default weight.

Fallback order:
- Use `consensus -> guidance midpoint -> historical trend`.
- If all are unavailable, return `insufficient data` instead of fabricating values.

## Core Formula Stack

- `Revenue = Σ(segment_volume × segment_price)`
- `Gross Profit = Revenue - COGS`
- `Gross Margin = Gross Profit / Revenue`
- `Operating Profit = Gross Profit - SG&A - R&D - Other Opex`
- `Pre-tax Profit = Operating Profit + Non-operating Items`
- `Net Profit = Pre-tax Profit - Tax`
- `Diluted EPS = Net Profit Attributable / Weighted Avg Diluted Shares`
- `FCF = CFO - Capex`

Derived views:
- `YoY`, `QoQ`, `TTM`, and annualized views.
- FX split: local-currency growth vs translation impact.
- One-off adjustment: separate normalized and reported earnings.

## Scenario Design

Set three scenarios with transparent deltas:

- Base: management-consistent trajectory.
- Bull: positive assumptions on price/volume/margin.
- Bear: conservative assumptions on demand/margin/cost.

Apply scenario deltas to these levers:
- Volume growth.
- Price growth.
- COGS ratio.
- Opex ratio.
- Effective tax rate.

## 3-Year FY Forecast Logic

Build annual forecasts as a chained model from base-year actuals:

- `Revenue_t = Revenue_(t-1) * (1 + Growth_t)`
- `Growth_t = Volume_Growth_t + Price_Growth_t + Share/New_Biz_Contribution_t - Churn/Headwind_t`
- `Gross_Profit_t = Revenue_t * Gross_Margin_t`
- `Operating_Profit_t = Gross_Profit_t - Revenue_t * (SG&A_t + R&D_t + Other_Opex_t)`
- `PreTax_t = Operating_Profit_t + NonOperating_t`
- `Net_Profit_t = PreTax_t - max(0, PreTax_t * Tax_Rate_t)`
- `EPS_t = Net_Profit_t / Diluted_Shares_t`

Annual forecasting discipline:
- Set FY+1 to reflect cycle and order visibility.
- Set FY+2 as transition toward normalized growth.
- Set FY+3 converging to long-term mid-cycle growth.

## Validation and Backtest

Use rolling out-of-sample backtest:
- Minimum window: 8 quarters (12 preferred).
- For each target quarter, train from preceding history only.

Track metrics:
- `MAPE`
- `RMSE`
- `Direction Accuracy` on YoY growth sign
- `Interval Coverage` for forecast confidence band

Report instability flags:
- Persistent directional miss.
- Error concentration around known shocks.
- Overly narrow intervals with low coverage.

## Capability Tiers

MVP:
- Single-company, single-quarter forecast.
- Three baselines with deterministic fallback.
- Base/Bull/Bear scenarios.
- Rolling backtest on revenue with MAPE/RMSE/direction/coverage.
- Evidence chain on core metrics.

Pro:
- Multi-company batch forecasting and cross-sectional comparison.
- Segment-level covariance and macro-linked dynamic elasticities.
- Explicit FX bridge, one-off normalization library, and analyst override governance.
- Probabilistic forecast intervals calibrated from historical residuals.
- Automated data-quality scoring and provider conflict resolution.
