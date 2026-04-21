# Data Sources

## Primary Provider

Use `Wind` as the primary provider for v1.
Optimize the field mapping and examples for Wind exports first.

## Recommended Wind Coverage

Collect these datasets for each analysis date:

- sector daily OHLCV for Wind industry and concept boards
- sector constituent list with effective date
- constituent daily OHLCV
- constituent turnover and free-float market value
- constituent main-force net inflow
- benchmark daily returns for `All A`
- optional event or catalyst tags maintained by the user

## Export Guidance

Prefer exporting daily snapshots plus at least 20 trading days of history for every sector and constituent included in the run.
For rotation analysis, export 20 to 60 trading days of daily sector returns.

## Known Data Gaps

- main-force net inflow may only exist at constituent level, not sector level
- concept-board constituent changes may be noisier than industry-board changes
- catalyst tagging is usually not available as a clean Wind-native field and may need manual enrichment

## Fallback Rules

1. Use sector-level main-force net inflow when available.
2. Otherwise aggregate constituent main-force net inflow.
3. If neither is available, use a large-order or related proxy and lower confidence.
