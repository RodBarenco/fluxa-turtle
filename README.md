# Fluxa Turtle

A visual programming tool written in Fluxa-lang. You write a sequence of
actions, save the file, and the screen responds — without restarting anything.
The turtles, the drawings, the positions and the steps already finished stay
alive, because the state survives the hot reload.

**Write, save, and watch the next action happen.**

![the example artwork](docs/example.png)

---

## Installing

Fluxa Turtle is written in Fluxa-lang, and the runtime is not shipped in this
repository. Build it once from the language repo:

**[github.com/RodBarenco/fluxa-lang](https://github.com/RodBarenco/fluxa-lang)**

You need **Linux with a working OpenGL driver** — the window, the baked texture
and the capture all go through the GPU. Three steps: the system libraries,
Raylib, then the runtime itself.

### 1. System libraries

`make build` builds the whole standard library, so it wants the development
packages of everything it can link. On Debian, Ubuntu or Pop!_OS:

```bash
sudo apt update
sudo apt install -y build-essential make python3 git pkg-config \
    libsodium-dev libcurl4-openssl-dev libffi-dev zlib1g-dev \
    libsqlite3-dev libpq-dev libmicrohttpd-dev libmosquitto-dev
```

What each one is there for: **libsodium** (crypto), **libcurl** (`std.http`
client), **libffi** (the FFI), **zlib** (compression), **libsqlite3** and
**libpq** (the databases), **libmicrohttpd** (the HTTP server), **libmosquitto**
(MQTT). Turtle itself uses none of them — they are the cost of building the full
runtime. Fedora: the same names with `-devel`. Arch: `libsodium curl libffi zlib
sqlite postgresql-libs libmicrohttpd mosquitto`.

### 2. Raylib

This is the one Turtle actually needs, and the one no distribution ships in a
current enough version — build it from source:

```bash
sudo apt install -y libgl1-mesa-dev libx11-dev libxrandr-dev \
    libxinerama-dev libxcursor-dev libxi-dev

git clone --depth 1 https://github.com/raysan5/raylib
cd raylib/src
make PLATFORM=PLATFORM_DESKTOP
sudo make install
sudo ldconfig
```

It installs into `/usr/local/lib`. This project is developed against **raylib
6.0** (`libraylib.so.600`).

### 3. The runtime

```bash
git clone https://github.com/RodBarenco/fluxa-lang
cd fluxa-lang
make build FLUXA_GRAPH_RAYLIB=1 FLUXA_IMAGE_RAYLIB=1
```

The two flags are what Turtle needs: the window, the strokes and the baked
texture come from `std.graph`, and the canvas, the capture and the PNGs from
`std.image` — both on Raylib. The language README is the authority on the build
flags if they change.

The binary lands in the repository root. Put it in this project's root, or
anywhere on your `PATH`:

```bash
cp fluxa /path/to/fluxa-turtle/
```

To check it came out with the graphics in it:

```bash
ldd ./fluxa | grep raylib      # libraylib.so.600 => /usr/local/lib/...
```

If that prints nothing, the build did not pick up Raylib and the window will
never open. `ffmpeg` is worth having too, but only to turn an export into a
video.

The libs this project uses are already declared in `fluxa.toml`: `std.graph`,
`std.image`, `std.math`, `std.time`, `std.strings` and `std.fs`.

### Windows

**Turtle does not work on Windows yet: the hot reload does not run there.** The
language itself builds on Windows (MSYS2 — see `docs/WINDOWS.md` in the language
repository), but `-dev` — watch the file, reload on save, keep the window and
the finished steps alive — is what this whole tool is, and it is not available
in that build. Linux is the supported platform; macOS builds the language but is
untested here.

---

## Running it

```bash
./fluxa run main.flx -dev
```

`-dev` is the mode that matters: it watches the file and reloads on every save,
preserving what already happened. The window does not blink, the drawing does
not disappear, and only the new steps are animated.

Without `-dev` the program runs once and leaves the artwork on screen until you
close the window.

---

## The core idea: the step

Every action carries a **step** number. That number is the composition's
logical stage, and it is what organises everything:

```fluxa
leo.go(1, 200.0, 0.0)     // step 1: walk 200 px, no turn
leo.go(2, 200.0, 144.0)   // step 2: turn 144 degrees and walk 200 px
```

Three rules follow from it:

**Finished steps do not repeat.** When you save again, what already happened is
rebuilt instantly and execution carries on from the next step not yet
performed. That is what lets you build the artwork bit by bit.

**The same step means simultaneous.** Different turtles with actions on the
same step move at the same time. The step only ends when the last of them
arrives.

```fluxa
leo.go(1, 200.0, 0.0)     // both set off together
ana.go(1, 220.0, 0.0)     // and step 1 lasts as long as the slower one
```

**One action per turtle per step.** If the same turtle gets two actions on the
same step, the first one counts and the second is ignored — a turtle cannot
make two movements at once. Execution is not interrupted by it.

---

## Getting started

`main.flx` already comes with an artwork, almost entirely commented out on
purpose. Uncomment **one stage**, save, and see what shows up. Then the next.

| Stage | What it shows |
|---|---|
| 1 | one turtle, one stroke |
| 2 | thirty-five more steps turn it into the rosette |
| 3 | a second turtle drawing at the same time, entering without a trail |
| 4 | the stroke changing from the step where you change it |
| 5 | an image as the background |
| 6 | exporting the artwork as frames |

The image at the top of this page is what those stages produce — captured from
the window, not an illustration.

**[docs/ARTWORKS.md](docs/ARTWORKS.md)** has eight complete compositions ready
to paste — rosettes, spirals, mandalas, a flower. Each one comes with the image
that this exact code produces.

**[docs/RECIPES.md](docs/RECIPES.md)** has the loose pieces: ready-made
turtles, closed shapes, palettes, rhythm tricks.

---

## The turtle

Each turtle is an independent instance:

```fluxa
Block leo typeof turtle.Turtle
leo.spawn(340.0, 363.0)
```

Angles are in degrees: **0 points right** and the angle grows
counter-clockwise, as on the cartesian plane.

### Appearance

```fluxa
leo.color(0, 224, 150)      // body colour (RGB 0–255)
leo.size(9.0)               // body radius
leo.face(90.0)              // initial heading, in degrees
leo.speed(260.0)            // default speed, in pixels per second
leo.hide()                  // hide her (she still moves and draws)
leo.show()
```

### Path

```fluxa
leo.path_color(0, 224, 150)
leo.path_width(3)
leo.path_opacity(70)        // 0 to 100

leo.path_solid()            // solid line
leo.path_dotted()           // dotted
leo.path_dashed()           // dashed
leo.path_dots()             // round dots
leo.path_dash(14, 9)        // adjusts the dash and gap of any of them

leo.path_off()              // stop drawing
leo.path_on()

leo.path_clear(7)           // on step 7, clear THIS turtle's path
```

### Appearance applies from where you write it

An appearance call is not retroactive. It takes effect from the **next step that
turtle declares**, and what is already drawn keeps the look it was drawn with:

```fluxa
leo.path_color(90, 200, 255)   // her starting colour: no step declared yet
leo.ring(1, 36, 500.0, 170.0)  // steps 1 to 36 come out blue

leo.path_color(255, 90, 160)   // from here on
leo.ring(37, 36, 500.0, 170.0) // steps 37 to 72 come out pink
```

To change the whole artwork, move the call above the steps it should affect. The
rule is the same for `color`, `size`, `speed`, `show`/`hide` and every `path_*`
— the changes live in the timeline, at the step where they were written, and the
rebuild replays them there ([adr 0009](docs/adr/0009-appearance-is-a-timeline-event.md)).

`face` is the exception: it is the heading the turtle is born with, part of her
declaration rather than something that happens on a step.

### Movement

```fluxa
leo.go(1, 200.0, 90.0)                 // turn 90 degrees and walk 200 px
leo.go_silent(2, 300.0, 0.0)           // same displacement, without drawing
leo.go_at(3, 200.0, 0.0, 700.0)        // this action at 700 px/s
leo.go_silent_at(4, 400.0, 0.0, 900.0)
```

The speed declared on the action beats the turtle's own speed. That is how one
turtle speeds up on one leg and crawls on the next.

### The stage

```fluxa
stage.Stage.background(16, 17, 24)     // solid colour

danger { bg = image.load("texture.png") }
if err != nil { print(err[0]) }
stage.Stage.image_tile()               // repeat across the whole stage
stage.Stage.image_center()             // once, in the middle
stage.Stage.image_stretch(bg)          // taken to the screen size
stage.Stage.image_scale(2.0)
stage.Stage.image_off()
```

The background image is a `dyn`, so it lives in `main.flx` as `prst dyn bg` and
arrives at the Stage as a parameter.

---

## Replay

With the window focused, press **R**. The artwork is redone from step 1,
animated, the way someone would see it watching the whole composition at once.
It is the same code path as normal execution — it is not a recording.

---

## Exporting

```fluxa
exporter.Exporter.setup("export", 60)   // folder and frame rate
exporter.Exporter.hold(30, 90)          // still frames at the start and end
exporter.Exporter.range(1, 5)           // optional: only part of the artwork
runner.Runner.export(win, canvas, bg)
```

Exporting **does not record the screen**. It redoes the artwork from the
beginning and renders each frame with time advancing `1/fps` per frame — never
by the clock. A slow machine takes longer to generate, and the video comes out
exactly the same. Two runs produce byte-identical frames.

What comes out is a sequence of numbered PNGs. Fluxa does not have a video
encoder yet, so the last step is an external command — which the program itself
prints, ready to paste, when it finishes:

```bash
ffmpeg -framerate 60 -i export/frame_%06d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
```

---

## How the project is laid out

```
main.flx              your artwork — the file you edit
static/config.flx     the shared numbers
static/stage.flx      the stage (background)
static/pool.flx       the turtles' state
static/timeline.flx   the action queue, by step
static/painter.flx    the path and its baked texture
static/turtle.flx     the turtle (the type you use)
static/exporter.flx   exporting as frames
static/runner.flx     execution
lab/                  verification harnesses
docs/                 artworks, recipes, changelog and design decisions
```

There is no real importing. The loader runs before the lexer, prefixes each
module's declarations with its namespace and inserts them before the `main`
body — the runtime sees **one single flat program** (spec §9.5). Two rules
follow: names must be unique across modules, and whatever depends on another
comes later in the list. That is why `runner` is last.

---

## Known limits

- **8 turtles**, 4096 steps, 16384 actions. The limits are in
  `static/config.flx` and in the pool declarations. Going past the turtle limit
  prints a warning and ignores the extra ones.
- **Opacity is not an alpha channel.** `graph.draw_line` only takes R, G and B,
  so transparency is obtained by mixing with the background. Two translucent
  paths crossing do not add up.
- **No video encoder.** Exporting delivers numbered PNGs.
- **Saving in the middle of a movement restarts that step.** Only finished
  steps count; partial progress does not survive the reload yet.
- **512 appearance changes** across the whole artwork. Past that the extra ones
  are ignored.

---

## Verification

The harnesses in `lab/` check the behaviour and produce an image:

```bash
./fluxa run lab/shot.flx        # pillar rules: simultaneity, conflict, go_silent
./fluxa run lab/paths.flx       # the four styles, opacity and path_clear
./fluxa run lab/styles.flx      # an appearance change only affects later steps
./fluxa run lab/speed.flx       # each step's duration against the expected one
./fluxa run lab/stress.flx      # 3000 steps: rebuild and per-frame cost
./fluxa run lab/export.flx      # frame count and determinism
./fluxa run lab/background.flx  # the three background image modes
./fluxa run lab/preview.flx     # the main.flx artwork with everything on
```

---

## License

MIT — see [LICENSE](LICENSE).
