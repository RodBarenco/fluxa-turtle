# Changelog

All notable changes to this project.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.19.0] — 2026-08-18

### Added

- **`follow(step, points, px_s)`** and **`follow_silent`** — a whole trajectory
  in one call, one step per segment, returning the next free step.

  ```fluxa
  dyn wave = [140.0, 200.0, 220.0, 140.0, 300.0, 240.0]
  int s = leo.follow(1, wave, 900.0)
  ```

  The step model is untouched — what shrinks is the artwork file, not the
  timeline. Verified by drawing the same trajectory as `follow` and as
  hand-written `toward` calls and comparing the frames: pixel-identical, same
  step count, and `follow_silent` leaves zero ink.

  Not called `path`: ten calls already begin with `path_` and all of them are
  about how the trail looks.

- **`tools/trace.py --emit follow`** — the same artwork as lists of points.
  Leonardo goes from **1510 lines to 314**, for the same 387 steps and 1406
  actions, rendering pixel-identically.

  Two parser rules shape what it emits, and both are worth knowing before
  hand-writing something similar: a literal holds about a hundred points
  (expression depth is guarded at 200, and a list element counts as a level),
  and a literal is only legal as the initialiser of a declaration — not as an
  argument, not as a reassignment. So every leg is its own `dyn` and a pen-up
  hop is a `jump`.

## [0.18.0] — 2026-08-17

### Added

- **`path_image(path, scale)`** — a path made of pictures, and the last item in
  pillars §1–§10 that was not built. Footprints, leaves, symbols, a fragment of
  a drawing, stamped along the stroke and each one turned the way she walks.

  ```fluxa
  leo.path_image("leaf.png", 0.5)
  leo.path_dash(0, 34)              // one every 34 px
  ```

  For this style the rhythm is the **gap** alone, because a stamp's size comes
  from its scale rather than from a dash length. Measured on a straight 680 px
  run: twenty stamps, the first exactly on the start point, every gap 34.0. It
  costs 57 ms over 600 segments against 52 for a plain stroke.

### Changed

- **The sprite sheet is passed to whoever draws.** `Painter.paint`, `stroke`,
  `replay`, `draw` and `Runner.rebuild`, `instant`, `frame` all take it now, so
  `Runner.rebuild(win, canvas, sheet, upto)` is the new shape — every harness
  changed with it. The alternative was a queue the runner drained afterwards,
  which buys an ordering question and a second kind of painter state; the
  language's own rule decides it, since a function sees only its parameters
  ([adr 0020](adr/0020-the-sheet-is-passed-to-whoever-draws.md)).

## [0.17.0] — 2026-08-17

### Added

- **Sound** (expansions §11), now that the runtime can make one —
  `sound.version()` answers `miniaudio/0.11.25`:

  ```fluxa
  audio.Cue(1, "sounds/place.wav")   // fires when step 1 is animated
  audio.Track("music.mp3")           // plays while the artwork runs
  audio.Volume(70)
  ```

  **A soundtrack keeps playing across a save**, and **a rebuild is silent** —
  the two facts the design is built on, both measured first
  ([adr 0019](adr/0019-sound-crosses-the-save-and-a-rebuild-is-silent.md)). The
  engine and its loaded files ride in a `prst dyn` in `main.flx` because
  `sound.init()` gives out four engines and no more, and a Block field would
  burn one per save.

- **A sound for every step**: `audio.Place()`, `Tap()`, `Slide()`, `Pencil()`,
  `Stroke()`, `Quiet()`. A movement makes a noise the way a chess piece does
  when it is put down, and which noise is a **band on the timeline** like a
  colour — it applies from the step where it is written, so an artwork can knock
  through its outline and scribble through its shading. Two step sounds are
  never closer together than 70 ms: a traced drawing has a thousand steps and a
  sound every 11 ms is a buzz, not a rhythm.

- **50000 steps**, up from 6000, because drawing by hand — the studio that is
  coming — spends steps the way written code does not. Measured: the occupancy
  grid went from 192032 to 1600032 slots and the process from 101.4 MB to
  134.5 MB, `Timeline.reset` stayed at 0 ms because it clears only what was
  written, and a reload does not grow it. The rebuild is the part that felt it:
  it walks every step from 1 to where the artwork is, so the worst case the caps
  allow now measures 7.1 s against about a second at 6000. An artwork of 500
  steps still rebuilds in milliseconds, and making `instant` walk the actions
  instead of the steps is written down in the roadmap as what a 50000-step
  artwork will need first.

