"""Honey Static v2 - song data. Catchy-but-quirky synth pop.
Chords: all 9ths/13ths/half-dim, walking bass line C-B-A-G-F-E-D-G
(like Killing Time's bassline-driven harmony). Hook: pickup + leap +
held high note. Bridge 6/8. 112 BPM, C major.
"""

SR = 44100
BPM = 112.0
BEAT = 60.0 / BPM          # 0.536 s
BAR44 = 4.0 * BEAT         # 2.143 s
BAR68 = 3.0 * BEAT         # 1.607 s

# Open 4-note voicings with 9ths (spread, not block chords)
CHORDS = {
    "Cmaj9":  [48, 55, 59, 62],   # C3 G3 B3 D4
    "Bm7b5":  [47, 53, 57, 62],   # B2 F3 A3 D4 (half-dim!)
    "Am9":    [45, 52, 55, 59],   # A2 E3 G3 B3
    "G13":    [43, 53, 57, 64],   # G2 F3 A3 E4
    "Fmaj9":  [41, 57, 60, 67],   # F2 A3 C4 G4
    "Em9":    [40, 55, 59, 66],   # E2 G3 B3 F#4
    "Dm9":    [38, 53, 60, 64],   # D2 F3 C4 E4
    "E7#9":   [40, 56, 62, 67],   # E2 G#3 D4 G4 (Hendrix!)
    "F#m7b5": [42, 57, 60, 64],   # F#2 A3 C4 E4 (half-dim)
    "G7":     [43, 55, 59, 62],   # G2 B3 D4 F4? no - G7 = G B D F
}

# Fix: G7 proper voicing (G3 B3 D4 F4)
CHORDS["G7"] = [43, 59, 62, 65]

# Bass root per chord (walks down the C major scale)
BASS = {
    "Cmaj9": 36, "Bm7b5": 35, "Am9": 33, "G13": 31,
    "Fmaj9": 29, "Em9": 28, "Dm9": 26, "E7#9": 28,
    "F#m7b5": 30, "G7": 31,
}

# (name, start_bar, n_bars, chords_cycle, style, beats_per_bar)
SECTIONS = [
    ("intro",   1,  8, ["Cmaj9", "G13", "Am9", "G13"], "lounge", 4),
    ("verse",   9,  8, ["Cmaj9", "Bm7b5", "Am9", "G13",
                        "Fmaj9", "Em9", "Dm9", "G13"], "verse",  4),
    ("pre",    17,  4, ["Dm9", "G13", "Cmaj9", "E7#9"], "pre",    4),
    ("chorus", 21,  8, ["Fmaj9", "G13", "Em9", "Am9",
                        "Dm9", "G13", "Cmaj9", "E7#9"], "chorus", 4),
    ("verse",  29,  8, ["Cmaj9", "Bm7b5", "Am9", "G13",
                        "Fmaj9", "Em9", "Dm9", "G13"], "verse",  4),
    ("pre",    37,  4, ["Dm9", "G13", "Cmaj9", "E7#9"], "pre",    4),
    ("chorus2", 41, 8, ["Fmaj9", "G13", "Em9", "Am9",
                        "Dm9", "G13", "Cmaj9", "E7#9"], "chorus", 4),
    ("bridge", 49,  8, ["Am9", "F#m7b5", "Dm9", "G13"], "bridge", 3),
    ("chorus3", 57, 4, ["Fmaj9", "G13", "Cmaj9", "E7#9"], "chorus", 4),
    ("outro",  61,  8, ["Cmaj9", "E7#9", "Fmaj9", "G13"], "outro",  4),
]

