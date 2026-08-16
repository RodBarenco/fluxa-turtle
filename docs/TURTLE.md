# The turtle — every call, one by one

The [README](../README.md) shows enough to draw something. This page is the
reference: every call the turtle has, what each argument means, and when it
takes effect.

```fluxa
Block leo typeof turtle.Turtle
leo.spawn(340.0, 363.0)
```

Angles are in degrees: **0 points right** and the angle grows counter-clockwise,
as on the cartesian plane. The stage is 800×600, `y` grows downward, and both
numbers are in `static/config.flx`.

**Types are not converted for you.** A parameter declared `float` needs `340.0`,
not `340`; one declared `int` refuses `3.0`. That is the language, and it is the
most common first error.

---

## The three kinds of call

Knowing which kind a call is explains most of what surprises people:

| Kind | When it takes effect |
|---|---|
| **declaration** | at once, before anything runs |
| **appearance** | from the **next step this turtle declares** — never backwards |
| **step** | on the step number you give it |

```fluxa
leo.path_color(90, 200, 255)   // no step declared yet: her starting colour
leo.ring(1, 36, 500.0, 170.0)  // steps 1 to 36 come out blue

leo.path_color(255, 90, 160)   // from here on
leo.ring(37, 36, 500.0, 170.0) // steps 37 to 72 come out pink
```

To change what is already drawn, move the call above the steps it should affect
([adr 0009](adr/0009-appearance-is-a-timeline-event.md)).

---

# Being born

### `spawn(x, y)` — declaration

Puts her on the stage. Every turtle needs it, first.

| | |
|---|---|
| `x`, `y` | `float` — where she starts, in pixels from the top-left |

The point she is spawned at is also the point she returns to when the artwork is
rebuilt or replayed. Past 32 turtles, `spawn` warns and the extra one is
ignored.

### `face(deg)` — declaration

The heading she is **born** with.

| | |
|---|---|
| `deg` | `float` — degrees; 0 is right, 90 is up, 180 is left |

Not a step and not an appearance: it is part of her declaration, so a replay
starts her pointing the same way. Turning *during* the drawing is what the
`turn` argument of `go` does.

---

# Her own body

### `color(r, g, b)` — appearance

The colour of the turtle herself, not of her trail.

| | |
|---|---|
| `r`, `g`, `b` | `int` — 0 to 255 |

Only visible when she is shown and has no picture.

### `size(s)` — appearance

Her body radius, in pixels.

| | |
|---|---|
| `s` | `float` — radius; the head is drawn at 55% of it |

### `show()` · `hide()` — appearance

Whether she is drawn at all. Hidden, she still moves and still draws her trail —
most artworks hide every turtle, because the turtle is the instrument and the
trail is the picture.

### `speed(px_s)` — appearance

Her default speed.

| | |
|---|---|
| `px_s` | `float` — pixels per second |

This is what decides how long a step takes, on screen and in the video: a step
of 200 px at 200 px/s lasts a second. A speed declared on the action itself
(`go_at`) beats this one.

---

# A picture instead of a circle

### `image(path, scale)` — declaration

Draws her as a whole PNG.

| | |
|---|---|
| `path` | `str` — the file, relative to where you run `fluxa` |
| `scale` | `float` — 1.0 is the file's own size, 0.5 is half |

Draw the art **facing right**: it is turned by her heading, so she points where
she walks. A file that cannot be read prints why and she stays a circle.

### `sprite(path, sx, sy, sw, sh, scale)` — declaration

The same, using one region of a spritesheet — several turtles, one file, a
different look each.

| | |
|---|---|
| `path` | `str` — the sheet |
| `sx`, `sy` | `int` — the region's top-left corner, in the **file's own pixels** |
| `sw`, `sh` | `int` — the region's width and height |
| `scale` | `float` — applied to the region as well |

Every sprite in the artwork is composed into a single 1024×1024 sheet before the
frame loop starts, because a body is drawn every frame and decoding a PNG that
often is not affordable ([adr 0013](adr/0013-one-sheet-for-every-sprite.md)).
Eight files; the scale belongs to the entry, so the same picture at two scales
is two entries and two turtles can wear it at different sizes. Transparency
comes from the file: a PNG with no alpha channel brings its background along.

---

# The stroke

### `path_color(r, g, b)` — appearance

| | |
|---|---|
| `r`, `g`, `b` | `int` — 0 to 255 |

### `path_width(w)` — appearance

| | |
|---|---|
| `w` | `int` — pixels |

