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

### The richer strokes — appearance

Seven more looks, and they are the same kind of call as the four above: an
appearance change that applies from the next step this turtle declares.

| Call | What it is |
|---|---|
| `path_brush()` | the width breathes along the stroke, like a loaded brush |
| `path_marker()` | a translucent halo the width of the nib, with a solid core |
| `path_glow()` | drawn three times, wide and faint to narrow and solid: neon |
| `path_spray()` | dots scattered around the line, thicker near it |
| `path_triangles()` | triangles repeated along the path, pointing the way she walks |
| `path_squares()` | the same with squares |
| `path_stars()` | the same with five-pointed stars |
| `path_image(path, scale)` | a **picture** stamped along the path, turned the way she walks |

```fluxa
leo.path_glow()
leo.path_width(3)
leo.ring(1, 36, 500.0, 170.0)
```

The three shape styles use the rhythm as **size and spacing**, so `path_dash(10,
24)` makes them bigger and further apart. Their default is a size the stroke's
width looks right against.

The rhythm — dots, dashes, shapes — belongs to the **path**, not to each
segment: it runs continuously through corners, so a figure written as a loop of
short strokes gets an even row of shapes instead of one at every joint
([adr 0018](adr/0018-a-stroke-can-be-drawn-in-layers.md)).

**What they cost.** Nothing per frame — they are baked like every other stroke.
They cost the **rebuild**, which happens once per save. Measured over 600
segments: solid 50 ms, brush 49, spray 49, stars 64, marker 117, glow 100. A
marker or a glow is drawn in two passes over the whole artwork — every halo
first, every core over them, because otherwise each halo covers the previous
core and the stroke comes out looking dashed — so an artwork containing one
takes about twice as long to rebuild. That is the price of the look, and it is
worth knowing before painting three thousand segments with it.

`path_spray` is scattered from the coordinates and not from a random number: a
rebuild, a replay and an export all produce the same speckle.

### `path_image(path, scale)` — declaration

A path made of pictures: footprints, leaves, symbols, a fragment of a drawing —
stamped along the stroke instead of a line drawn along it, each one turned the
way she is walking.

```fluxa
leo.path_image("leaf.png", 0.5)
leo.path_dash(0, 34)              // and one every 34 px
```

| | |
|---|---|
| `path` | `str` — the file, relative to where you run `fluxa` |
| `scale` | `float` — 1.0 is the file's own size |

Draw the art **facing right**, as everywhere else here. The picture goes into
the same 1024×1024 sheet the turtles' own bodies use, so the **eight files are
shared** between pictures a turtle *is* and pictures a turtle *stamps*
([adr 0013](adr/0013-one-sheet-for-every-sprite.md)).

For this one style the rhythm is only the **gap** — `path_dash(0, 34)` is one
picture every 34 px — because a stamp's size comes from its own scale, not from
a dash length. Measured on a straight 680 px run at 34: twenty stamps, the first
exactly on the start point, every gap 34.0. Twenty and not twenty-one because
the mark at the very end of a segment belongs to the next one, which is the rule
every dash follows.

It is a **declaration** — it says which picture this turtle stamps, the way
`image` says which picture she *is* — and it switches the style on at the same
time. A `path_solid()` later stops the stamping from that step; asking for a
style again resumes it.

**What it costs:** 57 ms over 600 segments against 52 for a plain stroke,
measured — cheaper than a marker, dearer than nothing, and still only at the
rebuild.

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
| `step` | `int` — 1 to 50000 |
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

### `go_accel(step, dist, turn, start_px_s, end_px_s)` — step

The same walk, beginning at one speed and ending at another.

```fluxa
leo.go_accel(1, 400.0, 0.0, 100.0, 800.0)   // sets off and gathers pace
leo.go_accel(2, 400.0, 0.0, 800.0, 60.0)    // and arrives gently
```

Every other movement here is linear, which is what makes an artwork look
mechanical. Two speeds are a curve said in the unit you already have — the same
reason `circle(cx, cy, r)` beat working out a polar loop.

**It takes distance over the AVERAGE of the two speeds**, `2d / (v0 + v1)`, not
over the one it ends at. So 400 px from 100 to 800 px/s takes 0.89 s, and
swapping the two numbers takes exactly as long — measured, 908 ms and 917 ms
against the 889 the arithmetic predicts, the difference being the frame the
window was in the middle of.

