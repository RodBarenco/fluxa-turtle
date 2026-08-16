# 0016 — A shape is a batch of steps that returns the next one

**Status:** accepted

## Context

Every figure was a walk: `go` repeated, or `ring` with a turn that divides 360.
That is the right way to *learn* what a polygon is, and the wrong way to place a
circle of radius 70 at (660, 120) — which needs a distance, a turn, an entry
angle and a starting point worked out by hand, none of them the numbers you
actually have.

The recipes file was full of exactly that arithmetic, which is a sign the tool
was missing a call.

## Decision

Eight calls on the turtle — `polygon`, `triangle`, `square`, `rect`, `circle`,
`ellipse`, `star`, `arc` — with three rules that are the whole design.

**Placed by the centre, in stage coordinates.** The same coordinates `toward`
and `jump` use, and the ones a person has in mind ("a circle here, this big").
Each shape opens with a pen-up move to its first vertex, so it never drags a
line in from wherever the turtle was standing; that move costs one step. Closed
shapes end on the vertex they started from.

**A batch of steps, not a special case.** One side per step, declared through
the same `Timeline.add` as everything else — so a shape animates side by side,
obeys the colour and style in force at that step, moves with `pivot` and
`shift`, and can be taken back out with `erase`. Nothing in the runner, the
painter or the timeline knows shapes exist.

**They return the next free step.** A circle's step count depends on its radius,
so requiring the artwork to know it would make the ergonomic gain a loss:

```fluxa
int s = leo.circle(1, 400.0, 300.0, 120.0)
s = leo.star(s, 400.0, 300.0, 90.0, 36.0, 5)
```

A value-returning method can be called as a statement in Fluxa and the value
discarded — verified before the design leaned on it — so `leo.circle(1, ...)`
alone stays legal for someone who is numbering the steps by hand.

Two smaller choices, both about not making a person do a rotation in their head:

- **A curve picks its own number of sides**: one per about 12 px of
  circumference, clamped to 12…90. `polygon` is the escape hatch for choosing —
  a 100-gon is a rounder circle, a 7-gon is a deliberate one.
- **Figures sit flat.** An odd number of sides gets a corner up and a horizontal
  side at the bottom; an even number gets a horizontal side top and bottom. That
  is the difference between a square and a diamond.

## Consequences

- The common case went from four numbers nobody has to four numbers everybody
  has.
- A circle of radius 70 costs 36 steps out of 6000, and a 90-side curve costs
  91. Step budget is now something an artwork made of many circles can feel; the
  panel's "step n / m" is where you see it.
- The animation time of a figure does not depend on its number of sides — each
  side is `length / speed`, and they sum to the perimeter either way. Smoothness
  is free in time and costs only steps.
- `arc` is deliberately the odd one: it does not close and it leaves the turtle
  at the far end facing along the curve, because a piece of a circle exists to
  be joined onto something else.
- The recipes that computed these walks by hand are still there, and still worth
  reading once — they now say so, and point at the calls.
