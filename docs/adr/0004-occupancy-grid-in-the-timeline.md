# 0004 — An occupancy grid instead of scanning the queue

**Status:** accepted

## Context

Two linear searches were hiding in the timeline:

1. the conflict check scanned the whole queue on every action declared;
2. `instant` and `animate` scanned every action to find the ones on a step.

Both are O(n²) in the number of steps. On an artwork with thousands of steps
that would show up as a stutter on every save — exactly when the tool needs to
feel instant.

## Decision

An occupancy grid indexed by turtle × step stores the action's index, offset by
one (`0` means empty):

```fluxa
int arr taken[32768] = 0        // 8 turtles × 4096 steps
taken[t * 4096 + s] = n + 1
```

The conflict check is one lookup. Walking a step is eight lookups, one per
turtle, instead of scanning the queue.

## Consequences

- Declaring 3000 steps: 8 ms.
- The turtle count and the maximum step become hard limits (8 and 4096), because
  the grid is sized by them. Raising them costs linear memory.
- Execution order within a step became per turtle, not per declaration order.
  Since actions on the same step are simultaneous by definition, that does not
  change the result.
- 262 KB of array. Acceptable here; on an embedded target it would need review.
