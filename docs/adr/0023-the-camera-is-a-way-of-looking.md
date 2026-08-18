# 0023 — The camera is a way of looking

**Status:** accepted — first half of sprint 9, on the answer in
[0022](0022-the-bake-can-be-larger-than-the-window.md)

## Context

`graph.begin_cam2d` gives pan and zoom over whatever is drawn, which makes
"look closer at the artwork" a small feature — the roadmap said as much, and
0022's measurements confirmed the surface underneath can grow later without
this changing.

Small features are where a tool acquires the wrong idea about itself. A camera
can be two things: a **view**, which is how the person looking moves their head,
or a **declaration**, which is part of the composition and belongs in the video.
They cannot both be true, because an artwork that zoomed would render one thing
on screen and another into the export.

## Decision

**A view.** `static/view.flx` holds zoom and target and nothing else about the
artwork; the wheel zooms at the cursor, the right button drags, `Z` puts it
back. Not a step, not on the turtle, not in the timeline, not saved.

Three lines draw the boundary:

- **The export never asks.** Every call into the View is guarded by
  `exporting == 0`, so a video renders exactly as it did before this existed
  (adr 0006). The rebuild is not guarded because it never had a camera: the bake
  is the artwork at 1:1 and the camera is applied when the bake is *drawn to the
  window*.
- **It wraps the artwork and stops.** `View.on` opens after the stage is
  cleared, `View.off` closes before the panel is drawn, so the panel and the key
  line are the same pixels at any zoom. Measured: two captures at 1x and 2x
  differ *only* in the rows the artwork's stroke occupies.
- **Untouched, it is not applied at all.** `idle()` is true while the target is
  the window centre and the zoom is 1, and then `begin_cam2d` is never called.
  A capture taken today is pixel-identical to one taken before the Block
  existed, which is what every harness in `lab/` depends on.

## Consequences

- **The arithmetic is here, not in the library.** `graph.screen_to_world`
  answers from the camera the library currently has active, and the keys are
  read after `end_frame`, where there is none. So `world_x`/`world_y` compute
  the inverse directly, with the library's own convention — offset at the window
  centre. Measured against it: looking at (200,300) at 2x puts world 200 at
  screen 400 and the window's right edge at world 400.
- **`View.look(x, y, zoom)`** exists because a key cannot be pressed from a
  harness, and a camera nobody can point is a camera nobody can measure. It is
  the same setter the wheel and the drag use.
- **The zoom is clamped to 0.2x–8x.** Below that the artwork is a dot and above
  it a single stroke fills the screen; both are ways of losing the drawing with
  no way back except `Z`, which is a key you have to know about.
- **The right button drags, not the left.** The studio wants the left one, and a
  tool that pans when you click on the artwork is a tool that cannot be clicked
  on.
- **It costs nothing measurable** — 120 frames at 2.5x against 120 at 1x is
  inside the noise, because a camera is a matrix and the drawing is the same
  drawing.
- **What it does not do is see outside the stage.** Zooming out past 1x shows
  the window's own background around an 800×600 artwork, because that is all
  there is. A world larger than the window is the second half of the sprint, and
  0022 is what says it is possible.
