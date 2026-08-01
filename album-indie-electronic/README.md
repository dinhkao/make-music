# 🎧 Album indie-electronic (04 → 13)

10 bài, mỗi bài **1 file `.py` tự chứa** (chỉ cần `numpy` + `scipy`, không đọc file ngoài).
Mỗi file render ra **bản có giọng** + **bản instrumental**.

```bash
python3 04-plastic-halo.py              # cả hai bản .wav
python3 04-plastic-halo.py --vocals     # chỉ bản hát
python3 04-plastic-halo.py --no-vocals  # chỉ instrumental
ffmpeg -i 04-plastic-halo.wav -codec:a libmp3lame -b:a 192k 04-plastic-halo.mp3
```

File `.wav` không được commit (698MB) — chạy lại `.py` để tạo. `.mp3` 192kbps có sẵn ở đây.

## Danh sách

| # | Bài | Giọng · Nhịp · BPM | Dài | Chiêu nhạc lý chính | "Khúc gãy" giữa bài |
|---|---|---|---|---|---|
| 04 | [plastic-halo](04-plastic-halo.mp3) | Em · 4/4 · 122 | 3:23 | Vòng Andalusia i–VII–VI–V; **giai điệu đứng im ở B4** trong khi hợp âm trượt xuống ⇒ cùng một nốt lần lượt là 5–6–M7–1 | BRK mượn **A trưởng** (E dorian), bỏ kick |
| 05 | [supermarket-saints](05-supermarket-saints.mp3) | D · 4/4 · 108 | 3:32 | Chorus vi–I–V–**II trưởng**; hợp âm **đẩy sớm nửa phách**; verse không có snare | BRIDGE G–F–C–G (bVII), chỉ tom + shaker |
| 06 | [cassette-angel](06-cassette-angel.mp3) | C → **Eb** · 4/4 · 115 | 3:28 | Hòa âm chậm 2 ô/hợp âm, snare gate phách 3, chorus mở trên **bậc 9** | Chorus cuối **chuyển giọng lên Eb** |
| 07 | [motorik-lavender](07-motorik-lavender.mp3) | A · **4/4 + 7/8** · 132 | 3:15 | Imaj7–III7–vi9–ii7 kiểu lounge; **mỗi 8 ô có 1 ô 7/8**; tiến triển bằng chồng lớp, trống không đổi | BRIDGE maj7 trượt nửa cung (planing) |
| 08 | [the-glitter-is-a-lie](08-the-glitter-is-a-lie.mp3) | F#m · 4/4 · 134 | 3:19 | i–III–VI–iv, giai điệu đâm vào bậc 9/11, chorus là **chant đội cổ vũ** | **DROP**: tắt hết, còn kick + chant + tiếng rít |
| 09 | [teeth-in-the-swimming-pool](09-teeth-in-the-swimming-pool.mp3) | Ab · 4/4 · 120 | 3:51 | **Chord-bass melody**: giữ chùm Ab, bass đi xuống Ab–G–F–Eb; chorus có **Cbmaj7** | **WARP**: tape stop → nửa nhịp → bật lại |
| 10 | [slow-motion-crush](10-slow-motion-crush.mp3) | Bm · 4/4 · 116 | 3:30 | **Bassline là hook**; chorus mượn **E trưởng** (IV từ B dorian) | **FLIP**: trống nửa nhịp, bass giữ nguyên câu |
| 11 | [television-daughter](11-television-daughter.mp3) | Fm · 4/4 · 96 | 3:34 | i–VI–III–VII6 chậm, pre chèn **viio (Edim7)**; chorus to bằng mật độ chứ không bằng âm lượng | **HOLLOW**: 8 ô **không có trống** |
| 12 | [neon-cathedral](12-neon-cathedral.mp3) | E · 4/4 · 128 | 3:22 | Jangle I–V–ii–IV; chorus có **C trưởng = bVI mượn**; hook là **một nốt B5 giữ dài** đổi màu theo hợp âm | **CHIME**: không trống, chỉ guitar 12 dây vang |
| 13 | [two-suns-no-shadow](13-two-suns-no-shadow.mp3) | C#m → E · **5/4 → 4/4 → 6/4** · 100 | 3:15 | Verse 5/4 (3+2) ở Do# thứ, chorus 4/4 bùng sang **Mi trưởng**, bridge 6/4 | Kết **treo trên B (V)**, không giải quyết |

