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

---

# 📄 BẢN ONE-FILE: `the-great-indoors.py`

**1 file .py duy nhất, tự chứa 100%** — chạy được ở bất kỳ máy nào chỉ cần numpy + scipy:

```bash
python3 the-great-indoors.py   # -> THE-GREAT-INDOORS-v2.wav (24 giây)
```

Bên trong file (1109 dòng):
1. **Engine tempo + nhạc cụ** — tempo map 118→119, Karplus-Strong guitar, Wurli FM, organ, bass, horn, vocal formant (gi_engine)
2. **Trống modal synthesis** — Bessel membrane, snare wire buzz, hi-hat 2 cymbal (kit)
3. **Performer nhân hóa** — systematic offsets + Gauss, accent, 5 mic ảo + bleed (perform)
4. **Render FX** — reverb convolution, chorus, WAV writer
5. **Drum arrangement** — 12 đoạn, từ cross-stick tới disco choke
6. **Arrangement** — 312 beat đầy đủ + mix (ducking, carve, Fridmann squash)

Không cần file ngoài, không cần drums_new.npy — mọi thứ trong 1 file.

---

# 🎧 ALBUM INDIE-ELECTRONIC (bài 04 → 13)

📁 **Toàn bộ album nằm trong thư mục [`album-indie-electronic/`](album-indie-electronic/)**

10 bài mới, mỗi bài **1 file `.py` tự chứa** (chỉ cần numpy + scipy), render ra
**bản có giọng** + **bản instrumental**. Chạy:

```bash
cd album-indie-electronic
python3 04-plastic-halo.py              # -> .wav (cả hai bản)
python3 04-plastic-halo.py --vocals     # chỉ bản hát
python3 04-plastic-halo.py --no-vocals  # chỉ instrumental
ffmpeg -i 04-plastic-halo.wav -codec:a libmp3lame -b:a 192k 04-plastic-halo.mp3
```

## Nghiên cứu trước khi viết (nguồn thật)

| Bài gốc | Dữ liệu lấy được | Áp dụng vào bài nào |
|---|---|---|
| Ladytron – *Destroy Everything You Touch* | E minor, 120bpm, Em–D–C–B (i–VII–VI–V) | 04 |
| Ladytron – *Seventeen* | C minor, 121bpm, giọng deadpan một cao độ | 04 |
| MGMT – *Time to Pretend* | D major → F#m, D–G–A–F#m, trống tom + shaker | 05 |
| MGMT – *Electric Feel* | vòng lặp thôi miên i–v–VI–VII, mượn hợp âm song song | 05 |
| Sky Ferreira – *Everything Is Embarrassing* | C major, 115bpm, C–Am7–F–G, beat R&B 80s mờ, bass gảy ngón, piano lẻ loi | 06 |
| Stereolab | motorik krautrock + hợp âm lounge maj7/min9, **nhịp lẻ**, organ Farfisa | 07 |
| Grimes – *Kill V. Maim* | B minor, ~134bpm, i–III–VI–iv, "chord-melody tension" cao | 08 |
| Grimes – *Oblivion* | D major, 156bpm, độ phức tạp giai điệu cao, arp là xương sống | 08 |
| Magdalena Bay – *Chaeri* | Ab major, 120bpm, cao ở **Chord Complexity / Progression Novelty / Chord-Bass Melody** | 09 |
| Tame Impala – *The Less I Know The Better* | bassline **là** hook; hợp âm trưởng mượn từ điệu thức song song | 10 |
| Broadcast / hauntology | mellotron, piano tack, trống nhỏ, tiếng đĩa than | 11 |
| Alvvays – *Archie, Marry Me* | I–V–ii–IV, guitar jangle 12 dây, ~110–120bpm | 12 |

Nguồn: Hooktheory TheoryTab (Grimes, MGMT, Ladytron, Sky Ferreira, Magdalena Bay,
Alvvays, Tame Impala), Wikipedia, và các bài phân tích production.

## 10 bài

