# 0012 — A turtle can move what she has already drawn

**Status:** accepted

## Context

The first animation in this project was a flipper beating: draw the flipper,
`path_clear`, draw it again a few degrees over, and so on. It works, and it is
wrong.

Every pose is drawn **stroke by stroke**. A flipper is thirty strokes, and a
step is at least one frame of the video, so each pose takes a second to appear.
What you watch is not an animal swimming, it is a drawing being sketched, wiped,
and sketched again. The person who asked for it said so in one sentence: *it
does not look like a beat, it looks like it is being redrawn*.

Making the pose faster does not fix it. In the live window it is fast enough —
thirty strokes at 2600 px/s is a tenth of a second — but the export renders by
frame index, and a step is never less than one frame ([0006](0006-deterministic-render-by-frame-index.md)).
The video always shows the sketching. Fewer strokes per pose means a cruder
flipper. There is no setting that makes redrawing look like motion.

## Decision

A turtle can **move what she has already drawn**:

```fluxa
fin.pivot(300, 6.0, 467, 470)     // from step 300, her whole trail is turned
fin.pivot(301, 9.0, 467, 470)     // 6°, then 9°, about the point (467, 470)
fin.shift(400, 0, -12)            // and displaced, if that is what is wanted
```

The flipper is drawn **once**, with the rest of the animal, and after that only
its angle changes: one angle per step, which is one frame. That is a beat.

- The angle is **absolute**, not added to the last one, so a loop can sweep it
  and come back to exactly where it started.
- The move applies to **everything that turtle has drawn**, including strokes
  from steps long before the move. The rebuild asks the timeline for the last
  move due at or before the step it is rebuilding to, and draws her whole trail
  through it (`Timeline.apply_moves`).
- The transform is per turtle. Nothing else on the stage notices, which is why
  the body can be one turtle and each flipper another.
- A move is something that happens on a step, so `max_step` counts it: the
  artwork does not end before the last pivot.

## Consequences

- **A move repaints the artwork.** The strokes are already in the baked texture,
  so moving them means rebuilding it — the same cost `path_clear` already had,
  and the runner triggers it the same way (`Timeline.moves_at`). One rebuild per
  step the move happens on. For "One Night" that is 300 rebuilds of a
  900-action artwork; measured at about 20 ms each, the whole beat costs six
  seconds of rendering, once, offline.
- It is the cheap way round for an animation of a *part*. The alternative —
  redrawing the part every frame — costs the same rebuild plus thirty steps of
  sketching, and looks wrong.
- `Painter.at_x` / `at_y` put every stroke through the turtle's transform, in
  both places a stroke is drawn: the live one and the recorded one. A turtle
  with no transform pays one comparison.
- Rotation is about a point given in screen coordinates, not about the turtle's
  own position. A flipper turns about its shoulder, which is not where the
  turtle's pen happens to be standing.
- It does not move the turtle herself, only her drawing. Her position, heading
  and next step are untouched — `pivot` is not a way to walk.