Along the way it follows `v0·t + ½at²`, which in fractions of the time and the
distance is `p(u) = u(2v0 + (v1 − v0)u) / (v0 + v1)` — measured at a quarter, a
half and three quarters: 0.1042, 0.3056, 0.6042. It is a function of the
fraction and of nothing else, so an accelerated artwork still exports
byte-identically twice ([adr 0006](adr/0006-deterministic-render-by-frame-index.md)),
and rewinding one retraces the same curve backwards in the same time.

Both speeds have to be above zero: a movement that starts and ends at zero never
arrives.

### `go_silent_accel(step, dist, turn, start_px_s, end_px_s)` — step

The same, with no trail.

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

# Ready-made shapes

A figure is a batch of steps like any other — these declare it for you. You give
the **centre** and the size, and where it means something, how many sides or
points.

```fluxa
leo.circle(1, 400.0, 300.0, 120.0)
```

Every shape here behaves the same way:

- it is placed by its **centre**, in stage coordinates — the same ones `toward`
  and `jump` use;
- it starts with a **pen-up move** to the first vertex, so it does not drag a
  line in from wherever she was standing. That move costs one step;
- it **closes**: the last stroke lands back on the first vertex, and she ends
  standing there. `arc` is the exception — it is a piece of a circle and it
  leaves her at the far end;
- it draws with the colour, width and style she has at that step, one side per
  step, at her speed;
- it **returns the next free step**.

That return is the whole ergonomic point. Nothing forces you to use it —
`leo.circle(1, ...)` on its own is fine, and the panel (key `P`) tells you how
far the artwork goes now — but with it you never count sides:

```fluxa
int s = leo.circle(1, 400.0, 300.0, 120.0)
s = leo.star(s, 400.0, 300.0, 90.0, 36.0, 5)
s = leo.square(s, 400.0, 300.0, 60.0)
```

Angles are the ones the whole tool uses: **0 points right and they grow
anticlockwise**, so 90 is the top of the screen.

### `polygon(step, cx, cy, r, sides)` — steps

| | |
|---|---|
| `step` | `int` — the step the figure starts on |
| `cx`, `cy` | `float` — the centre |
| `r` | `float` — from the centre to a **corner**, not to a side |
| `sides` | `int` — 3 or more; fewer is treated as 3 |

Costs `1 + sides` steps.

```fluxa
leo.polygon(1, 400.0, 300.0, 90.0, 12)    // a dodecagon
```

It sits flat, which is not the same as "starts at angle zero": an **odd** number
of sides gets a corner pointing up and a horizontal side at the bottom, an
**even** number gets a horizontal side top and bottom. That is the difference
between a square and a diamond, and nobody should have to work out the rotation
for it.

### `triangle(step, cx, cy, r)` — steps

`polygon` with three sides: point up, flat bottom. Four steps.

### `square(step, cx, cy, side)` · `rect(step, cx, cy, w, h)` — steps

Sides parallel to the screen, corners clockwise from the top left. `side` and
`w`/`h` are the **full** width and height, not half. Five steps each.

```fluxa
leo.rect(1, 400.0, 300.0, 240.0, 120.0)
```

`polygon(step, cx, cy, r, 4)` is the other square — the one whose `r` reaches
the corners, useful when it has to fit a circle.

### `circle(step, cx, cy, r)` — steps

The polygon that picks its own number of sides: one per about 12 px of
circumference, never fewer than 12, never more than 90. A radius of 70 comes out
as 35 sides, so the call costs 36 steps.

```fluxa
leo.circle(1, 400.0, 300.0, 70.0)
```

If you want to choose the smoothness, that is what `polygon` is for — a 100-gon
is a rounder circle, and a 7-gon is a deliberate one.

### `ellipse(step, cx, cy, rx, ry)` — steps

An oval: one radius across, another down. `rx` equal to `ry` is a circle. The
smoothness comes from the larger of the two.

```fluxa
leo.ellipse(1, 400.0, 300.0, 140.0, 80.0)
```

### `star(step, cx, cy, r, inner, points)` — steps

| | |
|---|---|
| `r` | `float` — out to the tips |
| `inner` | `float` — out to the valleys between them |
| `points` | `int` — how many arms, one pointing up |

Costs `1 + 2 * points` steps.

```fluxa
leo.star(1, 400.0, 300.0, 80.0, 32.0, 5)
```

`inner` around 0.4 of `r` is the classic five-pointed star. Closer to `r` and it
becomes a flower; much smaller and it becomes a spike.

### `arc(step, cx, cy, r, from_deg, to_deg)` — steps

A piece of a circle. The only shape here that does not close: it leaves her at
the far end, facing along the curve, which is what makes it join onto whatever
comes next.

