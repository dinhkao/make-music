"""Nick Villa-style drum patterns v2 - denser, drum-forward.
Kick syncopated + ghost snare + 16th hats + ride bell (his tricks),
PLUS tom fills and crashes so it actually sounds like drums.
Events: (beat, instrument, amp, [pitch]) - beats in 16th units.
"""

KICK, SNARE, HAT, OPEN, SHAKER, TAMB, BELL, CRASH, TOM = range(9)


def drum_events(style, bar, beats_per_bar):
    n16 = beats_per_bar * 4
    ev = []
    if style == "lounge":
        for p in [0, 6]: ev.append((p, KICK, 0.5))
        for p in range(0, n16, 2):
            ev.append((p, HAT, 0.09) if p % 4 == 2 else (p, SHAKER, 0.05))
    elif style == "verse":
        for p in [0, 6, 10, 14]: ev.append((p, KICK, 0.42))
        ev.append((7, KICK, 0.16))
        for p in [4, 12]: ev.append((p, SNARE, 0.30))
        for p in [6, 14]: ev.append((p, SNARE, 0.10))
        ev.append((2, SNARE, 0.09))
        for p in range(n16): ev.append((p, HAT, 0.085))
        for p in range(0, n16, 2): ev.append((p, SHAKER, 0.04))
    elif style == "pre":
        for p in [0, 4, 8, 12]: ev.append((p, KICK, 0.5))
        for p in [6, 14]: ev.append((p, KICK, 0.28))
        for p in [4, 12]: ev.append((p, SNARE, 0.38))
        for p in [2, 10]: ev.append((p, SNARE, 0.1))
        for p in range(n16): ev.append((p, HAT, 0.11))
        ev.append((14, OPEN, 0.1))
        if bar == 4:  # TOM fill into chorus (16ths 8-15, descending)
            for i, p in enumerate(range(8, n16)):
                ev.append((p, TOM, 0.30 + 0.14 * i / 7, 1.2 - 0.25 * i / 7))
            ev.append((0, CRASH, 0.2))
    elif style == "chorus":
        for p in [0, 4, 8, 10, 12]: ev.append((p, KICK, 0.5))
        ev.append((6, KICK, 0.22))
        for p in [4, 12]: ev.append((p, SNARE, 0.45))
        for p in [2, 6, 14]: ev.append((p, SNARE, 0.12))
        for p in range(n16): ev.append((p, HAT, 0.12))
        for p in [0, 4, 8, 12]: ev.append((p, BELL, 0.18))
        for p in range(0, n16, 2): ev.append((p, TAMB, 0.06))
        if bar % 2 == 0: ev.append((14, OPEN, 0.12))
        if bar in (1, 5): ev.append((0, CRASH, 0.22))
        if bar == 4:  # tom fill mid-chorus
            for i, p in enumerate(range(12, n16)):
                ev.append((p, TOM, 0.26 + 0.15 * i / 3, 1.1 - 0.2 * i / 3))
        if bar == 8:  # double-kick finish
            for p in range(10, n16):
                ev.append((p, KICK, 0.4))
            ev.append((0, CRASH, 0.24))
    elif style == "bridge":  # 6/8 lope
        for p in [0, 7]: ev.append((p, KICK, 0.48))
        ev.append((4, SNARE, 0.38))
        for p in [6, 10]: ev.append((p, SNARE, 0.1))
        for p in range(n16): ev.append((p, HAT, 0.09))
        if bar % 2 == 0: ev.append((n16 - 1, OPEN, 0.09))
        if bar == 4: ev.append((n16 - 1, TOM, 0.3, 1.0))
    elif style == "outro":
        for p in [0, 6]: ev.append((p, KICK, 0.45))
        for p in range(0, n16, 2):
            ev.append((p, HAT, 0.08) if p % 4 == 2 else (p, SHAKER, 0.05))
        if bar == 8:  # glitch stutter + final crash
            for p in range(0, n16, 2):
                ev.append((p, KICK, 0.35))
            ev.append((0, CRASH, 0.2))
    return ev
