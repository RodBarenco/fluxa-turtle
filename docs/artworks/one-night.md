# One Night

*A nest opens after dark. Eight hatchlings, one wrong turn, and the oldest
compass there is.*

![One Night](one-night.png)

**[Watch it draw itself](one-night.mp4)** — ten seconds, 800×600, written by the
program itself with `export.Video`.

---

## The night

A sea turtle lays her eggs above the tide line and leaves. Two months later,
underground, the hatchlings dig upward together and wait just under the surface
for the sand to go cold — which is how they know the sun is down and the birds
are gone.

Then they run. It is the first thing they ever do and one of the hardest: a few
dozen metres of open beach, on flippers built for water, in the dark.

They are not lost in that dark. They steer by it. A hatchling turns toward the
brightest, most open horizon it can see, and on an undeveloped beach that is
always the sea — the sky is wider over water, and the moon lays a road of light
straight across it. That is the whole compass: **go where it is bright and low
and open**.

It works because for a hundred million years nothing on the land side was
brighter than the sea. A single lamp behind the beach breaks it. The hatchlings
turn inland, toward a road, a porch, a hotel — and crawl until something eats
them or the sun comes up. The estimates people quote for how many make it to
adulthood vary wildly, one in a hundred, one in a thousand. All of them are
small, and every one of those numbers assumes the hatchling at least got the
direction right.

In this drawing seven of them make it. The dotted lines are tracks in the sand;
they turn to solid water-colour at the foam line, where a track stops being a
track and becomes a swim. One of them turned the wrong way. Her line goes
orange, and it ends at the lamp.

---

## What is on the screen

| The scene | How it is drawn |
|---|---|
| **The moon and its haze** | three circles — a circle here is a 36-sided polygon, one turtle, one `ring` |
| **The stars** | one turtle, twenty times: a jump with the pen up, one dot with it down |
| **The sea** | four long shallow arcs, dashed far away and solid near the shore |
| **The moonlight on the water** | one turtle walking down, the stroke widening three times on the way |
| **The tracks** | eight turtles leaving the nest at the same step, each bending toward the light |
| **The wrong turn** | the same, aimed at the lamp — the only warm colour in the frame |

Two things the tool does are doing most of the work here.

**Appearance belongs to the step where it is written.** Each hatchling declares
sand colour, walks her way across the beach, and only then declares the water
colour — so the track behind her stays sand while the part ahead comes out
teal. One turtle, one continuous line, two materials.

**A step is a moment, not a turn in a queue.** All eight leave on step 50 and
move together, every one at her own curve, and the step ends when the last one
arrives. That is why it reads as a run and not as a list.

---

## Paste it

Open `main.flx`, delete whatever sits between `timeline.Timeline.reset()` and
the execution line, and paste this in its place. Save. The window is already
open, so the drawing simply happens.

