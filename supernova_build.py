"""Static Supernova - render engine (Oasis-inspired indie anthem).
Run: python3 supernova_build.py -> static-supernova.wav
"""
import numpy as np

import supernova_notes as N
from instruments import (note_freq, ep, bass, strings, lead, choir, ks, clap)
from drums import kick, snare, hat, tamb, crash
from dsp import filt, make_ir, reverb, delay, master, write_wav
from supernova_drums import (drum_events, KICK, SNARE, HAT, TAMB, CLAP, CRASH)

SR = N.SR
BEAT = N.BEAT
rng = np.random.default_rng(13)

TOTAL = int((sum(s[2] for s in N.SECTIONS) * N.BAR + 4.0) * SR)


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
    return rng.uniform(-0.006, 0.006)


def strum(buf, chord, t0, amp, pan=0.4, spread=0.008):
    """KS guitar strum: strings plucked 8ms apart (down-up feel)."""
    freqs = [note_freq(m) for m in N.GUITAR[chord]]
    for i, f in enumerate(freqs):
        place(buf, ks(f, 1.6, amp * (1.0 - i * 0.08), SR),
              t0 + i * spread, pan)


def render_section(section, L, send, offset):
    name, start, nbars, chords, style = section
    for i in range(nbars):
        t0 = offset + i * N.BAR
        ch = chords[i % len(chords)]
        # Guitar strums (swung eighths)
        for s in [0.0, 2.0 / 3.0, 1.0, 1.0 + 2.0 / 3.0, 2.0,
                  2.0 + 2.0 / 3.0, 3.0, 3.0 + 2.0 / 3.0]:
            if style in ("intro", "outro") and s not in (0.0, 1.0, 2.0, 3.0):
                continue
            if style == "verse" and s in (1.0 + 2.0 / 3.0, 3.0 + 2.0 / 3.0):
                strum(L, ch, t0 + (s + jit()) * BEAT, 0.16)
            else:
                strum(L, ch, t0 + (s + jit()) * BEAT, 0.20)
        # EP pad ring
        for m in N.PAD[ch]:
            place(L, ep(note_freq(m), N.BAR * 1.2, 0.045, SR), t0, 0.35)
        # Bass (swung pulse, roots + 5ths)
        root = N.BASS[ch]
        pat = [(0, 0, 1.33), (1.33, 7, 0.67), (2, 0, 1.33), (3.33, 0, 0.67)]
        if style == "chorus":
            pat = [(0, 0, 0.67), (0.67, 7, 0.67), (1.33, 0, 0.67),
                   (2, 0, 0.67), (2.67, 7, 0.67), (3.33, 0, 0.67)]
        for b, off, d in pat:
            place(L, bass(note_freq(root + off), d * BEAT, 0.22, SR),
                  t0 + (b + jit()) * BEAT, 0.5)
        # Drums
        for ev in drum_events(style, i + 1):
            b, inst, amp = ev[0], ev[1], ev[2]
            if inst == KICK:
                sig = kick(amp, SR)
            elif inst == SNARE:
                sig = snare(amp, SR)
            elif inst == HAT:
                sig = hat(amp, SR)
            elif inst == TAMB:
                sig = tamb(amp, SR)
            elif inst == CLAP:
                sig = clap(amp, SR)
            else:
                sig = crash(amp, SR)
            place(L, sig, t0 + (b + jit()) * BEAT, 0.5)
        # Strings in big sections
        if style in ("pre", "chorus", "bridge", "solo"):
            amp, cut = (0.20, 1300) if style == "pre" else (0.40, 1500)
            freqs = [note_freq(m) for m in N.PAD[ch]]
            sig = strings(freqs, N.BAR * 1.2, amp, SR, cut)
            place(L, sig, t0, 0.5)
            send += to_send(sig * 0.6, t0, send)
    # Melody
    if name in ("verse", "pre", "chorus", "chorus2", "bridge", "chorus3"):
        mkey = "chorus" if name.startswith("chorus") else name
        lead_amp = {"verse": 0.4, "pre": 0.35, "chorus": 0.55,
                    "chorus2": 0.55, "chorus3": 0.55, "bridge": 0.42}.get(name, 0.4)
        for lb, b, m, d in N.MELODY[mkey]:
            t = offset + (lb - 1) * N.BAR + b * BEAT
            sig = lead(note_freq(m), d * BEAT, lead_amp, SR)
            place(L, delay(sig, SR), t, 0.55)
            send += to_send(sig * 0.3, t, send)
            if name in ("chorus2", "chorus3"):  # 3rd harmony
                h = lead(note_freq(m - 3), d * BEAT, 0.13, SR)
                place(L, h, t + 0.01, 0.6)
                send += to_send(h * 0.3, t, send)
            if name in ("chorus", "chorus2", "chorus3"):
                o = lead(note_freq(m + 12), d * BEAT, 0.07, SR)
                place(L, o, t + 0.005, 0.7)


