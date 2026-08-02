#!/usr/bin/env python3
"""
01-opus-klezmer.py — Klezmer Post-Rock / Post-Punk (inspired by Black Country, New Road 'Opus' & 'Instrumental')
D Phrygian Dominant / Freygish scale (D, Eb, F#, G, A, Bb, C).
Nick Villa drum style: 7/8 syncopated accents (3+2+2), fast modal tom rolls, hi-hat chokes, explosive 4/4 klezmer dance section.
Outputs: 01-opus-klezmer.mp3 and 01-opus-klezmer-instrumental.mp3
"""
import os
import sys
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "01-opus-klezmer"

import re

def nn(s):
    m = re.match(r"^([A-Ga-g][#b]?)[^\d]*(\d+)$", s)
    if m:
        note_part, oct_part = m.group(1).upper(), int(m.group(2))
        base = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        n = base[note_part[0]]
        if len(note_part) > 1:
            n += 1 if note_part[1] == '#' else -1
        return 12 * (oct_part + 1) + n
    return 60

def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

# --- DSP & Synthesis ---
def env(L, a, d, s, r):
    e = np.ones(L)
    ai = min(int(a * SR), L)
    if ai > 0: e[:ai] = np.linspace(0, 1, ai)
    di = int(d * SR)
    if ai + di < L: e[ai:ai+di] = np.linspace(1, s, di); e[ai+di:] = s
    else: e[ai:] = np.linspace(1, s, max(L - ai, 1))
    ri = min(int(r * SR), L)
    if ri > 0: e[L-ri:] *= np.linspace(1, 0, ri)**1.3
    return e

def put(b, t0, x, g=1.0):
    i = int(t0 * SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(b) - i)
    if n > 0: b[i:i+n] += x[:n] * g

_KS = {}
def ks(m, dur, damp=0.996, bright=0.6, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m)
    N = max(int(round(SR / f)), 2)
    L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1000 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(900 + 7000 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.5)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def horn(m, dur, g=0.12, rough=0.8, det=0.0):
    L = int(dur * SR) + int(0.2 * SR)
    t = np.arange(L) / SR
    f = hz(m) * 2**(det / 1200)
    vf = 1 + 0.005 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t * 2.0)
    ph = 2 * np.pi * np.cumsum(f * vf) / SR
    x = sum(np.sin(ph * k) / (k**1.1) for k in range(1, 16))
    x = np.tanh(x * (1.1 + rough))
    bq, aq = sg.butter(2, [250 / (SR / 2), 4800 / (SR / 2)], 'band')
    x = sg.lfilter(bq, aq, x)
    return (x * env(L, 0.04, 0.15, 0.82, 0.18) * g).astype(np.float32)

def bassn(m, dur, g=0.28):
    L = int(dur * SR) + int(0.15 * SR)
    t = np.arange(L) / SR
    f = hz(m)
    ph = 2 * np.pi * f * t
    x = np.sin(ph) * 0.7 + np.sin(2 * ph) * 0.3 + np.sin(3 * ph) * 0.15
    x = np.tanh(x * 1.6)
    bq, aq = sg.butter(2, 650 / (SR / 2), 'low')
    x = sg.lfilter(bq, aq, x)
    return (x * env(L, 0.008, 0.08, 0.85, 0.1) * g).astype(np.float32)

def organ(m, dur, g=0.10):
    L = int(dur * SR) + int(0.1 * SR)
    t = np.arange(L) / SR
    f = hz(m)
    x = sum(np.sin(2 * np.pi * f * k * t) * (1.0 / k**0.8) for k in (1, 2, 3, 4, 6))
    x *= (1 + 0.06 * np.sin(2 * np.pi * 6.0 * t))
    bq, aq = sg.butter(2, 3500 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.01, 0.05, 0.9, 0.08) * g).astype(np.float32)

