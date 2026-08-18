# 0024 — A world larger than the window

**Status:** accepted — carries out
[0022](0022-the-bake-can-be-larger-than-the-window.md), completes sprint 9

## Context

0022 measured the answer: `graph.render_target` gives an off-screen surface up
to 16384 px a side, it keeps what is drawn into it, it is transparent where
nothing was, and it costs *less* per frame than the `draw_image` the tool was
already doing. 0023 built the camera on top of that answer. What was left was
the surface itself.

## Decision

**The bake is a render target the size of the world, and the world is declared
on the stage.**

```fluxa
stage.Stage.world(1600, 1200)     // the window stays 800x600
```

Not declared, the world *is* the window, and every artwork written before this
draws exactly the same pixels — which is the property the whole change was
shaped around.

Four things follow, and each one is a place the old design leaked out:

- **`Painter.bake` is gone.** It captured the presented frame and blitted it
  into an image; the rebuild now opens the surface, draws into it, and closes
  it. One `graph.capture` and one `image.blit` per rebuild disappear with it,
  and so does the ceiling: a capture could never have returned more than the
  window.
- **`canvas` is gone from `Runner.play`.** It was a `prst dyn` in every artwork
  file, there so the bake could survive a save — and it never needed to, because
  `play` rebuilds on every pass anyway. The surface is a local of `play`, made
  and released there, exactly like the sprite sheet and the typeface
  ([adr 0020](0020-the-sheet-is-passed-to-whoever-draws.md)). An artwork now
  opens with `runner.Runner.play(win, part, snd, done)`.
- **The background covers the world**, not the window: a stretched image is
  resized to the world, a centred one is centred in it, and a tiled one tiles
  across it.
- **The camera's home is the world's centre**, and a world larger than the
  window is *never* idle — at the identity the window would show the world's
  top-left corner rather than its middle.

**The export gets its own camera, computed and not remembered.** A video renders
by frame index and two renders have to be identical (adr 0006), so it cannot
inherit wherever somebody left the wheel. `View.whole` is a pure function of the
stage: the whole world, fitted and centred. With the world the size of the
window it is the identity and is not applied at all, so every video this tool
has written still comes out the same; with a bigger world it is the whole scene,
which is the only framing that makes a video of it mean anything. Measured: with
the wheel left at 4x, the exported frame is pixel-identical to the fitted view.

## Consequences

- **`lab/world.flx`** is the sprint's gate-out: a 1600×1200 world through an
  800×600 window, four marks in four quarters, the camera pointed at three
  places, and each capture checked against the region it should show. 120 frames
  of it cost 92 ms; one rebuild costs 6 ms.
- **A world-sized still is still not possible in one call.** `graph.capture`
  inside a render target returns the *window* — 0022 measured that too. Frames
  and video are what the window sees, fitted; a full-resolution still has to be
  taken in tiles, and that belongs to the export sprint.
- **Layers are the piece of sprint 9 that is not built.** 0022 measured them at
  0.83 ms a frame for four; what is missing is the artwork-level idea of which
  layer a turtle draws on, and that is a sprint of its own rather than a
  parameter.
- **A step that takes no time was cancelling itself**, and this is where it was
  found: the fraction of the step in flight was written as `elapsed / duration`
  with a duration of zero. A jump to where she already stands is exactly that,
  and two hundred of them are the last thing the Leonardo artwork does — every
  one of them dropped, in silence, because a cancelled step carries on at the
  next statement. `lab/toward.flx` measures it now.
