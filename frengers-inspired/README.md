# Frengers-inspired — 10 bài theo Mew (Frengers, 2003) + trống Nick Villa

Một album 10 bài tự viết, mô phỏng **từng bài một** trong *Frengers* của Mew —
không sample, không AI sinh audio: mọi âm thanh đều tính ra từ code
(engine + body, numpy/scipy thuần).

## Vì sao viết như vậy

Quy tắc của dự án: **cách duy nhất để output hay là làm đúng như nghệ sĩ làm**.
Mỗi bài = skeleton của 1 track Frengers (progression, cấu trúc, bass line,
melody contour — đo đạc trực tiếp từ stem tách bằng Demucs + đối chiếu
Hooktheory/Songsterr/CifraClub), transpose sang tông khác, phối lại bằng nhạc cụ
của engine, trống viết theo **Nick Villa** (Magdalena Bay, Imaginal Disk):
offbeat-8th pulse, phrase-based fills, kick hỗ trợ bass, dynamic contrast,
climax 16th barrage.

Chi tiết nghiên cứu: `REF-NOTES.md`. Bảng so khớp số đo với bản gốc ở cuối file này.

## 10 bài

| # | Bài | Model (Frengers) | Tông | BPM | Điểm nhấn |
|---|---|---|---|---|---|
| 1 | Glass Over the Harbor | Am I Wry? No | F | 128 | riff xuống + outro lặp lời, bass bơm 8ths |
| 2 | From the Bedroom Window | 156 | E (C#m-A-E-B) | 130 | bass 8ths octave-jump, drive đều |
| 3 | Snowflakes in July | Snow Brigade | Am | 123 | chant "I will find you in the snow" ×8 |
| 4 | Mirror of the Mind | Symmetry | Eb | 61 | chậm mơ, wurli+strings, rim shots |
| 5 | Behind the Curtain | Behind the Drapes | G | 96 | march, ride bell, ghost snare |
| 6 | A Voice Beyond the Years | Her Voice Is Beyond Her Years | Eb | 136 | ngắn dồn dập, bass riff C3-Bb2 |
| 7 | Seven Flew Over the Rooftops | Eight Flew Over, One Was Destroyed | Bm | 129 | pedal drone B1 tối, climax 16ths |
| 8 | She Came Home in Winter | She Came Home for Christmas | F# | 136 | gentle, glock, pedal C#2, rim shots |
| 9 | She Spins in the Moonlight | She Spider | D | 74 | half-time spacious, tackpiano, F#/Bb |
| 10 | Comforting Noise | Comforting Sounds | A | 80 | crescendo 12x, bass vào muộn, không trống đầu |

## Build

```bash
./_build.sh body_01.py 01-glass-over-the-harbor
```
→ viết `NN-ten-bai.py` (engine+body), render WAV vocal + instrumental, encode MP3 192k, xoá WAV.

QC số: `python3 qc.py *.mp3` (peak, RMS, corrLR, năng lượng 8-16k).

## Nhạc cụ (engine.py trong `_eng.txt`)

Jangle/crunch/airlead/glassarp/ebow (guitar Mew, double-track L/R), strings/glock
(mới cho album này), wurli/organ/tackpiano/mellotron (keys), bassn/fingerbass/
fuzzbass/subbass, giọng falsetto (say/line), Kit+Performer trống (Nick Villa
humanised) — tất cả tổng hợp thuần, không mẫu.

## Đo đạc so với bản gốc (corrLR / năng lượng 8-16k)

| Bài | Ta | Bản gốc |
|---|---|---|
| 01 | 0.60 / 1.03% | 0.46 / 0.86% |
| 02 | 0.59 / 0.52% | 0.58 / 0.62% |
| 03 | 0.52 / 0.55% | 0.52 / 0.88% |
| 04 | 0.66 / 0.60% | 0.51 / 0.63% |
| 05 | 0.51 / 0.59% | 0.47 / 0.54% |
| 06 | 0.50 / 0.84% | 0.55 / 0.46% |
| 07 | 0.74 / 0.55% | 0.61 / 0.42% |
| 08 | 0.66 / 0.63% | 0.50 / 0.67% |
| 09 | 0.72 / 0.33% | — |
| 10 | 0.70 / 0.44% | 0.56 / 0.50% |

Mọi bài ≤ 4:00. `ref/` chứa audio gốc tải về để phân tích (4.8GB, đã gitignore — xoá được).