- **The A key** turns the sound off and on while the artwork runs. The
  listener's choice and the export's mute are separate flags, so finishing an
  export does not turn the sound back on for somebody who asked for silence.

- **Five sounds ship with the tool**, in `sounds/`, and none of them beeps: they
  sit between a chess piece set down on a board and a pencil on paper — `place`,
  `tap`, `slide`, `pencil`, `stroke`. They are synthesised by `tools/sounds.py`
  from decaying inharmonic partials over a click and from filtered noise with a
  grainy envelope, so the repository holds the recipe and every machine gets the
  same bytes. Measured: `place` peaks at 95 Hz, `tap` at 171 Hz.

- `lab/audio.flx` — sound is the one thing here a PNG cannot check, so the
  module counts what it did and the harness asserts it: zero cues after a
  rebuild, exactly one press of the track after three opens, two cues after four
  animated steps, and nothing at all while muted.

## [0.16.0] — 2026-08-16

### Added

- **`tools/cutout.py`** — takes the paper out of a photo of a drawing and writes
  it on transparency, cropped, ready to be a sprite or to be traced. It decides
  by two tests together, because both are needed: the paper is pale and grey, so
  everything the pencil or the paint touched is either coloured or darker than
  the sheet around it. `--shrink` pulls the edge in, which is what kills the pale
  halo of paper a photographed edge leaves around a sprite, and `--width` writes
  it small enough to fit the 1024×1024 sprite sheet.

- **`trace.py --emit svg`** — the same outlines as an SVG instead of turtle code,
  so a photograph can become a vector file that is kept, edited and traced again
  at any size. Plus `--blur`, without which a pencil line photographed on paper
  traces as a cloud of specks, and transparency handled properly: a cut-out is
  composited onto white first, so tracing it traces the drawing and not the hole
  it was cut from.

- **`erase_at(step, from, to)`** — `erase` on a step you choose. `erase` happens
  after everything that turtle has declared, which is right at the end of a file
  and wrong in a composition where something else has to happen first.

### Fixed

- **An erased stroke came back in the second pass.** The layered rebuild added in
  0.15.0 re-homed the turtles and reset their styles before its second pass, but
  did not re-apply the moves and the erases — so an artwork using a glow *and* an
  erase drew the erased strokes again. The preamble is now one function,
  `Runner.ready(upto)`, used by both passes
  ([adr 0018](adr/0018-a-stroke-can-be-drawn-in-layers.md)).

## [0.15.0] — 2026-08-16

### Added

- **Seven richer strokes** (pillars §4): `path_brush`, `path_marker`,
  `path_glow`, `path_spray`, `path_triangles`, `path_squares`, `path_stars`.
  They are style values on the same appearance event as the four that already
  existed, so they apply from the next step the turtle declares, the rebuild
  replays them, and they cost nothing per frame. The shape styles use the rhythm
  as size and spacing, so `path_dash(10, 24)` tunes them
  ([adr 0018](adr/0018-a-stroke-can-be-drawn-in-layers.md)).

  Measured over 600 segments: solid 50 ms, brush 49, spray 49, stars 64, marker
  117, glow 100 — the last two are drawn in two passes over the whole artwork,
  so an artwork containing one takes about twice as long to rebuild.

  `path_spray` scatters from the coordinates and not from a random number, so a
  rebuild, a replay and an export produce the same speckle — verified by
  rendering it twice and comparing the PNGs.

- `lab/brush.flx` — the eight looks over one wave, the cost of each, and the
  spray drawn twice.

### Fixed

- **A dash, a dot or a shape restarted at every segment.** The rhythm is now
  measured along the whole path: the painter keeps a per-turtle running length,
  records it on each segment, and starts the pattern from it. A figure written
  as a loop of short strokes gets an even row of shapes instead of one at every
  joint, and dotted and dashed strokes stopped resynchronising at corners.

## [0.14.0] — 2026-08-16

### Added