def main():
    L = np.zeros((TOTAL, 2), dtype=np.float64)
    send = np.zeros(TOTAL)
    ir0, ir1 = make_ir(SR, seed=0), make_ir(SR, seed=1)
    offsets = []
    acc = 0.0
    for s in N.SECTIONS:
        offsets.append(acc)
        acc += s[2] * N.BAR

    for idx, section in enumerate(N.SECTIONS):
        render_section(section, L, send, offsets[idx])

    # Guitar solo (E major pentatonic, KS plucks, 4 bars)
    penta = [52, 54, 56, 59, 61, 64, 66, 68]
    srng = np.random.default_rng(42)
    idx2 = 3
    solo_off = offsets[8]
    for bar in range(4):
        t0 = solo_off + bar * N.BAR
        for i in range(12):
            if i % 3 == 2:
                idx2 = min(7, max(0, idx2 + int(srng.integers(-2, 3))))
                m = penta[idx2]
                d = 0.67
            else:
                m = penta[max(0, idx2 - 1)]
                d = 0.33
            t = t0 + (i * 0.33 + jit()) * BEAT
            place(L, ks(note_freq(m), 1.2, 0.60, SR), t, 0.45)
        if bar == 3:  # end solo on held E5
            place(L, ks(note_freq(64), 2.5, 0.70, SR),
                  t0 + 3 * BEAT, 0.45)

    # Outro "la la" choir (swung pulses)
    outro_off = offsets[10]
    for i in range(12):
        t0 = outro_off + i * N.BAR
        ch = "E" if i % 2 == 0 else "A"
        freqs = [note_freq(m) for m in N.OUTRO_LA[ch]]
        for j in range(4):
            t = t0 + j * BEAT
            sig = choir(freqs, 0.5, 0.35, SR)
            place(L, sig, t, 0.5)
            send += to_send(sig * 0.4, t, send)

    # Vinyl crackle (light indie grit)
    cr = crackle_bed()
    L[:, 0] += cr
    L[:, 1] += cr * 0.95

    wet = reverb(send, SR, ir0, wet=1.0) - send
    wet2 = reverb(send, SR, ir1, wet=1.0) - send
    L[:, 0] += wet * 0.4
    L[:, 1] += wet2 * 0.4

    mix = master(L, SR)
    write_wav("static-supernova.wav", mix, SR)
    print("Wrote static-supernova.wav", mix.shape, "peak", np.max(np.abs(mix)))


def crackle_bed():
    from drums import crackle
    cr = crackle(TOTAL / SR, 1.0, SR)
    env = np.ones(TOTAL)
    n12 = int(12 * SR)
    env[:n12] = np.linspace(1.3, 0.7, n12)
    env[int(120 * SR):] = np.linspace(0.7, 1.4, TOTAL - int(120 * SR))
    return cr * env * 0.03


if __name__ == "__main__":
    main()
