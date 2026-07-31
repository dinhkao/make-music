"""TGI chord loops - render THE GREAT INDOORS progressions with the
magbay loop engine (render.py) and merge into ONE file.
Run: python3 tgi-loops.py -> THE-GREAT-INDOORS-VONG-HOP-AM.wav
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from render import render_file, write_wav, SR
from gi_engine import nn

CH = {'Amaj7':['A2','C#4','E4','G#4'],'C#7':['C#3','F3','G#3','B3'],
    'Dmaj7':['D3','F#3','A3','C#4'],'D#dim7':['D#3','F#3','A3','C4'],
    'A/E':['E2','A3','C#4','E4'],'F#7':['F#2','A#3','C#4','E4'],
    'Bm7':['B2','D3','F#3','A3'],'E7sus4':['E2','A3','B3','D4'],
    'A/C#':['C#3','E3','A3','C#4'],'E7':['E2','G#3','B3','D4'],
    'G#':['G#2','C4','D#4','G#4'],'C':['C3','E3','G3','C4'],
    'B7':['B2','D#3','F#3','A3'],'A7':['A2','C#4','E4','G4'],
    'D':['D3','F#3','A3','D4'],'G':['G2','B3','D4','G4'],
    'Gmaj7':['G2','B3','D4','F#4'],'Bm':['B2','D3','F#3','B3'],
    'Bm/A':['A2','D3','F#3','B3'],'A':['A2','C#4','E4','A4']}

PROG = {
    'intro':  ['Amaj7','C#7','Dmaj7','D#dim7'],
    'verse':  ['Amaj7','C#7','Dmaj7','D#dim7','A/E','F#7','Bm7','E7sus4'],
    'refrain':['Dmaj7','A/C#','Bm7','E7sus4','Dmaj7','A/C#','Bm7','E7'],
    'bridge': ['G#','Amaj7','G#','Amaj7','C','Dmaj7','C','Dmaj7'],
    'ramp':   ['F#7','B7','E7','A7'],
    'outro':  ['D','Dmaj7','G','Gmaj7','Bm','Bm/A','G','A'],
    'tag':    ['Amaj7'],
}

TPQ = 480
TEMPO = 118


def vlq(n):
    """MIDI variable-length quantity: most-significant 7-bit group first."""
    groups = [n & 0x7F]
    n >>= 7
    while n:
        groups.append(n & 0x7F)
        n >>= 7
    groups.reverse()
    return bytes([(g | 0x80) for g in groups[:-1]] + [groups[-1]])


def make_midi(path, prog):
    events = [(0, b'\xFF\x51\x03' + struct.pack('>I', 60000000 // TEMPO)[1:]),
              (0, b'\xFF\x58\x04' + bytes([4, 2, 24, 8]))]
    for bar, cn in enumerate(prog):
        t0 = bar * TPQ * 4
        for n in CH[cn]:
            m = nn(n)
            events.append((t0, bytes([0x90, m, 90])))
            events.append((t0 + TPQ * 4 - 10, bytes([0x80, m, 0])))
    events.sort()
    track = b''
    prev = 0
    for t, e in events:
        track += vlq(t - prev) + e
        prev = t
    track += b'\x00\xFF\x2F\x00'
    data = (b'MThd' + struct.pack('>IHHH', 6, 0, 1, TPQ)
            + b'MTrk' + struct.pack('>I', len(track)) + track)
    open(path, 'wb').write(data)


if __name__ == '__main__':
    os.makedirs('tgi-loops', exist_ok=True)
    combined = []
    for name, prog in PROG.items():
        mid = f'tgi-loops/{name}.mid'
        make_midi(mid, prog)
        a, tempo = render_file(mid)
        write_wav(f'tgi-loops/{name}.wav', a)
        combined.append(a)
        combined.append(np.zeros((int(1.0 * SR), 2), dtype=np.float32))
        print(f"{name:8s} {tempo:.0f}bpm {len(a)/SR:6.1f}s  ({len(prog)} bars x2)")
    merged = np.concatenate(combined)
    write_wav('THE-GREAT-INDOORS-VONG-HOP-AM.wav', merged)
    print(f"\nMERGED: THE-GREAT-INDOORS-VONG-HOP-AM.wav  {len(merged)/SR:.1f}s  "
          f"peak {float(np.abs(merged).max()):.3f}")
