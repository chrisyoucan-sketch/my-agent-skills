---
name: a-share-sector-tracker
description: Track A-share industry and concept sectors using Wind-based data contracts, main-force net inflow, technical and breadth indicators, correlation and rotation analysis, and leader-stock diagnostics. Use when asked to rank sectors, compare sector capital flow or momentum, monitor board rotation, identify leaders, or generate daily A-share sector notes.
---

# A-Share Sector Tracker

Build repeatable daily sector-monitoring outputs for A-share research.
Use this skill to turn Wind-aligned sector and constituent data into ranked sector tables, state labels, leader diagnostics, and a daily snapshot note.

## Workflow

1. Define scope.
- Choose `industry`, `concept`, or both.
- Use `All A` as the benchmark unless the user explicitly overrides it.
- Keep `1D`, `5D`, and `20D` windows as the default horizon set.

2. Validate inputs.
- Run `python scripts/validate_inputs.py --input <json>`.
- Reject or flag runs with missing benchmark returns, missing sector histories, or insufficient constituent coverage.

3. Score sectors.
- Run `python scripts/sector_score.py --input <json>`.
- Use main-force net inflow as the primary capital-flow metric.
- Keep capital flow, trend, breadth, leader, and catalyst sub-scores separate from the total score.

4. Identify leaders.
- Run `python scripts/sector_leaders.py --input <json>`.
- Treat leader selection as a rules-based output, not an analyst guess.
- Check whether the sector is broadening or still depends on one or two names.

5. Analyze rotation.
- Run `python scripts/sector_rotation.py --input <json>`.
- Use daily return series, not price levels, for correlation.
- Review both correlation clusters and simple lead-lag signals.

6. Publish the daily note.
- Run `python scripts/build_daily_note.py --input <json>`.
- Return ranked sectors, score changes, capital-flow highlights, breadth signals, leaders, catalysts, and risk flags in a fixed order.

## Quality Gates

- Reject outputs when the board source is unknown.
- Reject outputs when `All A` benchmark data is missing.
- Reject outputs when a sector lacks enough history to compute `20D` metrics.
- Flag sectors where capital-flow fields use a fallback proxy instead of main-force net inflow.
- Flag sectors with fewer than 3 valid constituents for leader analysis.
- Do not assign a sector state unless the evidence fields are present in the output payload.

## Data Contracts

Read these files before adapting the skill to a new Wind export:

- [references/data-sources.md](references/data-sources.md): Wind-first sourcing assumptions and export guidance.
- [references/data-contracts.md](references/data-contracts.md): Required and optional fields, units, and fallback rules.
- [references/indicator-definitions.md](references/indicator-definitions.md): Scoring and indicator formulas.
- [references/state-model.md](references/state-model.md): Sector state definitions and transition logic.
- [references/output-templates.md](references/output-templates.md): Daily snapshot structure and table schema.

## Script Usage

Validate a Wind-style daily payload:

```bash
python scripts/validate_inputs.py --input references/example-daily-input.json
```

Score sectors and print ranked JSON:

```bash
python scripts/sector_score.py --input references/example-daily-input.json
```

Identify sector leaders:

```bash
python scripts/sector_leaders.py --input references/example-daily-input.json
```

Run correlation and lead-lag analysis:

```bash
python scripts/sector_rotation.py --input references/example-weekly-input.json
```

Generate a daily markdown note:

```bash
python scripts/build_daily_note.py --input references/example-daily-input.json
```

## Output Standard

Return these sections in order for daily monitoring:

1. Daily sector ranking table with total score and sub-scores.
2. Score movers and state changes.
3. Capital-flow highlights.
4. Technical and breadth anomalies.
5. Leader-stock summary by sector.
6. Catalyst and risk flags.
7. Evidence rows for any strong conclusion or alert.