A thick stroke is a bundle of parallel lines with a dot at each end, so corners
close and caps are round. A very short stroke at a large width therefore reads
as a dot.

### `path_opacity(pct)` — appearance

| | |
|---|---|
| `pct` | `int` — 0 (invisible) to 100 (solid); outside that it is clamped |

Opacity here is a **mix with the background colour**, not an alpha channel:
two translucent strokes crossing do not add up
([adr 0008](adr/0008-opacity-by-mixing-with-the-background.md)). It is folded
into the stroke when it is drawn, so changing it later does not repaint what is
already there.

### `path_solid()` · `path_dotted()` · `path_dashed()` · `path_dots()` — appearance

The four styles. Each sets its own rhythm:

| Style | Dash | Gap |
|---|---|---|
| `path_solid` | — | — |
| `path_dotted` | 2 | 6 |
| `path_dashed` | 14 | 9 |
| `path_dots` | 1 | 12 (round dots, radius = half the width) |

`path_solid` leaves the rhythm alone, so going back to solid and then to dotted
keeps whatever `path_dash` you had set.

### `path_dash(dash, gap)` — appearance

Adjusts the rhythm of whichever style is on.

| | |
|---|---|
| `dash` | `int` — length of the mark, in pixels |
| `gap` | `int` — space before the next one |

### `path_on()` · `path_off()` — appearance

Whether she leaves a trail. `path_off` is for moving through the scene without
drawing — the same thing `go_silent` does for one movement.

---

# Walking

The first argument of every one of these is the **step**: the composition's
logical moment. Turtles with actions on the same step move together, and the
step ends when the last of them arrives. A turtle gets one action per step — a
second one on the same number is ignored, and the run is not interrupted.

Saving while a movement is in flight does not cost it: the step carries on from
the fraction it had reached, and only a step that actually arrived is counted as
done ([adr 0014](adr/0014-a-movement-survives-the-save.md)).

### `go(step, dist, turn)` — step

Turn, then walk, leaving a trail.

| | |
|---|---|
| `step` | `int` — 1 to 6000 |
| `dist` | `float` — pixels; negative walks backwards |
| `turn` | `float` — degrees to turn **before** setting off; positive is counter-clockwise |

```fluxa
leo.go(1, 200.0, 0.0)      // straight ahead
leo.go(2, 200.0, 144.0)    // turn 144° first — five of these draw a star
```

### `go_silent(step, dist, turn)` — step

The same displacement with no trail. This is how a turtle enters the scene,
crosses it, or leaves.

### `go_at(step, dist, turn, px_s)` — step

`go` with the speed declared on the action.

| | |
|---|---|
| `px_s` | `float` — pixels per second, for this movement only |

It beats her own `speed`, which is how one turtle sprints on one leg and crawls
on the next.

### `go_silent_at(step, dist, turn, px_s)` — step

Both at once: no trail, own speed.

---

# Walking in batches

Repeating one movement is what draws almost every figure, so the loop lives
inside the method — one call declares a run of steps.

### `ring(first, count, dist, turn)` — steps

| | |
|---|---|
| `first` | `int` — the step the run starts on |
| `count` | `int` — how many steps |
| `dist` | `float` — pixels per step |
| `turn` | `float` — degrees before each one |

```fluxa
leo.ring(1, 36, 470.0, 170.0)
```

A turn that divides 360 closes a polygon; one that does not draws a rosette —
170° never retraces its path and closes after seventeen laps.

### `ring_silent(first, count, dist, turn)` — steps

The same run with no trail.

### `spiral(first, count, dist, grow, turn)` — steps

A ring whose side grows.

| | |
|---|---|
| `grow` | `float` — pixels added to `dist` on every step |

```fluxa
leo.spiral(1, 60, 12.0, 14.0, 90.0)   // a square spiral
```

---

# Walking to a point

### `toward(step, x, y)` — step

Be at this point. The turn and the distance are worked out when the step runs,
from wherever she is standing.

| | |
|---|---|
| `x`, `y` | `float` — the destination, in screen pixels |

She ends up facing the point she walked to, so a `go` afterwards carries on from
that heading. This is what makes a shape writable as a loop over its points:

```fluxa
int i = 0
while i <= 72 {
    float a = math.to_float(i) * 5.0
    float r = 150.0 * math.cos(math.deg_to_rad(a * 2.0))
    rose.toward(5 + i, 560.0 + r * math.cos(math.deg_to_rad(a)),
                       300.0 - r * math.sin(math.deg_to_rad(a)))
    i = i + 1
}
```

### `jump(step, x, y)` — step

