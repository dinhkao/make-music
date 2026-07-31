# Sundial 🕰️

Bài nhạc synth-pop đầu tiên của dự án — **inspired by "Killing Time" – Magdalena Bay** (album *Imaginal Disk*, 2024).

**File nghe:** `sundial.mp3` (2:59, 192kbps) · `sundial.wav` (lossless)

## Bài hát mô phỏng gì từ Killing Time?

| Chi tiết Killing Time | Sundial làm |
|---|---|
| Verse dùng hợp âm thiếu bậc 3 (I + V no3) | Fmaj7 đủ + C(no3) mở |
| Bridge dùng viio/iii → I7 | G#dim → A7 → Dm7 → C7 |
| Melody stepwise, diatonic, syncopation nhẹ | Lead synth "giọng hát" đi nốt liền kề, gam F major |
| Lounge mở đầu → guitar solo psychedelic đỉnh cao | Intro piano điện êm → solo synth "guitar" pentatonic |
| Spoken word chants | Giọng Whisper (Mac `say`) pitch xuống 0.82×, reverb + delay |
| Trống live out-front | Kick/snare/hat tổng hợp, humanize ±4ms |
| 120 BPM, 4/4 | 120 BPM, 4/4 |
| Production "film grain" | Vinyl crackle bed khắp bài, đoạn giữa lọc radio 2.4kHz |

## Cấu trúc bài (88 ô nhịp)

```
0:00  Intro        lounge — EP Rhodes + bass + kick nhẹ + crackle vinyl
0:16  Verse 1      lead melody vào (F4 → C5, stepwise)
0:48  Verse 2      biến tấu, giữ minimal
1:20  Pre-chorus   Dm7 → Bbmaj7 → C7, strings nổi lên
1:36  Chorus 1     full band: kick 4-floor, strings, harmony
2:08  Chorus 2     + lớp harmony (quãng 5) — "vocal layering"
2:40  Verse B      lọc radio 2.4kHz, mơ màng
3:12  Bridge       G#dim drama, melody vút lên A5, whisper bắt đầu
3:44  Solo         synth "guitar" pentatonic random-walk + snare roll
4:16  Outro        choir "ah" + arpeggio EP + spoken word, fade
```

*Ghi chú: thời gian ở bảng là từ code (1 bar = 2.0s @ 120 BPM).*

## Lời (spoken word trong bài — giọng Whisper)

> "Tick. Tock. The clock has a tongue, but no teeth.
> It only bites you when you stop watching.
> I'm killing time. But time... is killing me.
> When the sun stands still, it's still moving.
> Sundial dream."

## Gợi ý lời hát (nếu bạn muốn hát lên sau này)

Verse:
```
The sun leans low, the minutes crawl,
I count the cracks along the wall.
Nothing starts and nothing ends,
Killing time with my best friend.
```

Chorus:
```
Sundial dream, the shadow spins,
Round and round where time begins.
Hold the hour, let it pass —
Sand is falling through the glass.
```

## Chạy lại từ đầu

```bash
python3 build.py          # render sundial.wav
ffmpeg -i sundial.wav -codec:a libmp3lame -b:a 192k sundial.mp3
```

Cần: Python 3 + numpy, macOS `say` (giọng Whisper), ffmpeg.

## Công thức âm thanh

