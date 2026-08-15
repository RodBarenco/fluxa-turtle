# One Night

*The oldest map there is, and the animal that reads it.*

![One Night](one-night.png)

**[Watch it draw itself](one-night.mp4)** — eleven seconds, 800×600, written by
the program itself with one line: `export.Video(1, 0, 30)`.

---

## The night

She is a few hundred metres out, in water she can stand still in, waiting.

Above her the moon is doing the only thing that matters tonight: it is making
the sea the brightest thing in the world. Not the beach, not the dunes behind
it — the water. Light comes down, breaks on the surface, and scatters into the
shards you can see in the drawing. From below, that is not decoration. That is a
direction.

Sea turtles have been reading that direction since the age of dinosaurs. A
hatchling digs out of the sand at night, sees a low bright open horizon, and
runs at it; that is the whole instinct, and for a hundred million years it was
enough, because nothing on the land side of a beach was ever brighter than the
sea. A female who survives the run comes back decades later to nest on the beach
where she hatched, crossing an ocean to get there, steering by the planet's
magnetic field — she reads the Earth like a page and arrives at the right
kilometre of the right coast.

Then somebody builds a road behind the dune and turns a light on, and the map
stops working. Hatchlings crawl inland toward the lamp and die of it. Females
turn around at the surf line and go back out without nesting.

The fix is almost insultingly small: point the lamps at the ground, use amber
instead of white, close the curtain in nesting season. Nobody has to care more
than they already do. The light just has to stay off the water's job.

So: one turtle, one night, and the light she is steering by — drawn by a program
whose only verb is *walk a bit, turn a bit*.

---

## What is on the screen

| The scene | How it is drawn |
|---|---|
| **The moon and its haze** | three circles — a circle here is a 36-sided polygon, one turtle, one `ring` |
| **The stars** | one turtle, twenty times: a jump with the pen up, one dot with it down |
| **The sea** | four long shallow arcs, dashed far away and solid near the shore |
| **The light on the water** | twenty-five short strokes scattered in a cone, getting brighter as they come down |
| **The turtle** | four turtles drawing at once: the shell, the head, the flippers, the plates |

### The line art

The turtle is not a picture the tool knows how to draw. It is a list of points —
the outline of a carapace, a head, four paddles, the seams between the plates —
and every stroke in the drawing is the same two numbers the rest of this project
uses: **how far to turn from where the pen is already pointing, and how far to
walk**. Four hundred and fifty-three of them.

That is the whole trick, and it is worth knowing because it means anything you
can describe as points, this tool can draw. The shape here was sketched as
control points, smoothed with a spline, rotated into place, and printed as
`go` and `go_silent` lines. `go_silent` is what lifts the pen between one line
and the next.

Two details that are easy to get wrong, both of which bit while this was made:

- **A jump turns from where the turtle is pointing**, not from the screen. Feed
  `go_silent` an absolute angle and your stars end up in the sea.
- **A jump still costs a step.** Twenty slow jumps quietly became four seconds
  of an eleven-second video until the star turtle's speed went up.

### The gradient in the water

The light gets brighter the closer it comes to shore, and that is one turtle
with one colour. The opacity is declared *between* the strokes it belongs to —
appearance in this tool belongs to the step where it is written, so a single
line can change material halfway down without touching what is already drawn.

---

## Paste it

Open `main.flx`, delete whatever sits between `timeline.Timeline.reset()` and
the execution line, and paste this in its place. Save. The window is already
open, so it simply happens.

It is 657 lines and 453 of them are strokes. You are not meant to read those —
paste them and change the four numbers at the top of each block.

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
// Light on water is broken, never a line drawn from the moon down. Short
// strokes scattered inside a cone that opens toward the shore, brighter the
// closer they come — the opacity is declared between the steps it belongs to,
// so one turtle paints the whole gradient.

