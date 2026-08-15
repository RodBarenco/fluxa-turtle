# Changelog

All notable changes to this project.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
