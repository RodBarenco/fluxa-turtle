# 0010 — The video is a second pass over the frames

**Status:** accepted

## Context

Language v0.30 brought `std.video`: MP4/H.264 written from inside Fluxa, taking
the same image handle `graph.capture` produces. That closes the gap
[0007](0007-export-as-a-png-sequence.md) had to live with, and 0007 predicted
the wiring: "`Exporter.save()` starts feeding the encoder instead of the disk,
and nothing else changes".

It is not that simple. A video cursor is a `dyn`, and a Block cannot hold a
`dyn` as a field — the reason every `dyn` in this project lives in `main.flx`
and arrives as a parameter. `Exporter.save` is called from inside
`Runner.animate` and `Runner.hold`, in the middle of the frame loop, so feeding
the encoder from there means threading the cursor through:

```fluxa
fn animate(dyn win, dyn canvas, dyn v, int s) nil
```

and `animate` is also the live path, where there is no video and nothing
sensible to pass. An export-only parameter would sit in the hot loop of the
normal execution, and every caller would have to invent a value for it.

## Decision

The frames stay the primary output, and the video is **one pass over them**:

```fluxa
runner.Runner.export(win, canvas, bg)          // writes the PNGs, unchanged

danger {
    dyn mp4 = video.open("artwork.mp4", config.W(), config.H(), exporter.Exporter.get_fps())
    exporter.Exporter.to_video(mp4, 0)         // reads them back into the video
    video.close(mp4)
}
```

`to_video` reads each PNG, appends it, and — with `keep = 0` — deletes it and
removes the folder at the end. The cursor is opened and closed in `main.flx`,
where the window and the canvas already live, so the rule about `dyn` holds
without an exception and the animation loop is untouched.

## Consequences

- Nothing changed in the render path. The export is byte-identical to what it
  was ([0006](0006-deterministic-render-by-frame-index.md) still holds), and the
  video is a function of those exact frames.
- The PNGs are written and read once more. Measured on the 100-frame harness at
  800×600, the second pass costs about a second — against a render that takes
  minutes. It is the wrong trade only for an export long enough that disk
  traffic beats rendering, which is not where this tool is.
- The frames remain useful on their own: an editor, a print, a contact sheet, or
  ffmpeg for a format `std.video` does not write. `keep = 0` is there for when
  they are not.
- Release stays the caller's job, as everywhere else in the standard library:
  whoever calls `video.open` calls `video.close`. `to_video` does not close a
  cursor it did not open.
- If `std.video` ever grows a way to hand the encoder a file path per frame, or
  the language a way to hold a `dyn` in a Block, the single-pass version becomes
  possible and this decision is the thing to revisit.
