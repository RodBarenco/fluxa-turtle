#!/usr/bin/env python3
"""sounds.py — the five sounds the tool ships with.

    python3 tools/sounds.py            # writes sounds/*.wav

Five short, dry, low sounds for a drawing that is being made: somewhere between
a chess piece set down on a board and a pencil on paper. Nothing beeps. A beep
announces an event; these sound like a thing being *done*, which is what a step
is.

    place    a piece set down — a low wooden knock
    tap      the same, lighter and higher: a small move
    slide    a piece pushed across the board
    stroke   a longer line being drawn

`pencil.wav` is not made here. It is a recording of a real pencil, brought in
with `tools/import_sound.py` — three goes at synthesising graphite got the
physics right and the sound wrong, and a phone in front of a sheet of paper
settled it in one take. Set SYNTH_PENCIL=1 to write the synthesised one anyway
and hear the difference.

They are synthesised rather than recorded, so they are tiny, they are in the
repository, and they are the same on every machine — the file is the recipe.
Nothing here is random in the loose sense: the noise runs from a fixed seed, so
running this twice writes identical bytes.

Wooden knock: a few decaying sine partials, low and inharmonic, with a click at
the very front — the click is most of what makes it read as *contact*.
Pencil: filtered noise with a grainy envelope, because paper is not smooth.
"""

import math
import os
import random
import struct
import wave

SR = 22050


def seeded(name):
    """One seed per sound, from its own name.

    A single seed at the top was not enough: the noise a sound draws depends on
    how much noise the sounds before it drew, so synthesising the pencil or not
    changed `stroke`. "Running this twice writes identical bytes" has to be
    true whatever else is switched on.
    """
    random.seed(sum(ord(c) * (i + 7) for i, c in enumerate(name)))


def write(name, samples, amp=0.9):
    peak = max(1e-9, max(abs(s) for s in samples))
    scale = amp / peak
    os.makedirs("sounds", exist_ok=True)
    path = os.path.join("sounds", name)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(32767 * s * scale))))
            for s in samples))
    print(f"[sounds] {path}  {len(samples) / SR * 1000:.0f} ms", )


def knock(ms, partials, click=0.5, decay=28.0):
    """A body struck: inharmonic partials that die fast, over a click."""
    n = int(SR * ms / 1000)
    out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-decay * t)
        v = sum(a * math.sin(2 * math.pi * f * t) for f, a in partials) * env
        if i < 60:                       # the contact itself
            v += click * (1 - i / 60) * (random.random() * 2 - 1)
        out.append(v)
    return out


# The filters take HERTZ, not a coefficient. Written the other way round once,
# with bare numbers, the pencil came out brighter than the beep it replaced —
# a coefficient tells you nothing about what you will hear.

def lowpass(seq, hz):
    """One pole: paper and felt have no top end."""
    k = 1.0 - math.exp(-2.0 * math.pi * hz / SR)
    out, last = [], 0.0
    for v in seq:
        last += k * (v - last)
        out.append(last)
    return out


def highpass(seq, hz):
    """One pole the other way: takes the rumble out, leaves the scratch."""
    k = 1.0 / (1.0 + 2.0 * math.pi * hz / SR)
    out, last_in, last_out = [], 0.0, 0.0
    for v in seq:
        last_out = k * (last_out + v - last_in)
        last_in = v
        out.append(last_out)
    return out


