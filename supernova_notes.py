"""Static Supernova - song data. Indie anthem inspired by Oasis' She's Electric.
Learned from the MIDI: E major, 127-ish BPM, heavy 2:1 swing, I-IV (E-A)
vamp with F# intro ring, B/C#m for the lift. Added: handclap chorus,
middle-8 bridge, KS guitar strums + solo, la-la outro.
126 BPM, 4/4, swung eighths (long=2/3, short=1/3).
"""

SR = 44100
BPM = 126.0
BEAT = 60.0 / BPM          # 0.476 s
BAR = 4.0 * BEAT           # 1.905 s
SWING_L, SWING_S = 2.0 / 3.0, 1.0 / 3.0   # swung 8th positions within a beat

# Guitar-strum voicings (open-string-ish, E major)
GUITAR = {
    "E":   [40, 52, 56, 59, 64],   # E2 E3 G#3 B3 E4
    "A":   [45, 52, 57, 61, 64],   # A2 E3 A3 C#4 E4
    "B":   [47, 54, 59, 63, 66],   # B2 F#3 B3 D#4 F#4
    "C#m": [49, 56, 61, 64, 68],   # C#3 G#3 C#4 E4 G#4
    "F#":  [42, 49, 54, 58, 61],   # F#2 C#3 F#3 A#3 C#4
    "F#m": [42, 49, 54, 57, 61],   # F#2 C#3 F#3 A3 C#4
}

# EP pad voicings (3-4 notes, mid register)
PAD = {
    "E":   [52, 56, 59, 64],   # E3 G#3 B3 E4
    "A":   [57, 61, 64, 69],   # A3 C#4 E4 A4
    "B":   [59, 63, 66, 71],   # B3 D#4 F#4 B4
    "C#m": [56, 61, 64, 68],   # G#3 C#4 E4 G#4
    "F#":  [54, 58, 61, 66],   # F#3 A#3 C#4 F#4
    "F#m": [54, 57, 61, 66],   # F#3 A3 C#4 F#4
}

BASS = {"E": 40, "A": 45, "B": 47, "C#m": 37, "F#": 42, "F#m": 42}

# (name, start_bar, n_bars, chords_cycle, style)
SECTIONS = [
    ("intro",   1,  4, ["F#", "F#", "E", "E"],       "intro"),
    ("verse",   5,  8, ["E", "A", "E", "A", "E", "A", "E", "A"], "verse"),
    ("pre",    13,  4, ["A", "E", "B", "C#m"],       "pre"),
    ("chorus", 17,  8, ["A", "E", "B", "C#m",
                        "A", "E", "B", "C#m"],       "chorus"),
    ("verse",  25,  8, ["E", "A", "E", "A", "E", "A", "E", "A"], "verse"),
    ("pre",    33,  4, ["A", "E", "B", "C#m"],       "pre"),
    ("chorus2", 37, 8, ["A", "E", "B", "C#m",
                        "A", "E", "B", "C#m"],       "chorus"),
    ("bridge", 45,  4, ["F#m", "C#m", "A", "B"],     "bridge"),
    ("solo",   49,  4, ["A", "E", "B", "C#m"],       "solo"),
    ("chorus3", 53, 8, ["A", "E", "B", "C#m",
                        "A", "E", "B", "C#m"],       "chorus"),
    ("outro",  61, 12, ["E", "A", "E", "A",
                        "E", "A", "E", "A",
                        "E", "A", "E", "E"],         "outro"),
]

# Melodies: SECTION-LOCAL bars, (local_bar, beat, midi, dur_beats)
MELODY = {
    "verse": [
        (1, 0, 59, 0.5), (1, 0.5, 57, 0.5), (1, 1, 56, 1), (1, 2, 54, 1),
        (1, 3, 56, 1),
        (2, 0, 57, 1), (2, 1, 59, 1), (2, 2, 61, 1), (2, 3, 59, 1),
        (3, 0, 59, 0.5), (3, 0.5, 61, 0.5), (3, 1, 59, 1), (3, 2, 56, 2),
        (4, 0, 54, 1), (4, 1, 56, 1), (4, 2, 57, 1), (4, 3, 59, 1),
        (5, 0, 59, 0.5), (5, 0.5, 57, 0.5), (5, 1, 56, 1), (5, 2, 54, 1),
        (5, 3, 56, 1),
        (6, 0, 57, 1), (6, 1, 59, 1), (6, 2, 61, 1), (6, 3, 59, 1),
        (7, 0, 59, 0.5), (7, 0.5, 61, 0.5), (7, 1, 59, 1), (7, 2, 56, 2),
        (8, 0, 57, 1), (8, 1, 59, 1), (8, 2, 61, 2),
    ],
    "pre": [
        (1, 0, 61, 1), (1, 1, 63, 1), (1, 2, 61, 1), (1, 3, 59, 1),
        (2, 0, 57, 1), (2, 1, 59, 1), (2, 2, 61, 1), (2, 3, 63, 1),
        (3, 0, 64, 2), (3, 2, 61, 1), (3, 3, 63, 1),
        (4, 0, 64, 3),
    ],
    "chorus": [
        # HOOK: "Sta-tic su-per-no-va" descending from E5
        (1, 0, 64, 0.5), (1, 0.5, 64, 0.5), (1, 1, 63, 1), (1, 2, 61, 1),
        (1, 3, 59, 1),
        (2, 0, 57, 2), (2, 2, 59, 1), (2, 3, 61, 1),
        (3, 0, 64, 0.5), (3, 0.5, 64, 0.5), (3, 1, 63, 1), (3, 2, 61, 1),
        (3, 3, 63, 1),
        (4, 0, 64, 3),
        (5, 0, 64, 0.5), (5, 0.5, 64, 0.5), (5, 1, 63, 1), (5, 2, 61, 1),
        (5, 3, 59, 1),
        (6, 0, 57, 1), (6, 1, 59, 1), (6, 2, 61, 1), (6, 3, 63, 1),
        (7, 0, 64, 1), (7, 1, 63, 1), (7, 2, 61, 1), (7, 3, 59, 1),
        (8, 0, 59, 1), (8, 1, 61, 1), (8, 2, 64, 2),
    ],
    "bridge": [
        (1, 0, 61, 1), (1, 1, 59, 1), (1, 2, 57, 1), (1, 3, 56, 1),
        (2, 0, 54, 2), (2, 2, 56, 1), (2, 3, 57, 1),
        (3, 0, 59, 1), (3, 1, 61, 1), (3, 2, 63, 1), (3, 3, 64, 1),
        (4, 0, 63, 2), (4, 2, 61, 1), (4, 3, 59, 1),
    ],
}

# Outro "la la" choir pulses (chord, midi notes, per bar)
OUTRO_LA = {
    "E": [52, 56, 59, 64],
    "A": [57, 61, 64, 69],
}

LYRICS = """\
[Verse]
You light up every room you're in
Like a circuit under my skin
Every spark you leave behind
Is a fire in my mind

[Chorus]
Static supernova
Burning through my radio
Static supernova
Wherever you go, I glow

[Bridge]
And the wires all hum your name
Every streetlight is a flame
"""
