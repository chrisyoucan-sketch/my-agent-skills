# State Model

## States

Use these labels for v1:

- `launch`
- `strengthening`
- `divergence`
- `fading`
- `bottoming`
- `range-bound`

## Rules

### Launch

Assign `launch` when:

- `return_5d > 0`
- `excess_return_vs_all_a_5d > 0`
- flow intensity is positive
- breadth is improving
- the latest close is above the 20-day average

### Strengthening

Assign `strengthening` when:

- `return_20d > 0`
- `excess_return_vs_all_a_20d > 0`
- flow remains positive
- breadth is healthy
- the sector is not excessively concentrated

### Divergence

Assign `divergence` when:

- sector return is still positive
- breadth is weak or deteriorating
- top-3 contribution is elevated
- leaders remain strong while followers lag

### Fading

Assign `fading` when:

- `return_5d < 0`
- flow is negative or decelerating
- the close loses the 20-day average
- the leader no longer confirms the move

### Bottoming

Assign `bottoming` when:

- `return_20d <= 0`
- short-term breadth improves from a weak base
- capital flow stops worsening
- realized volatility compresses or stabilizes

### Range-Bound

Assign `range-bound` when none of the above are met and the score remains mid-pack without clear trend confirmation.

## Interpretation Notes

- `launch` is an early signal, not a confirmation of trend durability
- `strengthening` is the preferred state for sustained monitoring
- `divergence` is a warning that broad participation is weakening
- `fading` should raise risk flags even if absolute rank stays high
