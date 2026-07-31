import struct, glob, os, numpy as np
from scipy import signal as sg

SR = 44100

# ---------- MIDI parse ----------
def parse_midi(path):
    d = open(path,'rb').read()
    tpq = struct.unpack('>H', d[12:14])[0]
    ln = struct.unpack('>I', d[18:22])[0]
    trk = d[22:22+ln]
    i=0; t=0; tempo=120; running=None; on={}; notes=[]
    def rv(i):
        n=0
        while True:
            b=trk[i]; i+=1; n=(n<<7)|(b&0x7F)
            if not b&0x80: return n,i
    while i < len(trk):
        dt,i = rv(i); t += dt
        b = trk[i]
        if b == 0xFF:
            i+=1; mt=trk[i]; i+=1; l,i=rv(i)
            if mt==0x51: tempo = 60_000_000/int.from_bytes(trk[i:i+3],'big')
            i+=l
            if mt==0x2F: break
        else:
            if b & 0x80: running=b; i+=1
            st=running>>4; n=trk[i]; v=trk[i+1]; i+=2
            if st==0x9 and v>0: on.setdefault(n,[]).append((t,v))
            else:
                if on.get(n):
                    t0,v0 = on[n].pop(0)
                    notes.append((t0/tpq, (t-t0)/tpq, n, v0))
    return tempo, sorted(notes)

# ---------- synth ----------
def adsr(n, a, d, s, r):
    env = np.ones(n)
    ai=int(a*SR); di=int(d*SR); ri=int(r*SR)
    ai=min(ai,n); env[:ai]=np.linspace(0,1,ai)
    if ai+di<n: env[ai:ai+di]=np.linspace(1,s,di); env[ai+di:]=s
    else: env[ai:]=np.linspace(1,s,n-ai)
    ri=min(ri,n); env[n-ri:]*=np.linspace(1,0,ri)
    return env

