# 🎧 For the first time — 10 songs (modeled on Black Country, New Road)

Research source: Black Country, New Road — **_For the first time_** (Ninja Tune, 2021),
plus the original **Sunglasses** single and tabs (Ultimate Guitar, Cifra Club, Hooktheory,
Wikipedia). Drum DNA: **Nick Villa** (Magdalena Bay / Imaginal Disk) — *even quiet 16th-hat
grid locked with accents on the off-16ths, kick played as a melodic counter-rhythm on
off-16ths (empty downbeats), snare backbeat + ghost notes, ride bell + tom rolls at climax*.

## Rules I kept

- Every sound comes only from the palette of `20franticchoir.py` (the engine head in
  `_eng.txt`): `ks/jangle/crunch/leadgtr/slidegtr/clav/nylon/chime12` (guitar),
  `bassn/fzbass/subbass/fingerbass` (bass), `wurli/organ/tackpiano/gospelorgan` (keys),
  `bowed` (violin — Georgia Ellery), `bone/hbone/horn` (sax/brass — Lewis Evans),
  `mellotron/saw_drone` (strings/choir swell), `say/line/chant/gang/shriek` (vocals),
  `Kit + Performer` (Nick Villa humanized drums).
- Write **like the artist**: each song copies a specific BCNR technique (form, tonal
  displacement, riffs/pedals, irregular meter, dynamic escalation, klezmer) — only the
  key / a slightly different drum beat / different lead instrument is changed.
- **No basic pop 4-chord loop, no bassline just following roots.** Bass is a moving line.
- **Humanized spacing/velocity** for arps/melody (Gauss jitter), no robotic grid.
- Drums **do not** just play a backbeat — they follow the band's density & section.
- Each song ≤ **3:00** and each is a **single self-contained `.py`** (numpy + scipy only).
- Every track renders **two mp3s**: full (with the Isaac-Wood-style vocal) + instrumental.

## The 10 songs

| # | File | BCNR model | Key / meter / BPM | What it copies from the artist | Arc (dyn) |
|---|---|---|---|---|---|
| 01 | `01-fifth-hour` | **Instrumental** | F#m · 4/4 · 104 | slow-burn crescendo by **orchestration/layering one motif** (violin→sax→dist-gtr→choir→massed drums); slow colour chords over a pedal; **false stop → harder re-entry** | 6.09× |
| 02 | `02-borrowed-light` | **Athens, France** | Cm · 4/4 · 118 | through-composed **patchwork of tonal centres** (riff cycle → Cm↔Abmaj7 arp → Eb→Fm "lands on beat 2" push → **12/8 Abmaj7 "chucka chucka" vamp** with Ab-Ab-F-Db bass walk) | 2.17× |
| 03 | `03-half-a-smile` | **Science Fair** | B tritone · 4/4 · 128 | anxious **circling on a tritone dyad B+F (Bm♭5)** that never resolves; **improvised fuzz** intro; builds by articulation/density, **2-chord blowout**, false stop | 8.16× |
| 04 | `04-static-bloom` | **Sunglasses** | C (drop-C) · 4/4 · 117 | low-**C pedal riff** + chromatic upper-neighbour + M7 colour; **sax/violin m2 clash (F/Gb)**; distorted intro solo; climax is a **2-chord tritone (C↔Gb) ad-infinitum blowout** | 5.51× |
| 05 | `05-glass-avenue` | **Track X** | D · 4/4 · 76 | the album's **"quietest & most considered"** acid-folk ballad; **sus2/sus4 chords that never cadence**; brushed/restrained kit; nylon + bowed + tackpiano; only warmth builds | 3.93× |
| 06 | `06-opal` | **Opus** | D (D Phryg. dom) · 4/4→6/8 · 140 | D pedal + **D-Eb-D klezmer turn (the 7h8p7)**; **4/4 verse → 6/8 variation**; **chromatic run Eb-D-C#-C-B** climbs the band; brass/horn stabs guide form | 2.79× |
| 07 | `07-north-light` | BCNR corpus — **irregular/changing meter** | Am · 4/4 (7/8-feel) · 104 | a true **7-note violin ostinato (3+2+2) cycling against 4/4** = the polymeter never settles; density-up climax; massed stop | 7.52× |
| 08 | `08-tide-and-tired` | BCNR corpus — **"quietest & considered" extreme** | Eb · 12/8 · 72 | **12/8 cathedral ballad**; lasting suspended tones (Ebsus2→Bbsus4→Abmaj7→Cm7) that **never resolve**; choir+mellotron+saw_drone wash; brushed 12/8; only register+warmth builds | 3.61× |
| 09 | `09-wire-house` | BCNR corpus — **free-jazz/klezmer stop-start** | C (C Phryg. dom) · 4/4 · 128 | C-Db-C klezmer turn; **abrupt CUTS** to near-silence then re-entry (Sunglasses/Science Fair spirit); brass stabs; fuzz improv interludes; tritone-ish C→Db blowout | 6.71× |
| 10 | `10-salt-cathedral` | BCNR corpus — **post-rock crescendo + Opus finale** | Em · 4/4 · 96→130 (accel) | through-composed **cathedral swell** (mellotron+saw_drone+brass wall by orchestration); **false stop**; final **Opus-style klezmer run** as the tempo has accelerated to 130 | 5.23× |

All tracks ≤ 2:49. All peak ≤ 0.94 (no clipping). Each `.py` is **self-contained** (the
engine is inlined — numpy + scipy only) and writes both `NN-name.mp3` and
`NN-name-instrumental.mp3` directly.

## How the drums were written (Nick Villa)

- **Even 16th-note hi-hats** locked to the grid, quietly (edge hats on the downbeats,
  tip hats on the offbeats), **accents on the off-16ths** ("e & a"), never speeding up.
- **Kick = a melody against the grid**: it lands on **off-16ths and leaves some downbeats
  empty** (busy/climax variants add off-16th kicks).
- **Snare backbeat + ghost notes** on the in-between 16ths; double sticks via the kit's
  `flam`/ghost articulations.
- **Ride bell + tom rolls + claps** join only at the climaxes; **cross-stick/brushes** on
  the quiet 12/8/acid-folk tracks.
- **Fills into "two-and" (2.5)** (the Villa move) and `burst32`/`stutter`/`tom` fills crash
  into the next section.
- The whole kit is **humanized** by `Performer` (systematic offsets + Gaussian timing +
  accent patterns + 6-mic bleed → `mix_kit`).

## Rebuild

```bash
# regenerate any song (self-contained, writes .wav then we -> .mp3)
./_build.sh body_NN.py NN-name   # concatenates _eng.txt + body_NN.py and renders
```

Sound source / engine: `_eng.txt` (the palette of `20franticchoir.py`).