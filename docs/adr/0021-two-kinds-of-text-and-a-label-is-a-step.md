# 0021 — Two kinds of text, and a label is a step

**Status:** accepted — sits beside
[0009](0009-appearance-is-a-timeline-event.md) and
[0020](0020-the-sheet-is-passed-to-whoever-draws.md)

## Context

`write` draws letters as strokes (0.22.0): they animate a letter at a time,
take path styles, and `erase`, `pivot` and the export reach them. That is the
right text for a drawing, and the wrong text for a title. A ten-letter word
costs about sixty steps, the glyphs come from a plotter font six units wide, and
nothing about it looks like type — which is the point, and also the limit.

The graphics library already draws the other kind: `graph.draw_text` in the
built-in font, `graph.load_font` + `graph.draw_text_font` for a TTF, kerned and
antialiased at any size. The panel has used it since 0015. Until now an artwork
could not.

## Decision

**Both, and they are different things on purpose.**

- `leo.write(step, x, y, s, size)` — letters as strokes. Part of the drawing.
- `leo.text(step, x, y, s, size)` — letters as type. One step, however long the
  string, drawn by the library and baked into the path texture.
- `stage.Stage.font(path, size)` — an optional TTF for all of them. Declared,
  never loaded: the file is opened once inside `Runner.play`, like every other
  file the artwork names (adr 0011).

A label is **a step**, not a decoration:

- it makes the artwork longer, so the last thing an artwork does can be its
  title and the export will contain it;
- it appears when that step runs, and going back takes it away again;
- it is baked into the texture like a stroke, so it costs nothing per frame
  afterwards.

It is **not a path**: `erase`, `pivot`, `shift` and the path styles do not reach
it, and it cannot be drawn stroke by stroke. That is the trade, and it is the
whole reason both calls exist.

## Consequences

- **A label claims its step.** `Timeline.claim(t, s)` moves the turtle's `last`
  forward without taking a slot in the occupancy grid — nothing moves, and two
  labels on one step is a legitimate thing to write. Moving `last` is what the
  colour depends on: an appearance starts at `last + 1` (adr 0009), so without
  it a `path_color` written *below* a label would reach *back* and repaint it.
  The harness measures exactly that — two labels, two colours, in declaration
  order.
- **The colour is read at replay, not at declaration.** `path_color` is a
  timeline event; the pool only holds the latest one. So the label stores which
  turtle it belongs to and `Runner.instant` draws it right after applying that
  step's appearance. Drawing every label at the end of a rebuild instead — the
  first version — gave all of them the colour the artwork finishes on.
- **The typeface travels like the sheet.** A Block field cannot hold a `dyn`, so
  the handle is a local of `play` passed to whoever draws (adr 0020) — `frame`,
  `instant`, `rebuild`, `animate`, `hold`, `shown`, `export`, `movie`,
  `deliver`. A `dyn` also cannot be nil or be declared inside a branch, so with
  no TTF asked for it is a 1×1 image nobody looks at: `has_face` decides, never
  the handle. A font that will not load prints why and the artwork carries on in
  the built-in one.
- **128 labels**, in fixed arrays like everything else, and it says so when the
  129th is ignored.
- **The hotkeys can step aside.** `Runner.typing(1)` silences F, P, R, A, SPACE
  and the arrows. Nothing sets it yet — `text` is written in the artwork's
  source, not on the stage — but the tool's hotkeys are bare letters, and the
  studio will have a text field. Nave solved this by asking, once per frame,
  whichever screen owns the field; this is the same shape, put in before the
  bug rather than after it.
- **A label-only step ends instantly.** `arm` finds no movement, `animate`
  returns arrived, and the label lands on the next presented frame — in an
  export, on the next step that draws. A title that should sit on screen by
  itself is a label on the artwork's last step, where the export's end hold
  keeps it, or a label on a step that something slow is also drawing.
