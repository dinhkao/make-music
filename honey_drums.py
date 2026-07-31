"""Nick Villa-style drum patterns for Honey Static.
Tricks learned from his tutorial/Q&A:
- syncopated kicks + snare GHOST notes coinciding near kicks
- hi-hat on 16ths to "lock into the grid"
- ride BELL pattern in choruses, fills coming in on "two and"
- double-kick fill for the big moment
Events: (beat_in_bar, instrument, amp, [open]) - beats in 16th units.
"""

KICK, SNARE, HAT, OPEN, SHAKER, TAMB, BELL, CRASH = range(8)

# 16th-grid patterns per style (bar = 16 sixteenths, bridge = 12)
def drum_events(style, bar, beats_per_bar):
    n16 = beats_per_bar * 4
    ev = []
    q16 = [i / 4 for i in range(n16)]  # beat positions of each 16th
    if style == "lounge":
        for p in [0, 6]: ev.append((p, KICK, 0.45))
        for p in range(0, n16, 2):
            if p % 4 == 2:
                ev.append((p, HAT, 0.07))
            else:
                ev.append((p, SHAKER, 0.04))
    elif style == "verse":
        # syncopated kicks (Death & Romance vibe) + ghost snare near kicks
        for p in [0, 6, 10, 14]: ev.append((p, KICK, 0.35))
        ev.append((7, KICK, 0.18))  # ghost kick
        for p in [4, 12]: ev.append((p, SNARE, 0.22))
        for p in [6, 14]: ev.append((p, SNARE, 0.08))  # ghosts w/ kicks
        ev.append((2, SNARE, 0.08))                     # extra ghost
        for p in range(n16): ev.append((p, HAT, 0.045))  # 16th hats
    elif style == "pre":
        for p in [0, 6, 8, 12, 14]: ev.append((p, KICK, 0.5))
        for p in [4, 12]: ev.append((p, SNARE, 0.3))
        for p in [2, 10]: ev.append((p, SNARE, 0.1))
        for p in range(n16): ev.append((p, HAT, 0.075))
        ev.append((14, OPEN, 0.09))
        if bar % 2 == 0: ev.append((0, CRASH, 0.10))
        if bar == 4:  # fill coming in on "two and" (beat 2.5 = 16th 10)
            for i, p in enumerate(range(9, n16)):
                ev.append((p, SNARE, 0.12 + 0.18 * i / (n16 - 9)))
    elif style == "chorus":
        for p in [0, 4, 8, 10, 12]: ev.append((p, KICK, 0.48))
        for p in [4, 12]: ev.append((p, SNARE, 0.30))
        for p in [2, 6, 14]: ev.append((p, SNARE, 0.1))
        for p in range(n16): ev.append((p, HAT, 0.07))
        for p in [0, 4, 8, 12]: ev.append((p, BELL, 0.20))  # ride bell!
        for p in range(0, n16, 2): ev.append((p, TAMB, 0.07))
        if bar % 2 == 0: ev.append((14, OPEN, 0.11))
        if bar % 2 == 1: ev.append((0, CRASH, 0.11))
        if bar == 8:  # double-kick fill (his Iron Cobra moment)
            for p in range(10, n16):
                ev.append((p, KICK, 0.4))
            ev.append((0, CRASH, 0.12))
    elif style == "bridge":  # 6/8 lope: backbeat on 8th 3 (16th 4)
        for p in [0, 7]: ev.append((p, KICK, 0.45))
        ev.append((4, SNARE, 0.3))
        for p in [6, 10]: ev.append((p, SNARE, 0.09))
        for p in range(n16): ev.append((p, HAT, 0.06))
        if bar % 2 == 1: ev.append((n16 - 1, OPEN, 0.08))
    elif style == "outro":
        for p in [0, 6]: ev.append((p, KICK, 0.4))
        for p in range(0, n16, 2):
            if p % 4 == 2:
                ev.append((p, HAT, 0.06))
            else:
                ev.append((p, SHAKER, 0.05))
        if bar == 8:  # glitch stutter kick + final hit
            for p in range(0, n16, 2):
                ev.append((p, KICK, 0.35))
            ev.append((0, CRASH, 0.12))
    return ev
