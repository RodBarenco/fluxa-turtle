# 0020 — The sheet is passed to whoever draws

**Status:** accepted

## Context

Pillars §4 asks for a path made of pictures — footprints, leaves, symbols,
fragments of an image — and it is the last item in §1–§10 that is not built. The
shapes styles cover the vector half of it; this is the half that needs a file.

Every picture in an artwork is composed into one sheet before the frame loop
starts, and that sheet is a `dyn` (adr 0013). A Block field cannot hold a `dyn`,
so it lives as a local of `Runner.play` and travels as a parameter. `Pool.draw`
already takes it, because the turtles' own bodies are drawn from it.

`Painter.paint` does not have it, and a stamped path is drawn there. Nor does
`Runner.instant`, nor `Runner.rebuild` — the whole replay path is one call chain
that never needed a picture until now.

## Decision

**Pass it.** `paint`, `stroke`, `replay`, `draw` and `pass` in the painter, and
`instant`, `rebuild` and `frame` in the runner, all take the sheet.

The alternative was a queue: the painter records "stamp this slot here, at this
angle" and the runner drains it while it still holds the sheet. That avoids
changing signatures and buys two problems — the stamps land at the end of the
frame rather than in the order the strokes were drawn, and the painter starts
owning a second kind of state that has to be reset in exactly the same places as
the first.

The language's own rule decides it. Guide rule 3: **a function sees only its
parameters, so everything is passed.** This project has been bitten by every
attempt to get around that rule — a Block field that resets on reload, a `prst`
that a function cannot see, a sheet that had to become a local. Passing the
sheet costs one parameter in eight signatures and every harness that calls
`rebuild`; it costs no new state, no new ordering question, and nothing to
explain later.

## Consequences

- `Runner.rebuild(win, canvas, sheet, upto)` — every harness in `lab/` changes,
  mechanically. They all build a sheet already.
- The painter draws pictures now, so it imports what it needs to draw one:
  `Pool.stamp(win, sheet, slot, x, y, deg)`, which is `draw_sprite` with the
  turtle taken out of it.
- A segment records which sheet slot it was drawn with, next to the colour and
  the width it already records, because a stamped path is a look and looks are
  resolved when the stroke closes (adr 0009).
- Sprite files stay at eight, shared between the turtles' bodies and the paths.
  An artwork where every turtle stamps a different picture runs out; it says so.
- The stamp is rotated by the direction of the segment it sits on, which the
  shape styles already compute. Draw the art facing right, as everywhere else.
