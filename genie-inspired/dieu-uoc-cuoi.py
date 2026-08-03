#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 DIEU UOC CUOI (The Last Wish) - bai hat lay cam hung tu SNSD "Genie" (2009)
================================================================================

 Cam hung tu "Tell Me Your Wish (Genie)" - SNSD (Dsign Music, 2009):
   - Tempo dance-pop ~123-124 BPM, kick 4-on-floor kieu Euro-dance
   - Verse am tham (minor) -> Chorus bung sang (relative major)
   - Key change o chorus cuoi (tro choi kinh dien cua K-pop 2009)
 NHUNG khong copy: giai dieu, loi, concept deu moi.
   - SNSD: "em la genie, noi dieu uoc di" (genie phuc vu nguoi yeu)
   - Bai nay LAT NGUOC: nguoi uoc dung dieu uoc cuoi de PHONG THICH genie.

 File nay KHONG CAN CAI GI CA (pure Python stdlib).
 Chay:  python3 dieu-uoc-cuoi.py
 No se render ra 2 file MP3 (co ffmpeg/lame thi ra mp3, khong co thi ra wav):
   - dieu-uoc-cuoi.mp3              (full: band + giong hat synth)
   - dieu-uoc-cuoi-instrumental.mp3 (khong giong hat)

 Synth tu che bang tay:
   - Wavetable band-limited (saw/square) cho supersaw, bass, pad, pluck, lead
   - Trum: kick/sine-drop, snare/noise+tone, clap, hat (noise vi-phan), crash
   - GIONG HAT: formant synthesis - saw source qua 2 bo loc bandpass (F1/F2)
     theo nguyen am tieng Viet, co vibrato + glide legato. Robot hat tieng Viet!
