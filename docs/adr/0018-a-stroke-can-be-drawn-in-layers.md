# 0018 — A stroke can be drawn in layers, and the rhythm belongs to the path

**Status:** accepted

## Context

Pillars §4 asks for more than four line styles: a brush, a marker, a texture, a
glow trail, particles, and shapes repeated along the path. Adding them turned up
two things the existing painter got away with only because its styles were
small.

**The rhythm restarted at every segment.** A dash pattern was measured from the
start of each segment, so a path made of many short strokes — which is every
path written as a loop, and every traced drawing — had its dashes resynchronised
at each corner. With a 2 px dot nobody noticed. With a triangle 7 px across and
segments 20 px long, every joint got a shape from each side, pointing two ways
at once, and the row of triangles came out as a row of blobs.

**A halo covers its neighbour's core.** A marker is a wide translucent stroke
with a solid one inside it, and a glow is that twice over. Drawn segment by
segment, the halo of segment *n+1* is painted over the core of segment *n* near
the point they share, so a marker stroke came out looking dashed — the opposite
of what it is.

## Decision

**The new looks are style values, not new machinery.** `path_brush`,
`path_marker`, `path_glow`, `path_spray`, `path_triangles`, `path_squares` and
`path_stars` set the same appearance event the existing four set — a style and a
rhythm (adr 0009). Everything already true of a style is true of them: it
applies from the next step the turtle declares, the rebuild replays it, and it
costs nothing per frame because the path is baked (adr 0003). The shapes reuse
`dash` as their size and `gap` as their spacing, so `path_dash` tunes them and
no new field was needed anywhere.

**The phase belongs to the path.** The painter keeps, per turtle, how far along
her own path she is. `add` records that phase on the segment; `replay` — the
rebuild's version of `stroke` — advances it by the length of what it just drew.
`paint` then starts the pattern at `-fmod(phase, period)` and clips a dash to
whichever part of it falls inside this segment. A pattern now runs continuously
through corners, which fixes the shapes and quietly improves dotted and dashed.

**A layered stroke is drawn in two passes over the whole path**: every halo
first, every core over them. In the segment pool that is two loops. In the
rebuild, where the artwork is replayed step by step and nothing is pooled, it is
the whole replay done twice — so the rebuild asks the timeline first whether any
layered style exists at all, and only pays when the answer is yes.

**The speckle is computed, not random.** `path_spray` scatters its dots from a
hash of the coordinates, because two renders of one artwork have to be identical
(adr 0006) — a random number would make an export differ from the screen and
from the next export.

## Consequences

- Measured over 600 segments on this machine: solid 50 ms, brush 49, spray 49,
  stars 64, and marker 117 / glow 100 — about double, which is the second pass.
  Any artwork containing one marker pays it on every rebuild, including the
  saves. That is the price of the look and it is worth saying out loud.
- The per-frame cost is unchanged. All of this is baked.
- `path_dash` now means "size and spacing" for the shape styles, which is a
  second meaning for one call; the alternative was a new event and a new field
  for something the existing pair already expresses.
- The brush's width comes from a function of the *point*, not of the stroke, so
  two segments meeting at a corner agree on the width there and a path swells
  continuously instead of breaking into leaves.
- `lab/brush.flx` draws all eight looks over the same wave, times each one, and
  renders the spray twice to compare the PNGs pixel by pixel.
- **A second pass has to start from the same state as the first.** The one it
  shipped with re-homed the turtles and reset their styles but did not re-apply
  the moves and the erases, so anything `erase`d came back from the dead in the
  second pass — visible only in an artwork that used a glow *and* an erase. The
  preamble is now one function, `Runner.ready(upto)`, called by both.
- One bug worth remembering: the shape helper declared `int n` for its number of
  sides, and `n` is the Painter's own field — the segment count. The local
  resolved to the field, so shapes came out with as many sides as the path had
  segments, and a path with none divided by zero. It is the trap AGENTS.md §3
  already describes, found again in new code.
