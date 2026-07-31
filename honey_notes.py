"""Honey Static - song data. Catchy-but-quirky synth pop.
Everything learned from Magdalena Bay / Nick Villa research:
- borrowed F#7 chord (Killing Time trick), 7th-heavy chords
- 6/8 bridge (Killing Time meter), syncopated kicks + snare ghost
  notes (Nick Villa's Death & Romance style), 16th-note hi-hats
- hook melody repeats twice per chorus, stepwise + big leap
Key C major, 112 BPM, 4/4 (bridge in 6/8 = 3 beats/bar).
"""

SR = 44100
BPM = 112.0
BEAT = 60.0 / BPM          # 0.536 s
BAR44 = 4.0 * BEAT         # 2.143 s (4/4)
BAR68 = 3.0 * BEAT         # 1.607 s (6/8)

# Chord voicings (midi)
CHORDS = {
    "Cmaj7":  [48, 52, 55, 59],   # C3 E3 G3 B3
    "F#7":    [54, 58, 61, 64],   # F#3 A#3 C#4 E4 (borrowed!)
    "G7":     [55, 59, 62, 65],   # G3 B3 D4 F4
    "Dm7":    [50, 53, 57, 60],   # D3 F3 A3 C4
    "A7":     [57, 61, 64, 67],   # A3 C#4 E4 G4
    "Em7":    [52, 55, 59, 62],   # E3 G3 B3 D4
    "Am7":    [57, 60, 64, 67],   # A3 C4 E4 G4
    "Fmaj7":  [53, 57, 60, 64],   # F3 A3 C4 E4
    "C7":     [55, 59, 62, 65],   # C3 E3 G3 Bb3 (voiced up)
    "Ebdim7": [51, 54, 57, 60],   # Eb3 Gb3 A3 C4
}

BASS = {
    "Cmaj7": 36, "F#7": 42, "G7": 43, "Dm7": 38, "A7": 45,
    "Em7": 40, "Am7": 45, "Fmaj7": 41, "C7": 36, "Ebdim7": 39,
}

# (name, start_bar, n_bars, chords_cycle, style, beats_per_bar)
SECTIONS = [
    ("intro",   1,  8, ["Cmaj7", "F#7", "Cmaj7", "G7"], "lounge", 4),
    ("verse",   9,  8, ["Cmaj7", "F#7", "Cmaj7", "G7"], "verse",  4),
    ("pre",    17,  4, ["Dm7", "G7", "Cmaj7", "A7"],   "pre",    4),
    ("chorus", 21,  8, ["Fmaj7", "G7", "Em7", "Am7",
                        "Fmaj7", "G7", "Cmaj7", "C7"], "chorus", 4),
    ("verse",  29,  8, ["Cmaj7", "F#7", "Cmaj7", "G7"], "verse",  4),
    ("pre",    37,  4, ["Dm7", "G7", "Cmaj7", "A7"],   "pre",    4),
    ("chorus2", 41, 8, ["Fmaj7", "G7", "Em7", "Am7",
                        "Fmaj7", "G7", "Cmaj7", "C7"], "chorus", 4),
    ("bridge", 49,  8, ["Ebdim7", "Dm7", "G7", "Cmaj7"], "bridge", 3),
    ("chorus3", 57, 4, ["Fmaj7", "G7", "Cmaj7", "C7"],  "chorus", 4),
    ("outro",  61,  8, ["Cmaj7", "F#7", "Cmaj7", "G7"], "outro",  4),
]

