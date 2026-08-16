# Changelog

All notable changes to this project.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

- **`docs/TURTLE.md`** — the full guide: every call the turtle has, grouped by
  *when* it happens (declaration, appearance, step), with the gotchas that
  follow from that and the limits at the end. Checked by script against
  `static/turtle.flx`: the guide names every call and invents none.

### Changed

- **The README keeps only the basics** and points at the guide. What is left is
  enough to draw something — spawn, a colour, `go`, `ring`, the three kinds of
  call in a table — and the reference lives in one place instead of two.

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
