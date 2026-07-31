"""Honey Static - render engine. Reuses instruments/drums/dsp from Sundial.
Run: python3 honey_build.py -> honey-static.wav
"""
import subprocess
import wave
import numpy as np

import honey_notes as N
from instruments import note_freq, ep, bass, strings, lead, choir
from drums import kick, snare, hat, shaker, tamb, crackle, tom, crash
from dsp import filt, make_ir, reverb, delay, master, write_wav
from honey_drums import (drum_events, KICK, SNARE, HAT, OPEN, SHAKER,
                         TAMB, BELL, CRASH, TOM)

SR = N.SR
BEAT = N.BEAT
rng = np.random.default_rng(7)

TOTAL_BARS = sum(s[2] for s in N.SECTIONS)
TOTAL = int((sum(s[2] * (s[5] * BEAT) for s in N.SECTIONS) + 4.0) * SR)


def place(buf, sig, t_abs, pan):
    i = max(0, int(t_abs * SR))
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    g = np.cos(pan * np.pi / 2), np.sin(pan * np.pi / 2)
    buf[i:i + n, 0] += sig[:n] * g[0]
    buf[i:i + n, 1] += sig[:n] * g[1]


def to_send(sig, t_abs, send):
    i = int(t_abs * SR)
    out = np.zeros(len(send))
    if i >= len(out):
        return out
    n = min(len(sig), len(out) - i)
    out[i:i + n] = sig[:n]
    return out


def jit():
    return rng.uniform(-0.004, 0.004)


def bell(freq, amp, sr):
    """Ride bell: bright partials, fast decay."""
    n = int(0.5 * sr)
    t = np.arange(n) / sr
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.6 * np.sin(2 * np.pi * freq * 2.76 * t)
           + 0.3 * np.sin(2 * np.pi * freq * 5.4 * t))
    env = np.exp(-t / 0.09) * np.minimum(1, t / 0.002)
    return (sig * env * amp).astype(np.float32)


def beep(sr):
    """TV power-on beep + static blip (quirky intro)."""
    n = int(0.14 * sr)
    t = np.arange(n) / sr
    f = 1000 + 900 * np.minimum(1, t / 0.1)
    sig = np.sin(2 * np.pi * np.cumsum(f) / sr)
    env = np.minimum(1, t / 0.005) * np.exp(-t / 0.05)
    return (sig * env * 0.10).astype(np.float32)


def bar_len(section):
    return section[5] * BEAT


def render_bars(section, buf, send, offset):
    """Render one section. Events placed at GLOBAL times (t = offset + local)."""
    name, start, nbars, chords, style, beats = section
    blen = bar_len(section)
    for i in range(nbars):
        t0 = offset + i * blen
        ch = chords[i % len(chords)]
        voicing = N.CHORDS[ch]
        root = N.BASS[ch]
        # EP chords
        for m in voicing:
            place(buf, ep(note_freq(m), blen * 1.1, 0.06, SR), t0, 0.35)
        # Bass
        for b, off, d in BASS_PAT[style]:
            place(buf, bass(note_freq(root + off), d * BEAT, 0.24, SR),
                  t0 + (b + jit()) * BEAT, 0.5)
        # Drums (Nick Villa style)
        for ev in drum_events(style, i + 1, beats):
            b, inst, amp = ev[0], ev[1], ev[2]
            if inst == KICK:
                sig = kick(amp, SR)
            elif inst == SNARE:
                sig = snare(amp, SR)
            elif inst == HAT:
                sig = hat(amp, SR)
            elif inst == OPEN:
                sig = hat(amp, SR, True)
            elif inst == SHAKER:
                sig = shaker(amp, SR)
            elif inst == TAMB:
                sig = tamb(amp, SR)
            elif inst == BELL:
                sig = bell(880, amp, SR)
            elif inst == TOM:
                pitch = ev[3] if len(ev) > 3 else 1.0
                sig = tom(amp, SR, pitch)
            elif inst == CRASH:
                sig = crash(amp, SR)
            else:
                sig = hat(amp, SR, True)
            place(buf, sig, t0 + b * BEAT, 0.5)
        # Strings
        if style in STRINGS:
            amp, cut, oct_ = STRINGS[style]
            freqs = [note_freq(m) for m in voicing]
            sf = freqs + ([f + 12 for f in freqs] if oct_ else [])
            sig = strings(sf, blen * 1.1, amp, SR, cut)
            place(buf, sig, t0, 0.5)
            send += to_send(sig * 0.6, t0, send)
    # Melody
    if name in ("verse", "pre", "chorus", "chorus2", "bridge", "chorus3"):
        mkey = "chorus" if name.startswith("chorus") else name
        lead_amp = {"verse": 0.42, "pre": 0.38, "chorus": 0.55,
                    "chorus2": 0.55, "chorus3": 0.55, "bridge": 0.50}.get(
                        name, 0.5)
        for lb, b, m, d in N.MELODY[mkey]:
            t = offset + (lb - 1) * blen + b * BEAT
            sig = lead(note_freq(m), d * BEAT, lead_amp, SR)
            place(buf, delay(sig, SR), t, 0.55)
            send += to_send(sig * 0.3, t, send)
            if name == "chorus2":  # 3rd harmony (girl-group layer)
                h = lead(note_freq(m - 3), d * BEAT, 0.15, SR)
                place(buf, h, t + 0.01, 0.6)
                send += to_send(h * 0.3, t, send)
            if name in ("chorus", "chorus2"):  # octave shimmer
                o = lead(note_freq(m + 12), d * BEAT, 0.12, SR)
                place(buf, o, t + 0.005, 0.7)
    return buf


