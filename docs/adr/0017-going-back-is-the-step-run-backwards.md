# 0017 — Going back is the step run backwards

**Status:** accepted — refines [0015](0015-one-live-loop-and-a-panel-to-learn-with.md)

## Context

Two things about the arrows were wrong, and both were the tool arguing with the
person using it.

`←` and `→` only worked while paused. Pressing `←` on a drawing that was still
being drawn did nothing at all: you had to press SPACE first, which is a rule
with no reason behind it — nobody wants to "pause and then go back", they want
to go back.

And going back was instant. 0015 made it a rebuild to the previous step, which
is correct about *what* the artwork should be but says nothing about *how* it
gets there: the stroke blinked out of existence in one frame. Going forward is
something you watch — that is the whole point of the tool — so a step that
disappears without being watched teaches nothing about what it was.

## Decision

**An arrow implies a pause.** Pressing either one stops the stage by itself.
Pressed while a step is in flight:

- `→` means "finish this step and stop there". The step being animated *is* the
  one step the key asked for, so it is consumed when it completes rather than
  causing another one afterwards.
- `←` drops the step in flight — it was never committed, so dropping it costs
  nothing — and unwinds the last completed one. It leaves the frame loop inside
  `animate` immediately instead of waiting for the stroke to finish, because
  waiting would be the tool arguing with the key.

**Going back is the step run the other way round**, over the same seconds it
took to draw: the stroke shrinks back into the point it grew from and the turtle
walks home.

Underneath, it is still the rebuild 0015 chose, and for the same reason — the
artwork is recomputed from the code, never undone (adr 0002). `rewind` rebuilds
to the previous step, which is what takes the stroke out of the baked texture
and puts the turtles back where the movement began, and then runs `animate`'s
own loop with the fraction going from 1 down to 0. The in-flight stroke is drawn
from the step's start point to wherever she is *now*, which is why it shortens
instead of being wiped. Nothing is committed at the end: the artwork is already
at `s - 1` and the turtles only have to land exactly where the rebuild put them.

Both directions of time need the same setup — who moves, from where to where,
how long it takes, whether it draws — so that came out of `animate` into `arm`,
with `span` for the step's duration. One place to arm a step, two ways to walk
it.

## Consequences

- The keys read the way a person expects: one press, one effect, no
  prerequisite.
- Going back costs the rebuild (~160 ms on a large artwork) *plus* the step's
  own duration. That is deliberate — the duration is the feature.
- The reverse run leaves the pool holding step `s`'s appearance while the
  artwork sits at `s - 1`, because `arm` applies it so the un-drawing looks like
  the drawing. The next `animate`, `rewind` or rebuild sets it right, so the
  only trace is the panel's colour swatch during that pause.
- A save landing inside a reverse run is harmless: the artwork is already the
  rebuild's, and the turtles are put home whether the loop finished or not.
- `lab/rewind.flx` measures all three claims that matter — the reverse takes as
  long as the step did (2050 ms against 2017 ms forward), it ends exactly where
  the step began, and what is left on screen is pixel-identical to the artwork
  at the previous step.
