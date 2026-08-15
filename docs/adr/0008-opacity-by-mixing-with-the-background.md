# 0008 — Opacity by mixing with the background

**Status:** accepted, with a caveat

## Context

The pillars ask for `Turtle.pathOpacity` (§4). The runtime's drawing primitives
take only R, G and B — `graph.draw_line(win, x1, y1, x2, y2, r, g, b)`. There is
no alpha channel anywhere in the graphics API.

## Decision

Transparency is obtained by mixing the path's colour with the background's, in
the requested proportion:

```fluxa
fn mix(int c, int bg, int opa) int { return bg + (c - bg) * opa / 100 }
```

It works because the path is always drawn over the stage.

## Consequences

- Visually correct over the background: four bars of the same colour at 100, 60,
  30 and 12 per cent fade as expected.
- **It is not real alpha.** Two translucent paths that cross do not add up — the
  one on top simply covers the one below with its already-mixed colour.
- The result changes if the background changes afterwards. Since the artwork is
  rebuilt on every save
  ([0002](0002-the-code-is-the-source-of-truth.md)), the mix is redone against
  the new background — which is the desired behaviour.
- Real alpha would need a new primitive in `std.graph`. If one appears, this
  decision should be revisited.