# Melodies: SECTION-LOCAL bars, (local_bar, beat, midi, dur_beats)
MELODY = {
    "verse": [
        # phrase 1 - motif G-A-C-D, pentatonic rise
        (1, 0, 67, 0.5), (1, 0.5, 69, 0.5), (1, 1, 72, 1), (1, 2, 74, 1),
        (1, 3, 72, 0.5), (1, 3.5, 71, 0.5),
        (2, 0, 69, 1.5), (2, 1.5, 67, 0.5), (2, 2, 69, 1), (2, 3, 71, 1),
        (3, 0, 72, 0.5), (3, 0.5, 74, 0.5), (3, 1, 76, 1), (3, 2, 79, 0.5),
        (3, 2.5, 76, 0.5), (3, 3, 74, 1),
        (4, 0, 72, 2), (4, 2, 74, 1), (4, 3, 76, 1),
        # phrase 2 - variation, ends low
        (5, 0, 67, 0.5), (5, 0.5, 69, 0.5), (5, 1, 72, 1), (5, 2, 74, 1),
        (5, 3, 76, 0.5), (5, 3.5, 74, 0.5),
        (6, 0, 72, 1.5), (6, 1.5, 69, 0.5), (6, 2, 71, 1), (6, 3, 72, 1),
        (7, 0, 76, 0.5), (7, 0.5, 74, 0.5), (7, 1, 72, 1), (7, 2, 74, 1),
        (7, 3, 76, 1),
        (8, 0, 74, 2), (8, 2, 72, 1), (8, 3, 67, 1),
    ],
    "pre": [
        (1, 0, 76, 1), (1, 1, 77, 1), (1, 2, 76, 1), (1, 3, 74, 1),
        (2, 0, 72, 1), (2, 1, 74, 1), (2, 2, 76, 1), (2, 3, 79, 1),
        (3, 0, 81, 2), (3, 2, 79, 1), (3, 3, 77, 1),
        (4, 0, 79, 3),
    ],
    "chorus": [
        # HOOK: pickup + leap to E5, held G5 "heart"
        (1, 0, 67, 0.5), (1, 0.5, 72, 0.5), (1, 1, 76, 1), (1, 2, 74, 0.5),
        (1, 2.5, 72, 0.5),
        (2, 0, 74, 0.5), (2, 0.5, 76, 0.5), (2, 1, 79, 2),
        (3, 0, 76, 0.5), (3, 0.5, 74, 0.5), (3, 1, 72, 1), (3, 2, 74, 1),
        (3, 3, 76, 1),
        (4, 0, 74, 2), (4, 2, 72, 1),
        (5, 0, 67, 0.5), (5, 0.5, 72, 0.5), (5, 1, 76, 1), (5, 2, 74, 0.5),
        (5, 2.5, 72, 0.5),
        (6, 0, 74, 0.5), (6, 0.5, 76, 0.5), (6, 1, 79, 2),
        (7, 0, 76, 0.5), (7, 0.5, 74, 0.5), (7, 1, 72, 1), (7, 2, 74, 1),
        (7, 3, 76, 1),
        (8, 0, 79, 1), (8, 1, 72, 3),
    ],
    "bridge": [  # 3-beat bars (6/8), soaring
        (1, 0, 72, 0.5), (1, 0.5, 74, 0.5), (1, 1, 76, 0.5), (1, 1.5, 79, 0.5),
        (1, 2, 81, 0.5), (1, 2.5, 79, 0.5),
        (2, 0, 76, 1.5), (2, 1.5, 74, 1), (2, 2.5, 72, 0.5),
        (3, 0, 74, 0.5), (3, 0.5, 76, 0.5), (3, 1, 77, 0.5), (3, 1.5, 81, 0.5),
        (3, 2, 79, 0.5), (3, 2.5, 77, 0.5),
        (4, 0, 76, 1.5), (4, 1.5, 74, 1), (4, 2.5, 72, 0.5),
        (5, 0, 72, 0.5), (5, 0.5, 74, 0.5), (5, 1, 76, 0.5), (5, 1.5, 79, 0.5),
        (5, 2, 81, 0.5), (5, 2.5, 79, 0.5),
        (6, 0, 76, 1), (6, 1, 77, 1), (6, 2, 81, 1),
        (7, 0, 79, 1.5), (7, 1.5, 77, 1), (7, 2.5, 76, 0.5),
        (8, 0, 76, 2),
    ],
}

# Spoken word (whisper, pitch-shifted): (bar, beat, text) - global bars
SPOKEN = [
    (19.5, "Pour the honey, hold the wire."),
    (50.0, "Tick-tock. The wires hum your name."),
    (53.5, "Static in the honey, buzzing in my brain."),
    (62.0, "Honey static."),
    (66.0, "Goodnight, television."),
]

LYRICS = """\
[Verse]
Pouring honey down the telephone line
You pick up and the signal's fine
Little sparks across the kitchen tile
Sweetest static, drive me wild

[Chorus]
Honey static, running through my automatic heart
Honey static, tear my circuits all apart

[Bridge]
Tick-tock, the wires hum your name
Static in the honey, buzzing in my brain
"""
