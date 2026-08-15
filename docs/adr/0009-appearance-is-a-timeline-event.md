# 0009 — An appearance change is a timeline event

**Status:** accepted

## Context

Until now the turtle's look — colour, width, style, opacity, size, speed, the
pen, whether she is visible — lived only in the pool, as her *current*
configuration. The painter read it at the moment of drawing, and the rebuild
redrew the whole artwork with whatever the code had declared last.

The consequence was retroactive: changing a colour after thirty-six steps
repainted those thirty-six steps too. There was no way to say "blue up to here,
green from here on", which is the ordinary thing to want — the file reads top to
bottom, and a change written halfway down looks like it happens halfway
through.

Keeping a colour per segment would fix the drawing and break
[0002](0002-the-code-is-the-source-of-truth.md): the artwork would stop being a
function of the code and become a stored picture, and editing an old step would
no longer change what it produced.

## Decision

An appearance call does not touch the pool directly. It records an event in the
timeline, starting at **the step after the last one that turtle has declared so
far**:

```fluxa
leo.path_color(90, 200, 255)   // no step declared yet: from step 1
leo.ring(1, 36, 500.0, 170.0)

leo.path_color(255, 90, 160)   // leo's last step is 36: from step 37
leo.ring(37, 36, 500.0, 170.0)
```

Whoever executes a step applies the events due at it first — `instant` during
the rebuild, `animate` during the animation — so every path through the artwork
(save, replay, export) sees the same look at the same step. The rebuild returns
the pool to the born-with defaults before replaying, so the events alone decide
what anything looks like.

The step is counted per turtle. A change to `ana` written after `leo`'s
thirty-six steps applies from *ana's* next step, not from 37.

`face` stays out of it: it is the heading a turtle is born with, part of her
declaration and not something that happens on a step.

## Consequences

- The artwork is still recomputed from the code, always
  ([0002](0002-the-code-is-the-source-of-truth.md)). Editing an old colour still
  changes the strokes it belongs to, on save — what changed is *which* strokes
  it belongs to.
- Order in the file now carries meaning for appearance, as it already did for
  the step numbers. A style declared after every movement affects nothing; the
  fix is to move it up.
- The segments not yet baked carry the look they were drawn with. The painter
  resolves colour, width, style and rhythm when the step closes and replays
  those, instead of asking the pool at draw time — otherwise a change made two
  steps later would leak backwards for as long as the run lasted.
- Opacity is folded into the recorded colour, since it is a mix with the
  background ([0008](0008-opacity-by-mixing-with-the-background.md)). A segment
  declared invisible is not recorded at all.
- It costs one pass over the event list per step, bounded by the number of
  changes declared (512 max), not by the size of the artwork. The 3000-step
  rebuild stayed at ~135 ms.