The same move with the pen up: how one line ends and the next begins.

---

# Erasing

Two erasers, and they do different things.

### `path_clear(step)` — step

On that step, everything this turtle has drawn **up to then** is gone.

| | |
|---|---|
| `step` | `int` — when it happens |

Her position, heading and colours are untouched: she carries on from where she
is, on a canvas of her own that is now empty. Being a timeline action, a replay
redoes the clearing at the same point.

### `erase(from, to)` — step

Takes a **piece** out: the strokes she made between those two steps stop being
drawn, and everything else of hers stays, before and after.

| | |
|---|---|
| `from`, `to` | `int` — the first and last step to remove, inclusive |

```fluxa
leo.ring(1, 12, 55.0, 0.0)   // twelve strokes in a row
leo.erase(5, 8)              // and the middle four are not there
```

It happens on the step **after the last one she has declared**, so written at
the end of a file it is the last thing that happens and you watch the piece
disappear — the artwork runs to that step even if nobody moves on it. Four
ranges per turtle.

Neither eraser touches another turtle's drawing.

---

# Moving what is already drawn

These two do not draw. They move **what that turtle has drawn**, all of it,
including strokes from two hundred steps earlier.

### `pivot(step, deg, cx, cy)` — step

Turns her whole trail about a point.

| | |
|---|---|
| `step` | `int` — when it happens |
| `deg` | `float` — **absolute** angle, not added to the last one |
| `cx`, `cy` | `int` — the point she turns about, in screen pixels |

Absolute is what makes an animation possible: a loop can sweep the angle and
land exactly where it started, and `pivot(s, 0.0, x, y)` puts the drawing back
where it was drawn.

```fluxa
int k = 0
while k < 60 {
    fin.pivot(300 + k, 16.0 * math.sin(math.deg_to_rad(math.to_float(k) * 6.0)), 467, 470)
    k = k + 1
}
```

That is a flipper beating: drawn once, then turned a few degrees per step. One
angle per step is one frame of the video. Redrawing a pose stroke by stroke
instead looks like sketching, because a step is never less than one frame
([adr 0012](adr/0012-a-turtle-can-move-what-she-has-drawn.md)).

### `shift(step, dx, dy)` — step

Displaces her whole trail.

| | |
|---|---|
| `dx`, `dy` | `int` — pixels, absolute, from where the strokes were drawn |

**Both cost a repaint.** The strokes are already in the baked texture, so the
step a move happens on rebuilds the artwork — about 20 ms for a 900-action
drawing. The turtle herself does not move: her position, heading and next step
are untouched.

---

# Everything at a glance

| Call | Kind |
|---|---|
| `spawn(x, y)` · `face(deg)` | declaration |
| `image(path, scale)` · `sprite(path, sx, sy, sw, sh, scale)` | declaration |
| `color(r, g, b)` · `size(s)` · `show()` · `hide()` · `speed(px_s)` | appearance |
| `path_color(r, g, b)` · `path_width(w)` · `path_opacity(pct)` | appearance |
| `path_solid()` · `path_dotted()` · `path_dashed()` · `path_dots()` · `path_dash(d, g)` | appearance |
| `path_on()` · `path_off()` | appearance |
| `go(step, dist, turn)` · `go_silent(...)` · `go_at(..., px_s)` · `go_silent_at(...)` | step |
| `ring(first, count, dist, turn)` · `ring_silent(...)` · `spiral(..., grow, turn)` | steps |
| `toward(step, x, y)` · `jump(step, x, y)` | step |
| `path_clear(step)` · `erase(from, to)` | step |
| `pivot(step, deg, cx, cy)` · `shift(step, dx, dy)` | step |

---

# The stage, and everything that is not a turtle

### `stage.Stage.background(r, g, b)`

The stage colour, under everything.

### `stage.Stage.tile(path, scale)` · `center(path, scale)` · `stretch(path)`

A PNG as the background: repeated across the surface, drawn once in the middle,
or taken to the screen size. `stage.Stage.image_off()` goes back to the plain
colour.

You give the Stage a **path**, never an image: the file is decoded during the
rebuild, once per save, and goes into the baked texture, so it costs nothing per
frame. A file that cannot be read prints why and the drawing carries on
([adr 0011](adr/0011-the-artwork-file-declares.md)).

### `export.Video(from, to, fps)` · `export.Frames(from, to, fps)`

| | |
|---|---|
| `from`, `to` | `int` — the step range; `0` as `to` means "through the last one" |
| `fps` | `int` — frames per second, 1 to 240 |

