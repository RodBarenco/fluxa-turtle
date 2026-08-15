# 0011 — The artwork file declares, the runner executes

**Status:** accepted

## Context

`main.flx` is the file somebody learning the tool reads first, and for a while
it was the only file where a `dyn` could live — the window, the canvas and the
background image all had to sit there, because a Block cannot hold a `dyn` as a
field. Everything that touched one leaked into the artwork:

```fluxa
danger { image.discard(bg)  bg = image.load("my_texture.png") }
if err != nil { print("background: ", err[0]) }
stage.Stage.image_tile()
stage.Stage.image_scale(1.0)

exporter.Exporter.setup("export", 60)
exporter.Exporter.hold(30, 90)
runner.Runner.export(win, canvas, bg)
```

Nothing there is about drawing. It is error handling, resource release, and
three handles being passed from one place to another — in the file whose whole
job is to say what the turtles do. A pillar of the project is that this file
teaches, and a beginner reading `runner.Runner.movie(win, canvas, bg, 1, 0, 60)`
learns about parameters, not about artwork.

The rest of the tool already had the answer. `leo.go(3, 200.0, 90.0)` does not
move anything: it declares that on step 3 there is a movement, and the Runner
performs it later. The step system is a declaration read by an executor.

## Decision

**Everything in `main.flx` is a declaration.** Anything needing a window, a
canvas, a frame loop or a file handle is recorded and carried out by the Runner
when execution reaches the stage.

```fluxa
stage.Stage.tile("my_texture.png", 1.0)     // the background
export.Video(1, 36, 5)                      // from, to, frames per second
export.Frames(1, 36, 60)                    // the same, as numbered PNGs
```

- The Stage holds the **path**, not the image. `Runner.rebuild` decodes it,
  draws it and releases it, once per save.
- `export.Video` / `export.Frames` are module-level functions that record a
  request. `Runner.deliver`, called at the top of `play`, generates it and
  reports what it actually did.
- Asking for more steps than the artwork has generates what there is and says
  so, rather than failing. The line is written once and the drawing keeps
  growing under it.

What is left in the artwork file is the window, the canvas and `done` — three
`prst` declarations under a comment explaining they survive the save — and then
turtles.

## Consequences

- `bg` is gone from `main.flx`, and with it the `bg` parameter of `play`,
  `export`, `movie` and `rebuild`.
- The background is decoded once per rebuild instead of once per program. That
  is once per save, of a file already on disk, and it goes into the baked
  texture either way.
- The background image must outlive `graph.end_frame`. It is a local `dyn` in
  `Runner.rebuild`, handed over by `Stage.picture()`: `graph.draw_image` batches,
  and releasing the buffer before the frame is flushed leaves the batch pointing
  at a texture that is gone — the background comes out black. Found by measuring
  the render, not by reading the code.
- An export declared in the file runs on **every save**, because the file is run
  again on every save. That is the same rule as everything else here, and
  commenting the line out is how you stop it. It is deliberately outside the
  replay loop: R redoes the drawing, not the file on disk.
- Two language facts came out of this, both now in AGENTS.md: a module-level
  function only sees a Block declared **above** it in the file, and a parameter
  that shares a name with a field of its own Block silently resolves to the
  field — `want_fps = fps` was reading the Block's 60 and ignoring the argument.