- **`tools/trace.py`** — an SVG or a raster image into turtle code.

  ```bash
  python3 tools/trace.py logo.svg --turtles 3 -o art.flx
  ```

  SVG needs nothing installed and keeps its shape: `path` with every command
  (`M L H V C S Q T A Z`, absolute and relative), `line`, `polyline`, `polygon`,
  `rect`, `circle`, `ellipse`, `transform` on elements and groups, `viewBox`,
  and colours from `stroke`, `fill` or `style`. A raster image needs Pillow and
  is traced by outlining its dark areas — the border of every shape and of every
  hole in it — which works on line art, logos and silhouettes and not on
  photographs.

  What it writes is ordinary turtle code: it animates, exports, and obeys
  `pivot`, `shift` and `erase`. Turtles draw in parallel, so the cost in steps
  is the longest turtle's run and `--turtles 4` costs about a quarter of the
  steps. `--max-steps` is a budget the tool meets by searching for the smallest
  simplification tolerance that fits, and it says which one it settled on.

  Verified against the geometry rather than by eye: a traced circle of radius
  100 in a 400×400 viewBox came out on the stage at 257.3–263.0 px from the
  centre against the 260 the fit arithmetic predicts, and a fixture with
  cubics, smooth cubics, quadratics, arcs, a rotated rect, a polyline, an
  ellipse and a scaled group rendered every one of them in the right place. The
  raster path was rewritten after its first version produced three fragments
  instead of a star — it now walks borders with Moore following, and traces the
  star and the hole inside it in 128 steps.

- `docs/TRACE.md`, and `tools/example.svg` to try it on.

## [0.13.0] — 2026-08-16

### Changed

- **An arrow implies a pause.** `←` and `→` no longer need SPACE first. Pressed
  while the artwork is still drawing, `→` means "finish this step and stop
  there" and `←` drops the step in flight — it was never committed — and unwinds
  the last completed one, leaving the animation immediately instead of waiting
  for the stroke to finish.

- **Going back is the step run the other way round**, over the same seconds it
  took to draw: the stroke shrinks back into the point it grew from and the
  turtle walks home. It is still a rebuild underneath, for the reason it always
  was — the artwork is recomputed from the code, never undone — so what is left
  on screen is exactly the drawing as it was at that step
  ([adr 0017](adr/0017-going-back-is-the-step-run-backwards.md)).

  Measured in `lab/rewind.flx`: 2050 ms back against 2017 ms forward for the
  same 400 px step at 200 px/s, ending exactly where the step began, with the
  result pixel-identical to the artwork at the previous step.

- Arming a step — who moves, from where to where, how long it takes, whether it
  draws — came out of `animate` into `Runner.arm`, with `Runner.span` for the
  duration. One place to arm a step, two ways to walk it.

## [0.12.0] — 2026-08-16

### Added

- **Ready-made shapes**: `polygon`, `triangle`, `square`, `rect`, `circle`,
  `ellipse`, `star` and `arc`. Each one is placed by its **centre**, in the same
  stage coordinates `toward` and `jump` use, opens with a pen-up move to its
  first vertex, closes on that vertex, and draws one side per step with whatever
  colour, width and style the turtle has at that step.

  ```fluxa
  int s = leo.circle(1, 400.0, 300.0, 120.0)
  s = leo.star(s, 400.0, 300.0, 90.0, 36.0, 5)
  s = leo.square(s, 400.0, 300.0, 60.0)
  ```

  They **return the next free step**, because a circle's step count depends on
  its radius and nobody should have to work it out. The return can be discarded:
  `leo.circle(1, ...)` on its own is legal.

  A curve picks its own number of sides — one per about 12 px of circumference,
  clamped to 12…90 — and `polygon` is how you choose instead. Figures sit flat:
  an odd number of sides gets a corner up and a horizontal side at the bottom,
  an even number gets a horizontal side top and bottom, which is the difference
  between a square and a diamond
  ([adr 0016](adr/0016-a-shape-is-a-batch-of-steps-that-returns-the-next-one.md)).

  Nothing in the runner, the painter or the timeline knows shapes exist — they
  are ordinary steps, so they animate side by side, move with `pivot`/`shift`
  and come back out with `erase`. Verified in `lab/shapes.flx`: the returned
  step of all eight against hand arithmetic, closure at the first vertex, and
  the outlines measured in the PNG against their intended centres and radii.

## [0.11.0] — 2026-08-16

### Added