def saw(f, n, harm_cap=14):
    t = np.arange(n)/SR
    K = int(min(harm_cap, (SR/2.2)//max(f,1)))
    out = np.zeros(n)
    for k in range(1, max(K,1)+1):
        out += np.sin(2*np.pi*f*k*t)/k
    return out*0.55

def sine(f, n):
    return np.sin(2*np.pi*f*np.arange(n)/SR)

def hz(m): return 440.0*2**((m-69)/12)

def render_pad(notes, total_s):
    buf = np.zeros(int(total_s*SR)+SR)
    for st, du, n, v in notes:
        L = int((du+0.7)*SR)
        e = adsr(L, 0.045, 0.35, 0.72, 0.55)
        f = hz(n)
        x = (saw(f*2**(-9/1200), L) + saw(f, L) + saw(f*2**(9/1200), L))/3
        x = x*e*(v/127)*0.20
        i0 = int(st*SR); buf[i0:i0+L] += x
    return buf

def render_sub(notes, total_s):
    buf = np.zeros(int(total_s*SR)+SR)
    # lowest note of each chord onset
    by_start = {}
    for st,du,n,v in notes: by_start.setdefault(round(st,4),[]).append((n,du))
    for st, lst in by_start.items():
        n, du = min(lst)
        L = int((du+0.25)*SR)
        f = hz(n-12)
        if f < 30: f *= 2
        e = adsr(L, 0.006, 0.10, 0.85, 0.20)
        buf[int(st*SR):int(st*SR)+L] += sine(f, L)*e*0.34
    return buf

def render_pluck(notes, total_s, beat_s):
    buf = np.zeros(int(total_s*SR)+SR)
    by_start = {}
    for st,du,n,v in notes: by_start.setdefault(round(st,4),[]).append(n)
    dur_at = {}
    for s_,d_,n_,v_ in notes: dur_at[round(s_,4)] = max(dur_at.get(round(s_,4),0), d_)
    for st, ns in sorted(by_start.items()):
        ns = sorted(ns)
        du = dur_at[st]
        step = beat_s/2
        k = 0; tt = st*60/60
        pos = st
        while pos < st+du-1e-6:
            n = ns[k % len(ns)] + 12
            if n > 96: n -= 12
            L = int(0.45*SR)
            f = hz(n)
            t = np.arange(L)/SR
            env = np.exp(-t*7.0)
            x = (np.sin(2*np.pi*f*t + 2.2*np.exp(-t*11)*np.sin(2*np.pi*f*3.5*t)))*env
            i0 = int(pos*SR)
            buf[i0:i0+L] += x*0.085
            pos += step
            k += 1
    return buf

def chorus(x):
    n=len(x); t=np.arange(n)/SR
    def tap(rate, depth_ms, ph):
        d = (12 + depth_ms*np.sin(2*np.pi*rate*t + ph))/1000*SR
        idx = np.arange(n) - d
        idx = np.clip(idx, 0, n-1)
        i0 = idx.astype(int); fr = idx-i0
        i1 = np.minimum(i0+1, n-1)
        return x[i0]*(1-fr) + x[i1]*fr
    l = 0.72*x + 0.5*tap(0.27, 5.5, 0.0) + 0.3*tap(0.41, 3.0, 1.1)
    r = 0.72*x + 0.5*tap(0.31, 5.5, 2.3) + 0.3*tap(0.37, 3.0, 3.9)
    return l, r

def wobble(x, rate=0.7, cents=6.0):
    n=len(x); t=np.arange(n)/SR
    dev = (2**((cents*np.sin(2*np.pi*rate*t))/1200) - 1)
    idx = np.cumsum(1+dev)
    idx = np.clip(idx, 0, n-1)
    i0=idx.astype(int); fr=idx-i0; i1=np.minimum(i0+1,n-1)
    return x[i0]*(1-fr)+x[i1]*fr

_IR = {}
def _ir(decay=1.6):
    if decay in _IR: return _IR[decay]
    n = int(decay*SR)
    rng = np.random.default_rng(7)
    env = np.exp(-np.arange(n)/(decay*SR/4.2))
    irL = rng.standard_normal(n)*env; irR = rng.standard_normal(n)*env
    b,a = sg.butter(2, 3600/(SR/2), 'low')
    irL = sg.lfilter(b,a,irL); irR = sg.lfilter(b,a,irR)
    irL[:int(0.035*SR)] = 0; irR[:int(0.035*SR)] = 0
    irL/=np.abs(irL).sum()/8; irR/=np.abs(irR).sum()/8
    _IR[decay]=(irL,irR); return _IR[decay]

def reverb(l, r, decay=1.6, wet=0.28):
    irL, irR = _ir(decay)
    wl = sg.fftconvolve(l, irL)[:len(l)]
    wr = sg.fftconvolve(r, irR)[:len(r)]
    return l*(1-wet)+wl*wet, r*(1-wet)+wr*wet

def render_file(path):
    tempo, notes = parse_midi(path)
    beat = 60.0/tempo
    end_beats = max(s+d for s,d,n,v in notes)
    # two passes
    notes2 = notes + [(s+end_beats, d, n, v) for s,d,n,v in notes]
    total_b = end_beats*2
    # beats -> seconds
    ns = [(s*beat, d*beat, n, v) for s,d,n,v in notes2]
    total_s = total_b*beat + 1.6
    pad = render_pad(ns, total_s)
    sub = render_sub(ns, total_s)
    plk = render_pluck(ns, total_s, beat)
    mono = pad + sub*0.9 + plk
    mono = wobble(mono)
    b,a = sg.butter(2, 5200/(SR/2), 'low'); mono = sg.lfilter(b,a,mono)
    l, r = chorus(mono)
    l, r = reverb(l, r)
    st = np.stack([l,r])
    st = np.tanh(st*1.25)*0.92
    st /= max(np.abs(st).max(), 1e-9); st *= 0.89
    # fade
    f = int(0.03*SR); st[:,:f]*=np.linspace(0,1,f); st[:,-int(0.35*SR):]*=np.linspace(1,0,int(0.35*SR))
    return st.T.astype(np.float32), tempo

def write_wav(path, data):
    d = np.clip(data, -1, 1)
    pcm = (d*32767).astype('<i2')
    n = pcm.size*2
    with open(path,'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,2,SR,SR*4,4,16)+b'data'+struct.pack('<I',n))
        f.write(pcm.tobytes())

if __name__ == '__main__':
    files = sorted(glob.glob('/home/claude/magbay-midi/**/*.mid', recursive=True))
    out = '/home/claude/magbay-audio'
    combined = []
    for p in files:
        rel = os.path.relpath(p, '/home/claude/magbay-midi')
        dst = os.path.join(out, os.path.dirname(rel))
        os.makedirs(dst, exist_ok=True)
        a, tempo = render_file(p)
        name = os.path.basename(p)[:-4]
        write_wav(os.path.join(dst, name+'.wav'), a)
        combined.append(a)
        combined.append(np.zeros((int(1.0*SR),2), dtype=np.float32))
        print(name, f"{tempo:.0f}bpm", f"{len(a)/SR:.1f}s")
    write_wav('/home/claude/magbay-audio/_TAT-CA-38-VONG.wav', np.concatenate(combined))
    print("total", sum(len(c) for c in combined)/SR, "s")
