# Font Fallback Rules

## Goal

Prevent missing-font substitution, garbled glyphs, and unstable text reflow on Windows playback and editing environments.

## Safe Chinese-First Chains

Prefer one of these chains:

1. `Microsoft YaHei -> DengXian -> SimSun`
2. `Source Han Sans SC -> Microsoft YaHei -> DengXian`
3. `PingFang SC -> Microsoft YaHei -> DengXian`

If cross-machine portability matters, prefer the first chain because it depends on common Windows fonts.

## Safe Latin Chains

Prefer one of these chains:

1. `Aptos -> Calibri -> Arial`
2. `Segoe UI -> Calibri -> Arial`
3. `Arial -> Helvetica -> sans-serif`

## Mixing Rules

- Avoid decorative display fonts for dense business slides.
- Avoid mixing too many families on one slide.
- Check punctuation and full-width versus half-width characters when mixing Chinese and English.
- Replace unusual symbols with common Unicode alternatives when a corporate font is unlikely to support them.

## Garbled Text Prevention

- Avoid icon fonts unless you control the full editing environment.
- Prefer native shapes or embedded SVG for icons.
- Normalize quotes, dashes, and bullets if text comes from varied sources.
- If a font is unavailable, switch to a safe fallback before final placement because text metrics may change.