BASS_PAT = {
    "lounge": [(0, 0, 1.5), (1.5, 0, 0.5), (2, 7, 1.0), (3, 0, 0.5),
               (3.5, 2, 0.5)],
    "verse":  [(0, 0, 1.0), (1, 0, 0.5), (1.5, 7, 0.5), (2, 0, 1.0),
               (3, 0, 0.5), (3.5, 2, 0.5)],
    "pre":    [(0, 0, 1.0), (1, 0, 1.0), (2, 7, 1.0), (3, 0, 1.0)],
    "chorus": [(0, 0, 0.5), (1, 0, 0.5), (1.5, 7, 0.5), (2, 0, 0.5),
               (2.5, 0, 0.5), (3, 0, 0.5), (3.5, 12, 0.5)],
    "bridge": [(0, 0, 1.5), (1, 7, 0.75), (2, 0, 0.75)],
    "outro":  [(0, 0, 1.5), (1.5, 0, 0.5), (2, 7, 1.0), (3, 0, 0.5),
               (3.5, 2, 0.5)],
}
STRINGS = {"pre": (0.22, 1100, False), "chorus": (0.40, 1400, False),
           "bridge": (0.45, 1500, True)}


def section_offset(idx):
    """Global time of section start (bars before it have their own meters)."""
    return sum(s[2] * bar_len(s) for s in N.SECTIONS[:idx])


def main():
    L = np.zeros((TOTAL, 2), dtype=np.float64)
    send = np.zeros(TOTAL)
    ir0, ir1 = make_ir(SR, seed=0), make_ir(SR, seed=1)

    for idx, section in enumerate(N.SECTIONS):
        offset = section_offset(idx)
        render_bars(section, L, send, offset)

    # TV beep at intro start
    place(L, beep(SR), 0.0, 0.5)
    place(L, beep(SR), 0.4, 0.5)

    # Choir in chorus3 + outro, arp in outro
    arp_pat = [48, 52, 55, 59, 55, 52, 55, 59]
    for section in N.SECTIONS:
        name, start, nbars, chords, style, beats = section
        offset = section_offset(N.SECTIONS.index(section))
        blen = bar_len(section)
        if name in ("chorus3", "outro"):
            for i in range(nbars):
                t0 = offset + i * blen
                ch = chords[i % len(chords)]
                freqs = [note_freq(m) for m in N.CHORDS[ch]]
                sig = choir(freqs, blen * 1.2, 0.30, SR)
                place(L, sig, t0, 0.5)
                send += to_send(sig * 0.45, t0, send)
        if name == "outro":
            for i in range(nbars):
                t0 = offset + i * blen
                for j, m in enumerate(arp_pat):
                    place(L, ep(note_freq(m), 0.4, 0.06, SR),
                          t0 + j * 0.25 * BEAT, 0.7)
    # Glitch stutter at the very end (16ths, decaying)
    end = section_offset(len(N.SECTIONS))
    gl = [72, 76, 79, 84]
    for i in range(16):
        t = end + (i - 4) * 0.25 * BEAT
        if t < 0:
            continue
        place(L, ep(note_freq(gl[i % 4]), 0.22, 0.16 * (1 - i / 20), SR),
              t, 0.5)

    # Spoken word
    for tb, text in N.SPOKEN:
        t = bar_time(tb)
        sp = make_spoken(text)
        sp = filt(sp, SR, "lp", 2500)
        sp = reverb(sp, SR, ir0, wet=1.0) - sp
        sp = delay(sp, SR, 0.45, 0.3)
        place(L, sp * 0.5, t, 0.5)
        send += to_send(sp * 0.55, t, send)

    # Vinyl crackle
    cr = crackle(TOTAL / SR, 1.0, SR)
    env = np.ones(TOTAL)
    n16 = int(16 * SR)
    env[:n16] = np.linspace(1.5, 0.8, n16)
    env[int(120 * SR):] = np.linspace(0.8, 1.6, TOTAL - int(120 * SR))
    cr *= env * 0.045
    L[:, 0] += cr
    L[:, 1] += cr * 0.95

    # Reverb
    wet = reverb(send, SR, ir0, wet=1.0) - send
    wet2 = reverb(send, SR, ir1, wet=1.0) - send
    L[:, 0] += wet * 0.45
    L[:, 1] += wet2 * 0.45

    mix = master(L, SR)
    write_wav("honey-static.wav", mix, SR)
    print("Wrote honey-static.wav", mix.shape, "peak", np.max(np.abs(mix)))


def bar_time(tb):
    """Global time of (bar, beat) - bars are local to sections, so walk."""
    total = 0.0
    for section in N.SECTIONS:
        name, start, nbars, chords, style, beats = section
        blen = bar_len(section)
        if tb < start + nbars:
            return total + (tb - start) * blen
        total += nbars * blen
    return total


def make_spoken(text):
    base = "/tmp/honey_spk"
    subprocess.run(["say", "-v", "Whisper", "-o", base + ".aiff", text],
                   check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@22050",
                    base + ".aiff", base + ".wav"], check=True)
    with wave.open(base + ".wav", "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()),
                          dtype="<i2").astype(np.float64) / 32768.0
    x1 = np.interp(np.linspace(0, len(x) - 1, len(x) * 2), np.arange(len(x)), x)
    out = np.interp(np.linspace(0, (len(x1) - 1) * 0.82, len(x1)),
                    np.arange(len(x1)), x1)
    out = np.tanh(out * 0.7) * 0.8
    peak = np.max(np.abs(out))
    if peak > 1e-9:
        out = out / peak * 0.2
    n_atk = int(0.008 * SR)
    out[:n_atk] *= np.linspace(0, 1, n_atk)
    return out


if __name__ == "__main__":
    main()