- **The panel, on P** (`static/panel.flx`). Over the stage: the step and the
  last one declared, how many actions the timeline holds and how many it
  ignored, and one line per turtle — pen colour, position, accumulated heading,
  pen up or down. Up to eight lines, then `+ n more`. Off by default, and muted
  for the length of an export: a controlled render is the artwork, not the
  workshop.

  The strings are cached and rebuilt only when the step or the number of turtles
  changes — once per step, not sixty times a second — with every `strings.concat`
  intermediate released by hand (guide §12.5). The heading is deliberately not
  wrapped to 360: `1800 deg` says she has turned five whole times.

- **Pause and walk a step at a time.** `SPACE` stops the artwork where it is,
  mid-movement included; `→` animates exactly one step; `←` goes back one. Back
  is a **rebuild** to the previous step, not an undo of the last stroke, so
  erased ranges, `pivot`, `shift` and appearance changes resolve as they did at
  that moment. Pause is a state of the window: saving while paused carries on.

### Changed

- **The live stage is one loop instead of three.** Replay, animation and idle
  now share a single loop with the state in Block fields (`paused`, `forward`,
  `back`, `replay`), read in one place. `Runner.frame()` no longer presents the
  frame — callers draw the panel over it and call `end_frame`; `Runner.shown()`
  is the pair, which is what the harnesses use
  ([adr 0015](adr/0015-one-live-loop-and-a-panel-to-learn-with.md)).

### Fixed

- **SPACE did not pause.** The keyboard was read twice per presented frame — by
  the outer loop and again inside `animate`, which presents frames of its own —
  so every press was counted twice and pause toggled back in the same frame. The
  keyboard is now read only where a frame is presented.
- **Arrow presses were lost.** The key flags were cleared unconditionally at the
  end of each turn, which threw away arrows pressed while an animation was
  running. A flag is now cleared only by the branch that acts on it.

## [0.10.0] — 2026-08-15

### Added

- **A movement survives the save** (pillars §5, the last pillar still open).
  `main.flx` carries a fourth `prst` — `part = [0.0, 0.0]`, the step in flight
  and how far into it — which `animate` writes on every frame and clears when
  the step completes. The next run picks that step up at the same fraction.

  Measured end to end with an eight-second step and three saves during it: the
  turtle carried on from 43%, then from 78%, then finished, and never went back
  to the start. The stroke has no gap, because the in-flight segment is drawn
  from the step's start point on every frame.

### Fixed

- **A save used to complete the movement instead of interrupting it.** The
  runtime cancels a script by breaking the loop it is in and carrying on at the
  next statement — so a save inside `animate` fell through to the code that
  closes the step, and the artwork gained a whole stroke nobody watched being
  drawn. `Runner.arrived` now compares elapsed against duration after the loop,
  which is the only place that can tell a completed movement from a cancelled
  one, and a step that did not arrive is not counted
  ([adr 0014](adr/0014-a-movement-survives-the-save.md)).

  That behaviour was not what the plan assumed either: the note said saving
  *restarted* the step. It completed it. Worth measuring before designing.

## [0.9.0] — 2026-08-15

### Added

- **A turtle can be a picture** (pillars §3, the sprint the pillars call
  fundamental to the artistic side):

  ```fluxa
  leo.image("turtle.png", 0.6)                   // the whole file
  ana.sprite("sheet.png", 0, 0, 64, 64, 1.0)     // one region of it
  ```

  Both forms, because both are wanted: one turtle with her own file, or several
  sharing a spritesheet with a region each. Draw the art facing right and it is
  turned by her heading, so she points where she walks. No picture, or a file
  that cannot be read: she is a circle, as before.

  Every sprite is composed into one 1024×1024 sheet before the frame loop, since
  a body is drawn every frame and a Block cannot hold a `dyn` — so it is a local
  of `Runner.play` and one parameter carries every sprite in the artwork
  ([adr 0013](adr/0013-one-sheet-for-every-sprite.md)). Eight files; the scale
  belongs to the entry, so one picture at two sizes is two entries. `main.flx`
  never sees any of it.

- `lab/sprite.flx` — draws its own art, then six turtles: a file whole, the same
  file at half size, three regions of a sheet, and one left as a circle.

### Fixed

- Two shadowing bugs of the kind AGENTS.md already warns about, found by
  scanning every Block for locals and parameters that share a field's name:
  `int y` inside the Pool (which has `float arr y[32]`) and `int step` as a
  parameter of `Timeline.style_at` (which has `int arr step[65536]`). The scan
  is worth keeping — it is four lines of regex and it caught both.

## [0.8.0] — 2026-08-15

### Added

