# Model Architecture

## Sheet Order

1. `Assumptions`
2. `Benchmarks`
3. `Revenue Build`
4. `Quarterly Model`
5. `Annual Model`
6. `Checks`

## Banking-Style Separation

- `Assumptions`: all editable hardcodes.
- `Benchmarks`: outside evidence and assumption support.
- `Revenue Build`: segment drivers, segment revenue, segment COGS, segment gross profit.
- `Quarterly Model`: company P&L by quarter.
- `Annual Model`: annual aggregation from quarterly sheet.
- `Checks`: mechanical integrity only.

## Formula Safety Rules

- One row, one concept.
- Break bridges into helper rows before the subtotal.
- Keep cross-sheet references simple.
- Use `IF(denominator=0,0,numerator/denominator)` for margins and per-share lines.
- Use `MAX(0, pre_tax * tax_rate)` for tax when the model assumes no tax shield carryforward.
- Never repeat the same business logic in both quarterly and annual sheets.

## Recommended Color Convention

- Blue font: editable inputs.
- Green font: cross-sheet links.
- Black font: calculation formulas.
- Dark fill header: section title.

## Minimum Checks

- Revenue build equals P&L revenue.
- Gross profit build equals P&L gross profit.
- Pre-tax bridge closes.
- Net income bridge closes.
- Annual revenue equals quarterly sum.
- Annual net income equals quarterly sum.
