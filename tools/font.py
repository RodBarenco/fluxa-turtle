#!/usr/bin/env python3
"""font.py — the stroke font the turtle writes with.

    python3 tools/font.py            # writes fonts/stroke.font

A plotter font: every glyph is a few polylines on a grid six wide and ten tall,
drawn with one pen. Not outlines — a letter is the path a hand takes, which is
what makes it a turtle's kind of letter: it animates, it takes any path style,
and it is erased and pivoted like any other stroke.

The file is data rather than code for the same reason the traced trajectories
are: a literal in Fluxa holds about two hundred numbers and this font is over a
thousand, and data never reaches the parser.

    -1      start a glyph; the next number is its index in ALPHABET
    -2      lift the pen: a new stroke inside the same glyph
    x y     a point, on the 0..6 by 0..10 grid

ALPHABET is the order, and `static/font.flx` holds the same string. The turtle
finds a character's glyph with `strings.find`, which is one call and no table.
"""

import os

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-:'"

G = {
    "A": [[(0,0),(3,10),(6,0)], [(1,3),(5,3)]],
    "B": [[(0,0),(0,10),(4,10),(5,9),(5,6),(4,5),(0,5)], [(0,5),(4,5),(5,4),(5,1),(4,0),(0,0)]],
    "C": [[(6,9),(4,10),(2,10),(0,8),(0,2),(2,0),(4,0),(6,1)]],
    "D": [[(0,0),(0,10),(3,10),(5,8),(5,2),(3,0),(0,0)]],
    "E": [[(6,10),(0,10),(0,0),(6,0)], [(0,5),(4,5)]],
    "F": [[(6,10),(0,10),(0,0)], [(0,5),(4,5)]],
    "G": [[(6,9),(4,10),(2,10),(0,8),(0,2),(2,0),(4,0),(6,2),(6,4),(3,4)]],
    "H": [[(0,10),(0,0)], [(6,10),(6,0)], [(0,5),(6,5)]],
    "I": [[(1,10),(5,10)], [(3,10),(3,0)], [(1,0),(5,0)]],
    "J": [[(5,10),(5,2),(3,0),(1,0),(0,2)]],
    "K": [[(0,10),(0,0)], [(5,10),(0,5)], [(1,6),(6,0)]],
    "L": [[(0,10),(0,0),(6,0)]],
    "M": [[(0,0),(0,10),(3,6),(6,10),(6,0)]],
    "N": [[(0,0),(0,10),(6,0),(6,10)]],
    "O": [[(2,10),(4,10),(6,8),(6,2),(4,0),(2,0),(0,2),(0,8),(2,10)]],
    "P": [[(0,0),(0,10),(4,10),(6,9),(6,7),(4,5),(0,5)]],
    "Q": [[(2,10),(4,10),(6,8),(6,2),(4,0),(2,0),(0,2),(0,8),(2,10)], [(4,2),(6,0)]],
    "R": [[(0,0),(0,10),(4,10),(6,9),(6,7),(4,5),(0,5)], [(3,5),(6,0)]],
    "S": [[(6,9),(4,10),(2,10),(0,8),(2,5),(4,5),(6,3),(4,0),(2,0),(0,1)]],
    "T": [[(0,10),(6,10)], [(3,10),(3,0)]],
    "U": [[(0,10),(0,2),(2,0),(4,0),(6,2),(6,10)]],
    "V": [[(0,10),(3,0),(6,10)]],
    "W": [[(0,10),(1,0),(3,5),(5,0),(6,10)]],
    "X": [[(0,10),(6,0)], [(0,0),(6,10)]],
    "Y": [[(0,10),(3,5),(6,10)], [(3,5),(3,0)]],
    "Z": [[(0,10),(6,10),(0,0),(6,0)]],
    "0": [[(2,10),(4,10),(6,8),(6,2),(4,0),(2,0),(0,2),(0,8),(2,10)], [(0,2),(6,8)]],
    "1": [[(1,8),(3,10),(3,0)], [(1,0),(5,0)]],
    "2": [[(0,9),(2,10),(4,10),(6,8),(6,6),(0,0),(6,0)]],
    "3": [[(0,9),(2,10),(5,10),(6,8),(4,5),(6,3),(5,0),(2,0),(0,1)]],
    "4": [[(5,0),(5,10),(0,3),(6,3)]],
    "5": [[(6,10),(0,10),(0,6),(4,6),(6,4),(6,2),(4,0),(1,0),(0,1)]],
    "6": [[(6,9),(4,10),(2,10),(0,8),(0,2),(2,0),(4,0),(6,2),(6,3),(4,5),(0,5)]],
    "7": [[(0,10),(6,10),(2,0)]],
    "8": [[(2,5),(0,7),(0,9),(2,10),(4,10),(6,9),(6,7),(4,5),(2,5),(0,3),(0,1),(2,0),(4,0),(6,1),(6,3),(4,5)]],
    "9": [[(0,1),(2,0),(4,0),(6,2),(6,8),(4,10),(2,10),(0,8),(0,7),(2,5),(6,5)]],
    " ": [],
    ".": [[(3,0),(3,1)]],
    ",": [[(3,1),(2,0)]],
    "!": [[(3,10),(3,3)], [(3,1),(3,0)]],
    "?": [[(0,9),(2,10),(4,10),(6,8),(4,5),(3,5),(3,4)], [(3,1),(3,0)]],
    "-": [[(1,5),(5,5)]],
    ":": [[(3,7),(3,6)], [(3,3),(3,2)]],
    "'": [[(3,10),(3,8)]],
}


def main():
    missing = [c for c in ALPHABET if c not in G]
    if missing:
        raise SystemExit(f"no glyph for {missing}")

    out, points, strokes = [], 0, 0
    for i, ch in enumerate(ALPHABET):
        out.append("-1")
        out.append(str(i))
        for si, stroke in enumerate(G[ch]):
            if si:
                out.append("-2")
            strokes += 1
            for x, y in stroke:
                out.append(str(x))
                out.append(str(y))
                points += 1

    os.makedirs("fonts", exist_ok=True)
    with open("fonts/stroke.font", "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"[font] {len(ALPHABET)} glyphs, {strokes} strokes, {points} points "
          f"-> fonts/stroke.font ({len(out)} lines)")


if __name__ == "__main__":
    main()
