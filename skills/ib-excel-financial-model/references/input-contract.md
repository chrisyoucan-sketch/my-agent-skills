# Input Contract

The builder script expects JSON with this structure:

```json
{
  "company": {
    "name": "Example Co",
    "ticker": "EXM US",
    "currency": "CNY",
    "unit": "CNY_mn"
  },
  "quarters": ["2025Q1A", "2025Q2A", "2025Q3A", "2025Q4A", "2026Q1E"],
  "forecast_start": "2026Q1E",
  "segments": [
    {
      "name": "Main Segment",
      "revenue_model": "volume_price",
      "drivers": {
        "volume": {
          "unit": "k units",
          "benchmark": "Shipments vs peers",
          "rationale": "Demand normalizes after inventory correction",
          "values": [100, 110, 120, 130, 140]
        },
        "price": {
          "unit": "CNY per unit",
          "benchmark": "ASP from filings",
          "rationale": "Mix upgrade offsets modest pricing pressure",
          "values": [8.0, 8.1, 8.2, 8.3, 8.4]
        }
      },
      "cost_model": "gross_margin",
      "cost_assumptions": {
        "gross_margin": {
          "unit": "%",
          "benchmark": "Peer GM 32-36%",
          "rationale": "Base case assumes utilization recovery but not peak mix",
          "values": [0.33, 0.335, 0.34, 0.342, 0.345]
        }
      }
    }
  ],
  "company_assumptions": {
    "sga_ratio": {
      "unit": "%",
      "benchmark": "Historical SG&A ratio",
      "rationale": "Scale offsets wage inflation",
      "values": [0.08, 0.08, 0.079, 0.079, 0.078]
    },
    "rnd_ratio": {
      "unit": "%",
      "benchmark": "Management target",
      "rationale": "Roadmap maintained through cycle",
      "values": [0.05, 0.05, 0.05, 0.05, 0.05]
    },
    "other_opex_ratio": {
      "unit": "%",
      "benchmark": "Stable support costs",
      "rationale": "No step-up expected",
      "values": [0.01, 0.01, 0.01, 0.01, 0.01]
    },
    "non_operating": {
      "unit": "CNY_mn",
      "benchmark": "Interest plus other income",
      "rationale": "Held near recent run rate",
      "values": [5, 5, 5, 5, 5]
    },
    "tax_rate": {
      "unit": "%",
      "benchmark": "Historical ETR",
      "rationale": "No major jurisdiction shift",
      "values": [0.16, 0.16, 0.16, 0.16, 0.16]
    },
    "diluted_shares": {
      "unit": "mn shares",
      "benchmark": "Latest diluted share count",
      "rationale": "Minor SBC dilution only",
      "values": [100, 100, 100, 100, 101]
    }
  },
  "benchmarks": [
    {
      "type": "peer",
      "entity": "Main Segment",
      "metric": "Gross margin",
      "reference_value": "32%-36%",
      "source": "Peer filings",
      "date": "2026-03-15",
      "note": "Base case set at 34.5% by 2026Q1E"
    }
  ]
}
```

## Notes

- Every `values` array must match the number of quarter labels.
- The script writes formulas into the workbook. The JSON only seeds assumptions.
- For `unit_cost`, provide a `cost_volume_driver` key in the segment object. Example: `"cost_volume_driver": "volume"`.