```fluxa
stage.Stage.background(8, 14, 26)

// ═══ the moon ═══════════════════════════════════════════════════
//
// A circle is a polygon with enough sides. Thirty-six strokes, ten degrees
// apart, and two fainter rings around it for the haze.
Block moon typeof turtle.Turtle
moon.spawn(246.0, 112.0)
moon.face(90.0)
moon.hide()
moon.speed(300.0)
moon.path_color(228, 234, 242)
moon.path_width(2)
moon.path_opacity(85)
moon.ring(1, 36, 8.02, 10.0)
Block haze typeof turtle.Turtle
haze.spawn(262.0, 112.0)
haze.face(90.0)
haze.hide()
haze.speed(700.0)
haze.path_color(150, 172, 202)
haze.path_width(1)
haze.path_opacity(20)
haze.ring(1, 36, 10.81, 10.0)
Block haze2 typeof turtle.Turtle
haze2.spawn(282.0, 112.0)
haze2.face(90.0)
haze2.hide()
haze2.speed(900.0)
haze2.path_color(120, 146, 184)
haze2.path_width(1)
haze2.path_opacity(10)
haze2.ring(1, 36, 14.29, 10.0)

// ═══ the sky ════════════════════════════════════════════════════
//
// One turtle draws every star: a jump with the pen up, one dot with it down.
// Three sizes and three brightnesses — a sky with one kind of star in it does
// not look like a sky.
//
// Careful with the jumps: the turn is measured from where the turtle is
// already pointing, not from the screen. Feed it absolute angles and the
// stars end up in the sea.

Block stars typeof turtle.Turtle
stars.spawn(784.0, 30.0)
stars.face(0.0)
stars.hide()
stars.speed(16000.0)
stars.path_color(228, 234, 246)
stars.path_dots()
stars.path_dash(1, 40)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(1, 7.1, 102.7)
stars.go(2, 1.0, 0.0)
stars.path_width(4)
stars.path_opacity(74)
stars.go_silent(3, 123.9, 157.9)
stars.go(4, 1.0, 0.0)
stars.go_silent(5, 116.1, -156.0)
stars.go(6, 1.0, 0.0)
stars.go_silent(7, 89.5, 139.5)
stars.go(8, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(9, 65.7, -145.6)
stars.go(10, 1.0, 0.0)
stars.go_silent(11, 90.3, 143.4)
stars.go(12, 1.0, 0.0)
stars.path_width(4)
stars.path_opacity(74)
stars.go_silent(13, 56.0, -116.5)
stars.go(14, 1.0, 0.0)
stars.go_silent(15, 75.2, 0.8)
stars.go(16, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(17, 50.7, 69.8)
stars.go(18, 1.0, 0.0)
stars.go_silent(19, 108.4, 69.3)
stars.go(20, 1.0, 0.0)
stars.path_width(4)
stars.path_opacity(74)
stars.go_silent(21, 67.1, -152.7)
stars.go(22, 1.0, 0.0)
stars.go_silent(23, 55.0, 123.0)
stars.go(24, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(25, 99.7, -134.6)
stars.go(26, 1.0, 0.0)
stars.path_width(4)
stars.path_opacity(74)
stars.go_silent(27, 96.5, 132.9)
stars.go(28, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(29, 46.1, 35.6)
stars.go(30, 1.0, 0.0)
stars.path_width(6)
stars.path_opacity(92)
stars.go_silent(31, 111.3, -177.5)
stars.go(32, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(33, 135.0, 158.5)
stars.go(34, 1.0, 0.0)
stars.path_width(6)
stars.path_opacity(92)
stars.go_silent(35, 79.5, -152.6)
stars.go(36, 1.0, 0.0)
stars.path_width(4)
stars.path_opacity(74)
stars.go_silent(37, 239.2, 79.1)
stars.go(38, 1.0, 0.0)
stars.path_width(2)
stars.path_opacity(56)
stars.go_silent(39, 92.2, 86.6)
stars.go(40, 1.0, 0.0)

// ═══ the sea ════════════════════════════════════════════════════
//
// Long shallow arcs, one behind the other. The far ones are dark and broken,
// the near ones lighter and whole: distance is drawn, not described. Each
// turtle draws one line, jumps back with go_silent, and draws the next.
Block far typeof turtle.Turtle
far.spawn(-30.0, 208.0)
far.face(2.0)
far.hide()
far.speed(900.0)
far.path_color(30, 60, 98)
far.path_width(1)
far.path_dashed()
far.path_dash(26, 20)
far.ring(1, 22, 40.0, -0.2)
far.go_silent(23, 900.0, 174.0)
far.path_color(36, 74, 116)
far.ring(24, 22, 40.0, -0.2)
Block mid typeof turtle.Turtle
mid.spawn(-30.0, 262.0)
mid.face(3.0)
mid.hide()
mid.speed(800.0)
mid.path_color(44, 96, 132)
mid.path_width(1)
mid.path_dashed()
mid.path_dash(38, 14)
mid.ring(1, 22, 40.0, -0.3)
mid.go_silent(23, 900.0, 172.0)
mid.path_color(52, 116, 148)
mid.ring(24, 22, 40.0, -0.3)
Block near typeof turtle.Turtle
near.spawn(-30.0, 306.0)
near.face(4.0)
near.hide()
near.speed(700.0)
near.path_color(66, 146, 164)
near.path_width(2)
near.path_solid()
near.ring(1, 22, 40.0, -0.45)
near.go_silent(23, 900.0, 170.0)
near.path_color(80, 172, 182)
near.ring(24, 22, 40.0, -0.45)
Block foam typeof turtle.Turtle
foam.spawn(-30.0, 352.0)
foam.face(5.0)
foam.hide()
foam.speed(700.0)
foam.path_color(132, 210, 206)
foam.path_width(2)
foam.path_dots()
foam.path_dash(1, 8)
foam.ring(1, 22, 40.0, -0.55)

// ═══ the moon on the water ══════════════════════════════════════
//
// The road the hatchlings steer by. The stroke widens as it comes down: three
// widths declared between the steps they belong to, so the column opens
// toward the shore.

Block glint typeof turtle.Turtle
glint.spawn(172.0, 190.0)
glint.face(-90.0)
glint.hide()
glint.speed(200.0)
glint.path_color(212, 228, 234)
glint.path_dots()
glint.path_dash(1, 11)
glint.path_opacity(40)
glint.path_width(5)
glint.ring(37, 5, 12.0, 0.0)
glint.path_width(9)
glint.path_opacity(52)
glint.ring(42, 5, 12.0, 0.0)
glint.path_width(15)
glint.path_opacity(66)
glint.ring(47, 5, 12.0, 0.0)

// ═══ the nest ═══════════════════════════════════════════════════
Block nest typeof turtle.Turtle
nest.spawn(663.0, 562.0)
nest.face(90.0)
nest.hide()
nest.speed(220.0)
nest.path_color(152, 134, 108)
nest.path_width(1)
nest.path_opacity(60)
nest.ring(37, 14, 6.68, 25.7)

// ═══ the run ════════════════════════════════════════════════════
//
// Eight hatchlings leave at once, every one of them bending toward the light
// on the water. Dotted while they are crossing the sand — that is what a track
// looks like — and solid once they are swimming. The colour is declared
// between the steps it belongs to, so the sand stays sand behind them.
Block h1 typeof turtle.Turtle
h1.spawn(650.0, 560.0)
h1.face(169.4)
h1.hide()
h1.speed(150.0)
h1.path_color(212, 190, 150)
h1.path_width(2)
h1.path_opacity(65)
h1.path_dots()
h1.path_dash(1, 7)
h1.ring(50, 26, 18.0, -1.26)
h1.path_solid()
h1.path_color(124, 210, 216)
h1.path_opacity(85)
h1.ring(76, 3, 18.0, -1.26)
Block h2 typeof turtle.Turtle
h2.spawn(672.0, 550.0)
h2.face(141.6)
h2.hide()
h2.speed(150.0)
h2.path_color(212, 190, 150)
h2.path_width(2)
h2.path_opacity(65)
h2.path_dots()
h2.path_dash(1, 7)
h2.ring(50, 29, 18.0, 1.03)
h2.path_solid()
h2.path_color(124, 210, 216)
h2.path_opacity(85)
h2.ring(79, 2, 18.0, 1.03)
Block h3 typeof turtle.Turtle
h3.spawn(656.0, 548.0)
h3.face(167.0)
h3.hide()
h3.speed(150.0)
h3.path_color(212, 190, 150)
h3.path_width(2)
h3.path_opacity(65)
h3.path_dots()
h3.path_dash(1, 7)
h3.ring(50, 28, 18.0, -0.73)
h3.path_solid()
h3.path_color(124, 210, 216)
h3.path_opacity(85)
h3.ring(78, 4, 18.0, -0.73)
Block h4 typeof turtle.Turtle
h4.spawn(676.0, 562.0)
h4.face(145.3)
h4.hide()
h4.speed(150.0)
h4.path_color(212, 190, 150)
h4.path_width(2)
h4.path_opacity(65)
h4.path_dots()
h4.path_dash(1, 7)
h4.ring(50, 31, 18.0, 0.75)
h4.path_solid()
h4.path_color(124, 210, 216)
h4.path_opacity(85)
h4.ring(81, 3, 18.0, 0.75)
Block h5 typeof turtle.Turtle
h5.spawn(648.0, 554.0)
h5.face(163.2)
h5.hide()
h5.speed(150.0)
h5.path_color(212, 190, 150)
h5.path_width(2)
h5.path_opacity(65)
h5.path_dots()
h5.path_dash(1, 7)
h5.ring(50, 29, 18.0, -0.45)
h5.path_solid()
h5.path_color(124, 210, 216)
h5.path_opacity(85)
h5.ring(79, 4, 18.0, -0.45)
Block h6 typeof turtle.Turtle
h6.spawn(666.0, 564.0)
h6.face(145.7)
h6.hide()
h6.speed(150.0)
h6.path_color(212, 190, 150)
h6.path_width(2)
h6.path_opacity(65)
h6.path_dots()
h6.path_dash(1, 7)
h6.ring(50, 29, 18.0, 0.64)
h6.path_solid()
h6.path_color(124, 210, 216)
h6.path_opacity(85)
h6.ring(79, 1, 18.0, 0.64)
Block h7 typeof turtle.Turtle
h7.spawn(660.0, 546.0)
h7.face(160.2)
h7.hide()
h7.speed(150.0)
h7.path_color(212, 190, 150)
h7.path_width(2)
h7.path_opacity(65)
h7.path_dots()
h7.path_dash(1, 7)
h7.ring(50, 28, 18.0, -0.28)
h7.path_solid()
h7.path_color(124, 210, 216)
h7.path_opacity(85)
h7.ring(78, 3, 18.0, -0.28)
Block h8 typeof turtle.Turtle
h8.spawn(670.0, 558.0)
h8.face(152.4)
h8.hide()
h8.speed(150.0)
h8.path_color(212, 190, 150)
h8.path_width(2)
h8.path_opacity(65)
h8.path_dots()
h8.path_dash(1, 7)
h8.ring(50, 31, 18.0, 0.32)
h8.path_solid()
h8.path_color(124, 210, 216)
h8.path_opacity(85)
h8.ring(81, 2, 18.0, 0.32)

// ═══ the one that turned the wrong way ══════════════════════════
//
// She leaves with the others and finds a brighter light behind the beach.

Block lost typeof turtle.Turtle
lost.spawn(664.0, 552.0)
lost.face(60.4)
lost.hide()
lost.speed(150.0)
lost.path_color(212, 190, 150)
lost.path_width(2)
lost.path_opacity(65)
lost.path_dots()
lost.path_dash(1, 7)
lost.ring(50, 4, 18.0, -4.67)
lost.path_solid()
lost.path_color(230, 154, 80)
lost.path_opacity(85)
lost.ring(54, 2, 18.0, -4.67)

// ═══ the lamp on the road ═══════════════════════════════════════
//
// Eight rays: each one walks out and comes straight back to the middle.
Block lamp typeof turtle.Turtle
lamp.spawn(751.0, 470.0)
lamp.face(90.0)
lamp.hide()
lamp.speed(300.0)
lamp.path_color(234, 166, 88)
lamp.path_width(1)
lamp.path_opacity(60)
lamp.ring(37, 12, 4.66, 30.0)

Block rays typeof turtle.Turtle
rays.spawn(742.0, 470.0)
rays.face(0.0)
rays.hide()
rays.speed(400.0)
rays.path_color(234, 166, 88)
rays.path_width(1)
rays.path_opacity(30)
rays.go(37, 30.0, 22.5)
rays.go_silent(38, -30.0, 0.0)
rays.go(39, 30.0, 45.0)
rays.go_silent(40, -30.0, 0.0)
rays.go(41, 30.0, 45.0)
rays.go_silent(42, -30.0, 0.0)
rays.go(43, 30.0, 45.0)
rays.go_silent(44, -30.0, 0.0)
rays.go(45, 30.0, 45.0)
rays.go_silent(46, -30.0, 0.0)
rays.go(47, 30.0, 45.0)
rays.go_silent(48, -30.0, 0.0)
rays.go(49, 30.0, 45.0)
rays.go_silent(50, -30.0, 0.0)
rays.go(51, 30.0, 45.0)
rays.go_silent(52, -30.0, 0.0)
```

