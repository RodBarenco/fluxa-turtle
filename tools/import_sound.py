#!/usr/bin/env python3
"""import_sound.py — a recording of your own, at the level of the others.

    python3 tools/import_sound.py note.ogg -o sounds/pencil.wav --from 0.19 --to 1.27

Records made on a phone arrive wrong in three ways that all matter here, and
this fixes the three: they are in a format `std.sound` does not read (ogg), they
are mostly silence with a thump at the end where the button was pressed, and
they are recorded at whatever level the microphone felt like — which is never
the level of the sounds already in `sounds/`.

Anything ffmpeg can decode goes in; a mono 22050 Hz wav comes out.

    --from / --to   seconds to keep. Run it once without them and read the
                    envelope it prints: the loud part of a voice note is very
                    often the phone being handled, not what you recorded.
    --level         match the kit's loudness (`rms`, the default) or its peak.
                    RMS is the honest one — two sounds with the same peak and
                    different density do not sound equally loud.
    --hp            high-pass, in Hz, for the rumble a hand on a phone makes.
"""

import argparse
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

SR = 22050
KIT = ["place.wav", "tap.wav", "slide.wav", "stroke.wav"]


def decode(path):
    out = os.path.join(tempfile.mkdtemp(), "in.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", path, "-ac", "1", "-ar", str(SR), out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg could not read {path}:\n{r.stderr.strip()}")
    return out


def read(path):
    with wave.open(path) as w:
        n = w.getnframes()
        raw = w.readframes(n)
    return [struct.unpack_from("<h", raw, 2 * i)[0] for i in range(n)]


def write(path, xs):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(round(v))))) for v in xs))


def rms(xs):
    if not xs:
        return 0.0
    return math.sqrt(sum(v * v for v in xs) / len(xs))


def envelope(xs, win_ms=20):
    w = max(1, int(SR * win_ms / 1000))
    out, acc = [], 0.0
    for i, v in enumerate(xs):
        acc += abs(v)
        if i >= w:
            acc -= abs(xs[i - w])
        out.append(acc / min(i + 1, w))
    return out


def show(xs):
    env = envelope(xs)
    top = max(env) or 1.0
    step = int(SR * 0.05)
    print("envelope, 50 ms a line, dB below the loudest:", file=sys.stderr)
    for i in range(0, len(env), step):
        seg = env[i:i + step]
        db = 20 * math.log10(max(max(seg), 1e-9) / top)
        print(f"  {i / SR * 1000:6.0f} ms {db:6.1f} {'#' * max(0, int(40 + db * 0.6))}",
              file=sys.stderr)


def highpass(xs, hz):
    k = 1.0 / (1.0 + 2.0 * math.pi * hz / SR)
    out, li, lo = [], 0.0, 0.0
    for v in xs:
        lo = k * (lo + v - li)
        li = v
        out.append(lo)
    return out


def fade(xs, ms=8.0):
    n = max(1, int(SR * ms / 1000))
    for i in range(min(n, len(xs))):
        xs[i] *= i / n
        xs[-1 - i] *= i / n
    return xs


def kit_level(kind):
    vals = []
    for name in KIT:
        p = os.path.join("sounds", name)
        if os.path.exists(p):
            xs = read(p)
            vals.append(rms(xs) if kind == "rms" else max(abs(v) for v in xs))
    if not vals:
        sys.exit("no sounds/ to match — run tools/sounds.py first")
    return sum(vals) / len(vals)


def main():
    ap = argparse.ArgumentParser(description="A recording, at the level of the others.")
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--from", dest="a", type=float, default=0.0, help="seconds")
    ap.add_argument("--to", dest="b", type=float, default=0.0, help="seconds; 0 = the end")
    ap.add_argument("--level", choices=("rms", "peak"), default="rms")
    ap.add_argument("--hp", type=float, default=70.0)
    ap.add_argument("--hard", action="store_true",
                    help="never touch the peaks: accept a quieter file instead")
    ap.add_argument("--show", action="store_true", help="print the envelope and stop")
    args = ap.parse_args()

    xs = read(decode(args.input))
    print(f"[import] {len(xs) / SR * 1000:.0f} ms in, peak {max(abs(v) for v in xs):.0f}, "
          f"rms {rms(xs):.0f}", file=sys.stderr)

    if args.show:
        show(xs)
        return

    a = int(args.a * SR)
    b = int(args.b * SR) if args.b > 0 else len(xs)
    xs = xs[a:b]
    if len(xs) < 64:
        sys.exit("nothing left after the trim")

    if args.hp > 0:
        xs = highpass(xs, args.hp)
    xs = fade(xs)

    want = kit_level(args.level)

    # Matching loudness by RMS often asks for a peak that does not fit, because
    # one transient somewhere — a knuckle on the phone — is far above the rest
    # of the recording. Pulling the whole thing down to fit that one sample
    # leaves the sound quieter than the kit; hard clipping it turns a scratch
    # into the gunshot this family of sounds exists to avoid.
    #
    # So the peak is rounded off instead, with a soft knee above `keep`, and
    # the gain is re-fitted after it. Two or three passes settle it. `--hard`
    # skips this and simply refuses to clip, at the price of a quieter file.
    keep = 0.72 * 32767
    ceil = 0.95 * 32767
    for _ in range(6):
        have = rms(xs) if args.level == "rms" else max(abs(v) for v in xs)
        gain = want / max(have, 1e-9)
        peak = max(abs(v) for v in xs) * gain
        if args.hard and peak > ceil:
            gain *= ceil / peak
            print("[import] gain held back to keep the peak under full scale", file=sys.stderr)
            xs = [v * gain for v in xs]
            break
        xs = [v * gain for v in xs]
        if max(abs(v) for v in xs) <= ceil:
            break
        # soft knee: linear up to `keep`, then curved into the ceiling
        span = ceil - keep
        soft = []
        for v in xs:
            a = abs(v)
            if a <= keep:
                soft.append(v)
            else:
                over = (a - keep) / span
                a2 = keep + span * math.tanh(over)
                soft.append(math.copysign(a2, v))
        xs = soft
    write(args.out, xs)
    print(f"[import] {len(xs) / SR * 1000:.0f} ms out, peak {max(abs(v) for v in xs):.0f}, "
          f"rms {rms(xs):.0f}, matching the kit's {args.level} of {want:.0f} -> {args.out}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
