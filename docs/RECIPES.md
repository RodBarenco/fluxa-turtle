# Recipes

Every call these use is in **[TURTLE.md](TURTLE.md)**, the full guide.

Loose pieces to build your artwork with. Each block goes in the part
indicated — either the **scene** (where the turtles are declared) or the
**steps** (where the actions are declared).

If you want a whole composition ready to go, see **[ARTWORKS.md](ARTWORKS.md)**.

Remember: the step number is what synchronises. Actions on the same step happen
at the same time, and a turtle only performs one action per step.

---

## Ready-made turtles

> goes in the **scene**

```fluxa
Block leo typeof turtle.Turtle
leo.spawn(400.0, 300.0)
leo.color(0, 224, 150)
leo.path_color(0, 224, 150)
leo.path_width(3)
leo.speed(260.0)
```

**Thin and fast**

```fluxa
Block streak typeof turtle.Turtle
streak.spawn(400.0, 300.0)
streak.color(255, 255, 255)
streak.path_color(200, 220, 255)
streak.path_width(1)
streak.speed(900.0)
```

**Thick, slow brush**

```fluxa
Block brush typeof turtle.Turtle
brush.spawn(400.0, 300.0)
brush.color(255, 180, 60)
brush.path_color(255, 180, 60)
brush.path_width(12)
brush.speed(90.0)
```

**Ghost — moves, but barely marks**

```fluxa
Block ghost typeof turtle.Turtle
ghost.spawn(400.0, 300.0)
ghost.color(150, 150, 170)
ghost.path_color(150, 150, 170)
ghost.path_width(8)
ghost.path_opacity(22)
ghost.hide()
```

**Trail of dots**

```fluxa
Block tracks typeof turtle.Turtle
tracks.spawn(400.0, 300.0)
tracks.color(120, 170, 255)
tracks.path_color(120, 170, 255)
tracks.path_width(7)
tracks.path_dots()
tracks.path_dash(1, 16)
```

---

## Closed shapes

> goes in the **steps**