Block shine typeof turtle.Turtle
shine.spawn(200.0, 212.0)
shine.face(0.0)
shine.hide()
shine.speed(1400.0)
shine.path_color(208, 226, 238)
shine.path_width(2)
shine.path_opacity(18)
shine.go_silent(37, 0.7, 0.0)
shine.go(38, 6.3, 0.0)
shine.path_opacity(21)
shine.go_silent(39, 15.6, -140.9)
shine.go(40, 6.7, 140.9)
shine.path_opacity(25)
shine.go_silent(41, 18.3, -137.0)
shine.go(42, 6.8, 137.0)
shine.path_opacity(28)
shine.go_silent(43, 9.3, -114.9)
shine.go(44, 7.9, 114.9)
shine.path_opacity(31)
shine.go_silent(45, 10.5, -54.1)
shine.go(46, 18.0, 54.1)
shine.path_opacity(33)
shine.go_silent(47, 45.6, -171.0)
shine.go(48, 9.6, 171.0)
shine.go_silent(49, 9.3, 0.0)
shine.go(50, 9.6, 0.0)
shine.go_silent(51, 3.7, -180.0)
shine.go(52, 13.2, -180.0)
shine.path_opacity(37)
shine.go_silent(53, 19.5, -144.1)
shine.go(54, 7.3, 144.1)
shine.go_silent(55, 1.3, 0.0)
shine.go(56, 16.8, 0.0)
shine.path_opacity(41)
shine.go_silent(57, 38.2, -165.7)
shine.go(58, 23.2, 165.7)
shine.go_silent(59, 10.2, -180.0)
shine.go(60, 12.2, -180.0)
shine.path_opacity(44)
shine.go_silent(61, 52.7, -169.9)
shine.go(62, 26.5, 169.9)
shine.go_silent(63, 15.6, -180.0)
shine.go(64, 15.3, -180.0)
shine.go_silent(65, 4.9, 0.0)
shine.go(66, 13.1, 0.0)
shine.path_opacity(47)
shine.go_silent(67, 47.8, -167.9)
shine.go(68, 26.6, 167.9)
shine.go_silent(69, 5.4, 0.0)
shine.go(70, 10.5, 0.0)
shine.path_opacity(50)
shine.go_silent(71, 44.4, -167.5)
shine.go(72, 32.1, 167.5)
shine.go_silent(73, 29.2, -180.0)
shine.go(74, 11.5, -180.0)
shine.go_silent(75, 6.0, 0.0)
shine.go(76, 30.2, 0.0)
shine.path_opacity(54)
shine.go_silent(77, 54.9, -170.0)
shine.go(78, 23.7, 170.0)
shine.go_silent(79, 30.4, 0.0)
shine.go(80, 17.4, 0.0)
shine.path_opacity(57)
shine.go_silent(81, 72.5, -173.2)
shine.go(82, 27.1, 173.2)
shine.go_silent(83, 17.3, -180.0)
shine.go(84, 33.8, -180.0)
shine.path_opacity(61)
shine.go_silent(85, 14.1, -52.7)
shine.go(86, 25.8, 52.7)

