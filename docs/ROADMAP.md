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

## Sprint 7 — Movement with a shape · easing and duration

**Deliver:** `ease_in()`, `ease_out()`, `ease_in_out()`, `ease_off()`, and
`go_for(step, dist, turn, seconds)` — a step declared by how long it should
take instead of how fast the turtle is.

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

**Verify:** `lab/ease.flx` — time each easing over the same step (the total must
not change), and sample the position at 25%, 50% and 75% against the curve's own
numbers. Plus one PNG with four turtles racing the same distance under the four
curves.

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

**Decide first:** whether `std.image` can be drawn into off-screen — a surface
that is not the window. That single question decides everything:

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

## Sprint 11 — Audio · **waiting on a runtime**

Measured today, with `std.sound = "1.0"` added to `fluxa.toml`:

```
fluxa-sound/1.0 (stub — no audio device)
```

The binary in this repository has no miniaudio compiled in. Everything below
waits for a build that does — and the day it arrives, the first thing to run is
that one line, because a stub answers every call successfully and plays nothing,
exactly like the graphics stub does.

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
2. **Sprint 7** — the biggest visible change per line of code, and it unblocks
   half of the expansions' animation list.
3. **Sprint 8** — text is the most asked-for thing in a turtle tool that does
   not have it.
4. **Sprint 10** — export options are small, independent, and each one is
   immediately useful.
5. **Sprint 12** — the panel is cheap to extend and it is the teaching half of
   the project.
6. **Sprint 9** — the camera is the largest and it should wait until the
   off-screen question is answered on paper.
7. **Sprint 11** — audio, the day the runtime can make a sound.
8. **Sprints 13 and 14** — when there is an artwork that wants them.

Sprints 6, 7, 8, 10 and 12 are independent of each other and can be done in any
order. 9 and 11 each have a question to answer before any code.
