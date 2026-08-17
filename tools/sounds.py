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
    pencil   a short scribble, graphite on paper
    stroke   a longer line being drawn

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


def lowpass(seq, k):
    """One pole, because paper and felt have no top end."""
    out, last = [], 0.0
    for v in seq:
        last += k * (v - last)
        out.append(last)
    return out


def scribble(ms, grain_hz, bright, rasp=0.6):
    """Graphite: noise, filtered, with the envelope bumping at grain_hz."""
    n = int(SR * ms / 1000)
    raw = [random.random() * 2 - 1 for _ in range(n)]
    band = lowpass(raw, bright)
    out = []
    for i, v in enumerate(band):
        t = i / SR
        body = min(1.0, t * 90) * math.exp(-4.5 * t)          # in fast, out slow
        grain = 1.0 - rasp * (0.5 + 0.5 * math.sin(2 * math.pi * grain_hz * t))
        out.append(v * body * grain)
    return out


def mix(a, b, wa=1.0, wb=1.0):
    n = max(len(a), len(b))
    a = a + [0.0] * (n - len(a))
    b = b + [0.0] * (n - len(b))
    return [wa * x + wb * y for x, y in zip(a, b)]


def main():
    random.seed(7)

    # A piece set down: heavy, short, mostly under 300 Hz.
    write("place.wav", knock(220, [(96, 1.0), (163, 0.55), (247, 0.3), (392, 0.12)],
                             click=0.55, decay=26.0))

    # The same gesture, smaller — for a step that is not the important one.
    write("tap.wav", knock(140, [(174, 1.0), (293, 0.45), (441, 0.2)],
                           click=0.4, decay=42.0))

    # Pushed across the board: a knock with a rasp dragged out of it.
    write("slide.wav", mix(knock(90, [(120, 1.0), (205, 0.4)], click=0.3, decay=40.0),
                           scribble(260, 70, 0.10, rasp=0.35), 0.7, 0.9))

    # Graphite, one short mark.
    write("pencil.wav", scribble(170, 95, 0.22, rasp=0.7))

    # A longer line, with the hand still moving at the end.
    write("stroke.wav", scribble(420, 58, 0.16, rasp=0.5))


if __name__ == "__main__":
    main()