Neither renders when it is called: they record what was asked for, and the
Runner delivers it when execution reaches the stage. Asking for more steps than
the artwork has generates what there is and says so. The video is `artwork.mp4`,
then `artwork1.mp4` — nothing is ever written over, and the frames folder
rotates the same way.

`export.Video` adds half a second of stillness at each end and deletes the PNGs
once they are in the file.

### The long way, when you want the frames

```fluxa
export.Exporter.setup("frames", 60)     // folder and frame rate
export.Exporter.hold(30, 90)            // still frames at the start and the end
export.Exporter.range(1, 5)             // only part of the artwork
runner.Runner.export(win, canvas, sheet)
```

That leaves a folder of numbered PNGs — what an editor, a print or a contact
sheet wants. To turn them into a video and keep them:

```fluxa
danger {
    dyn mp4 = video.open("artwork.mp4", config.W(), config.H(), export.Exporter.get_fps())
    export.Exporter.to_video(mp4, 1)    // 1 keeps the PNGs, 0 deletes them
    video.close(mp4)
}
if err != nil { print("video: ", err[0]) }
```

The video is a second pass over exactly those frames, not a different render
([adr 0010](adr/0010-the-video-is-a-second-pass-over-the-frames.md)). For WebM
or GIF the frames are still there and `finish()` prints the ffmpeg command.

---

# Watching it, key by key

None of this is written in the artwork: it is the window, and it works on any
composition. With the window focused:

| Key | What it does |
|---|---|
| **P** | The panel, over the stage. Off by default. |
| **SPACE** | Pause / carry on. |
| **→** | One step forward, animated. Only while paused. |
| **←** | One step back. Only while paused. |
| **R** | Replay from step 1. |
| **F** | Fullscreen, and back. |

### The panel

```
step 12 / 36   .   3 turtles
48 actions   .   0 ignored   .   PAUSED
■ #0   400,300   1800 deg   drawing
■ #1   112,205      90 deg   pen up
```

- **step 12 / 36** — where the artwork is, and the last step declared. If the
  second number grew after a save, the steps you just wrote were read.
- **48 actions · 0 ignored** — how many actions the timeline holds, and how many
  it refused. *Ignored* is almost always the same turtle given two actions on
  one step: the first one wins and the second is dropped, which is the usual
  reason a stroke you wrote never shows up.
- **one line per turtle** — her pen colour as a swatch, then position, heading
  and whether the pen is down. The heading is not wrapped to 360 on purpose: an
  accumulated `1800 deg` tells you she has turned five whole times, which a `0`
  would hide. Up to eight lines, then `+ n more`.

The panel is never in an export. `export.Video` and `export.Frames` mute it for
the duration of the render and give it back afterwards — a controlled render is
the artwork, not the workshop.

### Pausing, and walking a step at a time

`SPACE` stops the artwork where it is, mid-movement included: the turtle holds
the position the last frame gave her. From there, `→` animates exactly one step
and `←` goes back one.

Back is a **rebuild**, not an undo: the artwork is drawn again from step 1 up to
the step before, so what you see is the drawing as it was then — erased ranges,
`pivot`, `shift` and appearance changes all resolved the way they were at that
moment. It costs one rebuild (~160 ms for a large artwork), which is why it is a
key you press, not something that happens per frame.

Pausing is a state of the window, not of the artwork: it touches neither the
file, nor the progress that crosses a save, nor the export. **Saving while
paused carries on** — the new steps are read and animated, which is what you
saved for. Press SPACE again if you wanted to stay stopped.

---

# Limits

| | |
|---|---|
| turtles | 32 |
| steps | 6000 |
| actions, all turtles together | 65536 |
| appearance changes and moves | 2048 |
| erased ranges, per turtle | 4 |
| sprite files | 8, composed into one 1024×1024 sheet |
| strokes not yet baked | 8192 |

All of them are in `static/config.flx`, and each is mirrored by an array
declaration the file points at — a Fluxa array is declared with a literal size,
so the two change together. Going past one prints a warning and ignores the
extra; it never corrupts the drawing quietly.

---

# Where to look next

- **[ARTWORKS.md](ARTWORKS.md)** — complete compositions, each with the image
  the code produces.
- **[artworks/one-night.md](artworks/one-night.md)** — the large one: line art,
  a flipper beat, a video and the story behind it.
- **[RECIPES.md](RECIPES.md)** — loose pieces: ready-made turtles, closed
  shapes, palettes, rhythm tricks.
- **[adr/](adr/)** — why each of these decisions is the way it is.
