# Leonardo

*A drawing made by hand, drawn back by turtles — and then it says goodbye.*

![the last frame](leonardo.png)

**[Watch it](leonardo.mp4)** — 1425 frames at 30 fps, written by the program
itself with one line: `export.Video(1, 0, 30)`.

Six turtles draw a pencil drawing back, line by line. The forearm waves three
times. Then the photograph the line art was traced from lands on top of it —
exactly on top, to the pixel — and the piece is over.

Ten turtles, 558 steps, 317 outlines. Nothing in it was placed by eye.

---

## Where it comes from

A drawing on paper. Photographed, painted over, and handed to the tool, which
had never been given anything that did not start as code.

That is the point of the piece. Everything else in this repository is a figure
somebody typed — a rosette, a star, a turtle drawn out of arcs. This one starts
somewhere the tool cannot reach: graphite on a sheet, with a wobble in every
line and a thumb that the paint did not quite finish. The tracer's whole job is
to get that into steps without smoothing the hand out of it, and the ending
exists to prove it did: the photograph comes back and sits on its own outlines.

---

## How it goes

| Steps | What happens |
|---|---|
| 1 – 337 | six turtles draw the line art, three columns of bubbles rise behind it |
| 338 – 469 | the forearm waves, three times |
| 489 – 558 | the photograph lands on the line art, and holds |

---

## Making it

Two tools and a build script. The drawing itself is not in this repository —
what is published is the artwork, not somebody's sketchbook.

```bash
# the paper comes out, twice from the same mask: one full size to trace,
# one at 420 px to be worn as a sprite
python3 tools/cutout.py drawing.png -o cut.png    --shrink 3 --feather 1.2
python3 tools/cutout.py drawing.png -o sprite.png --shrink 3 --feather 1.2 --width 420

# the outlines become turtle code, the forearm on a turtle of its own
python3 art/build_leo.py > leo.flx
```

`cutout.py` decides what is drawing by two tests together, because the paper is
pale and grey and neither test alone finds a drawing: everything the pencil or
the paint touched is either **coloured** or **darker** than the sheet. The ink
lines are grey; the painted areas are pale. `--shrink 3` pulls the edge in by
three pixels, which is what kills the rim of paper that reads as a halo once a
sprite is over a dark stage.

The two cut-outs come from the same mask and therefore the same crop, which
matters more than it sounds. It is what makes the ending exact.

Everything after that is [`trace.py`](../TRACE.md) — 317 outlines, simplified
until the drawing fits a budget of 460 steps, spread over six turtles that draw
in parallel.

---

## The three things that had to be got right

### The forearm, not the arm

`pivot` turns everything **one turtle** has drawn, so the part that waves has to
have been drawn by its own turtle. But a traced outline runs from the fingertips
all the way down to the hip — sorting outlines whole puts the hip on the
forearm. So they are **cut**, per point, where the forearm meets the upper arm.

The cut is not a box. The head is "above the elbow" too, and a box would take it
along. It is the **elbow crease**: the half-plane on the forearm's side of a line
through the elbow, square to the forearm.

```python
UP = normalise(WRIST - ELBOW)                 # elbow (168,196) -> wrist (205,115)
inside = in_box(p) and dot(p - ELBOW, UP) > -6
```

Both points were read off the painting with a grid over it, in stage
coordinates. A first attempt swung the whole arm from the shoulder, which is a
different gesture entirely — that is not how anybody waves.

### The wave has to come home

`pivot(step, deg, cx, cy)` takes the angle the drawing should be **at**, not a
turn to add. So a sine of the step sweeps the forearm out and back and lands it
exactly where it started:

```fluxa
int wave = 0
while wave <= 132 {
    float ph = math.to_float(wave) / 132.0
    float ang = 15.0 * math.sin(ph * 18.84956)
    arm.pivot(337 + 1 + wave, ang, 168, 196)
    wave = wave + 1
}
```

Three cycles, fifteen degrees each way. If the angle accumulated instead of
being absolute, the arm would drift a little every cycle and the last frame
would not fit the photograph — which is the next problem.

### The photograph fits because it is the same arithmetic

The trace is fitted to the stage with one scale and one offset. The sprite is
the same cut-out, so the same two numbers say where it goes and how big it is:

```
k      = 0.2869                                     the fit
centre = (cut_w/2, cut_h/2) * k + offset  = (399.1, 278.7)
scale  = k * cut_w / sprite_w             = 1.2260
```

```fluxa
Block real typeof turtle.Turtle
real.spawn(0.0 - 400.0, 278.7)
real.image("sprite.png", 1.2260)
real.hide()
real.jump(488, 399.1, 278.7)     // into place, invisible, arriving from the left
real.show()
```

Measured on the render, the painting lands at (145, 29)–(649, 530) against the
(142, 25)–(657, 533) the arithmetic predicts — the difference is the transparent
margin of the sprite. Blending the two frames shows the traced outlines sitting
on the painted edges they came from:

![the trace over the painting](leonardo-drawing.png)

She arrives **hidden and from the left**, because a sprite is turned by its
turtle's heading and a jump leaves her facing the way she travelled. Coming in
from the left leaves her upright. Then `show()`, and a run of zero-length jumps
holds the final frame.

---

## What it uses

`jump` · `toward` · `pivot` · `image` · `show`/`hide` · `path_dots` ·
`path_opacity` · `export.Video`, and from the tools,
[`cutout.py` and `trace.py`](../TRACE.md).

It also found a real bug: the two-pass rebuild that draws layered strokes did
not re-apply erases before its second pass, so an erased sketch came back from
the dead. An artwork is a test with an audience.
