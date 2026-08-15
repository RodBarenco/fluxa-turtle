# 0010 — The video is a second pass over the frames

**Status:** accepted

## Context

Language v0.30 brought `std.video`: MP4/H.264 written from inside Fluxa, taking
the same image handle `graph.capture` produces. That closes the gap
[0007](0007-export-as-a-png-sequence.md) had to live with, and 0007 predicted
the wiring: "`Exporter.save()` starts feeding the encoder instead of the disk,
and nothing else changes".

It is not that simple. A video cursor is a `dyn`, and a Block cannot hold a
`dyn` as a **field** — it can only exist as a local inside a method, the way
`Painter.bake` holds a capture. `Exporter.save` is called from inside
`Runner.animate` and `Runner.hold`, in the middle of the frame loop, so the
cursor cannot be reached from there unless it is threaded through:

```fluxa
fn animate(dyn win, dyn canvas, dyn v, int s) nil
```

and `animate` is also the live path, where there is no video and nothing
sensible to pass. An export-only parameter would sit in the hot loop of the
normal execution, and every caller would have to invent a value for it.

## Decision

The frames stay the primary output, and the video is **one pass over them**.
`to_video` owns that pass, so the cursor only has to live for the length of one
method call — which a local `dyn` does:

```fluxa
fn movie(dyn win, dyn canvas, dyn bg, int from, int to, int fps) nil {
    ...
    export(win, canvas, bg)                    // renders the frames

    danger {
        dyn v = video.open("artwork.mp4", config.W(), config.H(), fps)
        exporter.Exporter.to_video(v, 0)       // reads them back into the video
        video.close(v)
    }
}
```

`to_video` reads each PNG, appends it, and — with `keep = 0` — deletes it and
removes the folder at the end. `Runner.movie` is the whole thing in one call
(from which step, to which step, at how many frames per second), and it is what
`main.flx` shows; the Exporter is still there for whoever wants the frames kept,
a different folder or a longer hold, and the cursor can equally be opened in
`main.flx` for that.

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
  the language a way to hold a `dyn` in a Block field, the single-pass version
  becomes possible and this decision is the thing to revisit.
