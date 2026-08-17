# Roadmap

Everything left, from the two documents that specify this project: **Pilares do
Projeto** (§1–§10, the normative one) and **Futuras expansões** (§11, the long
horizon).

Each sprint says what it delivers, where it lands, **the design decision to make
before writing any code**, the constraints already known, and how it gets
verified — because nothing here is finished until a harness in `lab/` measures
it.

---

## Where the project stands

**The pillars are done except one.** §1 environment, §2 turtles, §3 appearance,
§5 movement, §6 persistence and live coding, §7 replay, §8 controlled export,
§9 the four modes of use, §10 identity — all built and verified.

| Pillar | State |
|---|---|
| §4 `Turtle.pathTexture` | **the last gap** — a path made of pictures, not lines |
| §1 animated / video background | partial: colour and image, no animation |
| §8 export options | partial: MP4, PNG, step range, fps, holds — no output size, codec, transparency, file name |

From the expansions, already built: advanced trails, glow, brushes, special path
effects, vector shapes, sprites and spritesheets, generative art, importing
characters from a drawing (`tools/cutout.py` + `tools/trace.py`), step-by-step
execution, manual advance, the step panel, the turtle-state panel, MP4, image
sequence, step ranges and frame rates.

---

## Known before it bites: the rebuild is O(steps), not O(actions)

The step limit was raised from 6000 to **50000** for the studio, and the caps
took it well — the occupancy grid went from 192032 to 1600032 slots, the process
from 101.4 MB to 134.5 MB, and `Timeline.reset` stayed at 0 ms because it clears
only what was written.

What did not take it well is the rebuild. It walks **every step from 1 to where
the artwork is**, asking all 32 turtles what they do on each one, so the worst
case the caps now allow measures **7.1 s** against about a second at 6000. That
is fine today, because an artwork of 500 steps still rebuilds in milliseconds —
and it is not fine for a studio, where 50000 steps is the point and every save
pays for them.

**Before any 50000-step artwork is usable, `instant` has to walk the actions
instead of the steps.** The timeline already holds them in declaration order;
what a step-by-step walk buys is the appearance events, which apply per step. A
sparse walk over "steps that have anything at all" is the shape of the answer.
Measure it against `lab/limits.flx`, which is exactly this worst case.

---

## Sprint 6 — `pathTexture` · the last pillar gap

**Deliver:** `leo.path_image("leaf.png", 0.4)` — the stroke stamped with a
picture instead of drawn as a line. Footprints, leaves, stars, symbols,
fragments. The pillars ask for it by name and it is the only §1–§10 item
missing.

Not blocked any more: `graph.draw_sprite(win, img, sx, sy, sw, sh, dx, dy, rot,
r, g, b, a)` rotates about the centre, tints and takes an alpha, and
`static/pool.flx` already uses it for the turtles' own bodies.

**Where:** `static/painter.flx` (one more style value, in the periodic loop that
already places shapes along the phase), `static/pool.flx` (which sheet slot),
`static/turtle.flx` (the call).

**Decide first — and this is the whole sprint:** the sprite sheet is a `dyn`,
which means it is a local of `Runner.play` and a Block cannot hold it
([adr 0013](adr/0013-one-sheet-for-every-sprite.md)). `Painter.paint` does not
have it and cannot be given a field for it. Either the sheet is threaded through
`draw`/`instant`/`paint` as a parameter, or the painter grows a "stamp" queue
that the runner drains while it still has the sheet in hand. The first is
simpler and touches more signatures; the second keeps the painter honest about
what it owns. Choose before writing anything.

**Constraints:** eight sprite files in total, shared with the turtles' own
pictures. A stamp is rotated by the path's direction, which is already computed
for the shape styles. The rhythm is the phase's, not the segment's
([adr 0018](adr/0018-a-stroke-can-be-drawn-in-layers.md)).

**Verify:** a ninth row in `lab/brush.flx` — count the stamps along a known
length, check the spacing is uniform across corners, and time the rebuild
against a plain stroke.

