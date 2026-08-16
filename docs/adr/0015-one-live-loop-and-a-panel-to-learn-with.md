# 0015 — One live loop, and a panel to learn with

**Status:** accepted

## Context

The tool showed *what* was drawn and never *why*. When a stroke did not appear
the only way to find out was to comment lines out until it did — and the two
usual causes, a turtle pointing somewhere unexpected and two actions declared on
the same step, are both invisible in the drawing.

The live stage was also three loops: one while replaying, one while animating
new steps, one waiting for the next save. Each read the keyboard on its own, and
adding pause to that arrangement meant adding a state that all three had to
agree on.

## Decision

**A panel, on P.** `static/panel.flx` draws over the stage: the step and the
last one declared, how many actions the timeline holds and how many it ignored,
and one line per turtle — pen colour, position, accumulated heading, pen up or
down. Off by default, and muted for the length of an export: a controlled render
is the artwork, not the workshop.

Its strings are **cached**, rebuilt only when the step or the number of turtles
changes. Building text with `strings.concat` inside a loop that never ends is
the one thing this project has a rule about (guide §12.5), so the lines are
built once per step instead of sixty times a second, every intermediate is
`free()`d, and what survives is a field — reassigning a field releases what it
held. The heading is deliberately not wrapped to 360: `1800 deg` says she has
turned five whole times, which `0 deg` would hide.

**One live loop.** `play` now has a single loop with four states in Block fields
— `paused`, `forward`, `back`, `replay` — set by the keyboard and read in one
place. `frame()` presents nothing on its own; the caller draws the panel over it
and calls `end_frame` (`shown()` is the pair, for the harnesses). Stepping back
is a **rebuild** to the previous step, not an undo of the last stroke: erased
ranges, `pivot`, `shift` and appearance changes all resolve as they did at that
moment, which is the only way to be honest about a timeline that can rewrite its
own past.

**The keyboard is read exactly once per presented frame.** Not once per loop
turn: `animate` presents frames of its own, and reading in both places counted
every press twice — SPACE toggled pause and untoggled it in the same frame, so
pausing appeared not to work at all. A press is cleared only by the branch that
acts on it; clearing the flags unconditionally at the end of the turn threw away
arrows pressed while an animation was running.

## Consequences

- "Why did it draw that" has an answer that does not involve deleting code:
  pause, read the position and the heading, press `→` and watch the next action.
- `ignored` makes the most common declaration mistake visible — the same turtle
  given two actions on one step, where the first wins and the second is dropped.
- Back costs one rebuild (~160 ms on a large artwork), which is why it is a key
  and not a scrubber.
- Pause is a state of the window, not of the composition: it does not cross a
  save. Saving while paused carries on, which is what a save is for.
- The panel is over the stage, not in the canvas, so it is not baked, never
  reaches `graph.capture`, and cannot end up in a PNG or in the video.
- One loop instead of three means the next key to be added is a field and a
  branch, not a decision repeated in three places.