There is a call for each of these now — `leo.triangle(1, cx, cy, r)`,
`square`, `polygon`, `circle`, `ellipse`, `star`, `rect`, `arc` — placed by the
centre and returning the next free step. They are in
[TURTLE.md](TURTLE.md#ready-made-shapes), and they are what to reach for when
you want the figure rather than the walk.

What follows is the walk, because it is worth seeing once: every regular polygon
is the same movement repeated — walk one side, turn `360 / number of sides`.
Written this way the figure starts wherever she is standing and in whatever
direction she is facing, which the ready-made ones do not do.

**Triangle**

```fluxa
leo.go(1, 200.0,   0.0)
leo.go(2, 200.0, 120.0)
leo.go(3, 200.0, 120.0)
```

**Square**

```fluxa
leo.go(1, 160.0,  0.0)
leo.go(2, 160.0, 90.0)
leo.go(3, 160.0, 90.0)
leo.go(4, 160.0, 90.0)
```

**Hexagon** — a negative turn closes it clockwise

```fluxa
leo.go(1, 120.0,   0.0)
leo.go(2, 120.0, -60.0)
leo.go(3, 120.0, -60.0)
leo.go(4, 120.0, -60.0)
leo.go(5, 120.0, -60.0)
leo.go(6, 120.0, -60.0)
```

**Five-pointed star** — the 144-degree turn is the trick

```fluxa
leo.go(1, 200.0,   0.0)
leo.go(2, 200.0, 144.0)
leo.go(3, 200.0, 144.0)
leo.go(4, 200.0, 144.0)
leo.go(5, 200.0, 144.0)
```

**Circle** — many short sides

```fluxa
leo.go( 1, 26.0,  0.0)
leo.go( 2, 26.0, 30.0)
leo.go( 3, 26.0, 30.0)
leo.go( 4, 26.0, 30.0)
leo.go( 5, 26.0, 30.0)
leo.go( 6, 26.0, 30.0)
leo.go( 7, 26.0, 30.0)
leo.go( 8, 26.0, 30.0)
leo.go( 9, 26.0, 30.0)
leo.go(10, 26.0, 30.0)
leo.go(11, 26.0, 30.0)
leo.go(12, 26.0, 30.0)
```

**Spiral** — the side grows on each step

```fluxa
leo.go(1,  30.0, 60.0)
leo.go(2,  45.0, 60.0)
leo.go(3,  60.0, 60.0)
leo.go(4,  75.0, 60.0)
leo.go(5,  90.0, 60.0)
leo.go(6, 105.0, 60.0)
leo.go(7, 120.0, 60.0)
leo.go(8, 135.0, 60.0)
```

**Rosette** — a turn that does not close, repeated many times. Use 121 degrees
and let it run for dozens of steps.

```fluxa
leo.go(1, 150.0, 121.0)
leo.go(2, 150.0, 121.0)
leo.go(3, 150.0, 121.0)
leo.go(4, 150.0, 121.0)
leo.go(5, 150.0, 121.0)
leo.go(6, 150.0, 121.0)
leo.go(7, 150.0, 121.0)
leo.go(8, 150.0, 121.0)
```

---

## Two or more at the same time

> goes in the **steps**

The repeated step number is what makes it happen together.

**Mirror** — one to each side

```fluxa
leo.go(1, 150.0,   0.0)
ana.go(1, 150.0, 180.0)

leo.go(2, 150.0,  90.0)
ana.go(2, 150.0,  90.0)
```

**Chase** — same distance, different speeds. The step only ends when the slower
one arrives, so one waits for the other.

```fluxa
// in the scene:
//   leo.speed(120.0)
//   ana.speed(480.0)
leo.go(1, 300.0, 0.0)
ana.go(1, 300.0, 0.0)
```

**Taking turns** — one walks while the other rests. Just do not declare an
action for her on that step.

```fluxa
leo.go(1, 200.0,  0.0)
ana.go(2, 200.0, 90.0)
leo.go(3, 200.0, 90.0)
ana.go(4, 200.0, 90.0)
```

---

## Entering and leaving

> `spawn` in the **scene**, `go_silent` in the **steps**

Born off-screen and walks in, leaving no trail:

```fluxa
// in the scene:
//   bia.spawn(-100.0, 300.0)
bia.go_silent(1, 300.0, 0.0)   // enters invisibly
bia.go(2, 200.0, 0.0)          // and only then draws
```

Leaves at the end:

```fluxa
bia.go_silent(9, 500.0, 0.0)
```

Repositioning without drawing, mid-artwork:

```fluxa
leo.path_off()                 // in the scene, before the steps
// ...or per action:
leo.go_silent(5, 180.0, 90.0)
```

---

## Rhythm and speed

> `speed` in the **scene**, `go_at` in the **steps**

```fluxa
leo.speed(260.0)                    // this turtle's default
leo.go_at(3, 200.0, 0.0,  60.0)     // this leg crawls
leo.go_at(4, 200.0, 0.0, 900.0)     // this one bolts
```

A pause is a displacement of zero at a low speed — the artwork sits still for a
whole step:

```fluxa
leo.go_at(5, 0.0, 0.0, 1.0)
```

---

## Stroke styles

> goes in the **scene**

```fluxa
leo.path_solid()
leo.path_dotted()
leo.path_dashed()
leo.path_dots()

leo.path_dash(20, 14)      // long dash, wide gap
leo.path_dash(2, 4)        // almost a line
```

Clearing one turtle's path mid-artwork — her position does not change:

```fluxa
leo.path_clear(6)          // goes in the steps
```

---

## Backgrounds

> goes in the **scene**

Solid colour:

```fluxa
stage.Stage.background(16, 17, 24)
```

An image. `bg` is already declared in `main.flx` as `prst dyn bg`:

```fluxa
danger { image.discard(bg)  bg = image.load("texture.png") }
if err != nil { print("background: ", err[0]) }
stage.Stage.image_tile()        // repeats across the whole stage
stage.Stage.image_scale(1.5)
```

```fluxa
stage.Stage.image_center()      // once, in the middle
stage.Stage.image_stretch(bg)   // taken to the screen size
stage.Stage.image_off()         // back to the solid colour
```

---

## Palettes

> goes in the **scene**

**Night**

```fluxa
stage.Stage.background(16, 17, 24)
// 0 224 150   sea green
// 255 122 92  coral
// 120 170 255 blue
// 255 200 60  amber
```

**Paper**

```fluxa
stage.Stage.background(242, 238, 228)
// 40 44 52    graphite
// 190 60 60   red
// 60 110 180  ink blue
// 220 160 40  ochre
```

**Neon**

```fluxa
stage.Stage.background(10, 8, 20)
// 255 40 160  magenta
// 60 255 220  cyan
// 250 240 60  yellow
// 160 80 255  violet
```

**Earth**

```fluxa
stage.Stage.background(30, 26, 22)
// 214 158 106 sand
// 140 100 70  wood
// 90 120 80   moss
// 200 90 60   terracotta
```

---

## Exporting

> goes before the execution line, at the end of `main.flx`

```fluxa
exporter.Exporter.setup("export", 60)
exporter.Exporter.hold(30, 90)
runner.Runner.export(win, canvas, bg)
```

Only part of the artwork:

```fluxa
exporter.Exporter.range(4, 9)
```

Lighter, for testing:

```fluxa
exporter.Exporter.setup("export", 24)
exporter.Exporter.hold(6, 12)
```

After running, the `ffmpeg` command is printed in the terminal, ready to paste.
