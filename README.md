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
