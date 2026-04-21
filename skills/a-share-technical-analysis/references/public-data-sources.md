# Public Data Sources

Use this file when fetching live data for the skill.

## Primary Source

- `AKShare`

Validated public endpoints for this skill:

- Stock history: `stock_zh_a_hist`
- Stock history fallback: `stock_zh_a_daily`
- Stock profile: `stock_individual_info_em`
- Benchmark index fallback: `stock_zh_index_daily`

## Benchmark Mapping

- Main board: `sh000001` for `SSE Composite`
- ChiNext: `sz399006` for `ChiNext Index`
- STAR Market: `sh000688` for `STAR 50 Index`

## Frequency Rules

- Stock bars:
  - `daily`: fetch directly
  - `weekly`: fetch directly
  - `monthly`: fetch directly
- Benchmark bars:
  - fetch daily and derive trend state from the last 20 sessions

## Caveats

- Public endpoints can be less stable than paid terminals.
- `stock_zh_a_hist` can fail behind some VPN or system-proxy paths, especially when the route to `push2his.eastmoney.com` is unstable. The skill should retry it first, then fall back to `stock_zh_a_daily` and derive weekly/monthly bars locally.
- Industry-board history was not reliable in validation. Treat industry trend as optional unless the endpoint is known to work in the current environment.
- When industry trend is unavailable, continue with:
  - stock-level industry name if present
  - benchmark trend
  - stock relative strength versus benchmark

## Dependency Note

The live-fetch workflow requires local Python packages:

```bash
python -m pip install akshare pandas matplotlib mplfinance
```
