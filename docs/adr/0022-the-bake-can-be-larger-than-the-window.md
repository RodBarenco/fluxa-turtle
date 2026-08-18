# 0022 — The bake can be larger than the window

**Status:** accepted — answers the gate of sprint 9, and supersedes the size
limit in [0003](0003-path-baked-into-a-texture.md)

## Context

The roadmap put a hard gate in front of the camera sprint: **can `std.image` be
drawn into off-screen?** Everything about a world larger than the window follows
from that one fact, and nothing was to be designed before it was answered.

`std.image` cannot, and it never could: it is a buffer library — `new`, `load`,
`save`, `resize`, `blit`, `width`, `height`. There is not one drawing primitive
in it. The tool bakes with `graph.capture` + `image.blit` precisely because that
is the only bridge between the two libraries, and a capture is by definition
what the window can see.

**But the gate was asking the wrong library.** `std.graph` has off-screen
surfaces of its own:

```
graph.render_target(win, w, h)      graph.draw_render_target(win, rt, x, y)
graph.begin_render_target(win, rt)  graph.release_render_target(win, rt)
graph.end_render_target(win)
```

Up to 16384 px a side, with the same cursor discipline as a font or a window.

## Decision

**The answer is yes, and the bake becomes a render target.** Measured, not
assumed — `lab/target.flx`, 800×600 window, 2000×1500 world:

| | |
|---|---|
| a 2000×1500 surface | created |
| drawing lands where it is put | red at the world's (0,0) appears at the frame's (0,0) — no flip |
| **it keeps what was drawn** | a second frame that draws nothing into it still shows the first |
| an offset when it is drawn | `draw_render_target(win, world, -1200, -900)` shows the world's far corner, exactly |
| 120 frames, world drawn with the camera moving every frame | **60 ms** (0.5 ms a frame) |
| 120 frames, today's 800×600 `draw_image` | **69 ms** — the big surface is *cheaper*, because it is a GPU texture and the blit uploads a CPU buffer |
| 100 strokes drawn into the world, one per frame | **51 ms** — half a millisecond a step, against ~160 ms for one full rebuild |
| an uncleared surface | **transparent** where nothing was drawn — so a stack of them composites |
| 120 frames, four layers over each other | **100 ms** (0.83 ms a frame) |

So the "if yes" branch the roadmap wrote is the one that is real: the bake
becomes a world-sized surface, the camera is an offset and a scale applied when
it is drawn to the window, and layers are several surfaces composited in order.

**One thing does not follow, and it is the export's problem:** `graph.capture`
while a render target is bound still returns the **window**, 800×600. The
capture reads the frame, not the surface. A world-sized still therefore has to
be taken in tiles — point the camera at each region, capture, and `image.blit`
them into one image — which the export can do because it renders by frame index
and nothing there is timed (adr 0006).

## Consequences

- **adr 0003 stands, minus its size.** The path is still baked so that finished
  strokes cost one draw per frame instead of thousands. What changes is that the
  surface is no longer the window's size and is no longer produced by capturing
  the window: it is drawn into directly, which also removes the capture from the
  per-step path.
- **A render target is a `dyn` cursor**, so it lives exactly where the sheet and
  the typeface live — made in `Runner.play`, passed to whoever draws
  ([adr 0020](0020-the-sheet-is-passed-to-whoever-draws.md)). It must be
  released before `graph.close`, and released on reload, or every save leaks a
  world.
- **The camera is two numbers and a zoom**, and `graph.begin_cam2d` is not
  needed for the artwork itself — an offset in `draw_render_target` is the pan,
  and zoom is the one thing it does not do, so the camera keeps `begin_cam2d`
  for that and for the mouse round trip.
- **Layers are cheap enough to be a feature rather than a budget**: four of them
  full-screen cost 0.83 ms a frame, which is 5% of a 60 fps budget.
- **The stage grows a size of its own.** `stage.Stage.world(w, h)` is what makes
  the surface bigger than the window; without it the world is the window and
  nothing about today's artworks changes.
- **Not answered here, and first in the sprint:** whether a `prst dyn` render
  target survives a save the way the window does. If it does not, the bake is
  rebuilt on every reload — which is what happens today anyway, so it is a cost
  question rather than a design one.