```fluxa
leo.arc(1, 400.0, 300.0, 120.0, 0.0, 180.0)     // the top half
leo.arc(1, 400.0, 300.0, 120.0, 180.0, 0.0)     // the same half, drawn the other way
```

A `to_deg` smaller than `from_deg` sweeps the other way round. The number of
sides is the circle's, in proportion to the sweep — never fewer than two.

---

# A whole trajectory in one call

### `follow_accel(step, points, start_px_s, end_px_s)` · `follow_silent_accel(...)` — steps

A whole trajectory that gathers pace, or loses it.

```fluxa
int s = leo.follow_accel(1, coast, 60.0, 900.0)
```

The speed of each segment comes from **how far along the path it starts**, not
from its position in the list. Points out of a tracer are unevenly spaced, so a
progression by index would race through the dense parts and crawl through the
sparse ones — the same drawing would accelerate differently depending on how
finely it happened to be sampled.

Each segment carries its own pair of speeds, so the ramp is continuous rather
than a staircase: the speed at the end of one segment is the speed at the start
of the next, by construction. Measured on a path of 40, 80, 160 and 320 px
ramping from 60 to 900 px/s — 485, 483, 500 and 500 ms. Four segments of wildly
different lengths taking almost the same time is what accelerating along a path
looks like.

### `follow_file(step, path, px_s)` · `follow_file_silent(...)` — steps

The same trajectory, read from a file instead of written into the artwork.

```fluxa
int s = leo.follow_file(1, "leo.pts", 900.0)
```

For anything traced this is the honest shape. A literal holds about a hundred
points and a drawing has thousands, so the alternative is a wall of numbers in
the source or hundreds of chained calls — and either way the whole thing is
parsed again on every save.

**The file holds tenths of a pixel, as whole numbers, one per line**, and a line
of `-99999` lifts the pen:

```
1405        <- x = 140.5
2000        <- y = 200.0
-99999      <- the next point is a hop, not a stroke
2200
1400
```

Tenths because `std.strings` turns a string into an int and not into a float. A
tenth of a pixel is finer than anything this tool can draw and it is exactly the
precision `tools/trace.py` writes, so nothing is lost — and the file stays
something a person can open and edit.

**What it costs:** 1400 points read, parsed and declared in **13 ms**, once per
run. Leonardo written this way is **56 lines and six data files** against 1510
lines of `toward`, and the two render pixel-identically.

A file that is not there says so and the artwork carries on, the same courtesy
the background image and the sound files get.

### `follow(step, points, px_s)` · `follow_silent(...)` — steps

A list of `(x, y)` points, **one step per segment**, and it returns the next
free step.

```fluxa
dyn wave = [140.0, 200.0, 220.0, 140.0, 300.0, 240.0, 380.0, 150.0]
int s = leo.follow(1, wave, 900.0)
```

| | |
|---|---|
| `step` | `int` — the step the first segment runs on |
| `points` | `dyn` — x, y, x, y… |
| `px_s` | `float` — this trajectory's speed; `0.0` means her own |

The step model is untouched: every segment is still its own logical moment,
still animates, still obeys `pivot`, `erase` and everything else. **What shrinks
is the file, not the timeline** — a trajectory written as two hundred `toward`
lines is one call and a list, and it costs exactly the same two hundred steps.
Verified by drawing the same trajectory both ways and comparing the frames:
pixel-identical.

`follow_silent` walks the same points with the pen up.

**Three ways to fill the list**, and two of them are shaped by the parser rather
than by this tool:

| | |
|---|---|
| a literal | up to about **a hundred points**. Expression depth is guarded at 200 and a list element counts as a level, so 204 numbers in one literal is a parse error — and that is the parser's list path, not `dyn`: `float arr p[204] = [ … ]` fails in exactly the same place |
| a loop | any size — writing past the end grows the list |
| several calls | `follow` returns the next free step, so a long trajectory is chunks chained through it |

And a literal is only legal as the **initialiser of a declaration**: it cannot
be an argument (`follow(1, [1.0, 2.0], 900.0)` does not parse) and a `dyn`
cannot be reassigned to a new one. Declare it, then pass the name.

Not called `path`, because ten calls already start with `path_` and every one of
them is about how the trail *looks*.

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

### `erase_at(step, from, to)` — step

The same, on a step you choose.

| | |
|---|---|
| `step` | `int` — when the strokes stop being drawn |
| `from`, `to` | `int` — the range of her steps to take out |

```fluxa
lines.erase_at(436, 1, 387)     // the sketch goes the moment the painting arrives
```