================================================================================
"""

import math
import os
import sys
import wave
import random
import shutil
import subprocess
from array import array

# ---------------------------------------------------------------- cau hinh --
SR = 44100                 # sample rate chinh (drums, bass, mix)
VR = SR // 2               # sample rate nua (pad/supersaw/lead/vocal - toi uu toc do)
BPM = 124.0                # Genie = 123 BPM, minh 124 cho khoi giong het
BEAT = 60.0 / BPM
BAR = BEAT * 4.0
E8 = BEAT / 2.0            # mot note tam (eighth)
TOTAL_BARS = 86
TOTAL_S = TOTAL_BARS * BAR + 2.0
TOTAL_N = int(TOTAL_S * SR)

random.seed(19937)         # co dinh de moi lan chay giong nhau

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------- note & tan so --
MTF = [440.0 * (2.0 ** ((m - 69) / 12.0)) for m in range(128)]   # midi -> Hz

# bang ten note (chi de doc/ghi chu, data ben duoi dung so midi luon)
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def mname(m):
    return NOTE_NAMES[m % 12] + str(m // 12 - 1)


# ---------------------------------------------------------- wavetable synth --
T = 2048  # kich thuoc wavetable


def build_saw(harm):
    """Saw band-limited: cong don harmonic toi Nyquist de khong bi aliasing."""
    t = [0.0] * (T + 1)
    for i in range(T):
        ph = i / T
        x = 0.0
        for k in range(1, harm + 1):
            x += math.sin(2.0 * math.pi * k * ph) / k
        t[i] = x * (-2.0 / math.pi)
    t[T] = t[0]
    return t


def build_square(harm):
    t = [0.0] * (T + 1)
    k = 1
    while k <= harm:
        for i in range(T):
            t[i] += math.sin(2.0 * math.pi * k * i / T) / k
        k += 2
    for i in range(T + 1):
        t[i] *= 4.0 / math.pi
    t[T] = t[0]
    return t


print("[*] Dang xay wavetable (saw band-limited, square)...")
SAW = build_saw(16)        # cho bass/supersaw/lead (tan so thap-trung)
SAW12 = build_saw(12)      # cho vocal source (mem, khong alias o cao do cao)
SQR = build_square(13)
VB = [2.0 ** (26.0 * math.sin(2.0 * math.pi * k / 4096.0) / 1200.0) for k in range(4096)]  # bang vibrato +-26 cents


def lp_coef(cut, sr):
    return 1.0 - math.exp(-2.0 * math.pi * cut / sr)


# ------------------------------------------------------------ sidechain duck --
BAR_H = int(BAR * VR)
DUCK_H = []
_beatn_h = int(BEAT * VR)
for _i in range(BAR_H):
    _t = (_i % _beatn_h) / VR
    DUCK_H.append(1.0 - 0.55 * math.exp(-_t * 26.0))


# ===================================================================  TRUM  ==
def gen_kick(gain):
    n = int(0.40 * SR)
    b = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = 46.0 + 118.0 * math.exp(-t * 34.0)     # pitch drop 164 -> 46 Hz
        ph += 2.0 * math.pi * f / SR
        env = math.exp(-t * 10.5)
        click = 0.0
        if t < 0.012:
            click = (random.random() * 2.0 - 1.0) * math.exp(-t * 900.0) * 0.4
        b[i] = (math.sin(ph) * env + click) * gain
    return b


def gen_snare(gain):
    n = int(0.24 * SR)
    b = [0.0] * n
    prev = 0.0
    ph = 0.0
    for i in range(n):
        t = i / SR
        nz = random.random() * 2.0 - 1.0
        hp = nz - prev
        prev = nz
        ph += 2.0 * math.pi * 185.0 / SR
        tone = math.sin(ph) * math.exp(-t * 30.0)
        b[i] = (hp * 0.5 + tone * 0.5) * math.exp(-t * 22.0) * gain
    return b


def gen_clap(gain):
    n = int(0.30 * SR)
    b = [0.0] * n
    bursts = (0.0, 0.011, 0.023)
    for i in range(n):
        t = i / SR
        amp = 0.0
        for bt in bursts:
            if t >= bt:
                amp += math.exp(-(t - bt) * 60.0)
        amp += math.exp(-t * 9.0) * 0.6
        b[i] = (random.random() * 2.0 - 1.0) * amp
    p = 0.0
    a = 0.06
    for i in range(n):                              # highpass ~530 Hz
        v = b[i]
        p += a * (v - p)
        b[i] = (v - p) * gain
    return b


def gen_hat(dur, decay, gain):
    n = int(dur * SR)
    b = [0.0] * n
    prev = 0.0
    for i in range(n):
        t = i / SR
        nz = random.random() * 2.0 - 1.0
        v = nz - prev                               # vi-phan = highpass kim loai
        prev = nz
        b[i] = v * math.exp(-t * decay) * gain
    return b


def gen_crash(gain):
    n = int(1.5 * SR)
    b = [0.0] * n
    prev = 0.0
    for i in range(n):
        t = i / SR
        nz = random.random() * 2.0 - 1.0
        v = nz - prev
        prev = nz
        b[i] = v * math.exp(-t * 3.2) * gain
    return b


def gen_riser(gain):
    n = int(BAR * SR)
    b = [0.0] * n
    p = 0.0
    ph = 0.0
    for i in range(n):
        t = i / SR
        r = t / BAR
        nz = random.random() * 2.0 - 1.0
        p += (0.02 + 0.5 * r) * (nz - p)            # mo lowpass dan
        ph += 2.0 * math.pi * 220.0 * (2.0 ** (2.0 * r)) / SR
        saw = 2.0 * ((ph / (2.0 * math.pi)) % 1.0) - 1.0
        b[i] = (p * 0.7 + saw * 0.18) * r * gain
    return b


def gen_subdrop(gain):
    n = int(0.7 * SR)
    b = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        ph += 2.0 * math.pi * (32.0 + 45.0 * math.exp(-t * 3.0)) / SR
        b[i] = math.sin(ph) * math.exp(-t * 4.0) * gain
    return b


# ====================================================  NHAC CU (half-rate)  ==
SAWCACHE = {}
PADCACHE = {}
STABCACHE = {}
PLUCKCACHE = {}
LEADCACHE = {}
BASSCACHE = {}


def gen_saw_chord(midis, n2, cut, duck):
    """Supersaw: moi note 3 osc saw detune, qua lowpass, optional duck sidechain."""
    key = (tuple(midis), n2, duck)
    if key in SAWCACHE:
        return SAWCACHE[key]
    b = [0.0] * n2
    for m in midis:
        f0 = MTF[m]
        for dc in (-11.0, 0.0, 11.0):
            inc = f0 * (2.0 ** (dc / 1200.0)) * T / VR
            ph = float((m * 71 + int(dc) * 13) % T)
            for i in range(n2):
                ph += inc
                if ph >= T:
                    ph -= T
                ip = int(ph)
                fr = ph - ip
                b[i] += SAW[ip] + (SAW[ip + 1] - SAW[ip]) * fr
    na = int(0.008 * VR)
    nr = int(0.10 * VR)
    rs = n2 - nr
    a = lp_coef(cut, VR)
    y = 0.0
    g = 0.30 / 3.0
    dk = DUCK_H if duck else None
    for i in range(n2):
        y += a * (b[i] - y)
        e = 1.0
        if i < na:
            e = i / na
        elif i >= rs:
            e = (n2 - i) / nr
        if dk is not None:
            e *= dk[i] if i < BAR_H else 1.0
        b[i] = y * e * g
    SAWCACHE[key] = b
    return b


def gen_pad(midis, n2, cut, atk):
    """Pad am: 2 saw detune nhe, attack cham."""
    key = (tuple(midis), n2, atk)
    if key in PADCACHE:
        return PADCACHE[key]
    b = [0.0] * n2
    for m in midis:
        f0 = MTF[m]
        for dc in (-6.0, 6.0):
            inc = f0 * (2.0 ** (dc / 1200.0)) * T / VR
            ph = float((m * 37 + int(dc) * 7) % T)
            for i in range(n2):
                ph += inc
                if ph >= T:
                    ph -= T
                ip = int(ph)
                fr = ph - ip
                b[i] += SAW[ip] + (SAW[ip + 1] - SAW[ip]) * fr
    na = int(atk * VR)
    nr = int(0.4 * VR)
    rs = n2 - nr
    a = lp_coef(cut, VR)
    y = 0.0
    g = 0.16 / 3.0
    for i in range(n2):
        y += a * (b[i] - y)
        e = 1.0
        if i < na:
            e = i / na
        elif i >= rs:
            e = (n2 - i) / nr
        b[i] = y * e * g
    PADCACHE[key] = b
    return b


def gen_stab(midis):
    """Brass stab ngan kieu synth K-pop (hook tra loi)."""
    key = tuple(midis)
    if key in STABCACHE:
        return STABCACHE[key]
    n2 = int(0.15 * VR)
    b = [0.0] * n2
    for m in midis:
        f0 = MTF[m]
        for dc in (-9.0, 0.0, 9.0):
            inc = f0 * (2.0 ** (dc / 1200.0)) * T / VR
            ph = float((m * 53 + int(dc) * 11) % T)
            for i in range(n2):
                ph += inc
                if ph >= T:
                    ph -= T
                ip = int(ph)
                fr = ph - ip
                b[i] += SAW[ip] + (SAW[ip + 1] - SAW[ip]) * fr
    a = lp_coef(3400.0, VR)
    y = 0.0
    dec = 0.05 * VR
    g = 0.22 / 3.0
    for i in range(n2):
        y += a * (b[i] - y)
        b[i] = y * math.exp(-i / dec) * g
    STABCACHE[key] = b
    return b


def gen_pluck(m):
    if m in PLUCKCACHE:
        return PLUCKCACHE[m]
    n2 = int(0.35 * VR)
    b = [0.0] * n2
    inc = MTF[m] * T / VR
    ph = 0.0
    for i in range(n2):
        ph += inc
        if ph >= T:
            ph -= T
        ip = int(ph)
        fr = ph - ip
        b[i] = SAW[ip] + (SAW[ip + 1] - SAW[ip]) * fr
    a = lp_coef(3000.0, VR)
    y = 0.0
    dec = 0.09 * VR
    for i in range(n2):
        y += a * (b[i] - y)
        b[i] = y * math.exp(-i / dec) * 0.30
    PLUCKCACHE[m] = b
    return b


def gen_lead(m, n2):
    """Lead hook: square + vibrato nhe, cho phan post-chorus."""
    key = (m, n2)
    if key in LEADCACHE:
        return LEADCACHE[key]
    b = [0.0] * n2
    f0 = MTF[m]
    lfo = 0.0
    lfo_inc = 5.2 * 4096.0 / VR
    ph = 0.0
    for i in range(n2):
        lfo += lfo_inc
        inc = f0 * VB[int(lfo) & 4095] * T / VR
        ph += inc
        if ph >= T:
            ph -= T
        ip = int(ph)
        fr = ph - ip
        b[i] = SQR[ip] + (SQR[ip + 1] - SQR[ip]) * fr
    na = int(0.02 * VR)
    nr = int(0.08 * VR)
    rs = n2 - nr
    a = lp_coef(3600.0, VR)
    y = 0.0
    for i in range(n2):
        y += a * (b[i] - y)
        e = 1.0
        if i < na:
            e = i / na
        elif i >= rs:
            e = (n2 - i) / nr
        b[i] = y * e * 0.26
    LEADCACHE[key] = b
    return b


def gen_bass_bar(root):
    """Bass dance: 8 note tam, root + octave xen ke, note cuoi = quint."""
    if root in BASSCACHE:
        return BASSCACHE[root]
    n = int(BAR * SR) + int(0.05 * SR)
    b = [0.0] * n
    e8 = int(E8 * SR)
    rel = int(0.03 * SR)
    for k in range(8):
        m = root + (12 if k % 2 == 1 else 0)
        if k == 7:
            m = root + 7
        f = MTF[m]
        inc = f * T / SR
        st = k * e8
        ln = int(e8 * 0.92)
        ph = 0.0
        ph2 = 0.0
        inc2 = 2.0 * math.pi * f / (2.0 * SR)
        for j in range(ln):
            ph += inc
            if ph >= T:
                ph -= T
            ip = int(ph)
            fr = ph - ip
            s = SAW[ip] + (SAW[ip + 1] - SAW[ip]) * fr
            ph2 += inc2
            s += math.sin(ph2) * 0.7
            e = 1.0
            if j < 40:
                e = j / 40.0
            elif j > ln - rel:
                e = (ln - j) / rel
            b[st + j] += s * e
    a = lp_coef(750.0, SR)
    y = 0.0
    for i in range(n):
        y += a * (b[i] - y)
        b[i] = y * 0.42
    BASSCACHE[root] = b
    return b


# ====================================================  GIONG HAT FORMANT  ==
# ban do nguyen am tieng Viet (bo dau) -> formant F1/F2 (Hz)
FORMANTS = {
    "a": (850, 1220), "ă": (780, 1180), "â": (560, 1120),
    "e": (430, 2050), "ê": (450, 2150),
    "i": (290, 2280), "o": (560, 950), "ô": (440, 880),
    "ơ": (520, 1300), "u": (340, 820), "ư": (430, 1150), "y": (290, 2200),
}
_VSTR = "aàáảãạ|ăằắẳẵặ|âầấẩẫậ|eèéẻẽẹ|êềếểễệ|iìíỉĩị|oòóỏõọ|ôồốổỗộ|ơờớởỡợ|uùúủũụ|ưừứửữự|yỳýỷỹỵ"
VOWEL_MAP = {}
for _grp in _VSTR.split("|"):
    for _ch in _grp:
        VOWEL_MAP[_ch] = _grp[0]
# uu tien: nguyen am chinh cua van (khong phai i/y cuoi nhu "khoi", "thoi")
VOWEL_PRIORITY = ["ơ", "ê", "â", "ô", "ă", "a", "ư", "e", "o", "u", "i", "y"]


def vowel_of(syl):
    found = set()
    for ch in syl.lower():
        v = VOWEL_MAP.get(ch)
        if v:
            found.add(v)
    for v in VOWEL_PRIORITY:
        if v in found:
            return v
    return "a"


def biquad_bp(f, q, sr):
    """Bandpass biquad, 0 dB peak (RBJ: b0 = sin(w0)/2)."""
    w0 = 2.0 * math.pi * f / sr
    cw = math.cos(w0)
    sw = math.sin(w0)
    al = sw / (2.0 * q)
    a0 = 1.0 + al
    return (sw * 0.5 / a0, -2.0 * cw / a0, (1.0 - al) / a0)


def gen_vocal(m, dur, vowel, f_prev):
    """Hat: saw source + vibrato + glide, qua 2 formant bandpass F1/F2."""
    n2 = int(dur * VR)
    if n2 < 8:
        return [0.0] * 8
    f0 = MTF[m]
    f1, f2 = FORMANTS[vowel]
    b0a, a1a, a2a = biquad_bp(f1, f1 / 90.0, VR)
    b0b, a1b, a2b = biquad_bp(f2, f2 / 120.0, VR)
    gn = int(0.07 * VR)
    glide_r = 1.0
    fcur = f0
    if f_prev and f_prev > 0:
        fcur = f_prev
        glide_r = (f0 / f_prev) ** (1.0 / gn)
    vib_start = int(n2 * 0.30)
    lfo = 0.0
    lfo_inc = 5.5 * 4096.0 / VR
    na = int(0.028 * VR)
    nr = int(0.085 * VR)
    rs = n2 - nr
    x1a = x2a = y1a = y2a = 0.0
    x1b = x2b = y1b = y2b = 0.0
    ph = random.random() * T
    b = [0.0] * n2
    for i in range(n2):
        if i < gn:
            fcur *= glide_r
            f = fcur
        else:
            f = f0
        if i >= vib_start:
            lfo += lfo_inc
            f *= VB[int(lfo) & 4095]
        inc = f * T / VR
        ph += inc
        if ph >= T:
            ph -= T
        ip = int(ph)
        fr = ph - ip
        src = SAW12[ip] + (SAW12[ip + 1] - SAW12[ip]) * fr
        e = 1.0
        if i < na:
            e = i / na
        elif i >= rs:
            e = (n2 - i) / nr
        src *= e
        ya = b0a * (src - x2a) - a1a * y1a - a2a * y2a
        x2a = x1a
        x1a = src
        y2a = y1a
        y1a = ya
        yb = b0b * (src - x2b) - a1b * y1b - a2b * y2b
        x2b = x1b
        x1b = src
        y2b = y1b
        y1b = yb
        breath = (random.random() * 2.0 - 1.0) * 0.010 * e
        b[i] = (0.75 * (ya + yb) + src * 0.05 + breath) * 1.1
    return b


# ==================================================================  MIXER  ==
mixL = array("f", [0.0]) * TOTAL_N
mixR = array("f", [0.0]) * TOTAL_N
vL = array("f", [0.0]) * TOTAL_N      # bus vocal rieng (de lam ban instrumental)
vR = array("f", [0.0]) * TOTAL_N


def stamp(buf, t, gl=1.0, gr=1.0):
    """Dan buffer full-rate vao mix tai thoi diem t (giay)."""
    j = int(t * SR)
    n = len(buf)
    if j + n > TOTAL_N:
        n = TOTAL_N - j
    if n <= 0:
        return
    ml = mixL
    mr = mixR
    if gl == 1.0 and gr == 1.0:
        for i in range(n):
            v = buf[i]
            ml[j] += v
            mr[j] += v
            j += 1
    else:
        for i in range(n):
            v = buf[i]
            ml[j] += v * gl
            mr[j] += v * gr
            j += 1


def stamp_h(buf, t, gl=1.0, gr=1.0):
    """Dan buffer half-rate vao mix, noi suy tuyen tinh (khoi bong ma 18kHz)."""
    j = int(t * SR)
    n = len(buf)
    if j + 2 * n > TOTAL_N:
        n = (TOTAL_N - j) // 2
    if n <= 1:
        return
    ml = mixL
    mr = mixR
    p = j
    prev = buf[0]
    if gl == 1.0 and gr == 1.0:
        for i in range(1, n):
            v = buf[i]
            mid = (prev + v) * 0.5
            ml[p] += prev
            ml[p + 1] += mid
            mr[p] += prev
            mr[p + 1] += mid
            prev = v
            p += 2
    else:
        for i in range(1, n):
            v = buf[i]
            mid = (prev + v) * 0.5
            ml[p] += prev * gl
            ml[p + 1] += mid * gl
            mr[p] += prev * gr
            mr[p + 1] += mid * gr
            prev = v
            p += 2


def stamp_v(buf, t):
    """Dan vocal (half-rate) vao bus vocal rieng."""
    j = int(t * SR)
    n = len(buf)
    if j + 2 * n > TOTAL_N:
        n = (TOTAL_N - j) // 2
    if n <= 0:
        return
    vl = vL
    vr = vR
    p = j
    prev = buf[0]
    for i in range(1, n):
        v = buf[i]
        mid = (prev + v) * 0.5
        vl[p] += prev
        vl[p + 1] += mid
        vr[p] += prev
        vr[p + 1] += mid
        prev = v
        p += 2


# ===============================================================  DU LIEU  ==
# hop am: (bass root midi, triad, loai) - tone D minor, chorus sang F major
CHORDS = {
    "Dm": (38, [62, 65, 69], "m"),
    "Bb": (34, [58, 62, 65], "M"),
    "F":  (41, [65, 69, 72], "M"),
    "C":  (36, [60, 64, 67], "M"),
    "Gm": (43, [55, 58, 62], "m"),
    "D":  (38, [62, 66, 69], "M"),
    "G":  (43, [67, 71, 74], "M"),
    "Em": (40, [64, 67, 71], "m"),
}

# cau truc bai (86 o nhip, ~2:46):
#  intro8 | verse1 8 | pre1 8 | chorus1 8 | post4 | verse2 8 | pre2 8 |
#  chorus2 8 | post4 | bridge 8 | chorus3 (len 1 cung) 8 | outro 6
SEC = {
    "intro":   (0,  ["Dm", "Bb", "F", "C"] * 2),
    "verse1":  (8,  ["Dm", "Bb", "F", "C"] * 2),
    "pre1":    (16, ["Gm", "Bb", "C", "C"] * 2),
    "chorus1": (24, ["F", "C", "Dm", "Bb"] * 2),
    "post1":   (32, ["F", "C", "Dm", "Bb"]),
    "verse2":  (36, ["Dm", "Bb", "F", "C"] * 2),
    "pre2":    (44, ["Gm", "Bb", "C", "C"] * 2),
    "chorus2": (52, ["F", "C", "Dm", "Bb"] * 2),
    "post2":   (60, ["F", "C", "Dm", "Bb"]),
    "bridge":  (64, ["Bb", "C", "Dm", "Dm", "Bb", "C", "D", "D"]),
    "final":   (72, ["G", "D", "Em", "C"] * 2),
    "outro":   (80, ["Dm", "Bb", "F", "C", "Dm", "Dm"]),
}

# GIAI DIEU + LOI (moi dong = 2 o nhip = 16 slot note tam)
# (am tiet, midi, slot bat dau, do dai slot)
V1L1 = [("Đèn", 57, 0, 2), ("dầu", 60, 2, 1), ("cũ", 62, 3, 1), ("trong", 65, 4, 2), ("góc", 64, 6, 1), ("phòng", 62, 7, 1), ("mình", 62, 8, 3)]
V1L2 = [("Ngàn", 57, 0, 2), ("năm", 60, 2, 1), ("chờ", 62, 3, 1), ("một", 65, 4, 2), ("ai", 64, 6, 1), ("chạm", 62, 7, 1), ("vào", 64, 8, 3)]
V1L3 = [("Em", 57, 0, 2), ("lau", 60, 2, 1), ("nhẹ", 62, 3, 1), ("khói", 65, 4, 2), ("xanh", 64, 6, 1), ("bay", 62, 7, 1), ("lên", 65, 8, 3)]
V1L4 = [("Ge", 65, 0, 1), ("nie", 65, 1, 1), ("hiện", 64, 2, 1), ("ra", 62, 3, 1), ("hỏi", 60, 4, 2), ("em", 62, 6, 1), ("mơ", 64, 7, 1), ("điều", 64, 8, 1), ("gì", 67, 9, 3)]

P1L1 = [("Ngườii", 62, 0, 2)]
P1L1 = [("Ngườii", 62, 0, 2), ("ban", 62, 2, 1), ("ước", 60, 3, 1), ("mơ", 58, 4, 2), ("cho", 57, 6, 1), ("cả", 58, 7, 1), ("thế", 62, 8, 2), ("gian", 65, 10, 4)]
P1L2 = [("Mà", 64, 0, 2), ("đêm", 67, 2, 1), ("đêm", 65, 3, 1), ("ngồi", 64, 4, 2), ("trong", 62, 6, 1), ("đèn", 64, 7, 1), ("một", 60, 8, 2), ("mình", 64, 10, 4)]
P1L3 = [("Em", 62, 0, 2), ("nhìn", 65, 2, 1), ("sâu", 67, 3, 1), ("trong", 65, 4, 2), ("mắt", 64, 6, 1), ("ngườii".replace("ii", "i"), 65, 7, 1), ("buồn", 62, 8, 4)]
P1L4 = [("Tim", 67, 0, 2), ("em", 69, 2, 1), ("chợt", 67, 3, 1), ("nhói", 64, 4, 2), ("lên", 65, 6, 1), ("một", 67, 7, 1), ("điều", 69, 8, 4)]

CL1 = [("Này", 69, 0, 1), ("ge", 69, 1, 1), ("nie", 72, 2, 2), ("em", 72, 4, 1), ("ước", 69, 5, 1), ("điều", 65, 6, 1), ("cuối", 69, 7, 1), ("cùng", 67, 8, 3)]
CL2 = [("Cho", 69, 0, 1), ("ngườii".replace("ii", "i"), 69, 1, 1), ("tự", 74, 2, 2), ("do", 72, 4, 1), ("bay", 69, 5, 1), ("về", 65, 6, 2), ("trờii", 62, 8, 4)]
CL3 = [("Đừng", 69, 0, 1), ("quay", 69, 1, 1), ("lại", 72, 2, 2), ("đừng", 72, 4, 1), ("nhớ", 69, 5, 1), ("gì", 65, 6, 2), ("em", 64, 8, 3)]
CL4 = [("Ge", 65, 0, 1), ("nie", 65, 1, 1), ("ơi", 69, 2, 2), ("bay", 67, 4, 1), ("đi", 65, 5, 1), ("bay", 65, 6, 2), ("đi", 70, 8, 4)]

V2L1 = [("Ngườii", 57, 0, 2), ("cườii", 60, 2, 1), ("mà", 62, 3, 1), ("sao", 65, 4, 2), ("mắt", 64, 6, 1), ("long", 62, 7, 1), ("lanh", 62, 8, 3)]
V2L2 = [("Ngàn", 57, 0, 2), ("năm", 60, 2, 1), ("lần", 62, 3, 1), ("đầu", 65, 4, 2), ("biết", 64, 6, 1), ("rơi", 62, 7, 1), ("lệ", 64, 8, 3)]
V2L3 = [("Chiếc", 57, 0, 2), ("đèn", 60, 2, 1), ("rơi", 62, 3, 1), ("xuống", 65, 4, 2), ("cát", 64, 6, 1), ("êm", 62, 7, 1), ("đềm", 65, 8, 3)]
V2L4 = [("Còn", 65, 0, 1), ("em", 65, 1, 1), ("đứng", 64, 2, 1), ("đó", 62, 3, 1), ("mỉm", 60, 4, 2), ("cườii", 62, 6, 2), ("thôi", 67, 8, 3)]

P2L1 = [("Giờ", 62, 0, 2), ("đến", 62, 2, 1), ("lượt", 60, 3, 1), ("em", 58, 4, 2), ("ban", 57, 6, 1), ("cho", 58, 7, 1), ("ngườii".replace("ii", "i"), 62, 8, 4)]
P2L2 = [("Một", 64, 0, 2), ("điều", 67, 2, 1), ("ước", 65, 3, 1), ("chẳng", 64, 4, 2), ("củaa", 62, 6, 1), ("riêng", 60, 7, 1), ("em", 64, 8, 4)]
P2L3 = [("Mà", 62, 0, 2), ("là", 65, 2, 1), ("củaa", 67, 3, 1), ("ngườii".replace("ii", "i"), 65, 4, 2), ("tự", 64, 6, 1), ("do", 65, 7, 1), ("bay", 62, 8, 4)]
P2L4 = [("Từ", 67, 0, 2), ("nay", 69, 2, 1), ("trờii", 67, 3, 1), ("rộng", 64, 4, 2), ("mở", 65, 6, 1), ("gọi", 67, 7, 1), ("tên", 69, 8, 4)]

BL1 = [("Ngườii", 65, 0, 2), ("ta", 65, 2, 2), ("ước", 62, 4, 2), ("vàng", 65, 6, 2), ("ước", 64, 8, 2), ("tình", 67, 10, 2), ("yêu", 64, 12, 4)]
BL2 = [("Chẳng", 65, 0, 2), ("ai", 64, 2, 2), ("ước", 62, 4, 2), ("cho", 65, 6, 2), ("ge", 69, 8, 2), ("nie", 67, 10, 2), ("bao", 65, 12, 2), ("giờ", 62, 14, 2)]
BL3 = [("Nên", 65, 0, 2), ("em", 65, 2, 2), ("ước", 62, 4, 2), ("điều", 65, 6, 2), ("cuối", 67, 8, 2), ("cùng", 69, 10, 6)]
BL4 = [("Cho", 66, 0, 4), ("ngườii".replace("ii", "i"), 69, 4, 2), ("tự", 66, 6, 2), ("do", 69, 8, 8)]

OUTV = [("Ge", 69, 0, 2), ("nie", 67, 2, 2), ("ơi", 65, 4, 2), ("bay", 64, 6, 2), ("đi", 62, 8, 8)]


def transpose(line, semis):
    return [(s, m + semis, a, d) for (s, m, a, d) in line]


# (o nhip bat dau, line) - verse/pre/chorus/bridge/outro
VOCAL_LINES = [
    (8, V1L1), (10, V1L2), (12, V1L3), (14, V1L4),
    (16, P1L1), (18, P1L2), (20, P1L3), (22, P1L4),
    (24, CL1), (26, CL2), (28, CL3), (30, CL4),
    (36, V2L1), (38, V2L2), (40, V2L3), (42, V2L4),
    (44, P2L1), (46, P2L2), (48, P2L3), (50, P2L4),
    (52, CL1), (54, CL2), (56, CL3), (58, CL4),
    (64, BL1), (66, BL2), (68, BL3), (70, BL4),
    (72, transpose(CL1, 2)), (74, transpose(CL2, 2)),
    (76, transpose(CL3, 2)), (78, transpose(CL4, 2)),
    (84, OUTV),
]

# hook lead cho post-chorus = giai dieu chorus len octave
HOOK = [(-1,)]  # placeholder
HOOK = []
for _line in (CL1, CL2):
    for (s, m, a, d) in _line:
        HOOK.append((m + 12, a, d))
HOOK_POST = []          # (midi, slot tu dau post, dur slot)
_slot = 0
for _line in (CL1, CL2):
    for (s, m, a, d) in _line:
        HOOK_POST.append((m + 12, _slot + a, d))
    _slot += 16

# motif pluck intro/outro (chu ky "genie")
MOTIF = [69, 72, 74, 72, 69, 67, 65, 64]

# pattern arp 16 cho moi o nhip: index vao [t0, t1, t2, t0+12]
ARP_PAT = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 1, 2, 3]


# ======================================================  TU KIEM HOP AM  ==
def check_melody():
    """Kieu music21 mini: note manh (slot 0/4/8/12, dai >=2) nen la chord tone."""
    print("[*] Tu kiem tra hop am (melody vs chord tones)...")
    bar_of_section = {}
    for sec, (off, chords) in SEC.items():
        for i, ch in enumerate(chords):
            bar_of_section[off + i] = ch
    bad = 0
    for (start_bar, line) in VOCAL_LINES:
        for (syl, m, slot, dur) in line:
            strong = slot in (0, 4, 8, 12) and dur >= 2
            if not strong:
                continue
            ch = bar_of_section.get(start_bar + slot // 8)
            if ch is None:
                continue
            triad = CHORDS[ch][1]
            pcs = {t % 12 for t in triad}
            if (m % 12) not in pcs:
                print("    !! bar %d slot %d: '%s' %s tren %s (khong phai chord tone)"
                      % (start_bar + slot // 8, slot % 8, syl, mname(m), ch))
                bad += 1
    if bad == 0:
        print("    OK - moi note manh deu nam trong hop am.")
    return bad


# ================================================================  RENDER  ==
def add_arp(bar_idx, chord):
    tri = CHORDS[chord][1]
    notes = [tri[0], tri[1], tri[2], tri[0] + 12]
    t0 = bar_idx * BAR
    for k, ix in enumerate(ARP_PAT):
        stamp_h(gen_pluck(notes[ix]), t0 + k * E8 / 2.0, 0.9, 0.9)
        # echo dotted-8th (2 tap, pan trai/phai)
        stamp_h(gen_pluck(notes[ix]), t0 + k * E8 / 2.0 + 0.75 * BEAT, 0.32, 0.18)
        stamp_h(gen_pluck(notes[ix]), t0 + k * E8 / 2.0 + 1.5 * BEAT, 0.10, 0.20)


def drums_bar(bi, style, KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT):
    t0 = bi * BAR
    if style in ("verse", "pre", "chorus", "post", "final"):
        for q in range(4):
            stamp(KICK, t0 + q * BEAT)
    elif style in ("intro_l", "outro_l"):
        for q in range(4):
            stamp(KICK_S, t0 + q * BEAT)
    elif style == "halftime":
        stamp(KICK_S, t0)
        stamp(KICK_S, t0 + 2.5 * BEAT, 0.8, 0.8)
        stamp(SNARE_S, t0 + 2.0 * BEAT)

    if style == "verse":
        stamp(SNARE_S, t0 + BEAT)
        stamp(SNARE_S, t0 + 3 * BEAT)
        for k in range(8):
            stamp(HAT_A if k % 2 == 0 else HAT_B, t0 + k * E8)
    elif style == "pre":
        stamp(CLAP, t0 + BEAT)
        stamp(CLAP, t0 + 3 * BEAT)
        for k in range(8):
            stamp(HAT_A if k % 2 == 0 else HAT_B, t0 + k * E8)
        for k in range(4):
            stamp(OHAT, t0 + (k + 0.5) * BEAT, 0.5, 0.9)
    elif style in ("chorus", "post", "final"):
        stamp(CLAP, t0 + BEAT)
        stamp(CLAP, t0 + 3 * BEAT)
        stamp(SNARE, t0 + BEAT)
        stamp(SNARE, t0 + 3 * BEAT)
        for k in range(16):
            stamp(HAT_A if k % 2 == 0 else HAT_B, t0 + k * E8 / 2.0)
        for k in range(4):
            stamp(OHAT, t0 + (k + 0.5) * BEAT, 0.5, 0.9)
    elif style in ("intro_l", "outro_l"):
        for k in range(8):
            stamp(HAT_B, t0 + k * E8)
    elif style == "halftime":
        for k in range(8):
            stamp(HAT_B, t0 + k * E8, 0.7, 0.7)


def snare_roll(bi, div, SNARE):
    t0 = bi * BAR
    for k in range(div):
        g = 0.3 + 0.9 * (k / div)
        stamp(SNARE, t0 + k * BAR / div, g, g)


def render():
    print("[*] Dang tong hop trum...")
    KICK = gen_kick(0.95)
    KICK_S = gen_kick(0.6)
    SNARE = gen_snare(0.5)
    SNARE_S = gen_snare(0.3)
    CLAP = gen_clap(0.42)
    HAT_A = gen_hat(0.055, 40.0, 0.15)
    HAT_B = gen_hat(0.05, 44.0, 0.09)
    OHAT = gen_hat(0.32, 9.0, 0.18)
    CRASH = gen_crash(0.26)
    RISER = gen_riser(0.3)
    SUB = gen_subdrop(0.85)

    bar_h = BAR_H + int(0.12 * VR)

    def saw_bar(chord, duck=True):
        return gen_saw_chord(CHORDS[chord][1], bar_h, 2600.0, duck)

    def pad_bar(chord, bars=1, cut=1100.0, atk=0.35):
        return gen_pad(CHORDS[chord][1], bars * BAR_H + int(0.4 * VR), cut, atk)

    print("[*] Intro (arp + pad + riser)...")
    for i, ch in enumerate(SEC["intro"][1]):
        bi = i
        add_arp(bi, ch)
        if i % 2 == 0:
            stamp_h(pad_bar(ch, 2, 1100.0, 0.5), bi * BAR, 0.95, 0.95)
        if i >= 4:
            drums_bar(bi, "intro_l", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
    for k, m in enumerate(MOTIF):                    # motif "genie" 2 o dau
        stamp_h(gen_pluck(m + 12), k * E8, 1.0, 1.0)
        stamp_h(gen_pluck(m + 12), k * E8 + 0.75 * BEAT, 0.3, 0.15)
    stamp(RISER, 7 * BAR)

    for sec_name in ("verse1", "verse2"):
        off, chords = SEC[sec_name]
        print("[*] %s ..." % sec_name)
        for i, ch in enumerate(chords):
            bi = off + i
            drums_bar(bi, "verse", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
            stamp(gen_bass_bar(CHORDS[ch][0]), bi * BAR)
            if sec_name == "verse2":
                add_arp(bi, ch)

    for sec_name in ("pre1", "pre2"):
        off, chords = SEC[sec_name]
        print("[*] %s (build + snare roll)..." % sec_name)
        for i, ch in enumerate(chords):
            bi = off + i
            drums_bar(bi, "pre", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
            stamp(gen_bass_bar(CHORDS[ch][0]), bi * BAR)
            stamp_h(pad_bar(ch, 1, 1500.0, 0.2), bi * BAR, 0.8, 0.8)
        snare_roll(off + 6, 8, SNARE)
        snare_roll(off + 7, 16, SNARE)
        stamp(RISER, (off + 7) * BAR)

    for sec_name in ("chorus1", "post1", "chorus2", "post2", "final"):
        off, chords = SEC[sec_name]
        print("[*] %s (supersaw + stab + day du trum)..." % sec_name)
        for i, ch in enumerate(chords):
            bi = off + i
            drums_bar(bi, "chorus", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
            stamp(gen_bass_bar(CHORDS[ch][0]), bi * BAR)
            stamp_h(saw_bar(ch, True), bi * BAR, 1.0, 1.0)
            stamp_h(saw_bar(ch, True), bi * BAR + 0.012, 0.5, 0.5)   # wide layer
            stab = gen_stab([t + 12 for t in CHORDS[ch][1]])
            for k in range(4):
                stamp_h(stab, bi * BAR + (k + 0.5) * BEAT, 0.85, 0.85)
            if i == 0 and sec_name in ("chorus1", "chorus2", "final"):
                stamp(CRASH, bi * BAR)
                stamp(SUB, bi * BAR)
        if sec_name in ("post1", "post2"):           # hook lead tra loi
            for (m, slot, d) in HOOK_POST:
                t = (off + slot // 8) * BAR + (slot % 8) * E8
                stamp_h(gen_lead(m, int(d * E8 * VR)), t, 0.95, 0.95)

    print("[*] Bridge (half-time, pad, modulation sang G)...")
    off, chords = SEC["bridge"]
    for i, ch in enumerate(chords):
        bi = off + i
        if i < 6:
            drums_bar(bi, "halftime", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
        else:
            drums_bar(bi, "chorus", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
        stamp(gen_bass_bar(CHORDS[ch][0]), bi * BAR)
        stamp_h(pad_bar(ch, 1, 1300.0, 0.2), bi * BAR, 0.9, 0.9)
        if i >= 6:                                    # build vao final chorus
            stamp_h(saw_bar(ch, True), bi * BAR, 0.9, 0.9)
    snare_roll(off + 6, 8, SNARE)
    snare_roll(off + 7, 16, SNARE)
    stamp(RISER, (off + 7) * BAR)

    print("[*] Outro (motif genie + pad fade)...")
    off, chords = SEC["outro"]
    for i, ch in enumerate(chords):
        bi = off + i
        add_arp(bi, ch)
        stamp_h(pad_bar(ch, 1, 1000.0, 0.3), bi * BAR, 0.9, 0.9)
        if i < 4:
            drums_bar(bi, "outro_l", KICK, KICK_S, SNARE, SNARE_S, CLAP, HAT_A, HAT_B, OHAT)
        else:
            stamp(gen_bass_bar(CHORDS[ch][0]), bi * BAR)
    for k, m in enumerate(MOTIF):
        stamp_h(gen_pluck(m), 84 * BAR + k * E8, 1.0, 1.0)
        stamp_h(gen_pluck(m), 84 * BAR + k * E8 + 0.75 * BEAT, 0.25, 0.12)

    print("[*] Vocal formant (robot hat tieng Viet)...")
    f_prev = 0.0
    n_syl = 0
    for (start_bar, line) in VOCAL_LINES:
        for (syl, m, slot, dur) in line:
            t = start_bar * BAR + slot * E8
            d = dur * E8 + 0.03
            v = vowel_of(syl)
            buf = gen_vocal(m, d, v, f_prev)
            stamp_v(buf, t)
            f_prev = MTF[m]
            n_syl += 1
    print("    -> %d am tiet da hat." % n_syl)

    # echo cho vocal: 2 tap, tap 2 lech stereo cho rong
    print("[*] Vocal echo (2 tap)...")
    d1 = int(0.19 * SR)
    d2 = int(0.38 * SR)
    lim = TOTAL_N - d2
    for i in range(lim):
        vL[i + d1] += vL[i] * 0.30
        vR[i + d2] += vR[i] * 0.22
        vR[i + d1] += vL[i] * 0.10
        vL[i + d2] += vR[i] * 0.14


# ================================================================== MASTER ==
def analyze_harmony():
    print("")
    print("=" * 64)
    print(" PHAN TICH HOP AM (kieu music21, khong can thu vien)")
    print("=" * 64)
    print(" Tone chinh: D minor (chorus sang F major - relative major)")
    print("  verse : Dm  Bb  F   C   -> i - VI - III - VII  (D minor)")
    print("  pre   : Gm  Bb  C   C   -> iv - VI - VII       (day ve V cua F)")
    print("  chorus: F   C   Dm  Bb  -> I - V - vi - IV     (pop anthem)")
    print("  bridge: Bb  C   Dm  | Bb C D(major) -> picardy third,")
    print("          D major = V cua G -> modulation len 1 cung")
    print("  final : G   D   Em  C   -> I - V - vi - IV     (G major)")
    print(" Tempo: %d BPM | Genie goc: ~123 BPM (Dsign Music/SNSD 2009)" % BPM)


def rms_strided(arr, a, b):
    s = 0.0
    cnt = 0
    for i in range(a, b, 7):
        v = arr[i]
        s += v * v
        cnt += 1
    return math.sqrt(s / max(cnt, 1))


def write_wav(path, left, right, peak_target=0.94):
    pk = 1e-9
    m1 = max(left)
    m2 = max(right)
    n1 = min(left)
    n2 = min(right)
    pk = max(m1, m2, -n1, -n2, pk)
    g = peak_target / pk
    n = len(left)
    pcm = array("h", [0]) * n * 2
    for i in range(n):
        v = int(left[i] * g * 32767.0)
        if v > 32767:
            v = 32767
        elif v < -32768:
            v = -32768
        pcm[2 * i] = v
        v = int(right[i] * g * 32767.0)
        if v > 32767:
            v = 32767
        elif v < -32768:
            v = -32768
        pcm[2 * i + 1] = v
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
    w.close()
    return pk


def fade(arr, t_start, t_end, out=True):
    a = int(t_start * SR)
    b = min(int(t_end * SR), len(arr))
    n = b - a
    if n <= 0:
        return
    for i in range(n):
        arr[a + i] *= (1.0 - i / n) if out else (i / n)


def to_mp3(wav_path, mp3_path, title):
    ff = shutil.which("ffmpeg")
    if ff:
        cmd = [ff, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "192k",
               "-metadata", "title=" + title, "-metadata", "artist=Pi Formant Orchestra",
               "-metadata", "comment=inspired by SNSD Genie (2009)", mp3_path]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0:
            return True
    lm = shutil.which("lame")
    if lm:
        r = subprocess.run([lm, "-b", "192", wav_path, mp3_path], capture_output=True)
        return r.returncode == 0
    return False


def main():
    analyze_harmony()
    bad = check_melody()
    if bad:
        print("    (%d cho hoi cay - passing tone, chap nhan duoc)" % bad)
    print("[*] Render band (chi tiet tung section in ra ben duoi)...")
    render()

    print("[*] Master: fade in/out + can bang vocal/band...")
    fade(mixL, TOTAL_S - 2.4, TOTAL_S, out=True)
    fade(mixR, TOTAL_S - 2.4, TOTAL_S, out=True)
    fade(vL, TOTAL_S - 2.4, TOTAL_S, out=True)
    fade(vR, TOTAL_S - 2.4, TOTAL_S, out=True)
    fade(mixL, 0.0, 0.08, out=False)
    fade(mixR, 0.0, 0.08, out=False)
    fade(vL, 0.0, 0.08, out=False)
    fade(vR, 0.0, 0.08, out=False)

    # auto can bang: vocal RMS ~ 0.85 x band RMS trong vung co hat
    a = int(24 * BAR * SR)
    b = int(80 * BAR * SR)
    rb = rms_strided(mixL, a, b) + rms_strided(mixR, a, b)
    rv = rms_strided(vL, a, b) + rms_strided(vR, a, b)
    scale = (rb * 0.85) / max(rv, 1e-9)
    scale = min(max(scale, 0.2), 6.0)
    print("    band RMS=%.4f  vocal RMS=%.4f  -> vocal scale=%.2f" % (rb, rv, scale))
    for i in range(TOTAL_N):
        vL[i] *= scale
        vR[i] *= scale

    wav_full = os.path.join(HERE, "dieu-uoc-cuoi.wav")
    wav_inst = os.path.join(HERE, "dieu-uoc-cuoi-instrumental.wav")

    print("[*] Ghi WAV instrumental (band only)...")
    pk1 = write_wav(wav_inst, mixL, mixR)
    print("[*] Tron vocal + ghi WAV full...")
    for i in range(TOTAL_N):
        mixL[i] += vL[i]
        mixR[i] += vR[i]
    pk2 = write_wav(wav_full, mixL, mixR)

    mp3_full = os.path.join(HERE, "dieu-uoc-cuoi.mp3")
    mp3_inst = os.path.join(HERE, "dieu-uoc-cuoi-instrumental.mp3")
    ok1 = to_mp3(wav_full, mp3_full, "Dieu Uoc Cuoi (The Last Wish)")
    ok2 = to_mp3(wav_inst, mp3_inst, "Dieu Uoc Cuoi - Instrumental")
    if ok1 and ok2:
        os.remove(wav_full)
        os.remove(wav_inst)
        print("[*] Da xoa WAV tam, giu MP3 cho nhe.")
    else:
        print("[!] Khong thay ffmpeg/lame -> giu file WAV, tu convert nhe.")

    dur = TOTAL_N / SR
    print("")
    print("=" * 64)
    print(" XONG! Bai hat: DIEU UOC CUOI (The Last Wish)")
    print("  - Do dai      : %d:%02d" % (int(dur // 60), int(dur % 60)))
    print("  - Peak truoc normalize: full=%.2f inst=%.2f" % (pk2, pk1))
    print("  - File full   : %s" % (mp3_full if ok1 else wav_full))
    print("  - File instru : %s" % (mp3_inst if ok2 else wav_inst))
    print(" Cam hung: SNSD - Tell Me Your Wish (Genie), 2009")
    print(" Concept lat nguoc: dieu uoc cuoi = phong thich genie.")
    print("=" * 64)


if __name__ == "__main__":
    main()
