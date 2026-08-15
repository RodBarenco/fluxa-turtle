# 0007 — Export as a PNG sequence

**Status:** accepted

## Context

The pillars ask for video export (§8) and the future-expansions document lists
MP4, WebM, GIF and an **image sequence**.

Fluxa has no video encoder today. Verified in the stdlib: there is no video
library, and there is no process spawn — nothing that would let an external
encoder be called from inside the program. What does exist is `std.image`, which
writes PNG, JPG, BMP, TGA and QOI.

## Decision

Fluxa delivers the **sequence of numbered PNGs**, which is one of the formats
foreseen, and prints the command to assemble the video:

```
ffmpeg -framerate 60 -i export/frame_%06d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
```

All the hard parts of §8 — replay from the beginning, controlled render,
synchronisation between turtles, step range, still frames — stay on the Fluxa
side.

## Consequences

- The whole chain was verified end to end: 70 PNGs become an 800×600 MP4 at
  30 fps with 70 frames, confirmed by `ffprobe`.
- It depends on an external tool for the last step. The program does not pretend
  otherwise: it prints the command.
- Once a `std.video` exists it only replaces that last stage — `Exporter.save()`
  starts feeding the encoder instead of the disk, and nothing else changes.
  *(It arrived in language v0.30, and that last part turned out to be wrong: the
  video cursor is a `dyn`, which a Block cannot hold, so the encoder is fed by a
  second pass over the frames instead of from inside the frame loop — see
  [0010](0010-the-video-is-a-second-pass-over-the-frames.md). The PNG sequence
  stayed the primary output.)*
- The command must be built with `strings.concat`, not with a multi-argument
  `print`: `print` separates its arguments with spaces and the result does not
  paste into a terminal.