def band(n, lo_hz, hi_hz, poles=4):
    """Noise with both ends cut off — a scratch has neither rumble nor hiss.

    Cascaded, and that is the point. One pole rolls off at 6 dB per octave,
    which sounds like almost nothing when the material is white noise: with a
    single pole at 2.6 kHz the octaves above it still carried enough energy to
    put the spectral centre at 4.8 kHz, and the "pencil" came out brighter than
    the beep it was replacing. Four poles is 24 dB per octave and audibly a
    band.
    """
    seq = [random.random() * 2 - 1 for _ in range(n)]
    for _ in range(poles):
        seq = lowpass(seq, hi_hz)
    for _ in range(max(1, poles // 2)):
        seq = highpass(seq, lo_hz)
    return seq


def scratch(ms, lo_hz, hi_hz, grain_hz, rasp=0.45, attack_ms=9.0, decay=9.0):
    """One stroke of graphite.

    The attack is the whole difference between a pencil and a gunshot. Noise
    that starts at full amplitude in one sample IS a gunshot — that is what a
    click is — so this ramps in over about nine milliseconds, which is slow
    enough to read as contact and fast enough to still be a mark.
    """
    n = int(SR * ms / 1000)
    seq = band(n, lo_hz, hi_hz)
    rise = max(1, int(SR * attack_ms / 1000))
    out = []
    for i, v in enumerate(seq):
        t = i / SR
        env = min(1.0, i / rise) * math.exp(-decay * t)
        grain = 1.0 - rasp * (0.5 + 0.5 * math.sin(2 * math.pi * grain_hz * t))
        out.append(v * env * grain)
    return out


def tch(shape, hold, ms, gap_ms, lo_hz, hi_hz, grain_hz,
        rasp=0.45, attack_ms=9.0, decay=9.0):
    """tch-tch-tch: the same scratch a few times, with a shape to it.

    Two factors per mark, and they are what turn three bursts into a gesture:

      `shape`  the whole voice — both ends of the band and the grain — so 0.72
               is that mark said lower, not merely duller
      `hold`   how long it is held

    A hand does not repeat itself. This one goes down and longer in the middle
    and comes back short and level: shape [1.0, 0.72, 1.0], hold [1.0, 1.22,
    0.72].
    """
    out = []
    for k, f in enumerate(shape):
        piece = scratch(ms * hold[k], lo_hz * f, hi_hz * f, grain_hz * f,
                        rasp=rasp, attack_ms=attack_ms, decay=decay)
        out.extend(piece)
        out.extend([0.0] * int(SR * gap_ms / 1000))
    while out and abs(out[-1]) < 1e-6:
        out.pop()
    return out


def mix(a, b, wa=1.0, wb=1.0):
    n = max(len(a), len(b))
    a = a + [0.0] * (n - len(a))
    b = b + [0.0] * (n - len(b))
    return [wa * x + wb * y for x, y in zip(a, b)]


def main():

    # A piece set down: heavy, short, and now a fifth lower than it was — the
    # first version was right in character and a little bright for wood.
    seeded("place.wav")
    write("place.wav", knock(240, [(80, 1.0), (136, 0.55), (206, 0.3), (327, 0.12)],
                             click=0.5, decay=24.0))

    # The same gesture, smaller — for a step that is not the important one.
    seeded("tap.wav")
    write("tap.wav", knock(150, [(145, 1.0), (244, 0.45), (368, 0.2)],
                           click=0.36, decay=38.0))

    # Pushed across the board: a knock with a scratch dragged out of it.
    seeded("slide.wav")
    write("slide.wav", mix(knock(90, [(104, 1.0), (178, 0.4)], click=0.28, decay=38.0),
                           scratch(280, 420, 2100, 60, rasp=0.35, attack_ms=14.0, decay=6.0),
                           0.7, 0.85))

    # pencil.wav is NOT written here any more, and this script must not write
    # it: it is a recording of a real pencil, brought in with
    #
    #   python3 tools/import_sound.py art/pencil_recording.ogg \
    #           -o sounds/pencil.wav --from 0.19 --to 1.27
    #
    # Three goes at synthesising graphite got the physics right and the sound
    # wrong — a click is a gunshot, one filter pole is not a filter, a 62 ms
    # mark is over before the ear knows what it was — and the recording settled
    # it in one take. What is kept here is the recipe for the four that ARE
    # synthesised, and `synth_pencil` for anyone who wants to try again.
    if os.environ.get("SYNTH_PENCIL"):
        seeded("pencil.wav")
        write("pencil.wav", tch([1.0, 0.72, 1.0], [1.0, 1.28, 0.78], 185, 58, 180, 1100, 42,
                                rasp=0.38, attack_ms=30.0, decay=2.4))

    # A longer line, the same voice a good deal lower: one continuous mark with
    # the hand still moving at the end.
    seeded("stroke.wav")
    write("stroke.wav", scratch(430, 260, 1350, 46, rasp=0.5, attack_ms=22.0, decay=4.2))


if __name__ == "__main__":
    main()
