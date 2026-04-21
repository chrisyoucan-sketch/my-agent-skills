# Model Assumptions and Evidence Chain

## Assumption Hierarchy

Apply assumptions in this order:

1. Hard evidence
- Filed financial statements.
- Official company guidance.

2. Market evidence
- Consensus snapshots with sufficient analyst coverage.

3. Statistical evidence
- Historical trend and seasonality estimates.

4. Analyst judgment
- Explicit, bounded overrides with rationale.

## Baseline Selection Rules

- Prefer consensus when estimate count and recency are acceptable.
- Prefer guidance midpoint when consensus is stale or sparse.
- Use historical trend when both are missing.
- Document fallback path in output.

## Scenario Parameter Defaults

- Base: no adjustment (`1.00` multipliers).
- Bull: volume `+5%`, price `+2%`, cogs ratio `-1pp`, opex ratio `-0.5pp`.
- Bear: volume `-5%`, price `-2%`, cogs ratio `+1pp`, opex ratio `+0.5pp`.

Adjust by sector and company cycle.

## Evidence Chain Row Format

Output one row per metric:

| metric | value | formula | source | timestamp | assumption_note |
|---|---|---|---|---|---|
| revenue_base | 123.4 | sum(volume*price) | consensus + segment model | 2026-03-01 | blended baseline |

## Analyst Checklist

- Confirm accounting policy consistency vs history.
- Separate one-off items from normalized earnings.
- Confirm share count assumptions for diluted EPS.
- Check tax-rate logic against jurisdiction mix.
- Reconcile top-down macro view with bottom-up segment model.
