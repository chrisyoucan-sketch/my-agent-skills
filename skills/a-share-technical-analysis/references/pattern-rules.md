# Pattern Rules

Only report a pattern when its rule set is met.

## Single-Candle Signals

### Doji

- Open and close are close enough that the real body is very small.
- Report as meaningful only when it appears after a directional move.
- `low-volume doji` is notable when volume is below the 5-day average by at least 10 percent.

### Hammer

- Small real body near the high of the session.
- Lower shadow is at least twice the real body.
- Best treated as bullish only when it appears near support or after a decline.

### Hanging Man

- Same candle shape as a hammer.
- Only bearish when it appears after an advance and is followed by a weak confirmation candle.

### Bullish Engulfing

- A bullish candle fully engulfs the prior bearish real body.
- Stronger when it appears at support with expanding volume.

### Bearish Engulfing

- A bearish candle fully engulfs the prior bullish real body.
- Stronger when it appears at resistance with expanding volume.

## Multi-Candle Signals

### Morning Star

- Down move first.
- Small middle candle showing loss of downside momentum.
- Third candle closes deeply into the first candle body.

### Evening Star

- Up move first.
- Small middle candle showing loss of upside momentum.
- Third candle closes deeply into the first candle body.

### Three White Soldiers

- Three consecutive bullish candles.
- Each closes near its high and opens within the prior body.
- Stronger when volume does not shrink materially.

### Dark Cloud Cover

- Up move first.
- Bearish candle opens above prior high or close and closes into the prior bullish body.

## Structural Patterns

### W Bottom

- Two clear reaction lows separated by a rebound.
- Second low is near the first low, with tolerable deviation rather than a random retest.
- Neckline is the rebound high between the two lows.
- Confirm only after price closes above the neckline.
- Confirmation is stronger when `volume_ratio_5d >= 1.3`.

### M Top

- Two clear reaction highs separated by a pullback.
- Second high is near the first high.
- Neckline is the pullback low between the two highs.
- Confirm only after price closes below the neckline.
- Confirmation is stronger when the breakdown is accompanied by volume expansion.

### Head and Shoulders Top

- Left shoulder, higher head, lower right shoulder.
- Neckline may slope, but breakdown must be a real close below it.
- Volume should contract into the right shoulder and expand on the breakdown.

### Head and Shoulders Bottom

- Inverse structure of the top pattern.
- Confirmation requires a close above the neckline.

### Box Range

- At least two failed attempts near resistance and two near support.
- Use the box only when the boundaries are visually and structurally clear.

### Triangle

- Converging highs and lows over several swings.
- Confirmation requires a close beyond the trendline boundary.
- Volume often contracts before the breakout.

## Divergence Rules

- `top divergence`: price makes a higher high while MACD momentum fails to confirm and the second push occurs near resistance.
- `bottom divergence`: price makes a lower low while MACD momentum fails to confirm and the second push occurs near support.
- Divergence is a warning, not a standalone trade signal.
- Prefer divergence that spans meaningful swing points rather than adjacent noisy bars.