- **`erase(from, to)`** — takes a piece back out of a drawing: the strokes this
  turtle made between those two steps stop being drawn, and everything else of
  hers stays, before and after. It happens on the step after the last one she
  has declared — the appearance rule — so written at the end of a file it is the
  last thing that happens and the piece disappears on screen. Four ranges per
  turtle.

  A method and not a free function (`leo.erase(1, 8)`, not `erase(leo, 1, 8)`):
  every other call is already `leo.something(...)`, and a Block instance does not
  pass cleanly as an argument.

  `path_clear` remains the other eraser — it wipes everything up to a step;
  this one takes out a range and keeps the rest.

- **`docs/TURTLE.md`** — the reference: **one entry per call**, with its
  signature, a table saying what each argument is and what unit it is in, and
  the note that only matters for that call. Thirty-two entries, grouped by what
  they are for and labelled by when they take effect (declaration, appearance,
  step).

  Checked by script against `static/turtle.flx`: every call has an entry of its
  own, no entry describes a call that does not exist, no signature disagrees on
  arity, and no argument table describes a parameter the call does not take.

### Changed

- **The README keeps only the basics** and points at the guide. What is left is
  enough to draw something — spawn, a colour, `go`, `ring`, the three kinds of
  call in a table — and one short paragraph each for the stage and the export.
  The reference material moved out entirely, including the Exporter's long
  route, so nothing is written in two places and neither page can drift from
  the other.

## [0.7.0] — 2026-08-15

### Added

- **`toward` and `jump`** — walk to a point, or move there with the pen up. `go`
  says "turn this much and walk that far"; `toward` says "be here", and the turn
  and the distance are worked out when the step runs. It is what makes a drawing
  writable as a loop over its points, and what lets a shape sketched anywhere be
  printed straight out as steps. New action kinds in the timeline (3 and 4),
  resolved by `Runner.aim` at execution time.
- **`pivot` and `shift`** — move what a turtle has ALREADY drawn: turn her whole
  trail about a point, or displace it, from a given step on. The angle is
  absolute, so a loop can sweep it and land back where it started.

  This is what an animation of a part needs. Redrawing a flipper pose by pose
  works and looks wrong: every pose is thirty strokes, a step is never less than
  one frame, so the video shows a drawing being sketched and wiped rather than
  an animal swimming. With `pivot` the flipper is drawn once and only its angle
  changes — one angle per step, one frame per angle
  ([adr 0012](adr/0012-a-turtle-can-move-what-she-has-drawn.md)).

  A move repaints the artwork for that step, the same cost `path_clear` already
  had, and `max_step` counts it so the artwork does not end before the last one.

### Changed

- **`Painter.thick` closes its joints.** A thick stroke was a bundle of parallel
  lines with nothing at the ends, so a curve made of them had a pinhole at every
  joint — visible at width 2, ugly by width 4 — and an even width had no line
  down its middle at all, leaving a seam of background inside diagonal strokes.
  Now: a centre line for even widths, and a dot at each end that fills the wedge
  and gives a lone stroke a round cap. The 3000-segment rebuild went from 132 ms
  to ~160 ms for it.
- **`fluxa.toml` carries measured caps**, in the style of `nave/fluxa.toml`:
  `ast_pool_cap = 16384` (the artwork needs 5794 nodes; the default 4096
  overflows to a malloc per node) and `scope_cap = 512` (measured: 170 scopes).
  The string arena was measured too — the default is enough here, so it is left
  alone.

## [0.6.0] — 2026-08-15

### Added

- **"One Night"** — the first artwork with a story, a video and its own
  document: [docs/artworks/one-night.md](artworks/one-night.md). A sea turtle
  under a full moon, drawn as line art, and the broken light on the water she
  steers by. Thirteen turtles, 191 steps, 453 strokes.

  The line art is the piece's own lesson: the tool does not know what a turtle
  looks like. A shape is a list of points, and every stroke is the same two
  numbers as everything else — how far to turn from where the pen is pointing,
  and how far to walk.

  It is also the piece that shows what the tool grew this week: the tracks are
  dotted on the sand and solid in the water because appearance belongs to the
  step where it is written (0.2.0); the eight of them leave on the same step and
  arrive at their own pace; the video is one line, `export.Video(1, 0, 30)`
  (0.5.0); and the whole thing needs 21 of the 32 turtles the stage now holds
  (0.4.0).

  The document's code block was extracted, pasted into a copy of `main.flx` and
  rendered: pixel-identical to the published image. `lab/one_night.flx` is the
  same artwork as a harness.

