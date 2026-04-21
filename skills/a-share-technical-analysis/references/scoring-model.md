# Scoring Model

Use this file for rules-based scoring and evidence thresholds.

## 1. Trend Score (30)

Award points based on stacked alignment, slope, and timeframe confirmation.

- `+10`: `close > ma20 > ma60 > ma120`
- `+6`: `ma20_slope > 0` and `ma60_slope > 0`
- `+6`: `daily_trend = up` and `weekly_trend = up`
- `+4`: `monthly_trend = up`
- `+4`: current stage is `uptrend` or `uptrend_pullback`

Subtract for weak alignment:

- `-10`: `close < ma20 < ma60 < ma120`
- `-6`: `ma20_slope < 0` and `ma60_slope < 0`
- `-6`: `daily_trend = down` and `weekly_trend = down`
- `-4`: `monthly_trend = down`
- `-4`: current stage is `downtrend`

Clamp the block score to `0-30`.

## 2. Volume-Price Score (20)

Positive signals:

- `+8`: breakout above `breakout_level` with `volume_ratio_5d >= 1.5`
- `+4`: price stays within roughly `2%` of `breakout_level` and `volume_ratio_20d >= 1.2`, which captures strong stocks preparing to break out
- `+5`: pullback toward `ma10` or `ma20` with `volume_ratio_5d <= 0.9`
- `+4`: rebound from `support_level` with volume expansion
- `+3`: `turnover_rate > turnover_rate_20d_avg` during upward close

Negative signals:

- `-8`: break below `support_level` with `volume_ratio_5d >= 1.5`
- `-5`: sharp gain with weak volume, defined as positive close and `volume_ratio_5d < 0.8`
- `-4`: failed push near resistance, defined as a weak close, a clear retreat away from the breakout area, and volume expansion
- `-3`: panic selloff, defined as negative close and `volume_ratio_5d >= 2.0`

Clamp the block score to `0-20`.

## 3. Indicator Confirmation Score (20)

Positive signals:

- `+6`: `macd_cross = golden` and `macd_hist > macd_hist_prev`
- `+5`: `macd_hist > 0` and increasing for two periods
- `+4`: `macd_hist > 0` and `macd_dif > macd_dea`, even if the golden cross happened earlier
- `+5`: `close > boll_mid`
- `+3`: price stays near or above the upper Bollinger band during an uptrend, which is treated as continuation rather than automatic exhaustion
- `+4`: bandwidth expansion after compression, defined as `boll_bandwidth_pct_20d_rank <= 0.2` and current bandwidth rising
- `+4`: `macd_divergence = bottom` with price stabilization near support

Negative signals:

- `-6`: `macd_cross = dead` and `macd_hist < macd_hist_prev`
- `-5`: `close < boll_mid`
- `-5`: rejection near `boll_upper` followed by weak close outside an uptrend
- `-4`: `macd_divergence = top` near resistance
- `-4`: price walks below lower band during a downtrend

Clamp the block score to `0-20`.

## 4. Pattern and Position Score (20)

Positive signals:

- `+8`: valid `W bottom` with neckline breakout and volume confirmation
- `+6`: bullish reversal candle at support
- `+5`: box breakout or triangle breakout with confirmation
- `+4`: strong close above prior `20d` high

Negative signals:

- `-8`: valid `M top` with neckline breakdown and volume confirmation
- `-6`: bearish reversal candle at resistance
- `-5`: failed breakout with rapid return to range
- `-4`: strong close below prior `20d` low

Clamp the block score to `0-20`.

## 5. Market Context Score (10)

Positive signals:

- `+4`: benchmark trend is `up`
- `+3`: industry trend is `up`
- `+2`: `relative_strength_vs_index_20d > 0`
- `+1`: `relative_strength_vs_industry_20d > 0`

Negative signals:

- `-4`: benchmark trend is `down`
- `-3`: industry trend is `down`
- `-2`: `relative_strength_vs_index_20d < 0`
- `-1`: `relative_strength_vs_industry_20d < 0`

Clamp the block score to `0-10`.

## Trading Bias Mapping

Use total score plus evidence hierarchy.

- `bullish`: total score `>= 70`, or total score `>= 55` with strong multi-timeframe uptrend plus positive relative strength, and no major bearish invalidation
- `watch`: mixed evidence, or a strong-trend setup that has not yet converted into a clean breakout
- `bearish`: major bearish invalidation, or low total score without a strong-trend override

## Trigger and Invalidation Rules

- `watch for breakout`: price closes above `breakout_level` with `volume_ratio_5d >= 1.5`
- `watch for low-risk pullback`: price holds `ma10` or `ma20` while volume contracts
- `reduce or avoid`: price loses `support_level` with volume expansion and `macd_cross = dead`
- `invalidation`: always use the nearest structural failure level, not a generic percentage stop
