# Output Template

Use this fixed order.

## 0. Chart

- Always output one daily technical chart first for full diagnoses.
- The default chart must include:
  - candlesticks
  - MA `5/10/20/30/60/120/250`
  - volume panel
  - MACD `12/26/9` panel
  - support and resistance annotations
- Keep Bollinger Bands available as an overlay when they materially help explain compression, expansion, or band behavior.

## 1. Technical Conclusion

- `Conclusion`: `bullish`, `watch`, or `bearish`
- `Total Score`: integer out of 100
- `Score Breakdown`: trend, volume-price, indicator confirmation, pattern-position, market context

## 2. Multi-Timeframe Trend Summary

- `Monthly`: long-term direction and 120/250 MA read
- `Weekly`: mid-term direction and 60 MA read
- `Daily`: short-term structure and 5/10/20/30 MA read
- `Stage`: one of the five stage labels

## 3. Volume-Price and Indicator Review

- Summarize price-volume behavior in one short paragraph.
- Summarize MACD and Bollinger evidence in one short paragraph.
- State whether divergence exists and whether it is confirmed or only a warning.

## 4. Pattern and Key Levels

- Report only valid patterns.
- List:
  - `Support`
  - `Resistance`
  - `Breakout Trigger`
  - `Invalidation`

## 5. Trading Framework

- `Bias`: bullish, watch, or bearish
- `Trigger Conditions`: what must happen to turn more positive or more negative
- `Risk Flags`: failed breakout, trend mismatch, weak market context, overextended from moving averages, or missing confirmation

## Style Rules

- Keep the analysis explainable and auditable.
- Use exact indicator defaults.
- When the environment supports images, embed the generated chart with its local path before the text analysis.
- Do not give position size guidance.
- Do not use absolute wording such as "must rise" or "guaranteed reversal".
- When rendering a Chinese report, prefer concise paragraphs or flat bullets under the same section order.