**Size:** small once the decision is made. Half of it is the decision.

---

## Sprint 7 — Movement with a shape · acceleration and duration

**Deliver:** `go_accel(step, dist, turn, start_px_s, end_px_s)` and
`go_silent_accel(...)` — a movement that begins at one speed and ends at
another — plus `go_for(step, dist, turn, seconds)`, a step declared by how long
it should take instead of how fast the turtle is.

**Accel replaces the easing this sprint used to propose**, and it is the better
spelling for this tool. `ease_in_out()` names a curve; "start at 100 px/s and
finish at 800" is the same curve said in the unit the person already has, which
is the same reason `circle(cx, cy, r)` beat working out a polar loop. A named
easing can always be added later on top of it.

**The arithmetic, so nobody re-derives it.** A speed ramping linearly from `v0`
to `v1` over distance `d` takes `T = 2d / (v0 + v1)` — the average speed, not
the final one — and the distance at time `t` is `v0·t + ½·a·t²` with
`a = (v1 - v0) / T`. Both are exact and cheap; `arm` already computes a
duration, and this is a different formula in the same place.

**Careful:** `v0 + v1` must not be zero, and a movement that starts and ends at
zero never arrives.

Every movement in the tool is linear today: `animate` walks the fraction
straight from 0 to 1. This is the cheapest large improvement left, and it is
what makes "animated scale", "animated transparency" and "simultaneous property
animations" from the expansions easy afterwards — they all want a curve.

**Where:** `static/runner.flx` (`animate` and `rewind`, one function applied to
`p`), `static/pool.flx` (the field), `static/turtle.flx` (the calls),
`static/timeline.flx` (a style kind, exactly as the path styles are).

**Constraints:** the easing must be a pure function of the fraction. The export
renders by frame index and two renders have to be identical
([adr 0006](adr/0006-deterministic-render-by-frame-index.md)) — anything reading
a clock inside the curve breaks that. `rewind` walks the same fraction
backwards, so the curve has to be applied there too or going back will not
retrace going forward.

`arm(s)` already computes a duration from distance and speed; `go_for` gives it
one instead, which is a smaller change than it sounds.

**Storage:** an action carries one speed today (`Timeline.get_speed`). Accel
needs a second one, which is one more array of `MAX_ACTIONS` floats — 65536
of them, about 512 KB. That is the decision to take before writing anything:
a second speed on every action, or a separate small table for the actions that
accelerate.

**Verify:** `lab/accel.flx` — the duration against `2d / (v0 + v1)`, the
position sampled at a quarter, a half and three quarters of the time against the
equation, that the total time is the same whichever end is faster, and that a
rewind of an accelerated step takes as long as the step did.

---

## Sprint 7b — `follow` · a whole trajectory in one call

**Deliver** (from the path proposal, renamed — see below):

```fluxa
follow(first, points, px_s)                        // -> next free step
follow_silent(first, points, px_s)
follow_accel(first, points, start_px_s, end_px_s)
follow_silent_accel(first, points, start_px_s, end_px_s)
```

One `(x, y)` list, one call, **one step per segment** — the step model is
untouched, and what shrinks is the artwork file, not the timeline. That is worth
being clear about: a traced drawing still costs 1345 steps, it just stops
costing 1345 lines.

**Not called `path`.** The turtle already has `path_color`, `path_width`,
`path_dotted`, `path_opacity`, `path_clear`, `path_on/off` — nine calls where
`path_` means *how the trail looks*. Hanging movement off the same prefix puts
two unrelated ideas under one word in the API a beginner reads first, and
`path_silent` is worse than ambiguous now that the tool has sound: it reads as
"make the path quiet". `follow(first, points, ...)` says what it does, and
`follow_silent` inherits the meaning `go_silent` already established.

