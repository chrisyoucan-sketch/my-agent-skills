# Data Contracts

Use this file when mapping public online data into the skill's normalized schema.

## Required Fields

Top-level fields:

- `ticker`: Exchange ticker such as `600519.SH`, `300750.SZ`, `688981.SH`
- `name`: Stock name
- `market_board`: One of `main`, `chinext`, `star`
- `provider`: `akshare` or another public-source wrapper
- `as_of_date`: Analysis date in `YYYY-MM-DD`
- `daily_bars_count`: Integer history length

Price state fields:

- `close`
- `prev_close`
- `high_20d`
- `low_20d`
- `high_60d`
- `low_60d`
- `gap_type`: `none`, `common_up`, `breakaway_up`, `common_down`, `breakaway_down`, `exhaustion_up`, `exhaustion_down`

Moving-average fields:

- `ma5`
- `ma10`
- `ma20`
- `ma30`
- `ma60`
- `ma120`
- `ma250`
- `ma5_slope`
- `ma10_slope`
- `ma20_slope`
- `ma30_slope`
- `ma60_slope`
- `ma120_slope`
- `ma250_slope`

Volume and turnover fields:

- `volume`
- `volume_ratio_5d`
- `volume_ratio_20d`
- `turnover_rate`
- `turnover_rate_20d_avg`

MACD fields:

- `macd_dif`
- `macd_dea`
- `macd_hist`
- `macd_hist_prev`
- `macd_cross`: `golden`, `dead`, `none`
- `macd_divergence`: `top`, `bottom`, `none`

Bollinger fields:

- `boll_mid`
- `boll_upper`
- `boll_lower`
- `boll_bandwidth_pct`
- `boll_bandwidth_pct_20d_rank`

Pattern fields:

- `candlestick_signals`: Array of names from [pattern-rules.md](pattern-rules.md)
- `structure_signals`: Array of names from [pattern-rules.md](pattern-rules.md)

Market-context fields:

- `benchmark_index`: `sse`, `chinext`, or `star50`
- `benchmark_trend`: `up`, `range`, `down`
- `industry_name`
- `industry_trend`: `up`, `range`, `down`
- `relative_strength_vs_index_20d`
- `relative_strength_vs_industry_20d`

Multi-timeframe summary fields:

- `daily_trend`: `up`, `range`, `down`
- `weekly_trend`: `up`, `range`, `down`
- `monthly_trend`: `up`, `range`, `down`
- `stage`: `uptrend`, `uptrend_pullback`, `range`, `rebound_in_downtrend`, `downtrend`

Key levels:

- `support_level`
- `resistance_level`
- `breakout_level`
- `invalidation_level`

## Public Source Mapping Notes

AKShare:

- `stock_zh_a_hist` is the primary stock history source for `daily`, `weekly`, and `monthly`.
- `stock_zh_index_daily` is the preferred benchmark-index fallback because it worked in live validation for `sh000001` and `sh000688`.
- `stock_individual_info_em` can provide stock name and industry label.
- Some public industry-board endpoints may fail or change. When that happens:
  - keep `industry_name` if available
  - set `industry_trend` conservatively
  - flag the market-context block as partial

Adjusted prices:

- Prefer forward-adjusted prices when available.
- Use the same adjustment rule across daily, weekly, and monthly stock bars.

## Minimum History Rules

- Full diagnosis requires at least `250` daily bars.
- A reduced-confidence diagnosis may run with `120-249` daily bars, but long-term trend must be marked as limited.
- Reject outputs with fewer than `60` daily bars.
