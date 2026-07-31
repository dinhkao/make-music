"""Sundial - arrange sections, render stems, mix, export WAV.
Run: python3 build.py  ->  sundial.wav
"""
import subprocess
import wave
import numpy as np

import notes as N
from dsp import filt, make_ir, reverb, delay, master, write_wav
from instruments import (note_freq, ep, bass, strings, lead, solo, choir)
from drums import kick, snare, hat, shaker, tamb, crackle

SR = N.SR
BAR = N.BAR
TOTAL = int((N.TOTAL_BARS * BAR + 3.0) * SR)
rng = np.random.default_rng(11)

DRUMS = {
    "lounge": {"kick": [0, 2], "snare": [], "open": [], "tamb": False},
    "pre":    {"kick": [0, 2], "snare": [1, 3], "open": [], "tamb": False},
    "chorus": {"kick": [0, 1, 2, 3], "snare": [1, 3], "open": [3.5], "tamb": True},
    "chorus2": {"kick": [0, 1, 2, 3], "snare": [1, 3], "open": [3.5], "tamb": True},
    "bridge": {"kick": [0, 2], "snare": [3], "open": [], "tamb": False},
    "solo":   {"kick": [0, 1, 2, 3], "snare": [1, 3], "open": [3.5], "tamb": True},
    "outro":  {"kick": [0, 2], "snare": [], "open": [], "tamb": False},
}
BASS_PAT = {
    "lounge": [(0, 0, 1.5), (1.5, 0, 0.5), (2, 7, 1.0), (3, 0, 0.5), (3.5, 0, 0.5)],
    "pre":    [(0, 0, 1.0), (1, 0, 1.0), (2, 7, 1.0), (3, 0, 1.0)],
    "chorus": [(0, 0, 0.5), (1, 0, 0.5), (1.5, 7, 0.5), (2, 0, 0.5),
               (2.5, 0, 0.5), (3, 0, 0.5), (3.5, 12, 0.5)],
    "chorus2": [(0, 0, 0.5), (1, 0, 0.5), (1.5, 7, 0.5), (2, 0, 0.5),
                (2.5, 0, 0.5), (3, 0, 0.5), (3.5, 12, 0.5)],
    "bridge": [(0, 0, 1.5), (2, 7, 1.0), (3, 0, 1.0)],
    "solo":   [(0, 0, 0.5), (1, 0, 0.5), (1.5, 7, 0.5), (2, 0, 0.5),
               (2.5, 0, 0.5), (3, 0, 0.5), (3.5, 12, 0.5)],
    "outro":  [(0, 0, 1.5), (1.5, 0, 0.5), (2, 7, 1.0), (3, 0, 0.5), (3.5, 0, 0.5)],
}
STRINGS = {"pre": (0.05, 1100, False), "chorus": (0.065, 1400, False),
           "chorus2": (0.07, 1400, True), "bridge": (0.09, 1500, True),
           "solo": (0.055, 1400, False)}


def place(buf, sig, t_abs, pan):
    i = max(0, int(t_abs * SR))
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    g = np.cos(pan * np.pi / 2), np.sin(pan * np.pi / 2)
    buf[i:i + n, 0] += sig[:n] * g[0]
    buf[i:i + n, 1] += sig[:n] * g[1]


def jit():
    return rng.uniform(-0.004, 0.004)


def to_send(sig, t_abs, send):
    """Place sig into the reverb send bus at absolute time t_abs."""
    i = int(t_abs * SR)
    out = np.zeros(len(send))
    if i >= len(out):
        return out
    n = min(len(sig), len(out) - i)
    out[i:i + n] = sig[:n]
    return out


def chord_of(section, bar):
    _, start, _, chords, _ = section
    return chords[(bar - start) % len(chords)]


def bass_events(style, bar, root):
    return [(b + jit(), note_freq(root + off), d, 0.30)
            for b, off, d in BASS_PAT[style]]


def drum_events(style, bar):
    ev, p = [], DRUMS[style]
    for b in p["kick"]:
        ev.append((b + jit(), kick, 0.55))
    for b in p["snare"]:
        ev.append((b + jit(), snare, 0.35))
    for b in p["open"]:
        ev.append((b + jit(), hat, 0.12, True))
    for q in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]:
        if style in ("lounge", "outro"):
            if q % 1 == 0.5:
                ev.append((q + jit(), hat, 0.10))
            else:
                ev.append((q + jit(), shaker, 0.06))
        else:
            ev.append((q + jit(), hat, 0.10))
    if p["tamb"]:
        for q in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]:
            ev.append((q + jit(), tamb, 0.07))
    if style == "bridge" and bar == 64:
        for i in range(16):
            ev.append((i / 4.0, snare, 0.10 + 0.16 * i / 15.0))
    return ev