# --- Drum Kit (Nick Villa Style) ---
IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng, glide=0.05):
    t = np.arange(L) / SR
    g = 1 + glide * np.exp(-t / 0.02)
    ph = 2 * np.pi * np.cumsum(f0 * g) / SR
    out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        f = f0 * r
        if f < SR / 2.1:
            out += gn * np.exp(-t / tau) * np.sin(ph * (r + rng.uniform(-0.01, 0.01)))
    return out

class DrumKit:
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=48):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.5 * np.exp(-t / 0.025))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
        x += self.rng.standard_normal(L) * np.exp(-t / 0.005) * 0.2
        return (np.tanh(x * 1.5) * vel).astype(np.float32)
    def snare(self, vel=1.0, art='center'):
        L = int(0.35 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1])
        taus = np.array([0.05, 0.15, 0.12, 0.08, 0.06, 0.05])
        body = modal(190, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1200 / (SR / 2), 8500 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / (0.12 if art=='center' else 0.06))
        stick = self.rng.standard_normal(L) * np.exp(-t / 0.003) * 0.5
        x = body * 0.6 + wire * 0.8 + stick
        return (np.tanh(x * 1.3) * vel * (0.35 if art=='ghost' else 1.0)).astype(np.float32)
    def tom(self, vel=1.0, tune=110):
        L = int(0.55 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.7, 0.5, 0.3, 0.2, 0.1])
        taus = np.array([0.25, 0.2, 0.15, 0.12, 0.1, 0.08])
        x = modal(tune, taus, g, L, self.rng, glide=0.08)
        stick = self.rng.standard_normal(L) * np.exp(-t / 0.004) * 0.4
        return (np.tanh((x + stick) * 1.2) * vel).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.25 if op else 0.05) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 7500 / (SR / 2), 'high')
        x = sg.lfilter(bq, aq, n) * np.exp(-t / (0.18 if op else 0.025))
        return (x * vel * 0.4).astype(np.float32)

