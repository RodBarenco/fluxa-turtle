# Tracing a drawing into turtle code

```bash
python3 tools/trace.py logo.svg -o art.flx
```

`tools/trace.py` reads an SVG or a raster image, turns every outline it finds
into a run of `toward` steps, and writes Fluxa you can paste into `main.flx`
between the stage and the execution line.

What comes out is **ordinary turtle code**. Not a special import, not a data
file: turtles, colours and steps, which animate, obey `pivot`, `shift` and
`erase`, go into a video, and can be edited line by line. Tracing gives you the
first draft of a drawing that would take an hour to write by hand.

Try it on the example that ships with the tool:

```bash
python3 tools/trace.py tools/example.svg --turtles 3 --keep-colors -o art.flx
```

```
[trace] 6 outlines, 177 actions, 62 steps, 3 turtles -> art.flx
```

---

## Step zero: a photo of a drawing on paper

A drawing you photographed comes with the paper — an off-white that is never one
colour, darker in the corners, with the grain of the sheet in it. `cutout.py`
takes the paper out and writes the drawing on transparency, cropped:

```bash
python3 tools/cutout.py drawing.png -o cut.png --preview
[cutout] 2206x1920 -> 1795x1770, 41.9% of the photo was drawing
```

It decides by two tests together, and both are needed: the paper is pale and
grey, so everything the pencil or the paint touched is either **coloured** or
**darker** than the sheet around it — the ink lines are grey, and the painted
areas are pale. Then it keeps the largest piece and fills its holes, because a
drawing is an outline with paint inside it.

| | |
|---|---|
| `--tol` | how far from the paper's own colour still counts as paper (14) |
| `--dark` | how much darker than the paper counts as a line (26) |
| `--keep N` | keep the N largest pieces, for a drawing in separate parts |
| `--shrink N` | pull the edge in N pixels — kills the pale halo of paper that a photographed edge leaves around a sprite |
| `--width N` | write it this wide. **A sprite has to**: every picture in an artwork is composed into one 1024×1024 sheet, so a 1800 px photo does not fit |
| `--preview` | also write it on a chequerboard, to see the edge |

The result is ready to be either input of the tool below — a **sprite**
(`leo.image("cut.png", 0.6)`) or something to **trace**.

Run it **twice from the same settings** if you want both: once full size to
trace, once with `--width` for the sprite. The crop comes from the mask, so the
two land on the same rectangle and anything you compute for one is true of the
other — which is what lets a photograph be dropped exactly onto the line art
traced from it.

---

## The two inputs

**SVG** needs nothing installed. It is the input that keeps its shape: the file
is already made of lines and curves, so they are *sampled*, not guessed at.
Understood: `path` (every command, `M L H V C S Q T A Z`, absolute and
relative), `line`, `polyline`, `polygon`, `rect`, `circle`, `ellipse`, the
`transform` attribute on any of them and on the groups around them
(`translate`, `scale`, `rotate`, `matrix`, `skewX`, `skewY`), `viewBox`, and
colours from `stroke`, `fill` or `style`.

**A raster image** (`.png`, `.jpg`, …) needs Pillow — `pip install Pillow` — and
is traced by outlining its dark areas: the border of every shape and of every
hole inside it. That works on **line art, logos, silhouettes and lettering**. It
does not work on photographs, and no option will make it.

```bash
python3 tools/trace.py sketch.png --threshold 150 --blur 2.0 --max-steps 900 -o art.flx
```

A cut-out arrives with transparency, and transparent has to mean *paper* here,
not ink — it is composited onto white before anything is decided, so tracing a
cut-out traces the drawing and not the hole it was cut from.

**`--emit svg`** writes the same outlines as an SVG rather than as turtle code,
which is how a photograph becomes a vector file you can keep, edit in an editor,
and trace again later:

