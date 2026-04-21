---
name: a-share-technical-analysis
description: Diagnose a single A-share stock with rules-based technical analysis using public online market data, with AKShare as the primary fetch layer. Use when asked to review one stock's trend, moving averages, volume-price behavior, MACD, Bollinger Bands, market context, divergence, classic candlestick or chart patterns, daily/weekly/monthly alignment, buy-sell trigger levels, or a technical score with trading bias.
---

# A-Share Technical Analysis

## Overview

Deliver repeatable technical diagnostics for one A-share stock with explicit rules, fixed indicator defaults, auditable scoring, and a default annotated chart.
Use daily bars as the main analysis frame, then use weekly and monthly bars as direction filters before publishing a chart, score, trading bias, trigger levels, and invalidation levels.

## Workflow

1. Define scope.
- This skill is for one stock at a time.
- Prioritize outputs in this order: `technical diagnosis`, `daily review`, `stock selection`, `buy-sell trigger`.
- Default bar set: `daily` primary, `weekly` and `monthly` confirmation. Do not use intraday bars unless the user explicitly overrides the scope.

2. Fetch and normalize public data.
- Use `AKShare` as the primary public-data layer. Read [references/public-data-sources.md](references/public-data-sources.md) before changing interfaces.
- Prefer live fetch over manual export.
- Fetch:
  - stock `daily`, `weekly`, `monthly` bars
  - benchmark index daily bars
  - stock profile fields such as name and industry when available
- Map fetched data into the unified schema in [references/data-contracts.md](references/data-contracts.md).
- Keep all moving-average and indicator defaults fixed:
  - `MA`: `5, 10, 20, 30, 60, 120, 250`
  - `MACD`: `12, 26, 9`
  - `Bollinger`: `20, 2`
- Include market context for:
  - Main-board stocks: `SSE Composite`
  - ChiNext stocks: `ChiNext Index`
  - STAR Market stocks: `STAR 50 Index`
- Try to fetch industry name from public profile data. If public industry-trend data is unavailable, keep the industry name, downgrade confidence, and continue with index-level market context.
- For full diagnoses, also generate one default `daily` chart image before writing the narrative:
  - candlesticks
  - `MA 5/10/20/30/60/120/250`
  - `volume`
  - `MACD 12/26/9`
  - support and resistance annotations
  - optional Bollinger overlay when it improves the explanation

3. Classify trend and stage first.
- Determine `long-term`, `mid-term`, and `short-term` trend before reading entry signals.
- Use:
  - `120/250 MA` and monthly direction for long-term trend
  - `60 MA` and weekly direction for mid-term trend
  - `5/10/20/30 MA` plus daily structure for short-term trend
- Assign one stage only: `uptrend`, `uptrend pullback`, `range`, `rebound in downtrend`, or `downtrend`.

4. Validate price-volume structure.
- Judge whether price action is confirmed by turnover and volume.
- Apply the volume-price rules from [references/scoring-model.md](references/scoring-model.md) for:
  - `volume breakout`
  - `low-volume pullback`
  - `volume exhaustion`
  - `panic selloff`
  - `low-volume stabilization`

5. Check indicator confirmation.
- Use `MACD` and `Bollinger Bands` as core indicator evidence.
- Look for:
  - trend continuation
  - compression and expansion
  - top or bottom divergence
  - price versus middle band behavior
- Do not use divergence alone as a buy or sell conclusion. Treat it as a warning unless price structure and volume confirm.

6. Identify patterns.
- Read [references/pattern-rules.md](references/pattern-rules.md) and classify findings as:
  - `single-candle`
  - `multi-candle`
  - `structural pattern`
- Only report a pattern when the rule set is met. Do not force a name onto noisy price action.

7. Score and conclude.
- Score the stock with the five-block model in [references/scoring-model.md](references/scoring-model.md):
  - `Trend` 30
  - `Volume-Price` 20
  - `Indicator Confirmation` 20
  - `Pattern and Position` 20
  - `Market Context` 10
- Return both:
  - total score on a `100-point` scale
  - sub-scores by block
- Map the total score to:
  - `80-100`: strong
  - `60-79`: moderately strong
  - `40-59`: neutral
  - `20-39`: weak
  - `0-19`: avoid

8. Publish the output in a fixed order.
- Follow [references/output-template.md](references/output-template.md).
- Put the chart first. In environments that support image rendering, embed the local chart file path directly above the write-up.
- Always include:
  - chart path or rendered image
  - technical conclusion
  - score and sub-scores
  - trend summary
  - key levels
  - trigger conditions
  - invalidation level
  - risk flags
- Trading language should stay at `bullish`, `watch`, or `bearish`. Do not provide position sizing.

## Quality Gates

- Reject outputs when daily history is too short to compute `250 MA`.
- Reject full-diagnosis outputs that skip the default chart unless the user explicitly asks for text only.
- Flag outputs when market-context data is missing and downgrade confidence.
- Flag outputs when industry trend is unavailable from public sources and mark the market-context block as partial rather than complete.
- Reject claims of divergence, `M top`, `W bottom`, `head and shoulders`, or breakout confirmation unless the required price and volume conditions are present.
- Reject outputs that skip weekly or monthly confirmation when the user asked for a full diagnosis.
- Reject strong buy-sell wording when the evidence only comes from one indicator.

## References

- [references/public-data-sources.md](references/public-data-sources.md): AKShare endpoints, benchmark mapping, and public-data caveats.
- [references/data-contracts.md](references/data-contracts.md): Unified normalized schema after public fetching.
- [references/scoring-model.md](references/scoring-model.md): Trend, volume-price, indicator, pattern, and market-context scoring rules.
- [references/pattern-rules.md](references/pattern-rules.md): Explicit rules for candlestick and structural patterns.
- [references/output-template.md](references/output-template.md): Fixed response structure.
- [references/example_input.json](references/example_input.json): Example normalized payload.
- [references/sample_output.md](references/sample_output.md): Example finished write-up.

## Script Usage

Fetch live public data, normalize it, score it, and print JSON:

```bash
python scripts/fetch_and_score_stock.py --symbol 600519
```

Fetch live public data and print a Chinese technical diagnosis report:

```bash
python scripts/fetch_and_score_stock.py --symbol 600519 --report
```

Score a normalized payload and print JSON:

```bash
python scripts/score_stock.py --input references/example_input.json
```

Plot the default full technical chart with moving averages, volume, MACD, and annotated key levels:

```bash
python scripts/plot_stock_chart.py --symbol 601877 --period daily
```

Plot the default chart with Bollinger Bands overlaid on the price panel:

```bash
python scripts/plot_stock_chart.py --symbol 601877 --period daily --show-boll
```

Print a Chinese report and generate the default chart in the current directory:

```bash
python scripts/fetch_and_score_stock.py --symbol 600519 --report
```

## Output Standard

Return these sections in order:

1. Chart.
2. Technical conclusion and score.
3. Multi-timeframe trend summary.
4. Volume-price and indicator confirmation.
5. Pattern and key-level review.
6. Trading triggers, invalidation level, and risk flags.
