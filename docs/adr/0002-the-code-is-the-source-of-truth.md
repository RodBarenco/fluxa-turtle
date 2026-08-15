# 0002 — The code is the source of truth, not the drawing

**Status:** accepted

## Context

With only a handful of values crossing the reload
([0001](0001-persistent-state-at-program-level-only.md)), we had to decide what
to do about the turtles' positions, their headings and the segments already
drawn. Two ways out:

1. persist that state somehow and carry on from where it stopped;
2. recompute everything from the timeline, which the file itself declares on
   every run.

The second looked expensive — and it is the one the pillars describe when they
talk about "visual content fully reproducible from the source code".

## Decision

On every run, the finished artwork is **rebuilt** from the timeline: the turtles
return to their starting point and the steps from 1 to `done` are redone
instantly, without animation.

The only state crossing the save is *how many* steps were finished, not *what*
they produced.

## Consequences

- Editing an old step works. The stroke changes when you save, because it is
  recomputed, not restored.
- Replay and normal execution are the same code path. The replay only zeroes the
  counter and re-enters the same rebuild.
- Exporting is the same thing again, with another clock
  ([0006](0006-deterministic-render-by-frame-index.md)).
- It costs one rebuild per save: ~120 ms for 3000 segments. It grows with the
  artwork, but it happens once per save — not per frame.
- A stroke's colour is not stored with the stroke: it is recomputed like
  everything else. Which colour it recomputes to is decided by where the change
  sits in the file — the appearance changes are themselves timeline events
  ([0009](0009-appearance-is-a-timeline-event.md)), replayed at their own step
  during the rebuild.
