"""Static Supernova drums - Oasis-style swing groove.
Swung 8ths (long 2/3 + short 1/3), kick 1&3 + pickup, snare 2&4,
tambourine on swung 8ths, handclaps in chorus.
Events: (beat, instrument, amp) - beats in quarter units (swung).
"""

KICK, SNARE, HAT, TAMB, CLAP, CRASH = range(6)
SWING = [0.0, 2.0 / 3.0, 1.0, 1.0 + 2.0 / 3.0, 2.0, 2.0 + 2.0 / 3.0,
         3.0, 3.0 + 2.0 / 3.0]  # swung 8th positions


def drum_events(style, bar):
    ev = []
    if style == "intro":
        for s in SWING:
            ev.append((s, TAMB, 0.05))
        for s in SWING[::2]:
            ev.append((s, HAT, 0.07))
        ev.append((0, KICK, 0.45))
        ev.append((2, KICK, 0.45))
    elif style == "verse":
        for s in SWING:
            ev.append((s, HAT, 0.08))
        for s in SWING[::2]:
            ev.append((s, TAMB, 0.05))
        ev.append((0, KICK, 0.5))
        ev.append((2, KICK, 0.5))
        ev.append((3 + 2.0 / 3.0, KICK, 0.3))  # pickup into next bar
        ev.append((1, SNARE, 0.34))
        ev.append((3, SNARE, 0.34))
    elif style == "pre":
        for s in SWING:
            ev.append((s, HAT, 0.09))
        ev.append((0, KICK, 0.5))
        ev.append((2, KICK, 0.5))
        ev.append((3 + 2.0 / 3.0, KICK, 0.35))
        ev.append((1, SNARE, 0.36))
        ev.append((3, SNARE, 0.36))
        if bar == 4:  # snare build into chorus
            for i in range(8):
                ev.append((2 + i * 0.25, SNARE, 0.2 + 0.15 * i / 7))
    elif style == "chorus":
        for s in SWING:
            ev.append((s, HAT, 0.1))
        for s in SWING[::2]:
            ev.append((s, TAMB, 0.07))
        ev.append((0, KICK, 0.55))
        ev.append((2, KICK, 0.55))
        ev.append((3, KICK, 0.35))
        ev.append((1, SNARE, 0.4))
        ev.append((3, SNARE, 0.4))
        for s in [1, 3]:  # handclaps double the snare
            ev.append((s, CLAP, 0.4))
            ev.append((s + 0.5, CLAP, 0.3))
        if bar in (1, 5):
            ev.append((0, CRASH, 0.2))
    elif style == "bridge":
        for s in SWING:
            ev.append((s, HAT, 0.07))
        ev.append((0, KICK, 0.5))
        ev.append((2, KICK, 0.5))
        ev.append((1, SNARE, 0.32))
        ev.append((3, SNARE, 0.32))
    elif style == "solo":
        for s in SWING:
            ev.append((s, HAT, 0.1))
        ev.append((0, KICK, 0.55))
        ev.append((2, KICK, 0.55))
        ev.append((3, KICK, 0.4))
        ev.append((1, SNARE, 0.42))
        ev.append((3, SNARE, 0.42))
        ev.append((0, CRASH, 0.2))
    elif style == "outro":
        for s in SWING[::2]:
            ev.append((s, HAT, 0.07))
        for s in SWING:
            ev.append((s, TAMB, 0.05))
        ev.append((0, KICK, 0.45))
        ev.append((2, KICK, 0.45))
        if bar == 12:  # final hit
            ev.append((0, KICK, 0.5))
            ev.append((0, CRASH, 0.22))
            ev.append((3, SNARE, 0.4))
    return ev
