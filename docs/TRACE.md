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
python3 tools/trace.py sketch.png --threshold 150 --max-steps 900 -o art.flx
```

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
| `--invert` | raster: trace the light areas instead |

`--density` is about faithfulness and `--tolerance` is about cost, and they pull
against each other: sampling a curve finely and then simplifying hard gives a
better result than sampling it coarsely, because the simplification knows which
points matter and the sampler does not.

---

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
