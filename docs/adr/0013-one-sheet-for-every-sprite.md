# 0013 — One sheet for every sprite

**Status:** accepted

## Context

Pillars §3 asks for `Turtle.image`: a turtle drawn as a picture instead of a
circle, turned to face where she walks. Language v0.30 supplies the drawing side
— `graph.draw_image_rot` and `graph.draw_sprite`, both pivoting on the image's
own centre — so what was missing was ours.

The obstacle is where the image lives. A turtle's body is drawn **every frame**,
so decoding a PNG per turtle per frame is out; the image has to be a live handle
for the whole run. A Block cannot hold a `dyn`
([0011](0011-the-artwork-file-declares.md)), so it cannot be a field of the
Pool, and putting it in `main.flx` puts image plumbing back into the file that
should read like a drawing.

That leaves a local `dyn` in `Runner.play`, threaded through the frame loop —
which is the plumbing [0010](0010-the-video-is-a-second-pass-over-the-frames.md)
refused for the video cursor. One parameter is tolerable; one per sprite is not,
and "one per sprite" also caps the artwork at however many parameters were
written.

## Decision

**Every sprite in the artwork is composed into one sheet before the frame loop
starts.** One `dyn`, one parameter, any number of pictures.

```fluxa
leo.image("turtle.png", 0.6)                   // the whole file
ana.sprite("sheet.png", 0, 0, 64, 64, 1.0)     // one region of it
```

- The Pool keeps the **paths**, not the images: up to eight entries, each a path
  and a scale. The key is the pair, so the same picture at two scales is two
  entries and neither turtle has to give up the size she asked for.
- `Pool.atlas()` decodes each entry, scales it, and blits it down a 1024×1024
  image, recording where each one landed. Called once per run, by `play`, and
  handed to `frame` as a local — which is also where the background image
  already lives for the length of a rebuild.
- A turtle stores which entry she uses and, optionally, a region inside it in
  the file's own pixels. Regions scale with their entry.
- `Pool.draw` calls `graph.draw_sprite` with her heading negated, so art drawn
  facing **right** points where she walks — 0° is right everywhere else here.
- No sprite, or a file that could not be read: she is a circle, as before.

## Consequences

- `main.flx` is untouched. The sheet never appears in it, `play` still takes
  `(win, canvas, done)`, and an artwork with no sprites pays a 1×1 blank image.
- One parameter was added to `frame`, `animate`, `hold`, `export`, `movie` and
  `deliver` — the same shape `canvas` already had. That is the price, and it is
  the whole price.
- Eight files, one 1024×1024 sheet. A file that does not fit is skipped with a
  message and that turtle stays a circle. Eight is a limit on *files*, not on
  looks: a sheet of regions gives thirty-two turtles thirty-two appearances.
- The sheet is rebuilt once per run, so editing a PNG shows up on the next save,
  like everything else.
- Transparency comes from the file. A PNG without an alpha channel draws its
  background with it — which is what the harness's own generated art does, and
  it is worth knowing before wondering why a sprite has a black box around it.
- `graph.draw_sprite` has no scale parameter, which is why scale is applied when
  the sheet is composed rather than when the sprite is drawn. It also means a
  scale is a property of the entry: cheap, and predictable.