```bash
python3 tools/cutout.py drawing.png -o cut.png
python3 tools/trace.py  cut.png --emit svg --threshold 130 --blur 2.0 -o art.svg
python3 tools/trace.py  art.svg  --turtles 6 --max-steps 420 -o art.flx
```

Going through SVG is worth the extra step on a hand drawing: the raster pass is
the one that guesses, and once it is a vector you can retrace it at any size and
any step budget without guessing again.

---

## The numbers that matter

Two limits decide whether a drawing fits: **6000 steps** and **32 turtles**. The
tool prints what it used, every time, and warns if the step count is past the
stage's.

Steps are what a traced drawing spends fastest, so `--max-steps` (1500 by
default) is a budget, not a suggestion: the tool searches for the smallest
simplification tolerance that fits it and tells you what it settled on.

```
[trace] simplified with a tolerance of 1.02 px to fit --max-steps 400
```

Turtles draw **in parallel** — every one of them starts at step 1 — so the cost
in steps is the longest turtle's run, not the sum. `--turtles 4` on a drawing of
four outlines is roughly four times faster on screen and costs a quarter of the
steps. Outlines are handed to the emptiest turtle, longest first, so the runs
come out even.

---

## Options

| | |
|---|---|
| `-o FILE` | write there instead of stdout |
| `--turtles N` | draw with N turtles at once (1…32, default 1) |
| `--stage WxH` | the stage to fit into (default `800x600`) |
| `--margin PX` | space left around the drawing (default 40) |
| `--max-steps N` | simplify until it costs at most this (default 1500) |
| `--tolerance PX` | set the simplification by hand; `0` keeps every point |
| `--density PX` | one sample per this many pixels of curve (default 6) |
| `--speed PX_S` | the turtles' speed (default 900) |
| `--stroke W` | `path_width` (default 2) |
| `--color R,G,B` | one colour for everything |
| `--keep-colors` | use the colours in the SVG instead of the palette |
| `--min-points N` | drop outlines shorter than this |
| `--threshold N` | raster: a pixel darker than this is ink (default 128) |
| `--blur PX` | raster: smooth this much before deciding what is ink. A pencil line photographed on paper is grainy, and without this it traces as a cloud of specks |
| `--emit follow` | write the same artwork as `follow` lists — an order of magnitude fewer lines |
| `--emit svg` | write the outlines as an SVG instead of turtle code |
| `--invert` | raster: trace the light areas instead |

`--density` is about faithfulness and `--tolerance` is about cost, and they pull
against each other: sampling a curve finely and then simplifying hard gives a
better result than sampling it coarsely, because the simplification knows which
points matter and the sampler does not.

---

## `--emit follow`

The same artwork, written as lists of points instead of one call per point:

```bash
python3 tools/trace.py drawing.svg --turtles 6 --emit follow -o art.flx
```

Leonardo is **1510 lines** in the default form and **314** in this one, for the
same 387 steps and 1406 actions — and the two render pixel-identically, which
is checked rather than assumed.

Each leg is its own `dyn`, and a pen-up hop is a `jump`, because of two parser
rules worth knowing before hand-writing anything similar: a literal holds about
a hundred points, and a literal is only legal as the initialiser of a
declaration — never as an argument, never as a reassignment.

## After it is traced

The output is yours to edit, and the interesting part starts there:

```fluxa
t0.path_dotted()            // one line, and the whole outline is dotted
t0.speed(300.0)             // slower, so it can be watched
t0.pivot(200, 15.0, 400, 300)   // turn what has been drawn, from step 200 on
t0.erase(1, 40)             // take the first outline back out
```

Two things worth knowing about what it generates:

- Each turtle **jumps** to the start of each of its outlines, pen up, and that
  jump costs a step. An outline of 40 points costs 41.
- Turtles are numbered `t0`, `t1`, … and spawned at the first point of their
  first outline. Renaming them is safe; changing a step number is what changes
  the choreography.

Press **R** in the window to watch the whole thing drawn from the beginning, and
**P** to see which step it is on.
