# Leonardo

*A drawing made by hand, drawn back by turtles — and then it says goodbye.*

![the last frame](leonardo.png)

**[Watch it](leonardo.mp4)** — 2118 frames at 60 fps, 35 seconds, written by the
program itself with one line: `export.Video(1, 0, 60)`.

Six turtles draw a pencil drawing back, line by line. The forearm waves three
times. Then the photograph the line art was traced from lands on top of it —
exactly on top, to the pixel — and the piece is over.

Ten turtles, 822 steps, 317 outlines, neon on near-black. Nothing in it was
placed by eye.

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
| 1 – 379 | six turtles draw the line art, three columns of bubbles rise behind it |
| 380 – 643 | the forearm waves, three times |
| 683 – 822 | the photograph lands on the line art, and holds |

Each turtle draws in its own green, so the figure comes up in bands of colour as
the six of them work, and the forearm gets the brightest one — it is the part
that moves afterwards.

**Two things to know before changing the frame rate**, both learned the hard
way here.

A step that only pivots renders exactly **one frame whatever the rate** —
nothing moves in it, so there is no duration to divide — while a step that walks
renders as many frames as its seconds are worth. So doubling the frame rate
doubles the drawing's smoothness and *halves* the wave, unless the wave is given
twice the steps. That is why `export.Video(1, 0, 60)` and `WAVE_STEPS = 264`
belong together.

And **speed is not smoothness**. How long the drawing takes is the sum of every
segment and every jump divided by the turtles' speed, and the frame rate has
nothing to do with it. Halving the speed to "get more frames" simply makes the
video twice as long — it was tried. 317 outlines also means 317 pen-up jumps,
and those cost time too, which is why `SPEED` here is 2800 and not the 900 a
drawing of a few strokes would want.

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

The cut is a **capsule** around the axis that runs from the elbow through the
wrist and on to the fingertips: along the axis from just below the elbow to the
end of the hand, and no further than 55 px from it sideways.

```python
UP   = normalise(WRIST - ELBOW)        # elbow (168,196) -> wrist (205,115)
SIDE = (-UP.y, UP.x)
along = dot(p - ELBOW, UP)
inside = -8 < along < 195 and abs(dot(p - ELBOW, SIDE)) < 55
```

It took two wrong answers to get there. The first swung the **whole arm from the
shoulder**, which is a different gesture — that is not how anybody waves. The
second cut at the elbow crease with a half-plane, and the shoulder went along
with it: the forearm points up and to the right, so the shoulder's projection
onto that axis is positive too. **The sideways limit is what tells an arm from
the body it is attached to.**

The elbow and the wrist were read off the painting with a grid over it, in stage
coordinates.

### The wave has to come home

`pivot(step, deg, cx, cy)` takes the angle the drawing should be **at**, not a
turn to add. So a sine of the step sweeps the forearm out and back and lands it
exactly where it started:

```fluxa
int wave = 0
while wave <= 264 {
    float ph = math.to_float(wave) / 264.0
    float ang = 15.0 * math.sin(ph * 18.84956)
    arm.pivot(379 + 1 + wave, ang, 168, 196)
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
real.jump(682, 399.1, 278.7)     // into place, invisible, arriving from the left
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