---

## Make the video

Add one line to the same file, save again, and `one-night.mp4` writes itself —
no ffmpeg, nothing left on disk:

```fluxa
export.Video(1, 0, 30)      // from step 1, through the last one, at 30 fps
```

It is not a screen recording. The artwork is redone from the beginning with time
advancing 1/30 of a second per frame, so the result is the same on any machine,
and two runs come out byte for byte identical. Nothing is written over either:
the second render is `artwork1.mp4`.

For the frames instead — one PNG each, for an editor or a print:

```fluxa
export.Frames(1, 0, 30)
```

---

## Things worth changing

- **Move the lamp.** `lamp.spawn(742.0, 470.0)`, and the turtle that follows it.
  Put it out at sea and watch who the artwork is about change completely.
- **Turn the lamp off.** Delete the `lost`, `lamp` and `rays` blocks. Eight
  tracks, no orange. That is what a dark beach looks like.
- **Change the moon's height.** `moon.spawn(246.0, 112.0)` — the second number.
  The tracks aim at the reflection, not at the moon, so move the `glint` with it.
- **Slow the run down.** Every hatchling has `speed(150.0)`. At `40.0` you can
  watch a single track cross the sand.
- **Add more of them.** A hatchling is fifteen lines. The stage holds
  thirty-two turtles and this uses twenty-one.

---

## The light matters

This is a drawing, not a campaign, but the mechanism in it is real and the fix
for it is unusually simple. Lighting near a nesting beach is the one thing that
turns a hatchling's compass into a trap, and it is fixed by shielding lamps so
they point down, by using long-wavelength amber light instead of white, and by
closing a curtain in nesting season. Not by anybody caring more. Just by aiming
the light at the ground.

The turtles have been reading that horizon since before there were primates to
watch them do it. It costs nothing to leave it readable.