# Melodies: events in SECTION-LOCAL bars, (local_bar, beat, midi, dur_beats)
MELODY = {
    "verse": [
        (1, 0, 72, 0.5), (1, 0.5, 71, 0.5), (1, 1, 69, 1), (1, 2, 67, 0.5),
        (1, 2.5, 69, 0.5), (1, 3, 71, 1),
        (2, 0, 72, 1), (2, 1, 74, 0.5), (2, 1.5, 72, 0.5), (2, 2, 71, 1),
        (2, 3, 69, 1),
        (3, 0, 69, 0.5), (3, 0.5, 71, 0.5), (3, 1, 72, 1), (3, 2, 74, 1),
        (3, 3, 76, 1),
        (4, 0, 74, 2), (4, 2, 72, 1),
        (5, 0, 72, 0.5), (5, 0.5, 71, 0.5), (5, 1, 69, 1), (5, 2, 67, 0.5),
        (5, 2.5, 69, 0.5), (5, 3, 71, 1),
        (6, 0, 72, 1), (6, 1, 74, 0.5), (6, 1.5, 72, 0.5), (6, 2, 71, 1),
        (6, 3, 69, 1),
        (7, 0, 69, 0.5), (7, 0.5, 71, 0.5), (7, 1, 72, 1), (7, 2, 74, 1),
        (7, 3, 76, 1),
        (8, 0, 76, 1), (8, 1, 74, 1), (8, 2, 72, 2),
    ],
    "pre": [
        (1, 0, 76, 1), (1, 1, 77, 1), (1, 2, 76, 1), (1, 3, 74, 1),
        (2, 0, 72, 1), (2, 1, 74, 1), (2, 2, 76, 1), (2, 3, 77, 1),
        (3, 0, 79, 2), (3, 2, 76, 1), (3, 3, 77, 1),
        (4, 0, 79, 3),
    ],
    "chorus": [
        (1, 0, 76, 0.5), (1, 0.5, 76, 0.5), (1, 1, 74, 0.5), (1, 1.5, 72, 0.5),
        (1, 2, 74, 1), (1, 3, 76, 1),
        (2, 0, 79, 2), (2, 2, 77, 1),
        (3, 0, 76, 0.5), (3, 0.5, 74, 0.5), (3, 1, 72, 1), (3, 2, 74, 1),
        (3, 3, 76, 1),
        (4, 0, 74, 2), (4, 2, 72, 1),
        (5, 0, 76, 0.5), (5, 0.5, 76, 0.5), (5, 1, 74, 0.5), (5, 1.5, 72, 0.5),
        (5, 2, 74, 1), (5, 3, 76, 1),
        (6, 0, 79, 2), (6, 2, 77, 1),
        (7, 0, 76, 0.5), (7, 0.5, 74, 0.5), (7, 1, 72, 1), (7, 2, 74, 1),
        (7, 3, 76, 1),
        (8, 0, 79, 1), (8, 1, 72, 2),
    ],
    "bridge": [  # 3-beat bars (6/8)
        (1, 0, 72, 0.5), (1, 0.5, 74, 0.5), (1, 1, 76, 0.5), (1, 1.5, 77, 0.5),
        (1, 2, 79, 0.5), (1, 2.5, 81, 0.5),
        (2, 0, 79, 1.5), (2, 1.5, 76, 1), (2, 2.5, 72, 0.5),
        (3, 0, 74, 0.5), (3, 0.5, 76, 0.5), (3, 1, 77, 0.5), (3, 1.5, 79, 0.5),
        (3, 2, 81, 0.5), (3, 2.5, 83, 0.5),
        (4, 0, 81, 1.5), (4, 1.5, 79, 1), (4, 2.5, 76, 0.5),
        (5, 0, 72, 0.5), (5, 0.5, 74, 0.5), (5, 1, 76, 0.5), (5, 1.5, 77, 0.5),
        (5, 2, 79, 0.5), (5, 2.5, 81, 0.5),
        (6, 0, 79, 1.5), (6, 1.5, 76, 1), (6, 2.5, 72, 0.5),
        (7, 0, 76, 0.5), (7, 0.5, 77, 0.5), (7, 1, 79, 0.5), (7, 1.5, 81, 0.5),
        (7, 2, 79, 0.5), (7, 2.5, 77, 0.5),
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