// ═══ the turtle ═════════════════════════════════════════════════
//
// Line art, drawn the way a turtle draws: one stroke after another, no lifting
// except to start a new line. Four of them share the work so the drawing comes
// up as a whole instead of a part at a time — the shell and the head first, the
// flippers with them, the plates last.
//
// The shape is a list of points; each stroke is the turn from where the pen is
// already pointing to the next one, and the length between them. Nothing in the
// language knows what a turtle looks like. This is all arithmetic.
Block shell typeof turtle.Turtle
shell.spawn(432.4, 382.4)
shell.face(0.0)
shell.hide()
shell.speed(900.0)
shell.path_color(152, 222, 230)
shell.path_width(2)
shell.path_opacity(90)
shell.go(45, 4.2, -26.9)
shell.go(46, 6.0, 1.0)
shell.go(47, 7.0, -1.2)
shell.go(48, 7.1, -3.0)
shell.go(49, 6.4, -5.8)
shell.go(50, 5.8, -6.8)
shell.go(51, 5.8, -4.5)
shell.go(52, 5.8, -5.0)
shell.go(53, 5.7, -5.7)
shell.go(54, 5.7, -6.4)
shell.go(55, 5.8, -6.9)
shell.go(56, 6.0, -6.0)
shell.go(57, 6.2, -5.1)
shell.go(58, 6.2, -4.5)
shell.go(59, 6.2, -4.2)
shell.go(60, 6.3, -4.6)
shell.go(61, 6.5, -4.5)
shell.go(62, 6.6, -3.9)
shell.go(63, 6.6, -3.5)
shell.go(64, 6.5, -3.3)
shell.go(65, 6.5, -3.5)
shell.go(66, 6.5, -3.5)
shell.go(67, 6.6, -3.3)
shell.go(68, 6.6, -3.2)
shell.go(69, 6.6, -3.1)
shell.go(70, 6.7, -2.9)
shell.go(71, 6.8, -2.9)
shell.go(72, 6.9, -3.0)
shell.go(73, 6.8, -3.4)
shell.go(74, 6.7, -3.9)
shell.go(75, 6.7, -5.1)
shell.go(76, 6.9, -4.5)
shell.go(77, 6.9, -3.2)
shell.go(78, 6.5, -2.2)
shell.go(79, 5.8, -1.4)
shell.go(80, 5.1, -2.6)
shell.go(81, 4.6, -4.1)
shell.go(82, 4.2, -3.4)
shell.go(83, 3.8, -2.3)
shell.go(84, 3.3, -0.8)
shell.go(85, 2.9, -2.6)
shell.go(86, 2.5, -5.4)
shell.go(87, 2.1, -4.2)
shell.go(88, 1.7, -2.2)
shell.go(89, 1.2, 1.8)
shell.go(90, 0.7, 3.7)
shell.go(91, 0.1, 0.0)
shell.go(92, 0.2, 180.0)
shell.go(93, 0.3, 0.0)
shell.go(94, 0.2, -0.0)
shell.go(95, 0.2, -36.2)
shell.go(96, 0.3, 0.0)
shell.go(97, 0.2, -0.0)
shell.go(98, 0.1, 180.0)
shell.go(99, 0.7, 0.0)
shell.go(100, 1.2, 3.7)
shell.go(101, 1.7, 1.8)
shell.go(102, 2.1, -2.2)
shell.go(103, 2.5, -4.2)
shell.go(104, 2.9, -5.4)
shell.go(105, 3.3, -2.6)
shell.go(106, 3.8, -0.8)
shell.go(107, 4.2, -2.3)
shell.go(108, 4.6, -3.4)
shell.go(109, 5.1, -4.1)
shell.go(110, 5.8, -2.6)
shell.go(111, 6.5, -1.4)
shell.go(112, 6.9, -2.2)
shell.go(113, 6.9, -3.2)
shell.go(114, 6.7, -4.5)
shell.go(115, 6.7, -5.1)
shell.go(116, 6.8, -3.9)
shell.go(117, 6.9, -3.4)
shell.go(118, 6.8, -3.0)
shell.go(119, 6.7, -2.9)
shell.go(120, 6.6, -2.9)
shell.go(121, 6.6, -3.1)
shell.go(122, 6.6, -3.2)
shell.go(123, 6.5, -3.3)
shell.go(124, 6.5, -3.5)
shell.go(125, 6.5, -3.5)
shell.go(126, 6.6, -3.3)
shell.go(127, 6.6, -3.5)
shell.go(128, 6.5, -3.9)
shell.go(129, 6.3, -4.5)
shell.go(130, 6.2, -4.6)
shell.go(131, 6.2, -4.2)
shell.go(132, 6.2, -4.5)
shell.go(133, 6.0, -5.1)
shell.go(134, 5.8, -6.0)
shell.go(135, 5.7, -6.9)
shell.go(136, 5.7, -6.4)
shell.go(137, 5.8, -5.7)
shell.go(138, 5.8, -5.0)
shell.go(139, 5.8, -4.5)
shell.go(140, 6.4, -6.8)
shell.go(141, 7.1, -5.8)
shell.go(142, 7.0, -3.0)
shell.go(143, 6.0, -1.2)
shell.go(144, 4.2, 1.0)

Block neck typeof turtle.Turtle
neck.spawn(416.7, 385.1)
neck.face(0.0)
neck.hide()
neck.speed(620.0)
neck.path_color(152, 222, 230)
neck.path_width(2)
neck.path_opacity(90)
neck.go(45, 1.9, 91.5)
neck.go(46, 2.8, 0.6)
neck.go(47, 3.1, -3.8)
neck.go(48, 2.9, -8.7)
neck.go(49, 2.9, -11.3)
neck.go(50, 3.1, -6.6)
neck.go(51, 3.1, -6.1)
neck.go(52, 2.8, -7.0)
neck.go(53, 2.7, -9.5)
neck.go(54, 2.7, -8.6)
neck.go(55, 2.6, -7.2)
neck.go(56, 2.4, -7.0)
neck.go(57, 2.1, -10.0)
neck.go(58, 2.0, -11.1)
neck.go(59, 2.0, -8.4)
neck.go(60, 2.0, -5.3)
neck.go(61, 2.0, -3.3)
neck.go(62, 2.0, -5.3)
neck.go(63, 2.0, -8.4)
neck.go(64, 2.1, -11.1)
neck.go(65, 2.4, -10.0)
neck.go(66, 2.6, -7.0)
neck.go(67, 2.7, -7.2)
neck.go(68, 2.7, -8.6)
neck.go(69, 2.8, -9.5)
neck.go(70, 3.1, -7.0)
neck.go(71, 3.1, -6.1)
neck.go(72, 2.9, -6.6)
neck.go(73, 2.9, -11.3)
neck.go(74, 3.1, -8.7)
neck.go(75, 2.8, -3.8)
neck.go(76, 1.9, 0.6)
neck.go(77, 0.7, 4.0)
neck.go(78, 0.1, -180.0)
neck.go(79, 0.4, -0.0)
neck.go(80, 0.2, 0.0)
neck.go_silent(81, 30.8, 67.7)
neck.go(82, 3.0, -140.2)
neck.go_silent(83, 13.5, -0.0)
neck.go(84, 3.0, 0.0)

