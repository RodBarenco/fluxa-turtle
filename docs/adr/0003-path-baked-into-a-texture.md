# 0003 — The path lives in a texture, it is not redrawn

**Status:** accepted
**Supersedes:** the per-frame redraw of the first version

## Context

The first version kept the segments in arrays and redrew the whole trail every
frame. Measuring:

| | ms/frame |
|---|---|
| 5000 `draw_rect` | 4 |
| 5000 `draw_line` | 4 |

At width 3 each segment becomes three lines — the practical ceiling sat near
1400 segments, and the cost grew with the artwork. This contradicted the runtime
itself: `graph.draw_image` keeps the texture cached on the GPU and only
re-uploads it when the pixels change.

## Decision

The finished artwork's path is drawn **once** per run and pinned into a
persistent texture with `graph.capture` followed by `image.blit`. Each frame
draws that texture with a single `graph.draw_image`, plus the few segments born
in the current run.

`image.blit` is the key piece: it copies over the buffer that already exists and
**preserves the handle**, which allows re-baking from inside a method without
returning a `dyn` — something the language's own pattern does not do.

## Consequences

- The per-frame cost does not depend on the artwork's size: 3000 segments cost
  0–1 ms/frame, the same as 30.
- There is no ceiling on the artwork's size. The painter pool's limit of 2048 is
  only the budget of not-yet-baked segments within a single save.
- `graph.capture` only sees the complete frame — capturing between `begin_frame`
  and `end_frame` returns just the cleared background (verified). So the bake
  happens after `end_frame`, in a frame without turtles.
- Clearing one turtle's path requires redoing the whole texture, because there
  is no way to selectively erase a region of it.