- **Hợp âm**: Fmaj7 [F3 A3 C4 E4], C(no3) [C3 G3], Dm7, Bbmaj7, C7, A7 (C# borrowed), G#dim
- **Nhạc cụ**: Rhodes FM-additive, bass sine+tanh, strings detuned saw + lowpass, lead saw+LP+vibrato, solo saw+drive, choir formant (750/1150/2600Hz)
- **Trống**: kick sweep 120→45Hz, snare body+noise, hat noise HP 7kHz
- **Hiệu ứng**: reverb convolution (noise IR), delay dotted-8th, crackle vinyl, master tanh soft-clip

---

# 🍯 HONEY STATIC (bài thứ 2 — 2:25)

**File:** `honey-static.mp3` · `honey-static.wav`
**Ý tưởng:** nhạc pop catchy + quirky — áp dụng mọi thứ học được từ research Magdalena Bay + Nick Villa.

## Bài này học được gì từ ai?

| Chi tiết | Nguồn |
|---|---|
| Hợp âm mượn **F#7** trong verse (C → F#7 → Cmaj7 → G7) | Killing Time (tab UG) |
| **Kick syncopated** + **snare ghost notes** đặt gần kick | Nick Villa tutorial Death & Romance |
| **Hi-hat 16th xuyên suốt** ("lock vào grid") | Nick Villa tutorial |
| **Ride bell** pattern trong chorus | Nick Villa tutorial |
| Fill trống vào **"two and"** (beat 2.5) trước chorus | Nick Villa tutorial |
| **Double-kick fill** ở chorus2 | Nick Villa (Iron Cobra) |
| Bridge đổi nhịp **6/8** lắc lư | Killing Time (bass tab 6/8) |
| Hợp âm 7ths/9ths + melody stepwise diatonic | Imaginal Disk analysis |
| Whisper pitch-down + reverb | (giọng Mac Whisper) |
| Vinyl crackle, TV beep intro, **glitch stutter** outro | quirk riêng của bài |

## Cấu trúc (112 BPM, C major)

```
0:00  Intro lounge (TV beep + crackle)
0:17  Verse — melody vào, kick syncopated + ghost notes
0:34  Pre — strings nổi, snare fill "two and"
0:43  Chorus — HOOK "Honey static" ×2, ride bell, octave shimmer
1:00  Verse 2
1:17  Pre + fill
1:26  Chorus 2 — harmony quãng 3 + double-kick fill
1:43  Bridge 6/8 — gam tăng dần C→A, whisper "Tick-tock..."
1:56  Chorus 3 (tag) — choir + hook cuối
2:04  Outro — choir + arp + whisper "Goodnight, television" + glitch
```

## Lời (gợi ý hát lên)

```
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
```

## Chạy lại
```bash
python3 honey_build.py
ffmpeg -i honey-static.wav -codec:a libmp3lame -b:a 192k honey-static.mp3
```

---

# ⚡ STATIC SUPERNOVA (bài thứ 3 — 2:21)

**File:** `static-supernova.mp3` · `static-supernova.wav`
**Ý tưởng:** indie anthem học từ **"She's Electric" của Oasis** (phân tích MIDI thật).

## Học được gì từ MIDI She's Electric?

| Phát hiện từ MIDI | Áp dụng vào Static Supernova |
|---|---|
| Key **E major**, 127 BPM, 4/4 | E major, 126 BPM |
| **Swing mạnh 2:1** (strum dài 2/3 + ngắn 1/3) | Mọi strum/hat/tamb đều swing |
| Vòng **E ↔ A** (I-IV) — chiêu Oasis | Verse E-A, chorus A-E-B-C#m |
| Intro **F# ring** (C#+F# vang) | Intro 4 bar F# |
| Guitar acoustic strum dày | **Karplus-Strong** guitar tổng hợp, strum 5 dây lệch 8ms |
| Nốt vang dài | EP pad ring mỗi bar |

## Cấu trúc (2:21)
```
0:00  Intro — F# ring + tambourine swing
0:08  Verse — E-A bop, swing strum + melody
0:23  Pre — A-E-B-C#m leo lên
0:30  CHORUS — hook "Static supernova" + handclaps + strings
0:46  Verse 2
1:01  Pre
1:09  CHORUS 2 — harmony quãng 3
1:24  Bridge — F#m-C#m-A-B (middle 8)
1:31  GUITAR SOLO — KS pentatonic, đỉnh cao bài ⚡
1:39  CHORUS 3 — bùng nổ cuối
1:54  Outro — "la la" choir + strum, fade
```

## Hook chính
```
"Sta-tic su-per-no-va" = E5 E5 D#5 C#5 B4 — đi xuống từ nốt cao
"in my head" = A4 (giữ) B4 C#5
"va!" = E5 giữ 3 phách — nốt singalong
```

## Lời
```
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
```

## Chạy lại
```bash
python3 supernova_build.py
ffmpeg -i static-supernova.wav -codec:a libmp3lame -b:a 192k static-supernova.mp3
```

---

# 🏠 THE GREAT INDOORS (bài thứ 4 — 2:44)

**File:** `THE-GREAT-INDOORS.mp3` · `THE-GREAT-INDOORS-v2.wav`
**Engine:** gi_engine.py (tempo map 118→119 BPM, Karplus-Strong, Wurli FM, vocal formant, horns) + kit.py (modal synthesis trống: Bessel membrane modes, snare wire buzz, hi-hat 2-cymbal) + perform.py (nhân hóa: systematic offsets + Gauss jitter, accent patterns, micro/bleed model 5 mic ảo).

## Cấu trúc (312 beat, 4/4)
```
0:00  INTRO — Wurli lounge + cross-stick đếm
0:08  VERSE 1 — jangle arp + bass root + vocal (breath)
0:24  REFRAIN 1 — strum + bass walk + vocal + harmony thấp 1 quãng 8
0:41  VERSE 2 — + crunch guitar + organ
0:57  REFRAIN 2 — bass 8ths + gang vocal
1:13  BRIDGE — giữ 1 nốt G#4/E4, hòa âm trượt nửa cung
1:29  RAMP — vòng quãng 5 (F#7-B7-E7-A7) + gang
1:37  CUT — gần như im lặng + stutter fill kiểu Villa
1:41  OUTRO 1 — disco + hi-hat mở bị bóp (choke)
1:58  OUTRO 2 — + horn section + gang vocal 6 giọng
2:14  OUTRO 3 — MAX + guitar solo (bend) + horn octave
2:30  TAG — Wurli cô đơn, dừng trên Amaj7 (V — không giải quyết)
```

## Trống (drums_new.npy — script riêng)
- INTRO: cross-stick ×4 + snare fill
- VERSE: cross-stick, kick syncopated, hat 8th, foot-hat 2&4
- REFRAIN: snare center + tambourine Motown + open-hat choke
- VERSE 2: ride + bell + ghost notes
- REFRAIN 2: backbeat ghép snare+clap+tamb (0/+4/+9ms) + hat 16th
- BRIDGE: chỉ tom floor (tune 168→92) — "cả bàn cùng đánh accent"
- RAMP: mật độ 8→8→16→32 + snare roll 32
- CUT: cross-stick + foot-hat + stutter 3 beat
- OUTRO: disco kick elec + hi-hat mở bị bóp mọi phách lẻ + crash + ride bell
- TAG: chỉ 1 cross-stick cuối

## Chạy lại
```bash
python3 great-indoors-drums.py   # -> drums_new.npy
python3 great-indoors.py         # -> THE-GREAT-INDOORS-v2.wav
ffmpeg -i THE-GREAT-INDOORS-v2.wav -codec:a libmp3lame -b:a 192k THE-GREAT-INDOORS.mp3
```

---

# 🎹 THE GREAT INDOORS — VÒNG HỢP ÂM (3:12)

**File:** `THE-GREAT-INDOORS-VONG-HOP-AM.mp3` · `.wav`
Render bằng **engine magbay loop** (render.py): pad saw detuned 3 lớp + sub bass + pluck FM arpeggio + chorus L/R + tape wobble + reverb.

7 vòng hợp âm của bài, mỗi vòng chơi **2 lần** (loop ×2), nối nhau 1s im lặng:

```
0:00  INTRO   Amaj7 · C#7 · Dmaj7 · D#dim7
0:19  VERSE   Amaj7 C#7 Dmaj7 D#dim7 A/E F#7 Bm7 E7sus4
0:54  REFRAIN Dmaj7 A/C# Bm7 E7sus4 ×2
1:29  BRIDGE  G# Amaj7 G# Amaj7 C Dmaj7 C Dmaj7
2:04  RAMP    F#7 B7 E7 A7
2:23  OUTRO   D Dmaj7 G Gmaj7 Bm Bm/A G A
2:58  TAG     Amaj7 (V — không giải quyết) 🎯
```

MIDI gốc trong `tgi-loops/*.mid`, WAV từng vòng trong `tgi-loops/*.wav`.
Tạo lại: `python3 tgi-loops.py`