- `docs/artworks/one-night.mp4` — ten seconds, written by `export.Video`, and
  the first video the repository carries. `.gitignore` keeps ignoring `*.mp4`
  except under `docs/artworks/`.



### Changed

- **Everything in `main.flx` is a declaration now** — anything that needs a
  window, a canvas, a frame loop or a file handle is recorded and carried out by
  the Runner, the same way `leo.go(3, ...)` has always declared a movement
  instead of performing one ([adr 0011](adr/0011-the-artwork-file-declares.md)):

  ```fluxa
  stage.Stage.tile("my_texture.png", 1.0)
  export.Video(1, 36, 5)                    // from, to, frames per second
  export.Frames(1, 36, 60)                  // the same, as numbered PNGs
  ```

  Asking for more steps than the artwork has generates what there is and says
  so, so the line survives the drawing growing under it.

- **`bg` is gone from the artwork file**, and with it the `bg` parameter of
  `play`, `export`, `movie` and `rebuild`. The Stage holds the path and the
  rebuild decodes it — once per save, into the baked texture, so the per-frame
  cost is unchanged. What is left in `main.flx` is the window, the canvas,
  `done`, and turtles.
- `static/exporter.flx` is now `static/export.flx`, so the artwork file reads
  `export.Video(...)`.

- **A render is never written over.** The video takes the first free name —
  `artwork.mp4`, `artwork1.mp4`, `artwork2.mp4` — and the frames folder does the
  same: `export/`, `export1/`, `export2/`. Saving with the export line still
  uncommented costs a render, not the previous one.

### Fixed

- **`Exporter.request` took its frame rate from the Block's field instead of its
  argument.** A parameter that shares a name with a field of its own Block
  resolves to the field, silently: `want_fps = fps` read 60 and ignored what was
  asked for, so `export.Video(1, 36, 5)` rendered at 60 fps. The whole project
  was scanned for the same pattern afterwards — this was the only one.
- **The window showed the desktop until the first frame.** Nothing is presented
  between `graph.init` and the first `graph.end_frame`, so the window keeps
  whatever was behind it. `Runner.open(win)` paints one cleared frame, and every
  harness calls it right after choosing the stage colour — `lab/limits.flx`
  rebuilds 6000 steps before presenting anything, and for that second the window
  was an editor, measured at 686 colours. `play` calls it too, but only when
  nothing has been drawn yet: on a save with an artwork on screen, clearing would
  throw it away for as long as the rebuild takes. Measured in `main.flx`, the
  window is the stage colour at 0.20 s with or without the fix — the first run
  rebuilds from `done = 0`, which is instant, so the artwork file never had a
  visible gap.
- **The background drew black.** `graph.draw_image` batches, and the Stage was
  releasing the decoded image before `graph.end_frame`, leaving the batch
  pointing at a texture that was gone. The image is now a local `dyn` in
  `Runner.rebuild`, alive for exactly the frame it is drawn in.

## [0.4.0] — 2026-08-15

### Changed

- **Bigger stage: 32 turtles (was 8) and 6000 steps (was 4095)**, with 65536
  actions, 2048 appearance changes and 8192 not-yet-baked segments. Every limit
  now lives in `static/config.flx` and every array that mirrors one says so — a
  Fluxa array is declared with a literal size, so a limit cannot be read from
  config at declaration time and the two are changed together. `Timeline.reset`
  checks its own grid stride against `MAX_STEPS` on every run and says so out
  loud if they ever drift.
- **`main.flx` is the stage, not a manual.** The two blocks that read like
  library code are one line each now:

  ```fluxa
  bg = stage.Stage.tiled(bg, "texture.png", 1.0)   // also centered / stretched
  runner.Runner.movie(win, canvas, bg, 1, 0, 60)   // from, to, fps
  ```

  `Stage.tiled/centered/stretched` load the file, release the old background and
  set the mode in the call; a missing file keeps the drawing running and prints
  why. `Runner.movie` renders the frames, writes `artwork.mp4` and deletes them,
  with half a second of stillness at each end. The Exporter route is unchanged
  for whoever wants the PNGs — it is documented in the README instead of sitting
  in the artwork file.
- `main.flx` takes the window size from `config.W()`/`config.H()` instead of
  repeating 800 and 600.