def render_section(section, buf, send, offset):
    name, start, end, chords, style = section
    mkey = {"verse": "verse", "pre": "pre", "chorus": "chorus",
            "verseb": "verseb", "bridge": "bridge"}.get(name)
    for bar in range(start, end + 1):
        t0 = (bar - 1) * BAR
        ch = chord_of(section, bar)
        voicing = N.CHORDS[ch]
        freqs = [note_freq(m) for m in voicing]
        root = N.BASS[ch]
        # EP chords
        for m in voicing:
            place(buf, ep(note_freq(m), BAR * 1.1, 0.11, SR), t0 - offset, 0.35)
        # Bass
        for b, f, d, a in bass_events(style, bar, root):
            place(buf, bass(f, d * BAR, a, SR), t0 + b * N.BEAT - offset, 0.5)
        # Drums
        for ev in drum_events(style, bar):
            beat, inst, amp = ev[0], ev[1], ev[2]
            if inst == hat and len(ev) > 3:
                sig = hat(amp, SR, True)
            else:
                sig = inst(amp, SR)
            place(buf, sig, t0 + beat * N.BEAT - offset, 0.5)
        # Strings
        if style in STRINGS:
            amp, cut, oct_ = STRINGS[style]
            sf = freqs + ([f + 12 for f in freqs] if oct_ else [])
            sig = strings(sf, BAR * 1.1, amp, SR, cut)
            place(buf, sig, t0 - offset, 0.5)
            send += to_send(sig * 0.6, t0, send)
    # Lead melody ("voice") - OUTSIDE the bar loop (render each note once)
    if mkey:
        for bar_m, beat, m, d in N.MELODY[mkey]:
            tb = bar_m + (8 if style == "chorus2" else 0)
            t = (tb - 1) * BAR + beat * N.BEAT
            sig = lead(note_freq(m), d * N.BEAT, 0.22, SR)
            place(buf, delay(sig, SR), t - offset, 0.55)
            send += to_send(sig * 0.3, t, send)
            if style == "chorus2":
                place(buf, lead(note_freq(m + 7), d * N.BEAT, 0.06, SR),
                      t - offset + 0.01, 0.65)


def main():
    L = np.zeros((TOTAL, 2), dtype=np.float64)
    send = np.zeros(TOTAL)
    ir0, ir1 = make_ir(SR, seed=0), make_ir(SR, seed=1)

    for section in N.SECTIONS:
        name, start, end, chords, style = section
        offset = (start - 1) * BAR
        if name == "verseb":
            seg = np.zeros((int((end - start + 1) * BAR * SR) + SR, 2))
            render_section(section, seg, send, offset)
            for c in range(2):
                seg[:, c] = filt(seg[:, c], SR, "lp", 2400)
            L[int(offset * SR):int(offset * SR) + len(seg)] += seg
        else:
            render_section(section, L, send, 0.0)

    # Lead melody + harmony + solo
    # (melody is rendered inside render_section; solo lives here)
    # Guitar-ish solo (F pentatonic random walk)
    penta = [65, 67, 69, 72, 74, 77]
    idx, srng = 2, np.random.default_rng(42)
    for bar in range(65, 73):
        for i in range(8):
            idx = min(5, max(0, idx + int(srng.integers(-2, 3))))
            m = penta[idx]
            d = 1.0 if (bar == 72 and i == 7) else 0.5
            t = (bar - 1) * BAR + (i * 0.5) * N.BEAT
            sig = solo(note_freq(m), d * N.BEAT, 0.22, SR)
            place(L, sig, t, 0.5)
            send += to_send(sig * 0.2, t, send)
    # Outro choir + arp
    arp_pat = [53, 57, 60, 64, 60, 57, 60, 64]
    for bar in range(73, 89):
        t0 = (bar - 1) * BAR
        ch = "Fmaj7" if (bar - 73) % 2 == 0 else "C_No3"
        freqs = [note_freq(m) for m in N.CHORDS[ch]]
        sig = choir(freqs, BAR * 1.2, 0.07, SR)
        place(L, sig, t0, 0.5)
        send += to_send(sig * 0.45, t0, send)
        for i, m in enumerate(arp_pat):
            place(L, ep(note_freq(m), 0.45, 0.09, SR), t0 + (i * 0.5) * N.BEAT, 0.7)

    # Spoken word (Whisper, pitch-shifted)
    for tb, text in N.SPOKEN:
        t = (int(tb) - 1) * BAR + (tb - int(tb)) * N.BEAT
        sp = make_spoken(text)
        sp = filt(sp, SR, "lp", 2500)
        sp = reverb(sp, SR, ir0, wet=1.0) - sp
        sp = delay(sp, SR, 0.5, 0.3)
        place(L, sp * 0.5, t, 0.5)
        send += to_send(sp * 0.55, t, send)

    # Vinyl crackle bed
    cr = crackle(TOTAL / SR, 1.0, SR)
    env = np.ones(TOTAL)
    env[:int(16 * SR)] = np.linspace(1.4, 0.8, int(16 * SR))
    env[int(140 * SR):] = np.linspace(0.8, 1.6, TOTAL - int(140 * SR))
    cr *= env * 0.05
    L[:, 0] += cr
    L[:, 1] += cr * 0.95

    # Reverb
    wet = reverb(send, SR, ir0, wet=1.0) - send
    wet2 = reverb(send, SR, ir1, wet=1.0) - send
    L[:, 0] += wet * 0.45
    L[:, 1] += wet2 * 0.45

    mix = master(L, SR)
    write_wav("sundial.wav", mix, SR)
    print("Wrote sundial.wav", mix.shape, "peak", np.max(np.abs(mix)))


def make_spoken(text, i=0):
    base = f"/tmp/sundial_spk"
    subprocess.run(["say", "-v", "Whisper", "-o", base + ".aiff", text], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@22050",
                    base + ".aiff", base + ".wav"], check=True)
    with wave.open(base + ".wav", "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768.0
    # 22050 -> 44100
    x1 = np.interp(np.linspace(0, len(x) - 1, len(x) * 2), np.arange(len(x)), x)
    # pitch down 0.82x, same duration (slower playback of source)
    out = np.interp(np.linspace(0, (len(x1) - 1) * 0.82, len(x1)),
                    np.arange(len(x1)), x1)
    out = np.tanh(out * 0.7) * 0.8                       # tame plosives
    peak = np.max(np.abs(out))
    if peak > 1e-9:
        out = out / peak * 0.2                            # normalize to 0.2
    n_atk = int(0.008 * SR)
    out[:n_atk] *= np.linspace(0, 1, n_atk)              # attack ramp
    return out


if __name__ == "__main__":
    main()