| # | Tên | Giọng / Nhịp / BPM | Chiêu nhạc lý chính | "Khúc gãy" giữa bài |
|---|---|---|---|---|
| 04 | **plastic-halo** | E minor, 4/4, 122 | Vòng Andalusia i–VII–VI–V; **giai điệu đứng im ở nốt B4** trong khi hợp âm trượt xuống ⇒ cùng một nốt lần lượt là 5–6–M7–1 | BRK: mượn **A trưởng** (E dorian), bỏ kick |
| 05 | **supermarket-saints** | D major, 4/4, 108 | Chorus vi–I–V–**II trưởng** (E); hợp âm **đẩy sớm nửa phách** trước vạch nhịp | BRIDGE G–F–C–G (bVII mixolydian), chỉ tom + shaker |
| 06 | **cassette-angel** | C major → **Eb**, 4/4, 115 | Hòa âm chậm 2 ô/hợp âm, snare gate ở phách 3; chorus bắt đầu trên **bậc 9** | Chorus cuối **chuyển giọng lên Eb** (quãng 3 thứ) |
| 07 | **motorik-lavender** | A major, **4/4 + 7/8**, 132 | Imaj7–III7–vi9–ii7 kiểu lounge; **mỗi 8 ô có 1 ô 7/8**; tiến triển bằng **chồng lớp**, trống không đổi | BRIDGE maj7 trượt nửa cung (planing) |
| 08 | **the-glitter-is-a-lie** | F# minor, 4/4, 134 | i–III–VI–iv, giai điệu đâm vào bậc 9/11; chorus là **chant đội cổ vũ** | **DROP**: tắt hết, còn kick + chant + tiếng rít |
| 09 | **teeth-in-the-swimming-pool** | Ab major, 4/4, 120 | **Chord-bass melody**: giữ nguyên chùm Ab, bass đi xuống Ab–G–F–Eb; chorus có **Cb(B)maj7** (bIII trưởng mượn) | **WARP**: tape stop → nửa nhịp → bật lại |
| 10 | **slow-motion-crush** | B minor, 4/4, 116 | **Bassline là hook**; chorus mượn **E trưởng** (IV từ B dorian), bass đi vòng quãng 5 | **FLIP**: trống nửa nhịp, bass giữ nguyên câu |
| 11 | **television-daughter** | F minor, 4/4, 96 | i–VI–III–VII6 chậm; pre chèn **viio (Edim7)**; chorus to bằng **mật độ** chứ không bằng âm lượng | **HOLLOW**: 8 ô **không có trống** |
| 12 | **neon-cathedral** | E major, 4/4, 128 | I–V–ii–IV kiểu jangle; chorus có **C trưởng = bVI mượn**; hook là **một nốt B5 giữ dài** đổi màu theo hợp âm | **CHIME**: không trống, chỉ guitar 12 dây vang |
| 13 | **two-suns-no-shadow** | C#m → E, **5/4 → 4/4 → 6/4**, 100 | Verse 5/4 (3+2) ở C# thứ, chorus 4/4 bùng sang **Mi trưởng**; bridge 6/4 | Kết **treo trên B (V)**, không giải quyết |

## Nguyên tắc chống "AI slop" áp dụng cho cả 10 bài

- **Không loop vô tận**: mỗi bài có ít nhất một đoạn *phá cấu trúc* (cột "khúc gãy"),
  và gain/độ dày nhạc cụ tăng dần theo từng đoạn (intro → chorus cuối).
- **Giai điệu viết theo lời thật** (từng âm tiết có nguyên âm + phụ âm riêng), câu hát
  có chỗ nghỉ, có nốt giữ dài cuối câu, verse 2 **khác** verse 1.
- **Nhân hoá**: `line(... jit=, drag=)` làm mỗi âm tiết lệch vài ms và hát trễ/sớm;
  `Performer` thêm systematic offset + Gauss jitter + accent pattern cho từng cú trống.
- **Trống bám hòa âm**: đoạn hòa âm chuyển chậm → trống nửa nhịp/thưa; đoạn hòa âm
  chạy nhanh → trống dày; chorus đổi *loại* trống (ride/tambourine/clap) chứ không chỉ to hơn.
- **Bass là một bè riêng**, không phải nốt gốc máy móc: có đảo phách, nhảy quãng 8,
  đi bộ, slide, nốt chặn (dead note).

## Nhạc cụ mới thêm vào thư viện (dùng chung được cho mọi bài)

`synpluck` (pluck analog, bộ lọc động) · `analead` (lead 2 osc detune + glide + vibrato trễ) ·
`gatedpad` (pad bị gate 8th/16th kiểu Ladytron) · `bell` (chuông FM) · `crackle` (đĩa than + hiss) ·
`bitcrush` · `tapestop` · `reverse_seg` · `riser` (quét bộ lọc cộng hưởng) · `subdrop` (808 rơi) ·
`strum` (rải dây lệch ms) — tất cả nằm sẵn trong mỗi file bài hát.