`erase` happens after everything that turtle has declared, which is what you
want at the end of a file and not what you want in a composition where something
else has to happen first. The step here is explicit, so it can be earlier than
her last one, and the artwork runs to that step even if nobody moves on it.

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
| `path_brush()` · `path_marker()` · `path_glow()` · `path_spray()` | appearance |
| `path_triangles()` · `path_squares()` · `path_stars()` | appearance |
| `path_on()` · `path_off()` | appearance |
| `go(step, dist, turn)` · `go_silent(...)` · `go_at(..., px_s)` · `go_silent_at(...)` | step |
| `go_accel(step, dist, turn, v0, v1)` · `go_silent_accel(...)` | step |
| `ring(first, count, dist, turn)` · `ring_silent(...)` · `spiral(..., grow, turn)` | steps |
| `polygon(step, cx, cy, r, sides)` · `triangle(step, cx, cy, r)` | steps, returns the next |
| `square(step, cx, cy, side)` · `rect(step, cx, cy, w, h)` | steps, returns the next |
| `circle(step, cx, cy, r)` · `ellipse(step, cx, cy, rx, ry)` | steps, returns the next |
| `star(step, cx, cy, r, inner, points)` · `arc(step, cx, cy, r, from, to)` | steps, returns the next |
| `toward(step, x, y)` · `jump(step, x, y)` | step |
| `follow(step, points, px_s)` · `follow_silent(...)` | steps, returns the next |
| `follow_accel(step, points, v0, v1)` · `follow_silent_accel(...)` | steps, returns the next |
| `follow_file(step, path, px_s)` · `follow_file_silent(...)` | steps, returns the next |
| `path_clear(step)` · `erase(from, to)` · `erase_at(step, from, to)` | step |
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
| **A** | Sound off / on. |
| **SPACE** | Pause / carry on. |
| **→** | One step forward, animated. |
| **←** | One step back, animated in reverse. |
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
and `←` walks the last one back.

**Neither arrow needs SPACE first.** Pressing one pauses the stage by itself —
having to press two keys to look at something would be the tool arguing with
you. Pressed while the artwork is still drawing:

- `→` means "finish this step and stop there";
- `←` drops the step in flight — it was never committed — and unwinds the last
  completed one.

**Going back is the step run the other way round**, over the same seconds it
took to draw: the stroke shrinks back into the point it grew from and the turtle
walks home. Going forward is something you watch, so going back should be too; a
step that vanishes in one frame tells you nothing about what it was.

Underneath it is still a rebuild — the artwork is recomputed from the code, it
is never undone (adr 0002) — so what is left on screen is exactly the drawing as
it was at that step, with erased ranges, `pivot`, `shift` and appearance changes
all resolved the way they were then. Verified to the pixel in `lab/rewind.flx`.
The rebuild costs ~160 ms on a large artwork, and it happens before the reverse
animation starts.

Pausing is a state of the window, not of the artwork: it touches neither the
file, nor the progress that crosses a save, nor the export. **Saving while
paused carries on** — the new steps are read and animated, which is what you
saved for. Press SPACE again if you wanted to stay stopped.

---

# Sound

Sound is the stage's, not a turtle's, so it is written the way the background
and the video are — one line, in `main.flx`:

### `audio.Track(path)`

Plays while the artwork runs, and **keeps playing across a save** — unless you
change the filename, which is noticed: the path is hashed and carried with the
handle, so a slot that no longer holds what the artwork names is stopped,
released and read again. That is the
whole reason it exists as its own call: the engine and the loaded files survive
the reload, and `Track` presses play only when nothing is already playing. Live
coding with music that restarted on every Ctrl-S would be no fun.

### `audio.Cue(step, path)`

Fires when that step is **animated** — not when it is redrawn. Saving replays
the whole artwork instantly to bring it back, and a cue that fired from the
replay would fire four hundred times on one save.

```fluxa
audio.Cue(1, "sounds/place.wav")
audio.Cue(36, "sounds/stroke.wav")
```

### `audio.Place()` · `Tap()` · `Slide()` · `Pencil()` · `Draw()` · `Stroke()` · `Quiet()`

**What a step sounds like, from here on.** Every movement makes the noise — a
piece being put down, a pencil mark — and it is a **band on the timeline**, like
a colour: it applies from the step where you wrote it and leaves what came
before alone.

```fluxa
audio.Place()                  // the outline knocks its way along
leo.ring(1, 36, 500.0, 170.0)

audio.Pencil()                 // and the shading scribbles
leo.ring(37, 60, 120.0, 40.0)
```

`Place` is the one to start with — a step *is* a thing being put down. `Quiet()`
turns the step sound off from that point.

