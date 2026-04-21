# Data Contracts and Provider Mapping

## Unified Schema

Use this normalized record shape before modeling:

```json
{
  "company": {"ticker": "AAPL", "name": "Apple Inc.", "market": "US"},
  "target_period": "2026Q1",
  "currency": "USD",
  "segments": [
    {"name": "iPhone", "volume": 1.0, "price": 1.0, "cogs_ratio": 0.6}
  ],
  "opex": {"sga_ratio": 0.12, "rnd_ratio": 0.08, "other_opex_ratio": 0.01},
  "non_operating": {"amount": 0.0},
  "tax_rate": 0.2,
  "shares_diluted": 100.0,
  "cfo": 0.0,
  "capex": 0.0,
  "consensus": {"revenue": 0.0, "net_profit": 0.0, "eps": 0.0, "timestamp": "2026-03-01"},
  "guidance": {"revenue_low": 0.0, "revenue_high": 0.0, "timestamp": "2026-02-10"},
  "history": [{"period": "2025Q1", "revenue": 0.0, "net_profit": 0.0, "eps": 0.0}]
}
```

## Provider Abstraction

Treat providers as adapters into the unified schema:

- Financial statements provider: Bloomberg / FactSet / Wind / iFinD.
- Consensus provider: same stack or broker aggregator.
- Macro and industry provider: FRED / NBS / industry associations.
- News and disclosures provider: exchange filings and IR feeds.

## Mapping Template

Keep a mapping table for each provider:

| unified_field | provider | provider_field | transform | timezone | update_lag |
|---|---|---|---|---|---|
| `consensus.revenue` | `factset` | `FF_SALES_EST` | latest snapshot | UTC | T+0 |
| `guidance.revenue_low` | `exchange_filings` | `revenue_guidance_low` | parse numeric range | local | event-driven |
| `segments[].price` | `industry_feed` | `avg_selling_price` | weighted average | local | monthly |

## Timestamp and Traceability

For each forecasted metric, retain:
- Source system and field.
- Extraction timestamp.
- Transformation logic.
- Formula path to final metric.
