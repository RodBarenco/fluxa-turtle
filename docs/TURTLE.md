# The turtle — every call, and when it happens

The README shows enough to draw something. This is the whole of it.

A turtle is an independent instance:

```fluxa
Block leo typeof turtle.Turtle
leo.spawn(340.0, 363.0)
```

Angles are in degrees: **0 points right** and the angle grows counter-clockwise,
as on the cartesian plane. The stage is 800×600 by default, `y` grows downward,
and both numbers live in `static/config.flx`.

---

## The three kinds of call

Everything a turtle can do falls into one of three groups, and knowing which is
which explains most of what looks surprising at first.

| Kind | When it happens | Examples |
|---|---|---|
| **Declaration** | at once, before anything runs | `spawn`, `face` |
| **Appearance** | from the **next step this turtle declares** | `color`, `path_width`, `speed`, `hide` |
| **Step** | on the step number you give it | `go`, `toward`, `pivot`, `erase` |

An appearance call is never retroactive:

```fluxa
leo.path_color(90, 200, 255)   // no step declared yet: her starting colour
leo.ring(1, 36, 500.0, 170.0)  // steps 1 to 36 come out blue

leo.path_color(255, 90, 160)   // from here on
leo.ring(37, 36, 500.0, 170.0) // steps 37 to 72 come out pink
```

Move the call above the steps it should affect and it affects them. That is the
whole rule ([adr 0009](adr/0009-appearance-is-a-timeline-event.md)), and it is
why the drawing reads in the order the file does.

---

## Being born

```fluxa
leo.spawn(340.0, 363.0)    // where she starts
leo.face(90.0)             // the heading she is born with, in degrees
```

`face` is the one call that is not a step and not an appearance: it sets the
heading she returns to whenever the artwork is rebuilt or replayed. Turning
*during* the drawing is what `go` does.

---

## Her own body

```fluxa
leo.color(0, 224, 150)     // RGB 0-255
leo.size(9.0)              // body radius
leo.hide()                 // she still moves and draws
leo.show()
leo.speed(260.0)           // pixels per second, her default
```

Most artworks call `hide()`: the turtle is the instrument, not the picture.
`speed` matters for the animation and for the video — it decides how long a step
takes — and it is beaten by a speed declared on the action itself.

---

## The stroke

```fluxa
leo.path_color(0, 224, 150)
leo.path_width(3)
leo.path_opacity(70)       // 0 (invisible) to 100 (solid)

leo.path_solid()           // ————————
leo.path_dotted()          // · · · · ·
leo.path_dashed()          // – – – – –
leo.path_dots()            // round dots
leo.path_dash(14, 9)       // the dash and the gap of whichever style is on

leo.path_off()             // stop drawing, keep moving
leo.path_on()
```

Opacity is a **mix with the background**, not an alpha channel: two translucent
strokes crossing do not add up ([adr 0008](adr/0008-opacity-by-mixing-with-the-background.md)).

A thick stroke is a bundle of parallel lines with a dot at each end, so corners
close and caps are round — and a very short stroke at a large width reads as a
dot.

---

## Walking

```fluxa
leo.go(1, 200.0, 90.0)                  // turn 90°, then walk 200 px
leo.go_silent(2, 300.0, 0.0)            // the same, leaving no trail
leo.go_at(3, 200.0, 0.0, 700.0)         // this one action at 700 px/s
leo.go_silent_at(4, 400.0, 0.0, 900.0)
```

The first argument is always the **step**. Turtles with actions on the same step
move together, and the step ends when the last of them arrives. One action per
turtle per step: a second one on the same number is ignored, and the run is not
interrupted.

### In batches

```fluxa
leo.ring(2, 35, 470.0, 170.0)            // 35 steps from step 2, all the same
leo.ring_silent(2, 35, 470.0, 170.0)     // the same, no trail
leo.spiral(1, 60, 12.0, 14.0, 90.0)      // ... with the side growing 14 px
```

`ring(first, count, dist, turn)` is the loop written inside the method, which is
the idiomatic form here. `spiral` adds the growth per step.

### To a point

```fluxa
leo.toward(5, 400.0, 300.0)   // be at this point
leo.jump(6, 120.0, 480.0)     // be there, pen up
```

`go` says "turn this much and walk that far"; `toward` says "be here", and the
turn and the distance are worked out when the step runs. It is what makes a
shape writable as a loop over its points:

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

Seventy-two strokes of a rose curve in five lines. She ends up facing the point
she walked to, so a `go` after a `toward` carries on from that heading.

---

## Erasing

Two erasers, and they do different things.

```fluxa
leo.path_clear(7)     // on step 7, everything she drew UP TO THEN is gone
leo.erase(1, 8)       // steps 1 to 8 of hers are gone; the rest stays
```

`path_clear` is a step: it happens at that number and wipes her whole trail so
far. Her position, heading and colours are untouched — she carries on from where
she is, on a clean canvas of her own.

`erase(from, to)` takes a **piece** out. It happens on the step after the last
one she has declared, so written at the end of a file it is the last thing that
happens and you watch the piece disappear; the artwork runs to that step even if
nobody moves on it. Four ranges per turtle.