**The `dyn` question, which is smaller than it looks.** `points` is a `dyn`, and
a Block field cannot hold one (adr 0013) — but `follow` does not need to hold
it. It reads the list once, at declaration time, and emits one `toward` per
segment into the timeline, exactly as `ring` emits its `go`s. A `dyn` arriving
as a method parameter is the pattern the canvas already uses. **No new
architecture.**

**Decide first, and measure it:** how big a `dyn` literal `main.flx` can hold.
A traced drawing is ~2700 floats in one literal, and the caps in `fluxa.toml`
size the AST — `ast_pool_cap` is 16384 and a full artwork measured 5794 nodes.
Whether a 2700-element literal fits, and what it costs to parse on every save,
is a ten-minute experiment and it decides whether `follow` is what `trace.py`
should emit.

**Accel over a path is distance-based**, as the proposal says, and that is not a
detail: points come out of a tracer unevenly spaced, so a progression by point
index would accelerate through dense regions and crawl through sparse ones. The
speed at a point is a function of the distance travelled so far over the total.

There are two ways to spend that, and they should be measured against each
other rather than argued about: give each segment a constant speed sampled at
its midpoint (a staircase, invisible at ~10 px a segment, and it needs nothing
new), or give each segment its own `v0`/`v1` (exactly smooth, and it needs
Sprint 7's second speed field).

**Verify:** `lab/follow.flx` — the returned step against the point count, the
drawing pixel-identical to the same trajectory written as individual `toward`
calls, and for the accel version the time of each segment against the
distance-based speed at its midpoint.

**Then:** `tools/trace.py` gets a `--emit follow` mode, and the artwork it
writes goes from 1944 lines to a few dozen.

---

## Sprint 8 — Text · a turtle that writes

**Deliver:** `leo.write(step, "hello", size)` — letters drawn as strokes, so
text animates, takes any path style, can be erased, pivoted, and exported like
everything else. `graph.draw_text` would be a different thing entirely: flat on
the frame, not part of the artwork, invisible to the bake.

**Where:** a new `static/font.flx` holding a stroke font — a segment list per
glyph — and `write` on the turtle emitting `jump`/`toward` from it.

**Decide first:** where the glyphs come from. Typing a stroke font by hand is
a week; **tracing one is an afternoon**, because `tools/trace.py` already turns
an image of a character set into outlines. A traced font is heavier per letter
(outlines, not single strokes) but it is the same pipeline the project already
verifies.

**Constraints:** step cost. A word is dozens of steps and a sentence is
hundreds; `write` must return the next free step exactly as the shapes do
([adr 0016](adr/0016-a-shape-is-a-batch-of-steps-that-returns-the-next-one.md)),
and the glyph table must be a Block field, so a literal-sized array per glyph.

**Verify:** `lab/text.flx` — the same string at three sizes, the returned step
against hand arithmetic, and the ink bounding box against the size asked for.

---

## Sprint 9 — Camera, layers, a scene larger than the screen

**Deliver:** the expansions' "Camadas de renderização", "Sistema de câmera com
deslocamento e zoom" and "Cenários maiores que a área visível" — three items,
one design.

**The largest thing left, and the one to read before planning.** The whole
performance story of this tool is that the path is baked into a texture the size
of the window with `graph.capture` + `image.blit`
([adr 0003](adr/0003-path-baked-into-a-texture.md)). `graph.capture` returns the
window. A world larger than the window cannot be baked that way.

**Found while wiring the sound, and it changes this sprint:** `std.graph`
already has a 2D camera —

```
graph.begin_cam2d(win, x, y, rot, zoom)   graph.screen_to_world(win, sx, sy)
graph.end_cam2d(win)                      graph.world_to_screen(win, wx, wy)
```

That is pan and zoom over *what is drawn*, which makes "look closer at the
artwork" a small feature: draw the baked canvas inside a camera and the whole
thing pans and zooms. What it does **not** solve is a world larger than the
window, because the bake only ever captured what the window could see. So this
sprint splits in two, and the first half is now easy.

**Decide first (for the second half):** whether `std.image` can be drawn into
off-screen — a surface that is not the window. That single question decides
everything:

- **if yes:** the bake becomes a world-sized image, the camera is an offset and
  a scale applied when it is drawn to the window, and layers are several such
  images composited in order. Clean, and the per-frame cost stays one blit per
  layer.
- **if no:** the bake stays window-sized and the camera has to re-run the
  rebuild whenever it moves — which is 160 ms per camera movement, so panning
  would have to be a step-level event like `pivot` is, not a smooth thing.

Read `fluxa-docs/STDLIB.md` on `std.image` first, write the answer into an ADR,
and only then plan the sprint.

**Verify:** a harness that draws a 2000×1500 scene, points the camera at three
places, and checks each capture against the region it should show.

---

## Sprint 10 — Export options

**Deliver, in the order they are worth doing:**

1. **Output size** — render at 1920×1080 from an 800×600 stage. The export
   already renders by frame index, so this is a scale on the capture, not a new
   pipeline.
2. **A file name** — `export.Video(1, 0, 30, "leonardo")`. Today it is
   `artwork.mp4`, `artwork1.mp4`, …
3. **WebM and GIF** — `std.video` writes H.264 only. The frames are already
   written and `finish()` already prints the ffmpeg line
   ([adr 0010](adr/0010-the-video-is-a-second-pass-over-the-frames.md)); this is
   about making that path pleasant, not about writing an encoder.
4. **Transparent background** — needs the stage to have no colour and the
   capture to keep alpha. Check what `graph.capture` returns before promising
   it.

**Verify:** extend `lab/video.flx` — frame count, size and rate of each output,
and two runs byte-identical.

---

## Sprint 11 — Audio — DONE (project 0.17.0)

The runtime was swapped and now answers `miniaudio/0.11.25`. Built and shipped:
`audio.Track`, `audio.Cue`, `audio.Volume`, the **A** key, and five synthesised
sounds in `sounds/`. See
[adr 0019](adr/0019-sound-crosses-the-save-and-a-rebuild-is-silent.md) and
`lab/audio.flx`.

**What is still open here:** audio in the exported video. `std.video` writes
H.264 with no audio track, and a controlled render does not run at watching
speed, so a soundtrack over an export has to be muxed by timestamp — the same
answer adr 0010 gives for WebM. That belongs to Sprint 10.

The rest of this section is kept because it is what was known before, and it was
all confirmed by the build:

**Good news from the API**: `sound.init()`, `sound.load(eng, path)` and the rest
return **`int` handles, not `dyn`**. A Block can hold an int. So the sound engine
and the loaded sounds can live in a `static/audio.flx` singleton in the house
pattern, with none of the gymnastics the window and the canvas need.

```
sound.init() -> eng        sound.play(eng, h)      sound.volume(eng, h, v)
sound.load(eng, path) -> h sound.stop / pause / resume / is_playing
sound.tone(eng, hz, ms)    sound.close(eng)
```

**Deliver:** the expansions' four audio items — music, effects synchronised with
the steps, volume, musical events on the timeline:

```fluxa
audio.Track("sea.mp3")            // plays while the artwork runs
leo.sound(120, "splash.wav")      // on step 120, when that step runs
```

**Where:** a new `static/audio.flx` (the engine, the loaded table, volume), one
timeline event kind for "play this on this step", `static/turtle.flx` for the
call, `main.flx` for the track.

**Decide first — and this one has a trap the rest of the project already met:**
a **rebuild replays the whole artwork instantly**. If a sound event fires during
a replay, a save on step 400 fires four hundred sounds at once. Sound must be
audible only while a step is being *animated*, never during `instant`, and
`Panel.mute` is the precedent for how that is expressed.

**And the export has no answer yet.** A controlled render runs faster or slower
than real time, so audio cannot be recorded live; it has to be muxed by
timestamp. If `std.video` has no audio track, the honest deliverable is: sound
live, and a printed ffmpeg line that muxes the exported MP4 with a WAV the
export writes from the timeline — the same shape as the WebM answer in adr 0010.
Decide that before building, and write it into an ADR.

**Verify:** a harness cannot listen. It can check that `sound.version()` is not
a stub, that a step's event is registered once and not once per rebuild (a
counter in the audio Block, asserted after three rebuilds), and that the muxed
file has the duration the timeline says.

