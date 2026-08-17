# 0019 — Sound crosses the save, and a rebuild is silent

**Status:** accepted

## Context

The runtime gained audio (`miniaudio/0.11.25`), and the expansions ask for four
things: music, effects synchronised with the steps, volume, and musical events
on the timeline. Two facts about *this* tool decided the whole design, and both
were measured before anything was written.

**`sound.init()` hands out four engines and no more.** Measured with a `-dev`
session and five saves: the handles came back 1, 2, 3, 4 and then *too many
engines (max 4)*. A Block field is re-declared on every reload, so a module that
opened an engine whenever its field was zero would burn one per save and go
silent on the fourth — in a tool whose entire premise is saving constantly.
Closing the previous engine first does work (the handle stays 1, measured), but
closing frees its sounds, so every save would reload every file and the music
would restart.

**A rebuild replays the whole artwork instantly.** That is how a save brings the
drawing back (adr 0002). A cue that fired from the replay would fire once per
step in the artwork — four hundred sounds on one keystroke.

## Decision

**The engine and its loaded sounds live in a `prst dyn` in `main.flx`.**

```fluxa
prst dyn snd = [0.0, 0.0, 0.0, 0.0, 0.0]   // [engine, and one handle per file]
```

The same mechanism the canvas and the in-flight progress already use (adr 0014):
it survives a reload with its value, and a Block method can write through it as
a parameter. `Audio.open(snd)` initialises what is zero and reuses what is not,
so across a session there is exactly one engine and each file is loaded once.

That is also what makes **music keep playing across a save**: nothing is closed,
nothing is reloaded, and `Track` presses play only when `is_playing` says
nothing is. Live coding with a soundtrack that restarted on every Ctrl-S would
be unusable, and this costs one line in `main.flx` to avoid.

**Cues fire from `animate` and from nowhere else.** `instant` — the rebuild's
step — stays silent. This is the same distinction the panel makes with `mute`,
and it is the only reason a save does not make a noise.

**An export is silent.** A controlled render runs at whatever speed the machine
manages, so anything it played would not match what the video shows. `mute` is
the export's, `off` is the listener's (the **A** key), and they are separate
flags — otherwise finishing an export would turn the sound back on for somebody
who had asked for silence.

**A file that is missing is not an error.** It says why, once, and stays silent;
the slot is marked as tried so the message does not repeat on every save. The
background image already sets that precedent.

## Consequences

- Four sound files per artwork. The limit is the size of the array in
  `main.flx`, which is where it is declared and therefore where it is honest.
- `main.flx` grows one `prst` and the execution line one argument. That is the
  fifth thing that has to cross a save, and the price is stated in the file.
- Sound is the one thing here a PNG cannot verify, so `Audio` counts what it did
  — cues fired, and times the track was pressed. `lab/audio.flx` asserts the two
  that matter: zero cues after a rebuild, and exactly one press after three
  opens.
- The five sounds that ship are **synthesised** by `tools/sounds.py` rather than
  recorded, so the repository holds the recipe and every machine gets the same
  bytes. None of them beeps: a beep announces an event, and a step is a thing
  being done.
- No audio in the video. `std.video` writes H.264 with no audio track, and a
  render is not played at watching speed, so a soundtrack over an export has to
  be muxed by timestamp afterwards — the same answer adr 0010 gives for WebM.