Block fins typeof turtle.Turtle
fins.spawn(470.4, 434.1)
fins.face(0.0)
fins.hide()
fins.speed(1150.0)
fins.path_color(128, 206, 216)
fins.path_width(2)
fins.path_opacity(82)
fins.go(45, 7.1, -24.2)
fins.go(46, 10.2, 0.6)
fins.go(47, 11.4, -3.4)
fins.go(48, 10.9, -7.7)
fins.go(49, 10.6, -9.2)
fins.go(50, 11.2, -5.6)
fins.go(51, 11.4, -5.7)
fins.go(52, 11.5, -6.3)
fins.go(53, 12.2, -7.7)
fins.go(54, 13.0, -5.9)
fins.go(55, 12.8, -3.6)
fins.go(56, 11.6, -2.3)
fins.go(57, 10.7, -4.3)
fins.go(58, 10.3, -4.9)
fins.go(59, 8.8, -2.5)
fins.go(60, 6.2, 0.4)
fins.go(61, 2.5, 2.5)
fins.go(62, 0.3, -180.0)
fins.go(63, 1.4, -0.0)
fins.go(64, 0.8, 0.0)
fins.go(65, 5.9, 48.5)
fins.go(66, 8.4, 0.1)
fins.go(67, 9.7, -0.5)
fins.go(68, 9.6, -1.2)
fins.go(69, 9.6, -1.4)
fins.go(70, 10.2, -0.8)
fins.go(71, 10.1, -0.8)
fins.go(72, 9.5, -0.9)
fins.go(73, 8.9, -1.9)
fins.go(74, 8.5, -1.7)
fins.go(75, 8.0, -0.1)
fins.go(76, 7.3, 1.9)
fins.go(77, 7.0, 3.5)
fins.go(78, 6.6, 2.5)
fins.go(79, 5.6, 1.3)
fins.go(80, 3.9, -0.2)
fins.go(81, 1.6, -1.3)
fins.go(82, 0.2, -180.0)
fins.go(83, 0.9, -0.0)
fins.go(84, 0.5, 0.0)
fins.go_silent(85, 117.9, 177.6)
fins.go(86, 7.1, 29.2)
fins.go(87, 10.2, -0.6)
fins.go(88, 11.4, 3.4)
fins.go(89, 10.9, 7.7)
fins.go(90, 10.6, 9.2)
fins.go(91, 11.2, 5.6)
fins.go(92, 11.4, 5.7)
fins.go(93, 11.5, 6.3)
fins.go(94, 12.2, 7.7)
fins.go(95, 13.0, 5.9)
fins.go(96, 12.8, 3.6)
fins.go(97, 11.6, 2.3)
fins.go(98, 10.7, 4.3)
fins.go(99, 10.3, 4.9)
fins.go(100, 8.8, 2.5)
fins.go(101, 6.2, -0.4)
fins.go(102, 2.5, -2.5)
fins.go(103, 0.3, -180.0)
fins.go(104, 1.4, 0.0)
fins.go(105, 0.8, -0.0)
fins.go(106, 5.9, -48.5)
fins.go(107, 8.4, -0.1)
fins.go(108, 9.7, 0.5)
fins.go(109, 9.6, 1.2)
fins.go(110, 9.6, 1.4)
fins.go(111, 10.2, 0.8)
fins.go(112, 10.1, 0.8)
fins.go(113, 9.5, 0.9)
fins.go(114, 8.9, 1.9)
fins.go(115, 8.5, 1.7)
fins.go(116, 8.0, 0.1)
fins.go(117, 7.3, -1.9)
fins.go(118, 7.0, -3.5)
fins.go(119, 6.6, -2.5)
fins.go(120, 5.6, -1.3)
fins.go(121, 3.9, 0.2)
fins.go(122, 1.6, 1.3)
fins.go(123, 0.2, 180.0)
fins.go(124, 0.9, -0.0)
fins.go(125, 0.5, 0.0)
fins.go_silent(126, 113.8, 124.2)
fins.go(127, 4.8, -0.2)
fins.go(128, 6.9, 0.3)
fins.go(129, 7.6, -1.9)
fins.go(130, 6.9, -4.5)
fins.go(131, 6.2, -6.9)
fins.go(132, 6.2, -4.7)
fins.go(133, 5.9, -4.2)
fins.go(134, 5.2, -4.4)
fins.go(135, 4.7, -8.9)
fins.go(136, 4.4, -9.2)
fins.go(137, 3.8, -4.7)
fins.go(138, 2.7, 0.8)
fins.go(139, 1.1, 4.8)
fins.go(140, 0.1, 180.0)
fins.go(141, 0.6, 0.0)
fins.go(142, 0.4, -0.0)
fins.go(143, 3.6, 45.3)
fins.go(144, 5.1, 0.1)
fins.go(145, 5.8, -0.8)
fins.go(146, 5.6, -1.8)
fins.go(147, 5.3, -2.6)
fins.go(148, 5.5, -1.6)
fins.go(149, 5.5, -1.0)
fins.go(150, 5.2, -0.5)
fins.go(151, 5.4, -0.8)
fins.go(152, 5.4, -0.9)
fins.go(153, 4.8, -0.4)
fins.go(154, 3.3, 0.1)
fins.go(155, 1.3, 0.4)
fins.go(156, 0.1, 180.0)
fins.go(157, 0.7, 0.0)
fins.go(158, 0.4, -0.0)
fins.go_silent(159, 75.8, -148.3)
fins.go(160, 4.8, 42.8)
fins.go(161, 6.9, -0.3)
fins.go(162, 7.6, 1.9)
fins.go(163, 6.9, 4.5)
fins.go(164, 6.2, 6.9)
fins.go(165, 6.2, 4.7)
fins.go(166, 5.9, 4.2)
fins.go(167, 5.2, 4.4)
fins.go(168, 4.7, 8.9)
fins.go(169, 4.4, 9.2)
fins.go(170, 3.8, 4.7)
fins.go(171, 2.7, -0.8)
fins.go(172, 1.1, -4.8)
fins.go(173, 0.1, 180.0)
fins.go(174, 0.6, -0.0)
fins.go(175, 0.4, 0.0)
fins.go(176, 3.6, -45.3)
fins.go(177, 5.1, -0.1)
fins.go(178, 5.8, 0.8)
fins.go(179, 5.6, 1.8)
fins.go(180, 5.3, 2.6)
fins.go(181, 5.5, 1.6)
fins.go(182, 5.5, 1.0)
fins.go(183, 5.2, 0.5)
fins.go(184, 5.4, 0.8)
fins.go(185, 5.4, 0.9)
fins.go(186, 4.8, 0.4)
fins.go(187, 3.3, -0.1)
fins.go(188, 1.3, -0.4)
fins.go(189, 0.1, -180.0)
fins.go(190, 0.7, -0.0)
fins.go(191, 0.4, 0.0)