- The limits report themselves when reached: the action and appearance caps
  print once and drop the extra, the way the turtle cap already did.

### Added

- **F toggles fullscreen**, F again comes back — for two monitors: the code on
  one, the artwork filling the other. The stage keeps its logical size, scaled
  and letterboxed by the window, so `graph.capture`, the bake and the export do
  not notice. It answers in the live stage and during the animation, never
  during an export (adr 0006).
- `lab/limits.flx` — the pools at their declared size: 32 turtles with the 33rd
  warned and ignored, step 6000 accepted and 6001 refused, and the occupancy
  grid read back turtle by turtle at the far end of the range, which is what
  proves the stride keeps the rows apart. A 6000-step rebuild takes ~950 ms.
- `lab/video.flx` now covers both routes — the one-line `movie` and the long way
  that keeps the frames — and `lab/background.flx` covers the one-line
  background, including the missing-file path.

## [0.3.0] — 2026-08-15

### Added

- **Export straight to MP4**, with no ffmpeg and no external process.
  `Exporter.to_video(v, keep)` reads back the frames the export just wrote and
  appends them to a `std.video` cursor; `keep = 0` deletes each PNG as it goes in
  and removes the folder at the end. The cursor is opened and closed in
  `main.flx`, because a `dyn` cannot be a Block field — which is also why the
  video is a second pass instead of being fed from inside the frame loop
  ([adr 0010](adr/0010-the-video-is-a-second-pass-over-the-frames.md)).
- `Exporter.frame_path(i)` — the path of a numbered frame, now shared by `save`
  and `to_video`.
- `lab/video.flx` — exports 100 frames, turns them into an MP4, checks the
  folder is gone, then reads the video back: 800×600 at 30 fps, 100 frames, and
  a decoded frame from the middle saved as a PNG to prove it is the artwork and
  not a hundred empty images.
- `std.video` in `fluxa.toml`.

### Changed

- The render path is untouched: the export is byte-identical to 0.2.0 and the
  video is a function of those exact frames.
- `finish()` now prints the in-Fluxa MP4 recipe first, and keeps the ffmpeg
  commands for WebM, GIF and a hand-tuned x264.

## [0.2.0] — 2026-08-15

### Changed

- **An appearance change now applies from the step where it is written**, not to
  the whole artwork. `color`, `size`, `speed`, `show`, `hide` and every `path_*`
  go into the timeline as an event starting at the step after the last one that
  turtle has declared; the rebuild returns the pool to the born-with defaults and
  replays the events at their own step. Blue up to 36 and pink from 37 is now
  four lines, and the rosette does not change when you write them
  ([adr 0009](adr/0009-appearance-is-a-timeline-event.md)).

  `face` is deliberately not an event: it is the heading the turtle is born with.

  Existing artworks are unaffected — they all declare the look before the first
  movement, which is still "from step 1". What changes is code that declared a
  style *after* the steps: it used to repaint everything and now affects the
  steps that come after it, if any.

- **Segments not yet baked carry their own look.** The painter resolves colour,
  width, style and rhythm when a step closes and replays those on every frame,
  instead of asking the pool at draw time. Without it a change made two steps
  later leaked backwards until the next save.

### Added

- `lab/styles.flx` — five turtles, each changing one thing halfway: colour,
  width, style, opacity and the pen. Checks the rebuilt artwork and, on a second
  pass, the segments still held by the painter.
- `Timeline.styles()` and `Timeline.last_step(t)` — how many appearance events
  were declared, and the last step each turtle declared.
- `Pool.reset_styles()` — back to the born-with look, used by the rebuild.

### Fixed

- `lab/paths.flx` declared `path_opacity(60)` after the step it was checking, so
  the "100%" line was actually drawn at 60%. The line is gone and the four
  opacities in that harness now read 100, 60, 30 and 12 as documented.

### Documentation

- README: how to install the runtime from the language repository, what it needs
  to build, and that Turtle does not run on Windows yet.

## [0.1.0] — 2026-08-13

First working version. Covers pillars §1 to §7 and the part of §8 that does not
depend on a video encoder.

### Added

**Core**
- Step timeline with simultaneous execution: turtles with an action on the same
  step move together, and the step only ends when the last of them arrives.
- Conflict rule: a turtle only performs one action per step. The first declared
  wins, the second is ignored, and execution is not interrupted.
