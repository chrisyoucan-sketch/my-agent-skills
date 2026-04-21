---
name: ib-excel-financial-model
description: Build investment-banking-style Excel financial models with driver-based revenue and cost decomposition, benchmark-backed assumptions, quarterly and annual forecasts, and formula-linked workbooks that update automatically when assumptions change.
---

# IB Excel Financial Model

Use this skill when the user needs a financial model in Excel rather than only a written forecast.
The target output is a formula-driven workbook with clean sheet separation, editable assumptions,
quarterly and annual views, benchmark evidence, and checks that catch broken links or bad bridges.

## Deliverable Standard

Produce a workbook with these sheets:

1. `Assumptions`
2. `Benchmarks`
3. `Revenue Build`
4. `Quarterly Model`
5. `Annual Model`
6. `Checks`

The workbook must follow these rules:

- Hardcodes live in `Assumptions` only.
- External support and rationale live in `Benchmarks`.
- Revenue and cost logic are built in helper rows before they roll into the P&L.
- Output sheets should mostly link or aggregate, not hide logic inside nested formulas.
- Every major subtotal should have at least one check row.

## Workflow

1. Define the business model and output grain.
- Confirm company, currency, units, history period, forecast period, and whether the model is segment-level.
- Decide the revenue archetype for each segment using [business-driver-playbook.md](references/business-driver-playbook.md).

2. Identify the key business drivers.
- Break revenue into the smallest defensible operating drivers.
- Break cost into either `gross_margin`, `cogs_ratio`, or `unit_cost`.
- Keep operating expenses separate at company level unless the user explicitly needs segment opex.

3. Build assumption evidence.
- For every major driver, collect a benchmark or rationale.
- Use [benchmark-framework.md](references/benchmark-framework.md) to decide whether the anchor is filings, guidance, consensus, peers, or industry data.
- Record the source, date, and why the base case sits where it does inside the benchmark range.

4. Build the workbook.
- Create or update the input JSON using [input-contract.md](references/input-contract.md) and [example_model_input.json](references/example_model_input.json).
- Run the builder script:

```bash
python scripts/build_ib_model.py --input references/example_model_input.json --output out/example_ib_model.xlsx
```

5. Validate the workbook.
- Review `Checks` for any `FLAG`.
- Confirm quarterly sums roll correctly into annual values.
- Confirm benchmark notes cover all major revenue drivers, gross margin / cogs logic, and tax assumptions.

## Modeling Discipline

- Prefer helper rows over nested formulas.
- Avoid mixing hardcodes and formulas in the same line.
- Separate `driver`, `calculation`, and `output` rows.
- Link quarterly results into annual aggregation; do not duplicate logic on both sheets.
- If a business model does not fit a supported archetype exactly, approximate with the closest driver set and note the limitation.

## Supported Revenue Archetypes

The bundled builder script supports these revenue models:

- `volume_price`
- `users_arpu`
- `orders_aov`
- `gmv_take_rate`
- `stores_sales_per_store`
- `backlog_recognition`
- `capacity_utilization_price`

See [business-driver-playbook.md](references/business-driver-playbook.md) for mapping guidance.

## Supported Cost Archetypes

- `gross_margin`
- `cogs_ratio`
- `unit_cost`

## References

- [model-architecture.md](references/model-architecture.md): workbook structure, color conventions, and formula safety rules.
- [business-driver-playbook.md](references/business-driver-playbook.md): operating-driver templates by business type.
- [benchmark-framework.md](references/benchmark-framework.md): assumption evidence and benchmark hierarchy.
- [input-contract.md](references/input-contract.md): JSON structure for the builder script.
- [example_model_input.json](references/example_model_input.json): example input payload.

## Output Standard

When using this skill for a live company, return:

1. A short statement of the business decomposition used.
2. A benchmark-backed assumption table.
3. The generated `.xlsx` file path.
4. Any residual limitations or manual follow-up needed.