Bản instrumental: cùng tên + hậu tố `-instrumental.mp3`.

## Nghiên cứu trước khi viết

| Bài gốc | Dữ liệu lấy được | Dùng cho |
|---|---|---|
| Ladytron – *Destroy Everything You Touch* / *Seventeen* | Em 120bpm, Em–D–C–B; giọng deadpan một cao độ | 04 |
| MGMT – *Time to Pretend* / *Electric Feel* | D→F#m, D–G–A–F#m; vòng lặp thôi miên i–v–VI–VII; tom + shaker | 05 |
| Sky Ferreira – *Everything Is Embarrassing* | C 115bpm, C–Am7–F–G; beat R&B 80s mờ, bass gảy ngón, piano lẻ loi | 06 |
| Stereolab | motorik krautrock + hợp âm lounge maj7/min9, nhịp lẻ, organ Farfisa | 07 |
| Grimes – *Kill V. Maim* / *Oblivion* | Bm ~134bpm i–III–VI–iv; "chord-melody tension" cao; arp là xương sống | 08 |
| Magdalena Bay – *Chaeri* | Ab 120bpm, cao ở Chord Complexity / Progression Novelty / **Chord-Bass Melody** | 09 |
| Tame Impala – *The Less I Know The Better* | bassline **là** hook; hợp âm trưởng mượn từ điệu thức song song | 10 |
| Broadcast / hauntology | mellotron, piano tack, trống nhỏ, tiếng đĩa than | 11 |
| Alvvays – *Archie, Marry Me* | I–V–ii–IV, guitar jangle 12 dây | 12 |

Nguồn: Hooktheory TheoryTab, Wikipedia, các bài phân tích production.
(Hooktheory chặn fetch trực tiếp — dữ liệu lấy qua bản tóm tắt tìm kiếm.)

## Nguyên tắc chống "AI slop"

- **Không loop vô tận** — mỗi bài có ít nhất một đoạn phá cấu trúc (cột "khúc gãy"),
  độ dày nhạc cụ tăng dần từ intro tới chorus cuối.
- **Giai điệu viết theo lời thật** — từng âm tiết có nguyên âm + phụ âm riêng,
  câu hát có chỗ nghỉ, nốt giữ dài cuối câu, verse 2 **khác** verse 1.
- **Nhân hoá** — mỗi âm tiết lệch vài ms (`jit`, `drag`); trống có systematic offset
  + Gauss jitter + accent pattern.
- **Trống bám hòa âm** — hòa âm chuyển chậm ⇒ trống nửa nhịp/thưa; chuyển nhanh ⇒
  trống dày; chorus đổi *loại* trống (ride / tambourine / clap), không chỉ to hơn.
- **Bass là một bè riêng** — đảo phách, nhảy quãng 8, đi bộ, slide, nốt chặn.

## Đo kiểm (không nghe được thì đo)

Cả 20 bản render: **0 mẫu bị clip**, crest factor 15–17 dB (còn động, không bị bóp),
giọng hát có mặt ở mọi bài, chênh lệch năng lượng giữa đoạn to nhất và nhỏ nhất
**2.2×–4.5×** (07 thấp nhất là cố ý — bài motorik thôi miên).

## Nhạc cụ mới thêm vào engine

`synpluck` (pluck analog, bộ lọc động) · `analead` (lead 2 osc detune + glide + vibrato trễ) ·
`gatedpad` (pad bị gate 8th/16th kiểu Ladytron) · `bell` (chuông FM) · `crackle` (đĩa than + hiss) ·
`bitcrush` · `tapestop` · `reverse_seg` · `riser` · `subdrop` · `strum` —
tất cả nằm sẵn trong mỗi file bài hát.