**One sound at the start of the step, and no more** — a step is one gesture, so
it makes one noise when it begins, however long it takes to walk.

**And it does not outlive the step.** `draw` is four and a half seconds; a step
is often shorter, and one gesture's sound going on under the next three is not a
rhythm. When the step closes, whatever it was playing is faded over 70 ms and
stopped — long enough not to click, short enough to still belong to the step it
came from. `std.sound` has no fade, so it is a volume ramp driven once per
presented frame, which means the fade carries on across the beginning of the
next step rather than cutting.

**Two are never closer together than 70 ms.** That is a floor and nothing more:
a short step restarting the sound is the drawing keeping up with itself, and a
hand scribbling quickly does sound like that. Without any floor, a hundred steps
a second stops being a rhythm and becomes a tone.

**Changing it does not reach backwards.** Save with a different sound and the
steps that are already finished are not replayed — they never repeat, that is
the whole tool — so what you hear is the new sound on the steps animated *after*
the save. To hear it over what is already drawn, press **R**, or **←** and
**→**. It is the same rule a colour follows, and it surprises people once.

### `audio.Volume(pct)`

0 to 100, everything at once.

### The five that ship

In `sounds/`, and none of them beeps: a beep announces an event, and a step is
a thing being *done*. They sit between a chess piece set down on a board and a
pencil on paper.

| | |
|---|---|
| `place.wav` | a piece set down — a wooden knock, 240 ms, peak at 79 Hz |
| `tap.wav` | the same, lighter: a small move, peak at 147 Hz |
| `slide.wav` | pushed across the board — a knock with a scratch dragged out of it |
| `pencil.wav` | a real pencil, **recorded** — 1150 ms of graphite on paper |
| `draw.wav` | a real pencil again, **recorded**: one long even line, 4470 ms |
| `stroke.wav` | one longer line, the same voice lower — centre around 1.2 kHz |

Four of them are **synthesised**, by `tools/sounds.py`: the knocks are decaying
inharmonic partials over a click. Running that script writes identical bytes
every time, so the repository holds the recipe and not only the result.

**The pencil and the drawn line are recordings**, and they are the interesting ones. Three goes at
synthesising graphite got the physics right and the sound wrong — the click is
what makes a scratch a gunshot; one filter pole is not a filter when the
material is noise; a 62 ms mark is over before the ear has decided what it was
— and a phone in front of a sheet of paper settled it in one take.

Bringing a recording in is what `tools/import_sound.py` is for:

```bash
python3 tools/import_sound.py note.ogg -o sounds/pencil.wav --from 0.19 --to 1.27
```

It decodes anything ffmpeg reads (`std.sound` does not read ogg), trims to the
seconds you name, sets the level, and **does nothing else** — the recording's
own sample rate, no filtering, no limiting. That is deliberate and it was
learned the hard way: an earlier version resampled to 22 kHz, high-passed at
70 Hz and rounded the peaks with a soft knee, each defensible alone, and
together they made a recorded pencil thinner and duller than the take it came
from. What is left is a cut, a gain, and four milliseconds of fade so the cut
does not click. Measured after: the imported pencil's spectral centre is 3679 Hz
against the source segment's 3678.

Run it with `--show` first. In the voice note this pencil came from, the loudest
thing by 35 dB was the phone being handled at the end, and the graphite was the
quiet part in the middle.

**Level is matched over the loudest 300 ms**, not by peak and not by whole-file
RMS, and the whole kit is set the same way. The two recordings then sit
`--trim 3` — three decibels under — on purpose: measuring the same is where
levelling starts, not where it ends, and a scratch that goes on for a second
sits further forward than a knock that measures the same. A knock is a moment and a long
decay; a scratch is energy all the way through. Matched by peak, the scratch is
much the louder of the two — which is exactly how it sounded, and what the ear
judges is about a fifth of a second, so that is what gets measured. All six sit
at 4400 by that ruler; their peaks land anywhere from 19766 to 31783, which is
the point.

### What to know

| | |
|---|---|
| formats | wav, mp3, flac |
| how many | four files in one artwork |
| a missing file | says why, once, and stays silent — the drawing carries on |
| an export | silent, always: a controlled render is not played at watching speed |
| the **A** key | sound off and on, while it runs |

If the runtime was built without audio, `sound.version()` answers
`fluxa-sound/1.0 (stub — no audio device)`, every call succeeds and nothing is
heard. The artwork still draws.

---

# Limits

| | |
|---|---|
| turtles | 32 |
| steps | 50000 |
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