Neither one touches another turtle's drawing.

```fluxa
leo.ring(1, 12, 55.0, 0.0)   // twelve strokes in a row
leo.erase(5, 8)              // and the middle four are not there
```

---

## Moving what is already drawn

```fluxa
fin.pivot(300, 12.0, 467, 470)   // turn her whole trail 12° about (467, 470)
fin.shift(400, 0, -20)           // displace it
```

These do not draw. They move **what that turtle has drawn**, all of it, from
that step on — including strokes made two hundred steps earlier. The angle is
absolute, not added to the last one, so a loop can sweep it and land exactly
where it started:

```fluxa
int k = 0
while k < 60 {
    fin.pivot(300 + k, 16.0 * math.sin(math.deg_to_rad(math.to_float(k) * 6.0)), 467, 470)
    k = k + 1
}
```

That is how something animates without being wiped and sketched again — a
flipper drawn once and then turned a few degrees per step. Redrawing it pose by
pose looks like sketching, because a step is never less than one frame of the
video ([adr 0012](adr/0012-a-turtle-can-move-what-she-has-drawn.md)).

The turtle herself does not move: her position, heading and next step are
untouched. `pivot(s, 0.0, x, y)` puts her drawing back where she drew it.

**It costs a repaint.** The strokes are already in the baked texture, so the
step a move happens on rebuilds the artwork — about 20 ms for a 900-action
drawing. Three hundred steps of beating spend six seconds of rendering, once.

---

## The whole list

| Call | Kind | What it does |
|---|---|---|
| `spawn(x, y)` | declaration | where she is born |
| `face(deg)` | declaration | the heading she is born with |
| `color(r, g, b)` | appearance | her body colour |
| `size(s)` | appearance | her body radius |
| `show()` · `hide()` | appearance | whether she is drawn at all |
| `speed(px_s)` | appearance | her default speed, in pixels per second |
| `path_color(r, g, b)` | appearance | the stroke colour |
| `path_width(w)` | appearance | the stroke width |
| `path_opacity(pct)` | appearance | 0 to 100, mixed with the background |
| `path_solid()` · `path_dotted()` · `path_dashed()` · `path_dots()` | appearance | the four styles |
| `path_dash(dash, gap)` | appearance | the rhythm of whichever style is on |
| `path_on()` · `path_off()` | appearance | whether she leaves a trail |
| `go(step, dist, turn)` | step | turn, then walk |
| `go_silent(step, dist, turn)` | step | the same, no trail |
| `go_at(step, dist, turn, px_s)` | step | with the speed on the action |
| `go_silent_at(step, dist, turn, px_s)` | step | both |
| `ring(first, count, dist, turn)` | steps | a run of equal movements |
| `ring_silent(first, count, dist, turn)` | steps | the same, no trail |
| `spiral(first, count, dist, grow, turn)` | steps | with the side growing |
| `toward(step, x, y)` | step | be at this point |
| `jump(step, x, y)` | step | be there, pen up |
| `path_clear(step)` | step | wipe her trail up to that step |
| `erase(from, to)` | step | take those steps of hers out |
| `pivot(step, deg, cx, cy)` | step | turn what she has drawn |
| `shift(step, dx, dy)` | step | displace what she has drawn |

---

## The stage, and everything that is not a turtle

```fluxa
stage.Stage.background(16, 17, 24)          // solid colour
stage.Stage.tile("texture.png", 1.0)        // a PNG, repeated
stage.Stage.center("logo.png", 2.0)         // once, in the middle
stage.Stage.stretch("photo.png")            // to the screen size
stage.Stage.image_off()                     // back to the plain colour

export.Video(1, 36, 5)                      // from, to, frames per second
export.Frames(1, 36, 60)                    // the same, as numbered PNGs
```

The Stage takes a **path**, never an image: the file is decoded during the
rebuild, once per save, and goes into the baked texture. A file that cannot be
read prints why and the drawing carries on
([adr 0011](adr/0011-the-artwork-file-declares.md)).

`export.Video` and `export.Frames` do not render when they are called: they
record what was asked for, and the Runner delivers it when execution reaches the
stage. Asking for more steps than the artwork has generates what there is.

---

## Limits

| | |
|---|---|
| turtles | 32 |
| steps | 6000 |
| actions, all turtles together | 65536 |
| appearance changes and moves | 2048 |
| erased ranges, per turtle | 4 |
| strokes not yet baked | 8192 |

All of them are in `static/config.flx`, and each is mirrored by an array
declaration the file points at — a Fluxa array is declared with a literal size,
so the two are changed together. Going past one prints a warning and ignores the
extra; it never corrupts the drawing quietly.

---

## Where to look next

- **[ARTWORKS.md](ARTWORKS.md)** — nine complete compositions, each with the
  image the code produces.
- **[artworks/one-night.md](artworks/one-night.md)** — the large one: line art,
  a beat, a video and the story behind it.
- **[RECIPES.md](RECIPES.md)** — loose pieces: ready-made turtles, closed
  shapes, palettes, rhythm tricks.
- **[adr/](adr/)** — why each of these decisions is the way it is.