# --- Song Composition ---
def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(101)
    kit = DrumKit(77)
    
    TOTAL_SEC = 156.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    bpm_78 = 140.0
    s_per_8th = 60.0 / bpm_78
    bar78 = 7 * s_per_8th
    
    t_curr = 0.0
    chords_78 = [
        ('D2', ['D3', 'F3', 'A3']),
        ('D2', ['D3', 'F3', 'A3']),
        ('Eb2', ['Eb3', 'G3', 'Bb3']),
        ('F#2', ['F#3', 'A3', 'C4']),
        ('G2', ['G3', 'Bb3', 'D4']),
        ('A2', ['A3', 'C#4', 'E4']),
    ]
    
    for bar_idx in range(6):
        b_root, b_notes = chords_78[bar_idx % len(chords_78)]
        for step, beat_off in enumerate([0, 2, 4, 5]):
            t_note = t_curr + beat_off * s_per_8th + rng.uniform(-0.005, 0.005)
            put(inst_bus, t_note, bassn(nn(b_root), s_per_8th * 1.5, g=0.25))
            for n_str in b_notes:
                put(inst_bus, t_note, ks(nn(n_str), s_per_8th * 1.2, bright=0.5, seed=bar_idx*10+step), g=0.04)
        
        put(inst_bus, t_curr + 0 * s_per_8th, kit.kick(1.0))
        put(inst_bus, t_curr + 2 * s_per_8th, kit.hat(0.6))
        put(inst_bus, t_curr + 3 * s_per_8th, kit.snare(0.95))
        put(inst_bus, t_curr + 5 * s_per_8th, kit.kick(0.85))
        put(inst_bus, t_curr + 6 * s_per_8th, kit.snare(0.4, art='ghost'))
        put(inst_bus, t_curr + 6.5 * s_per_8th, kit.hat(0.8, op=True))
        
        t_curr += bar78

    klezmer_theme = [
        (0, 'D4', 1), (1, 'Eb4', 1), (2, 'F#4', 1), (3, 'G4', 2), (5, 'F#4', 1), (6, 'Eb4', 1),
        (7, 'D4', 2), (9, 'Eb4', 1), (10, 'F#4', 2), (12, 'Eb4', 2),
        (14, 'F#4', 1), (15, 'G4', 1), (16, 'A4', 1), (17, 'Bb4', 2), (19, 'A4', 1), (20, 'G4', 1),
        (21, 'F#4', 2), (23, 'Eb4', 1), (24, 'D4', 4)
    ]
    
    for loop in range(2):
        for off_8, note_s, d_8 in klezmer_theme:
            t_note = t_curr + off_8 * s_per_8th + rng.uniform(-0.006, 0.006)
            d_sec = d_8 * s_per_8th
            put(lead_bus, t_note, horn(nn(note_s), d_sec, g=0.18, rough=0.9), g=1.0)
            put(lead_bus, t_note, ks(nn(note_s)+12, d_sec*0.8, bright=0.75, seed=off_8), g=0.06)

        for b_idx in range(4):
            b_t = t_curr + b_idx * bar78
            b_root, b_notes = chords_78[b_idx % len(chords_78)]
            for step, beat_off in enumerate([0, 2, 4, 5]):
                put(inst_bus, b_t + beat_off * s_per_8th, bassn(nn(b_root), s_per_8th * 1.5, g=0.28))
                for n_str in b_notes:
                    put(inst_bus, b_t + beat_off * s_per_8th, organ(nn(n_str), s_per_8th * 1.2), g=0.05)
            
            put(inst_bus, b_t + 0 * s_per_8th, kit.kick(1.0))
            put(inst_bus, b_t + 2 * s_per_8th, kit.snare(0.8, art='center'))
            put(inst_bus, b_t + 4 * s_per_8th, kit.kick(0.9))
            put(inst_bus, b_t + 5 * s_per_8th, kit.snare(1.0, art='center'))
            if b_idx % 2 == 1:
                put(inst_bus, b_t + 6 * s_per_8th, kit.tom(0.9, tune=140))
                put(inst_bus, b_t + 6.5 * s_per_8th, kit.tom(1.0, tune=90))
        
        t_curr += 4 * bar78

    bpm_44 = 156.0
    spb = 60.0 / bpm_44
    bar44 = 4 * spb
    
    klezmer_fast_chords = [
        ('D3', ['D4', 'F#4', 'A4']),
        ('Eb3', ['Eb4', 'G4', 'Bb4']),
        ('Cm3', ['C4', 'Eb4', 'G4']),
        ('D3', ['D4', 'F#4', 'A4']),
    ]
    
    for bar_idx in range(16):
        b_t = t_curr + bar_idx * bar44
        c_root, c_notes = klezmer_fast_chords[bar_idx % len(klezmer_fast_chords)]
        
        for beat in range(4):
            b_m = nn(c_root) if beat % 2 == 0 else nn(c_root) + 7
            put(inst_bus, b_t + beat * spb, bassn(b_m, spb * 0.9, g=0.32))
            for n_s in c_notes:
                put(inst_bus, b_t + (beat + 0.5) * spb, ks(nn(n_s), spb * 0.6, bright=0.7, seed=bar_idx*4+beat), g=0.05)
        
        put(inst_bus, b_t + 0 * spb, kit.kick(1.0))
        put(inst_bus, b_t + 1 * spb, kit.snare(0.95))
        put(inst_bus, b_t + 1.5 * spb, kit.kick(0.85))
        put(inst_bus, b_t + 2 * spb, kit.kick(0.9))
        put(inst_bus, b_t + 3 * spb, kit.snare(1.0))
        put(inst_bus, b_t + 3.5 * spb, kit.hat(0.9, op=True))
        
        for h_step in np.arange(0, 4, 0.5):
            if h_step != 3.5:
                put(inst_bus, b_t + h_step * spb + rng.uniform(-0.003, 0.003), kit.hat(0.6))
        
        if bar_idx >= 4:
            run_notes = ['D5', 'Eb5', 'F#5', 'G5', 'A5', 'Bb5', 'C6', 'D6']
            for step in range(8):
                if (bar_idx + step) % 3 != 0:
                    n_s = run_notes[(bar_idx * 2 + step) % len(run_notes)]
                    t_n = b_t + (step * 0.5) * spb + rng.uniform(-0.005, 0.005)
                    put(lead_bus, t_n, horn(nn(n_s), spb * 0.6, g=0.16, rough=0.7), g=1.0)

    t_curr += 16 * bar44

    for bar_idx in range(8):
        b_t = t_curr + bar_idx * bar44
        g_mult = 1.0 + bar_idx * 0.04
        
        put(inst_bus, b_t + 0 * spb, bassn(nn('D2'), spb * 2, g=0.35 * g_mult))
        put(inst_bus, b_t + 2 * spb, bassn(nn('Eb2'), spb * 2, g=0.35 * g_mult))
        
        for n_s in ['D4', 'F#4', 'A4', 'D5']:
            put(lead_bus, b_t + 0 * spb, horn(nn(n_s), spb * 1.8, g=0.15 * g_mult), g=1.0)
            put(lead_bus, t_curr + 2 * spb, horn(nn(n_s) + 1, spb * 1.8, g=0.15 * g_mult), g=1.0)
            
        put(inst_bus, b_t + 0 * spb, kit.kick(1.1))
        put(inst_bus, b_t + 1 * spb, kit.snare(1.1))
        put(inst_bus, b_t + 2 * spb, kit.tom(1.0, tune=160))
        put(inst_bus, b_t + 2.5 * spb, kit.tom(1.0, tune=120))
        put(inst_bus, b_t + 3 * spb, kit.tom(1.1, tune=80))
        put(inst_bus, b_t + 3.5 * spb, kit.snare(1.2))

    t_curr += 8 * bar44
    put(inst_bus, t_curr, kit.kick(1.2))
    put(inst_bus, t_curr, kit.snare(1.2))
    put(inst_bus, t_curr, bassn(nn('D1'), 3.0, g=0.4))
    for n_s in ['D3', 'F#3', 'A3', 'D4']:
        put(lead_bus, t_curr, horn(nn(n_s), 3.0, g=0.2), g=1.0)

    print("Mixing and writing WAVs...")
    ir_len = int(1.2 * SR)
    ir = np.random.default_rng(12).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.4 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.25):
        padded = np.concatenate([np.zeros(int(0.02 * SR)), sig])
        res = sg.fftconvolve(padded, ir)[:len(sig)]
        return sig + wet * res

    mix_full = lead_bus + inst_bus
    mix_inst = inst_bus

    mix_full = np.tanh(apply_reverb(mix_full) * 1.2) * 0.85
    mix_inst = np.tanh(apply_reverb(mix_inst) * 1.2) * 0.85

    stereo_full = np.vstack([mix_full, mix_full]).T
    stereo_inst = np.vstack([mix_inst, mix_inst]).T

    wav_full = f"{NAME}.wav"
    wav_inst = f"{NAME}-instrumental.wav"
    mp3_full = f"{NAME}.mp3"
    mp3_inst = f"{NAME}-instrumental.mp3"

    import wave
    for pth, stm in [(wav_full, stereo_full), (wav_inst, stereo_inst)]:
        pcm = (np.clip(stm, -1, 1) * 32767.0).astype("<i2")
        with wave.open(pth, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(pcm.tobytes())

    print("Encoding MP3s with ffmpeg...")
    subprocess.run(["ffmpeg", "-y", "-i", wav_full, "-b:a", "320k", mp3_full], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", wav_inst, "-b:a", "320k", mp3_inst], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(wav_full): os.remove(wav_full)
    if os.path.exists(wav_inst): os.remove(wav_inst)
    print(f"Done: {mp3_full} & {mp3_inst}")

if __name__ == "__main__":
    build_song()
