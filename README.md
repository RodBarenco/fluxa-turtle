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
`std.image`, `std.math`, `std.time`, `std.strings`, `std.fs` and `std.video`.

### 4. Syntax highlighting

`.flx` files come out grey in an editor that has never heard of Fluxa. The
highlighter lives in **[github.com/RodBarenco/fluxa-tooling](https://github.com/RodBarenco/fluxa-tooling)**:

```bash
git clone https://github.com/RodBarenco/fluxa-tooling
cd fluxa-tooling
```

**VS Code** — it is not on the Marketplace, so install the `.vsix` by hand:

```bash
code --install-extension highlighter/vs-code/fluxa-lang-0.1.0.vsix
```

**Neovim** — copy the two files:

```bash
mkdir -p ~/.config/nvim/ftdetect ~/.config/nvim/syntax
cp highlighter/neovim/ftdetect/fluxa.vim ~/.config/nvim/ftdetect/
cp highlighter/neovim/syntax/fluxa.vim   ~/.config/nvim/syntax/
```

Or through a plugin manager — vim-plug:

```vim
Plug 'RodBarenco/fluxa-tooling'
```

lazy.nvim:

```lua
{
    "RodBarenco/fluxa-tooling",
    ft = "fluxa",
    config = function()
        vim.opt.rtp:append(vim.fn.stdpath("data") .. "/lazy/fluxa-tooling/highlighter/neovim")
    end
}
```

An LSP (go-to-definition, hover, diagnostics, completion) is announced there as
coming.

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
| 6 | one line that writes the artwork as an MP4 |

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
stage.Stage.background(16, 17, 24)          // solid colour

stage.Stage.tile("texture.png", 1.0)        // repeated across the stage
stage.Stage.center("logo.png", 2.0)         // once, in the middle
stage.Stage.stretch("photo.png")            // taken to the screen size
stage.Stage.image_off()                     // back to the plain colour
```

The last number is the scale. If the file cannot be read, the drawing carries on
and the reason is printed — a missing texture never costs you the artwork.

You give the Stage a **path**, never an image: the file is decoded during the
rebuild, which happens once per save, and goes into the baked texture, so it
costs nothing per frame. That is also why nothing about an image handle appears
in `main.flx` ([adr 0011](docs/adr/0011-the-artwork-file-declares.md)).

---

## Keys

With the window focused:

| Key | What it does |
|---|---|
| **R** | Replay. The artwork is redone from step 1, animated, the way someone would see the whole composition at once. Same code path as normal execution — it is not a recording. |
| **F** | Fullscreen, and F again to come back. Made for two monitors: the code on one, the artwork filling the other. The stage keeps its proportions, scaled up with bars on the sides if the screen is wider. |

---

## Exporting

One line in `main.flx` — from which step, to which step, and how many frames per
second:

```fluxa
export.Video(1, 36, 5)      // artwork.mp4
export.Frames(1, 36, 60)    // numbered PNGs, in export/
```

`0` as the second step means "through the last one". Asking for more steps than
the artwork has is not a mistake: it generates what there is and says so, so the
line can be written once and left there while the drawing grows under it.

The video is **H.264 written by Fluxa itself** — no ffmpeg, no external process,
nothing left behind. Half a second of stillness is added at each end so it does
not start and finish mid-gesture.

**Nothing is ever written over.** The first render is `artwork.mp4`, the next
`artwork1.mp4`, then `artwork2.mp4` — and the frames go to `export/`, `export1/`,
`export2/` the same way. A render is work, and a file saved with the line still
uncommented should not cost you the last one.

Neither call renders anything by itself. They record what was asked for, and the
Runner delivers it when execution reaches the stage — the artwork file declares,
the runner executes ([adr 0011](docs/adr/0011-the-artwork-file-declares.md)).

It **does not record the screen.** The artwork is redone from the beginning and
each frame is rendered with time advancing `1/fps` per frame — never by the
clock. A slow machine takes longer to generate and the video comes out exactly
the same; two runs produce byte-identical frames.

### The long way, for full control

```fluxa
export.Exporter.setup("frames", 60)     // folder and frame rate
export.Exporter.hold(30, 90)            // still frames at the start and end
export.Exporter.range(1, 5)             // only part of the artwork
runner.Runner.export(win, canvas)       // writes the numbered PNGs
```

To turn those frames into a video and keep them:

```fluxa
danger {
    dyn mp4 = video.open("artwork.mp4", config.W(), config.H(), export.Exporter.get_fps())
    export.Exporter.to_video(mp4, 1)    // 1 keeps the PNGs, 0 deletes them
    video.close(mp4)
}
if err != nil { print("video: ", err[0]) }
```

The video is a second pass over the frames that were just written, not a
different render — the same exact images, in order
([adr 0010](docs/adr/0010-the-video-is-a-second-pass-over-the-frames.md)).

For WebM or GIF the frames are still there, and `finish()` prints the ffmpeg
command ready to paste:

```bash
ffmpeg -framerate 60 -i frames/frame_%06d.png -vf split[a][b];[a]palettegen[p];[b][p]paletteuse out.gif
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
static/export.flx     exporting: frames and MP4
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

- **32 turtles, 6000 steps, 65536 actions, 2048 appearance changes, 8192
  not-yet-baked segments.** Every one of them is in `static/config.flx`, next to
  the stage size and the frame rate, and each is mirrored by an array
  declaration the file points at — a Fluxa array is declared with a literal
  size, so the two are changed together. Going past a limit prints a warning and
  ignores the extra, never silently corrupts the artwork.
- **A 6000-step artwork rebuilds in about a second**, once per save. It is the
  worst case of the declared limits (32 turtles × 6000 steps); 3000 steps with
  one turtle rebuild in 145 ms.
- **Opacity is not an alpha channel.** `graph.draw_line` only takes R, G and B,
  so transparency is obtained by mixing with the background. Two translucent
  paths crossing do not add up.
- **MP4 only, for video.** `std.video` writes H.264; WebM and GIF still go
  through ffmpeg, from the frames.
- **Saving in the middle of a movement restarts that step.** Only finished
  steps count; partial progress does not survive the reload yet.

---

## Verification

The harnesses in `lab/` check the behaviour and produce an image:

```bash
./fluxa run lab/shot.flx        # pillar rules: simultaneity, conflict, go_silent
./fluxa run lab/paths.flx       # the four styles, opacity and path_clear
./fluxa run lab/styles.flx      # an appearance change only affects later steps
./fluxa run lab/speed.flx       # each step's duration against the expected one
./fluxa run lab/stress.flx      # 3000 steps: rebuild and per-frame cost
./fluxa run lab/limits.flx      # 32 turtles, step 6000, and the occupancy grid
./fluxa run lab/export.flx      # frame count and determinism
./fluxa run lab/video.flx       # the MP4: frame count, size and frame rate
./fluxa run lab/background.flx  # the three background image modes
./fluxa run lab/preview.flx     # the main.flx artwork with everything on
```

---

## License

MIT — see [LICENSE](LICENSE).