Block plates typeof turtle.Turtle
plates.spawn(413.5, 386.8)
plates.face(0.0)
plates.hide()
plates.speed(700.0)
plates.path_color(76, 152, 168)
plates.path_width(1)
plates.path_opacity(70)
plates.go(85, 4.7, -132.9)
plates.go(86, 6.7, -0.4)
plates.go(87, 7.7, 2.3)
plates.go(88, 7.6, 4.9)
plates.go(89, 7.6, 6.2)
plates.go(90, 8.1, 3.6)
plates.go(91, 8.3, 2.4)
plates.go(92, 8.2, 1.5)
plates.go(93, 8.0, 1.5)
plates.go(94, 8.0, 1.9)
plates.go(95, 8.0, 1.7)
plates.go(96, 8.0, 1.6)
plates.go(97, 8.1, 1.2)
plates.go(98, 8.2, 1.4)
plates.go(99, 8.1, 2.1)
plates.go(100, 7.9, 3.0)
plates.go(101, 8.4, 4.8)
plates.go(102, 8.7, 3.5)
plates.go(103, 7.8, 1.5)
plates.go(104, 5.4, -0.3)
plates.go(105, 2.1, -1.6)
plates.go(106, 0.2, 180.0)
plates.go(107, 1.2, 0.0)
plates.go(108, 0.7, 0.0)
plates.go_silent(109, 152.3, -30.9)
plates.go(110, 4.7, -146.1)
plates.go(111, 6.7, 0.4)
plates.go(112, 7.7, -2.3)
plates.go(113, 7.6, -4.9)
plates.go(114, 7.6, -6.2)
plates.go(115, 8.1, -3.6)
plates.go(116, 8.3, -2.4)
plates.go(117, 8.2, -1.5)
plates.go(118, 8.0, -1.5)
plates.go(119, 8.0, -1.9)
plates.go(120, 8.0, -1.7)
plates.go(121, 8.0, -1.6)
plates.go(122, 8.1, -1.2)
plates.go(123, 8.2, -1.4)
plates.go(124, 8.1, -2.1)
plates.go(125, 7.9, -3.0)
plates.go(126, 8.4, -4.8)
plates.go(127, 8.7, -3.5)
plates.go(128, 7.8, -1.5)
plates.go(129, 5.4, 0.3)
plates.go(130, 2.1, 1.6)
plates.go(131, 0.2, 180.0)
plates.go(132, 1.2, 0.0)
plates.go(133, 0.7, -0.0)
plates.go_silent(134, 130.4, 37.0)
plates.go(135, 51.3, -107.1)
plates.go_silent(136, 63.1, -149.5)
plates.go(137, 57.5, 149.5)
plates.go_silent(138, 65.0, -150.5)
plates.go(139, 55.6, 150.5)
plates.go_silent(140, 60.1, -147.8)
plates.go(141, 46.2, 147.8)
plates.go_silent(142, 116.4, 113.4)
plates.go(143, 34.8, 66.6)
plates.go_silent(144, 41.3, 136.4)
plates.go(145, 42.0, -136.4)
plates.go_silent(146, 52.4, 142.3)
plates.go(147, 43.0, -142.3)
plates.go_silent(148, 57.3, 143.8)
plates.go(149, 38.1, -143.8)
plates.go_silent(150, 128.1, -132.6)
plates.go(151, 34.8, -47.4)
plates.go_silent(152, 41.3, -136.4)
plates.go(153, 42.0, 136.4)
plates.go_silent(154, 52.4, -142.3)
plates.go(155, 43.0, 142.3)
plates.go_silent(156, 57.3, -143.8)
plates.go(157, 38.1, 143.8)

