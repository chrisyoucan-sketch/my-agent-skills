# Business Driver Playbook

Choose the simplest driver set that explains the business without losing the economics.

## Revenue Archetypes

### `volume_price`

Use for manufacturing, branded products, components, commodity-like shipments, and hardware.

- Formula: `Revenue = Volume * Price`
- Typical drivers: `volume`, `price`
- Typical benchmarks: shipments growth, utilization, ASP trend, channel inventory

### `users_arpu`

Use for SaaS, subscriptions, telecom plans, and media memberships.

- Formula: `Revenue = Users * ARPU`
- Typical drivers: `users`, `arpu`
- Typical benchmarks: net adds, churn, upsell, penetration

### `orders_aov`

Use for e-commerce, marketplaces with gross sales basis, food delivery, and transactional retail.

- Formula: `Revenue = Orders * AOV`
- Typical drivers: `orders`, `aov`
- Typical benchmarks: order frequency, basket size, conversion

### `gmv_take_rate`

Use for marketplaces, payment processors, ad networks with spend basis, and platforms monetized on throughput.

- Formula: `Revenue = GMV * Take Rate`
- Typical drivers: `gmv`, `take_rate`
- Typical benchmarks: merchant count, TPV growth, monetization mix

### `stores_sales_per_store`

Use for offline retail, restaurants, and location-based services.

- Formula: `Revenue = Avg Stores * Sales per Store`
- Typical drivers: `avg_stores`, `sales_per_store`
- Typical benchmarks: openings, same-store sales growth, ticket size

### `backlog_recognition`

Use for EPC, defense, software implementation, and project-based services with backlog conversion.

- Formula: `Revenue = Opening Backlog * Recognition Rate`
- Typical drivers: `opening_backlog`, `recognition_rate`
- Typical benchmarks: book-to-bill, execution cycle, delivery capacity

### `capacity_utilization_price`

Use for fabs, plants, hotels, logistics capacity, and other constrained-asset models.

- Formula: `Revenue = Capacity * Utilization * Price`
- Typical drivers: `capacity`, `utilization`, `price`
- Typical benchmarks: installed capacity, occupancy, realized pricing

## Cost Archetypes

### `gross_margin`

Use when segment gross margin is the clearest and most defensible cost assumption.

- Formula: `COGS = Revenue * (1 - Gross Margin)`

### `cogs_ratio`

Use when management or peers disclose cost as a percent of revenue.

- Formula: `COGS = Revenue * COGS Ratio`

### `unit_cost`

Use when unit economics are stable enough to model costs directly.

- Formula: `COGS = Volume Driver * Unit Cost`

## Selection Rules

- Use the lowest-complexity model that still explains the economics.
- If revenue is mainly price / volume driven, do not start with top-down growth.
- If segment data are missing, use a corporate-level model and clearly state the limitation.
- If one segment has distinct economics, model it separately even if the rest are grouped.