- Persistence across saves: finished steps do not repeat. The artwork is rebuilt
  instantly and only the new steps are animated.
- A pool of 8 turtles with independent state — position, heading, colour, size,
  speed and path configuration.

**The turtle**
- `spawn`, `color`, `size`, `face`, `show`, `hide`
- `speed` — default speed in pixels per second
- `go`, `go_silent` — displacement with and without a trail
- `go_at`, `go_silent_at` — speed declared on the action itself, which beats the
  turtle's own speed

**The path**
- `path_color`, `path_width`, `path_on`, `path_off`
- `path_solid`, `path_dotted`, `path_dashed`, `path_dots` — the four styles,
  each with its own default dash and gap
- `path_dash` — adjusts the rhythm of any style
- `path_opacity` — transparency from 0 to 100
- `path_clear` — clears one specific turtle's path, on a step, without touching
  her position or state

**The stage**
- `background` — solid colour
- `image_tile`, `image_center`, `image_stretch`, `image_scale`, `image_off` —
  an image as the background, going into the baked texture so it costs nothing
  per frame

**Replay**
- Key R redoes the whole artwork from step 1, animated. It is the same code path
  as normal execution.

**Export**
- Controlled render: time advances `1/fps` per frame, never by the clock. Two
  runs produce byte-identical frames.
- Configurable folder, frame rate, step range and still frames at each end.
- Output as a sequence of numbered PNGs, with the `ffmpeg` command printed ready
  to paste on completion.

**Documentation**
- `docs/ARTWORKS.md` — eight complete compositions ready to paste, each with the
  image that this exact code produces: rosette, square spiral, snail,
  eight-pointed star, hexagram, mandala, flower and target.
- `docs/RECIPES.md` — loose pieces: ready-made turtles, closed shapes,
  simultaneity, rhythm, styles, backgrounds and palettes.
- `docs/adr/` — eight design decisions, each with its reason and its cost.

**Verification**
- `lab/shot.flx` — pillar rules
- `lab/paths.flx` — styles, opacity and `path_clear`
- `lab/speed.flx` — each step's duration against the expected one
- `lab/stress.flx` — 3000 steps
- `lab/export.flx` — frame count and determinism
- `lab/background.flx` — the three background image modes
- `lab/preview.flx` — the `main.flx` artwork with everything on

### Performance

Measured on this machine (Intel/Mesa, 800×600):

| | |
|---|---|
| declaring 3000 steps | 8 ms |
| rebuilding 3000 segments and baking the texture | ~120 ms (once per save) |
| live stage with the whole artwork | 0–1 ms/frame |
| exporting 70 frames | 6.1 s for 2.3 s of video |

The per-frame cost does not grow with the artwork: the path lives in a cached
texture and is drawn with a single `graph.draw_image`.

### Fixed during development

- **Trail redrawn every frame.** The first version redrew every segment per
  frame, which stalled near 1400 segments. It now bakes into a texture with
  `graph.capture` + `image.blit`.
- **O(n²) action conflict.** The check scanned the whole queue on every
  declaration. It became an occupancy grid indexed by turtle × step, with a
  direct lookup. Declaring 3000 steps dropped to 8 ms.
- **O(n) timeline walk per step.** `instant` and `animate` scanned every action
  on each step. They now query the grid: eight lookups per step, one per turtle.
- **One extra frame per step when exporting.** Adding `1/fps` repeatedly
  accumulates rounding error and yielded 74 frames where 70 were due. The step
  now has a whole, exact frame count, with each instant computed from the index.
- **Unusable `ffmpeg` command.** It was built with a multi-argument `print`,
  which inserts spaces. It is now built with `strings.concat`.
- **Silent turtle-limit overflow.** Past 8 turtles, `spawn` returned slot 0 and
  the artwork came out wrong with no sign of it. It now warns and ignores.

### Known limits

- Opacity is a mix with the background, not an alpha channel: two translucent
  paths crossing do not add up.
- Saving in the middle of a movement restarts that step — partial progress does
  not survive the reload yet (pillars §5).
- A stroke's colour is the turtle's current one, not the one it had when the
  stroke was made. *(Changed in 0.2.0 — it is now the colour declared before that
  step.)*
- No video encoder: exporting delivers numbered PNGs.
- No `Turtle.image` (pillars §3) — the turtle is drawn with circles, because
  `graph.draw_image` has no rotation.
