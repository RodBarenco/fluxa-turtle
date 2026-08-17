#!/usr/bin/env python3
"""import_sound.py — a recording of your own, at the level of the others.

    python3 tools/import_sound.py note.ogg -o sounds/pencil.wav --from 0.19 --to 1.27

A recording arrives in a format `std.sound` does not read (ogg), mostly silence,
with a thump at the end where the button was pressed, and at whatever level the
microphone felt like. This cuts it, converts it, and sets the level — and it
does **nothing else**, which is the point.

An earlier version resampled to 22 kHz, high-passed at 70 Hz and rounded the
peaks off with a soft knee. Each of those is defensible on its own and together
they made a recorded pencil sound thinner and duller than the file it came from
— it was no longer the take that had been approved. What is left here is a cut,
a gain, and four milliseconds of fade so the cut does not click. The sample rate
is the recording's.

    --from / --to   seconds to keep. Run it once with --show and read the
                    envelope: the loud part of a voice note is very often the
                    phone being handled, not what you recorded.
    --level         loud (default), rms or peak — see below.
    --hp            high-pass in Hz if you want one. Off by default.
"""

import argparse
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

KIT = ["place.wav", "tap.wav", "slide.wav"]     # the knocks are the reference


def decode(path):
    """To wav, mono, at the recording's OWN sample rate — resampling it down is
    the first thing that stops it being the take you approved."""
    out = os.path.join(tempfile.mkdtemp(), "in.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", path, "-ac", "1", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg could not read {path}:\n{r.stderr.strip()}")
    return out


def read(path):
    with wave.open(path) as w:
        n = w.getnframes()
        sr = w.getframerate()
        raw = w.readframes(n)
    return [struct.unpack_from("<h", raw, 2 * i)[0] for i in range(n)], sr


def write(path, xs, sr):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(round(v))))) for v in xs))


def loud(xs, sr, ms=300):
    """The RMS of the loudest 300 ms in the file.

    Whole-file RMS is the wrong ruler here and it was audibly wrong: a knock is
    a moment and a long decay, a scribble is energy all the way through, so
    matching their RMS leaves the scribble much the louder of the two. Loudness
    is judged over a fifth of a second or so, and this measures that.
    """
    w = max(1, int(sr * ms / 1000))
    if len(xs) <= w:
        return rms(xs)
    acc = sum(v * v for v in xs[:w])
    best = acc
    for i in range(w, len(xs)):
        acc += xs[i] * xs[i] - xs[i - w] * xs[i - w]
        if acc > best:
            best = acc
    return math.sqrt(best / w)


def rms(xs):
    if not xs:
        return 0.0
    return math.sqrt(sum(v * v for v in xs) / len(xs))


def envelope(xs, sr, win_ms=20):
    w = max(1, int(sr * win_ms / 1000))
    out, acc = [], 0.0
    for i, v in enumerate(xs):
        acc += abs(v)
        if i >= w:
            acc -= abs(xs[i - w])
        out.append(acc / min(i + 1, w))
    return out


def show(xs, sr):
    env = envelope(xs, sr)
    top = max(env) or 1.0
    step = int(sr * 0.05)
    print("envelope, 50 ms a line, dB below the loudest:", file=sys.stderr)
    for i in range(0, len(env), step):
        seg = env[i:i + step]
        db = 20 * math.log10(max(max(seg), 1e-9) / top)
        print(f"  {i / sr * 1000:6.0f} ms {db:6.1f} {'#' * max(0, int(40 + db * 0.6))}",
              file=sys.stderr)


def highpass(xs, hz, sr):
    k = 1.0 / (1.0 + 2.0 * math.pi * hz / sr)
    out, li, lo = [], 0.0, 0.0
    for v in xs:
        lo = k * (lo + v - li)
        li = v
        out.append(lo)
    return out


def fade(xs, sr, ms=4.0):
    n = max(1, int(sr * ms / 1000))
    for i in range(min(n, len(xs))):
        xs[i] *= i / n
        xs[-1 - i] *= i / n
    return xs


def measure(xs, sr, kind):
    if kind == "peak":
        return max(abs(v) for v in xs)
    if kind == "rms":
        return rms(xs)
    return loud(xs, sr)


def kit_level(kind):
    vals = []
    for name in KIT:
        p = os.path.join("sounds", name)
        if os.path.exists(p):
            xs, sr = read(p)
            vals.append(measure(xs, sr, kind))
    if not vals:
        sys.exit("no sounds/ to match — run tools/sounds.py first")
    return sum(vals) / len(vals)


def main():
    ap = argparse.ArgumentParser(description="A recording, at the level of the others.")
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--from", dest="a", type=float, default=0.0, help="seconds")
    ap.add_argument("--to", dest="b", type=float, default=0.0, help="seconds; 0 = the end")
    ap.add_argument("--level", choices=("loud", "rms", "peak"), default="loud")
    ap.add_argument("--hp", type=float, default=0.0, help="high-pass in Hz; off by default")
    ap.add_argument("--show", action="store_true", help="print the envelope and stop")
    args = ap.parse_args()

    xs, sr = read(decode(args.input))
    print(f"[import] {len(xs) / sr * 1000:.0f} ms in at {sr} Hz, "
          f"peak {max(abs(v) for v in xs):.0f}, loudest 300 ms {loud(xs, sr):.0f}",
          file=sys.stderr)

    if args.show:
        show(xs, sr)
        return

    a = int(args.a * sr)
    b = int(args.b * sr) if args.b > 0 else len(xs)
    xs = xs[a:b]
    if len(xs) < 64:
        sys.exit("nothing left after the trim")

    if args.hp > 0:
        xs = highpass(xs, args.hp, sr)
    xs = fade(xs, sr)

    want = kit_level(args.level)
    gain = want / max(measure(xs, sr, args.level), 1e-9)

    # Scaling up is where a recording gets hurt, so it is the one case that
    # gets refused rather than solved: no limiter, no knee, nothing that would
    # change the sound. It says what it did instead.
    peak = max(abs(v) for v in xs) * gain
    if peak > 0.97 * 32767:
        held = 0.97 * 32767 / peak
        gain *= held
        print(f"[import] gain held back {20 * math.log10(held):.1f} dB — the peak "
              f"would not fit, and nothing here will squash it", file=sys.stderr)

    xs = [v * gain for v in xs]
    write(args.out, xs, sr)
    print(f"[import] {len(xs) / sr * 1000:.0f} ms out at {sr} Hz, gain "
          f"{20 * math.log10(max(gain, 1e-9)):+.1f} dB, loudest 300 ms "
          f"{loud(xs, sr):.0f} against the kit's {want:.0f} -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
