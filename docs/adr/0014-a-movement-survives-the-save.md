# 0014 — A movement survives the save

**Status:** accepted

## Context

Pillars §5 says a turtle interrupted mid-movement "can carry on from the
progress already reached". Until now she could not: only whole steps crossed a
save, because only `done` — the number of finished steps — was persistent.

Measuring what actually happened on a save turned out to matter more than the
plan did. The runtime cancels a script at a safe point by **breaking the loop it
is in and carrying on at the next statement**; it does not abandon the script.
So a save landing in the middle of `animate` broke the frame loop, fell through
to the code that closes the step — final position, segment added to the path —
and returned to `play`, which counted the step and moved on. The movement did
not restart, as the plan assumed: it **completed instantly**, and the drawing
jumped to the end of a stroke nobody watched being made.

That is worse than restarting, and it explains why the artwork sometimes gained
a stroke out of nowhere on a save.

## Decision

Two things, and they only work together.

**A step is finished only if it arrived.** `animate` compares the elapsed time
against the step's duration after its loop ends, and records the answer in
`Runner.arrived`. That is the only place able to tell a completed movement from
a cancelled one, because the cancellation looks exactly like the loop ending.

- arrived: the step closes as it always did, `play` counts it, `cur` advances.
- not arrived: nothing is closed, nothing is added to the path, the turtles stay
  exactly where the last frame put them, and `play` stops without counting the
  step.

**The progress crosses the save.** `main.flx` carries a fourth `prst`:

```fluxa
prst dyn part = [0.0, 0.0]      // the step in flight, and how far into it
```

`animate` writes both on every frame — a save can land on any of them — and
clears them when the step completes. On the next run, if `part[0]` names the
step about to be animated, the loop starts at `dmax * part[1]` instead of at
zero.

A `prst dyn` with a literal initializer is what survives a reload with its value
(spec §133), and a Block method can write through it as a parameter — the same
mutate-through-the-handle trick `canvas` uses. A Block field would be
re-declared on every save, and a function cannot see the artwork's scope.

## Consequences

- Saving during a long movement no longer costs it. Measured with an eight
  second step and three saves: the turtle carried on from 43%, then from 78%,
  then finished — and never went back to the start.
- The stroke has no gap. The in-flight segment is drawn from the step's start
  point to the current position on every frame, so the first frame after a
  resume draws the 43% that was already walked and the walk carries on.
- The progress is a fraction, not a distance, so editing the step's length or
  speed while it is in flight is harmless: it resumes at the same fraction of
  the new movement.
- Progress belonging to a different step is ignored, which is what happens when
  the artwork is edited enough that the numbering moves.
- Pressing R clears it: a replay starts clean.
- The export never touches it. A controlled render is not a run being watched,
  so it gets a scratch pair of its own and the live progress is left alone.
- One more argument in `main.flx`'s execution line, and one more `prst` above
  it. That is the price of the only mechanism that can cross a reload, and it is
  four lines in the file that documents them.
