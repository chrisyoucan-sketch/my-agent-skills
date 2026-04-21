# Indicator Definitions

## Performance

- `excess_return_vs_all_a_Xd = sector_return_Xd - benchmark_return_Xd`
- required windows: `1D`, `5D`, `20D`

## Capital Flow

- `flow_intensity_1d = main_force_net_inflow_1d / turnover_value`
- `flow_intensity_5d = main_force_net_inflow_5d / max(sum(turnover over 5d proxy), turnover_value * 5)`
- v1 proxy uses `turnover_value * window` when rolling turnover is not supplied

## Technical

- moving-average alignment uses 5, 10, 20, 60-day averages where history is available
- `volume_ratio = latest volume / average(volume[-5:])`
- `bollinger_position = (last_close - mid_band) / (2 * std20)` with a zero guard
- `macd_state` is derived from 12/26 EMA difference versus 9 EMA signal

## Breadth

- `breadth_above_ma20 = count(above_ma20) / valid_constituents`
- `breadth_above_ma60 = count(above_ma60) / valid_constituents`
- `up_stock_ratio = count(return_1d > 0) / valid_constituents`
- `new_20d_high_ratio = count(new_20d_high) / valid_constituents`

## Concentration

- `top3_return_contribution = sum(top 3 contribution_to_sector_return values)`
- concentration warning triggers when top-3 contribution exceeds 60 percent of absolute contribution mass

## Leader Score

Normalize and combine:

- turnover value
- 1D return
- 5D return
- 20D return
- main-force net inflow
- volume ratio
- limit-up flag
- contribution to sector return

Recommended v1 weights:

- turnover: `20%`
- return_1d: `10%`
- return_5d: `20%`
- return_20d: `20%`
- flow: `15%`
- volume ratio: `5%`
- limit_up: `5%`
- contribution: `5%`

## Sector Composite Score

Normalize every sub-score to `0-100`.
Recommended v1 weights:

- capital flow: `30%`
- trend / technical: `25%`
- breadth / diffusion: `20%`
- leader strength: `15%`
- catalyst: `10%`

## Confidence

Start from `1.0` and subtract:

- `0.15` if sector flow uses stock aggregation fallback
- `0.20` if flow uses a non-main-force proxy
- `0.10` if fewer than 5 constituents are available
- `0.10` if catalysts are missing

Clamp the result to `0.0-1.0`.