---

## Sprint 12 — The rest of the educational panel

**Deliver:** the queue of actions still to come — what each turtle is about to
do, two or three steps ahead — and visual debugging: heading arrows, the point a
`pivot` turns about, the coordinate under the pointer.

**Where:** `static/panel.flx`. Everything it needs is already exposed —
`Timeline.action_of`, `get_kind`, the pool's `get_*`.

**Constraints:** the panel's strings are cached and rebuilt only when the step
changes, never inside the frame loop (guide §12.5,
[adr 0015](adr/0015-one-live-loop-and-a-panel-to-learn-with.md)). A queue view is
more strings; the cache rule does not bend for it.

**Not reachable:** "destaque da linha atualmente em execução". Nothing hands a
running Fluxa program its own source position. If the language ever exposes it,
this becomes trivial; until then it is not a sprint, it is a language request.

---

## Sprint 13 — Particles, gradients, animated backgrounds

The expansions' remaining visual list, roughly in order of what the tool can
already almost do.

- **A particle system proper.** `path_spray` scatters dots along a stroke, which
  is the shape of the idea but not the thing: no emitter, no lifetime, no
  gravity. A real one wants a pool in the house pattern (`nave/static/burst.flx`
  is the reference) and a decision about whether particles are baked — they
  cannot be, if they move, which makes them the first thing in this project that
  costs per frame.
