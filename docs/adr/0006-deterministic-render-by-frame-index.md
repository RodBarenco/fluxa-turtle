# 0006 — Deterministic render by frame index

**Status:** accepted

## Context

The pillars are explicit about exporting: the render "can render the frames in a
controlled way, without depending directly on the computer's real speed. So even
if generating takes longer, the final video keeps a correct frame rate".

The live animation uses `time.now_ms()`. If exporting used the same clock, the
video would inherit the machine's speed — and the time to write each PNG (tens
of milliseconds) would count as animation time.

The first attempt advanced `el = el + 1/fps` per frame. That accumulates
rounding error: a 1.0 s step at 30 fps yielded 31 frames instead of 30, and the
total came to 74 where 70 were due.

## Decision

While exporting, a step has a **whole and exact** number of frames, and each
frame's instant is computed from the index — never accumulated:

```fluxa
nf = math.to_int(math.round(dmax * fps))
el = dmax * math.to_float(fk) / math.to_float(nf)
```

The frame at instant zero is not written again: it is already the previous
step's last frame, or the opening still frames.

## Consequences

- Exact count: 70 frames for 5 still + 30 + 30 + 5 still.
- Two runs produce **byte-identical** frames (same md5 over the set), including
  generating 2.3 s of video in 6.1 s.
- The live animation stays on the clock, as it should. The two time sources
  coexist in the same loop, selected by a flag.
- Joins between steps carry no duplicate frame.
