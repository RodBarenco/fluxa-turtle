# 0005 — Turtle as a `typeof` instance, state in singleton pools

**Status:** accepted

## Context

The project's reference pattern (the `nave/` game) uses one singleton Block per
file, with state in concrete-typed fields — including parallel arrays for entity
pools — and `dyn` only in `main.flx`, arriving in methods as a parameter.

A first attempt at this project ignored that and built one giant flat `dyn` with
hand-computed offsets. It was slower (reading a `dyn` costs ~1.2 µs against
~0.2 µs for a typed array), it did not nest, and it departed from the language's
pattern for no gain.

At the same time, a turtle is genuinely multi-instance — which is exactly what
`typeof` exists for — and `leo.go(1, 200.0, 0.0)` reads far better for a learner
than a call with the identifier on the outside.

## Decision

State lives in singleton pools with parallel typed arrays (`pool.Pool`,
`timeline.Timeline`, `painter.Painter`). The turtle that shows up in the user's
code is a `typeof` instance holding **only an `int id`**, delegating to the
pools.

```fluxa
Block Turtle {
    int id = 0
    fn go(int step, float dist, float turn) nil {
        timeline.Timeline.add(id, step, 0, dist, turn, 0.0)
    }
}
```

No `dyn` field on a Block, anywhere. `win`, `canvas` and `bg` arrive as method
parameters, as in `fn draw(dyn win)`.

## Consequences

- The user-facing API stays clean: `leo.color(...)`, `leo.go(...)`.
- The `id` is rebuilt on every run by `spawn`, in declaration order — which is
  stable because the whole file re-executes on every save.
- Turtle configuration (colour, width, style) does not need to persist: it is
  redeclared on every save, by definition.
- Reading state goes through accessor methods, which is more verbose than
  touching the array directly. That is the price of keeping the pools
  encapsulated.