- **Gradients.** The painter mixes a colour with the stage for opacity
  ([adr 0008](adr/0008-opacity-by-mixing-with-the-background.md)); a gradient
  along the path is the same mix with the phase as the factor, and the phase
  already exists.
- **Animated background, and video as a background** (§1). The stage holds a
  path and decodes once per rebuild; an animation means a sequence and a clock,
  and it costs per frame, so it needs the same measurement the bake got.
- **Shadow and lighting.** Cheap version: the same stroke offset and darkened,
  drawn in the halo pass that markers and glows already use.

---

## Sprint 14 — Extensibility

The longest horizon in the expansions, and the least specified: a library of
ready-made objects, composed objects, reusable components, plugins, agents that
are not turtles, integration with Fluxa's other graphics libraries.

Two of these are close. **A library of ready-made objects** is `docs/RECIPES.md`
plus the eight shapes, one step away from being a `static/objects.flx` anyone
can call. **Composed objects** — a group of turtles that move together — is
`pivot`/`shift` applied to several turtles at once, which is a loop and a name.

The other three are architecture, not features, and none of them should be
designed before something actually needs them.

---

## Order, and why

1. **Sprint 6** — the last pillar item, and small now that rotation exists.
2. **Sprint 7b** before **7**, if the studio is the goal. `follow` is
   independent of everything else, it is what `trace.py` should have been
   emitting all along, and a studio that records a hand moving produces exactly
   one thing: a list of points. Accel is the bigger visual change; `follow` is
   the one the rest of the plan leans on.
3. **Sprint 7** — the biggest visible change per line of code, and it unblocks
   half of the expansions' animation list.
4. **Sprint 8** — text is the most asked-for thing in a turtle tool that does
   not have it.
5. **Sprint 10** — export options are small, independent, and each one is
   immediately useful.
6. **Sprint 12** — the panel is cheap to extend and it is the teaching half of
   the project.
7. **Sprint 9** — the camera is the largest and it should wait until the
   off-screen question is answered on paper.
8. **Sprints 13 and 14** — when there is an artwork that wants them.

Sprint 11 (audio) is done.

Sprints 6, 7, 8, 10 and 12 are independent of each other and can be done in any
order. 9 and 11 each have a question to answer before any code.