```

---

## Make the video

Add one line to the same file and save again:

```fluxa
export.Video(1, 0, 30)      // from step 1, through the last one, at 30 fps
```

`artwork.mp4` writes itself — H.264, no ffmpeg, nothing left on disk. It is not
a screen recording: the artwork is redone from the beginning with time advancing
1/30 of a second per frame, so the file is the same on any machine and two runs
come out byte for byte identical. Nothing is written over, either: the second
render is `artwork1.mp4`.

For the frames instead — one PNG each, for an editor or a print:

```fluxa
export.Frames(1, 0, 30)
```

---

## Things worth changing

- **Turn the moon into a sun.** `moon.path_color(228, 234, 242)` → `(255, 214, 140)`,
  the haze with it, and the water strokes to match. Same drawing, different hour.
- **Move the turtle.** Every one of her strokes is relative, so the four blocks
  (`shell`, `neck`, `fins`, `plates`) move together if you change where each one
  spawns — by the same amount. Easier: change `stage.Stage.background` to
  something lighter and let her sit where she is.
- **Take the plates out.** Delete the `plates` block. A bare outline reads as a
  silhouette, and it is closer to how a woodcut would do it.
- **Slow her down.** `shell.speed(900.0)` and the three others. At `200.0` you
  can watch the outline being felt out stroke by stroke.
- **Make the water busier.** The `shine` block is twenty-five strokes; more of
  them, shorter, is a rougher sea.

---

*Sea turtle facts in this page are the ordinary ones: night emergence,
orientation toward the brightest open horizon, natal homing by geomagnetic cues,
and disorientation caused by coastal lighting. Any conservation group working on
a nesting beach will tell you the same three fixes.*
