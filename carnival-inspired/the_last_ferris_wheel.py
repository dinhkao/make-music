#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE LAST FERRIS WHEEL  -  a song inspired by The Cardigans' "Carnival" (album: Life, 1995)
======================================================================================
Self-contained: only numpy + scipy (+ stdlib + ffmpeg via subprocess).
Builds the WHOLE arrangement from raw synthesis (no samples, no MIDI libs).
Outputs:
    the_last_ferris_wheel.wav          (full mix)
    the_last_ferris_wheel_instrumental.wav   (no vocals)
    the_last_ferris_wheel.mp3         (192k)
    the_last_ferris_wheel_instrumental.mp3   (192k)

Imagery: a faded carnival at night, a last ferris-wheel ride reaching for someone
you can never quite touch.  Bouncy-but-melancholy, loungy jazz harmonism
(harmonic-minor + neapolitan + ii-V-I extended), but a darker homemade-synth
take rather than a vintage-band pastiche.  All "instruments" synthesised below.

Run:  python3 the_last_ferris_wheel.py
"""
import os, sys, wave, struct, subprocess, math
import numpy as np
from scipy import signal

# ----------------------------------------------------------------------------
# 0.  GLOBALS
# ----------------------------------------------------------------------------
SR        = 44100
A4        = 440.0
BPM       = 122.0
SPB       = 60.0 / BPM                 # seconds per beat
N_CHORUS  = 2                          # how many times chorus lyric returns
SEED      = 7
np.random.seed(SEED)

def mtof(m):  return A4 * 2 ** ((m - 69) / 12.0)
def db(x):    return 10.0 ** (x / 20.0)
def clk(b):   return int(round(b * SPB * SR))   # beats -> samples

# note name parser  "C4"->60  "Bb2"->34  "F#5"->78
def pc(name):
    m = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    n,acc,octv = name[0], name[1], name[-1]
    semis = m[n]
    if acc == '#': semis += 1
    elif acc == 'b': semis -= 1
    return semis + 12*(int(octv)+1)

# ----------------------------------------------------------------------------
# 1. SONG FORM  (96 bars, ~3:13)
#    bar indices are 1-based; bar1 beat1 = absolute beat 0
# ----------------------------------------------------------------------------
# section           bars     prog (tiled)
# INTRO              1-8     Amadd9 Bb7#11 E7b9 Amadd9  x2
# VERSE1            9-24     VP x2
# PRE1             25-28     PRE
# CHORUS1          29-44     CH x2
# VERSE2           45-60     VP x2
# PRE2             61-64     PRE
# CHORUS2          65-80     CH x2
# OUTRO            81-96     INTRO x2  (instrumental)
# ----------------------------------------------------------------------------
TOTAL_BARS = 96
TOTAL_BEATS = TOTAL_BARS * 4
TOTAL_SEC = TOTAL_BEATS * SPB + 5.0      # +5s tail for reverb/release
NS = int(TOTAL_SEC * SR)

def ab(bar, beat): return (bar - 1) * 4 + (beat - 1)   # absolute beat

# ----------------------------------------------------------------------------
# 2. CHORD DICTIONARY  (color voicings + bass).  Key: A harmonic minor / C major
#    voicing = mid chord tones used by keys/pad/pluck; bass plays root low.
# ----------------------------------------------------------------------------
VOIC = {
 "Am9"     : [57,60,64,67,71],     # A C E G B
 "Amadd9"  : [57,64,71],           # A E B  (open, mysterious)
 "Am_final": [57,60,64,69,71],     # A C E A B
 "Cmaj9"   : [60,64,71,74],        # C E B D
 "Dm9"     : [62,65,69,72,76],     # D F A C E
 "Fmaj9"   : [53,57,60,64,67],     # F A C E G
 "G13"     : [55,65,69,76],        # G F A E  (jazz drop)
 "E7b9b13" : [56,62,65,72],        # G# D F C  (altered, bass E)
 "E7b9"    : [56,59,62,65],        # G# B D F
 "Bb13#11" : [58,65,69,76],        # Bb F A E  (neapolitan lydian dom)
 "Bb7#11"  : [58,62,65,69],        # Bb D F A
}
BASS = {
 "Am9":45,"Amadd9":45,"Am_final":45,"Am":45,
 "Cmaj9":48,"Dm9":50,"Fmaj9":41,"G13":43,
 "E7b9b13":40,"E7b9":40,
 "Bb13#11":46,"Bb7#11":46,"Bb":46,
}

# build per-bar chord table (1-indexed)
CHBAR = [None]*(TOTAL_BARS+1)
def fill(start,end,prog):
    for i,b in enumerate(range(start,end+1)):
        CHBAR[b] = prog[i % len(prog)]
fill(1,8,  ["Amadd9","Bb7#11","E7b9","Amadd9","Amadd9","Bb7#11","E7b9","Amadd9"])
fill(9,24, ["Dm9","G13","Cmaj9","Fmaj9","Dm9","G13","Cmaj9","E7b9b13"])
fill(25,28,["Fmaj9","Bb13#11","E7b9b13","E7b9b13"])
fill(29,44,["Am9","Dm9","G13","Cmaj9","Fmaj9","Bb13#11","E7b9b13","Am9"])
fill(45,60,["Dm9","G13","Cmaj9","Fmaj9","Dm9","G13","Cmaj9","E7b9b13"])
fill(61,64,["Fmaj9","Bb13#11","E7b9b13","E7b9b13"])
fill(65,80,["Am9","Dm9","G13","Cmaj9","Fmaj9","Bb13#11","E7b9b13","Am9"])
fill(81,96,["Amadd9","Bb7#11","E7b9","Amadd9","Amadd9","Bb7#11","E7b9","Amadd9"])

def chord_of(bar): return CHBAR[bar]

# ----------------------------------------------------------------------------
# 3. SYNTH PRIMITIVES  (all return mono float64 numpy arrays)
# ----------------------------------------------------------------------------
def env_adsr(n, a=0.005, d=0.08, s=0.7, r=0.12, sr=SR):
    """vector adsr over n samples; sustains for the middle, releases at end."""
    out = np.ones(n)
    A = int(a*sr); D = int(d*sr); R = int(r*sr)
    A=max(A,1);D=max(D,1);R=max(R,1)
    if A+D+R < n:
        out[:A] = np.linspace(0,1,A)
        out[A:A+D] = np.linspace(1,s,D)
        out[A+D:n-R] = s
        out[n-R:] = np.linspace(s,0,R)
    else:
        # short note: simple attack/release
        out[:A] = np.linspace(0,1,A)
        out[A:] = np.linspace(1,0,n-A)
    return out

def fade_edges(x, nin=256, nout=512):
    if nin:  x[:nin]  *= np.linspace(0,1,nin)
    if nout: x[-nout:] *= np.linspace(1,0,nout)
    return x

def saw(freq, n, sr=SR, phase0=0.0, n_part=None):
    """naive additive saw with bandlimit by partial count."""
    kmax = n_part or max(2, int(9000.0/max(freq,1)))
    kmax = min(kmax, 80)
    t = np.arange(n)/sr
    out = np.zeros(n)
    for k in range(1,kmax+1):
        out += np.sin(2*np.pi*k*freq*t + phase0)/k
    return (2.0/np.pi)*out

def ks_pluck(freq, dur, amp=1.0, decay=0.0, bright=1.0):
    """Karplus-Strong plucked string."""
    n = int(dur*SR)
    L = max(int(round(SR/freq)), 3)
    if decay == 0.0:
        loops = max(dur*SR/L, 1.0)
        decay = math.exp(-3.4 / loops)
        decay = min(max(decay,0.93),0.996)
    init = (np.random.rand(L)*2-1)
    x = np.zeros(n)
    m = min(L,n); x[:m] = init[:m]
    a = np.zeros(L+1); a[0]=1.0; a[L]=-decay
    y = signal.lfilter([1.0], a, x)
    y *= env_adsr(n, a=0.005, d=0.2, s=0.2, r=0.25)
    return fade_edges(y*np.sqrt(amp/3.0))*np.sqrt(amp)

def fm_ep(freq, dur, amp=1.0, ratio=1.0, mod_i=2.2):
    """Wurlitzer-ish FM electric piano."""
    n=int(dur*SR); t=np.arange(n)/SR
    mi = mod_i*np.exp(-t*5.5)
    sig = np.sin(2*np.pi*freq*t + mi*np.sin(2*np.pi*ratio*freq*t))
    # tine click
    tine = 0.25*np.exp(-t*60)*np.sin(2*np.pi*freq*4*t)
    sig = (sig + tine)
    e = env_adsr(n, a=0.003, d=0.5, s=0.45, r=0.35)
    # tremolo
    trem = 1+0.06*np.sin(2*np.pi*5.4*t)
    return fade_edges(sig*e*trem*(amp*0.9))

def organ(freq, dur, amp=1.0, drawbars=(1.0,0.5,0.6,0.35,0.25,0.0,0.15), leslie=0.10, lp=3500):
    """organ: additive drawbars + leslie tremolo/vibrato."""
    n=int(dur*SR); t=np.arange(n)/SR
    vib = 1 + 0.0016*np.sin(2*np.pi*5.3*t + 0.7)
    sig=np.zeros(n)
    for k,db in enumerate(drawbars, start=1):
        if db<=0: continue
        sig += db*np.sin(2*np.pi*k*freq*t*vib)
    sig*=0.18
    trem = 1 + leslie*np.sin(2*np.pi*5.3*t)
    e = env_adsr(n, a=0.012, d=0.08, s=0.95, r=0.18)
    b,a = signal.butter(2, lp/(SR/2), 'low')
    sig = signal.lfilter(b,a, sig)
    return fade_edges(sig*e*trem*amp)

def bell(freq, dur, amp=1.0, partials=((1.0,1.0,3.0),(2.0,0.5,4.5),(2.76,0.34,7.0),(5.5,0.22,11.0))):
    """FM/inharmonic bell / carnival chime."""
    n=int(dur*SR); t=np.arange(n)/SR
    sig=np.zeros(n)
    for p,amp_p,rr in partials:
        sig += amp_p*np.sin(2*np.pi*p*freq*t)*np.exp(-t*rr)
    e = env_adsr(n, a=0.002, d=0.05, s=0.4, r=0.5)
    vib = 1+0.001*np.sin(2*np.pi*4.5*t)
    sig = sig*vib
    return fade_edges(sig*e*(amp*0.8))

def calliope(freq, dur, amp=1.0):
    """bright carnival calliope: organ+bell hybrid lead."""
    n=int(dur*SR); t=np.arange(n)/SR
    vib=1+0.004*(1-np.exp(-t*2))*np.sin(2*np.pi*5.7*t)
    sig=np.zeros(n)
    for k,db in ((1,1.0),(2,0.5),(3,0.35),(4,0.25),(5,0.18),(6,0.1),(8,0.06)):
        sig += db*np.sin(2*np.pi*k*freq*t*vib)
    sig*=0.13
    sig += 0.25*np.exp(-t*9)*np.sin(2*np.pi*2.76*freq*t)   # bell hit
    e = env_adsr(n, a=0.004, d=0.18, s=0.9, r=0.18)
    trem=1+0.05*np.sin(2*np.pi*6.2*t)
    return fade_edges(sig*e*trem*amp)

def pad(freq, dur, amp=1.0, lp=2400):
    """supersaw string/choir pad."""
    n=int(dur*SR); t=np.arange(n)/SR
    det=[-0.006,-0.003,0.0,0.0035,0.0065]
    sig=np.zeros(n)
    for d in det:
        f=freq*(1+d)
        sig += saw(f, n, n_part=18)
    sig*=0.18
    vib=1+0.003*np.sin(2*np.pi*4.0*t+np.random.rand()*6)
    b,a=signal.butter(2, lp/(SR/2),'low')
    sig=signal.lfilter(b,a,sig)
    # slow swell
    e=np.ones(n)
    A=int(0.4*SR); R=int(0.5*SR)
    if A+R < n:
        e[:A]=np.linspace(0,1,A); e[-R:]=np.linspace(1,0,R)
    return fade_edges(sig*e*amp)

def bowed(freq, dur, amp=1.0):
    """bowed-string lead (violin tribute)."""
    n=int(dur*SR); t=np.arange(n)/SR
    vib=1+0.005*(1-np.exp(-t*3))*np.sin(2*np.pi*5.6*t)
    s1 = saw(freq*vib, n, n_part=24)
    s2 = 0.4*signal.sawtooth(2*np.pi*freq*vib*t+0.3)
    sig = s1*0.7 + s2
    bow_noise = 0.03*np.random.randn(n)*np.exp(-t*1)*(t<0.25)
    sig += bow_noise
    b,a=signal.butter(2, 2600/(SR/2),'low')
    sig=signal.lfilter(b,a,sig)
    e=env_adsr(n, a=0.06, d=0.1, s=0.95, r=0.25)
    return fade_edges(sig*e*(amp*0.9))

def synth_bass(freq, dur, amp=1.0, cutoff=600, slide_to=None):
    """synth bass: sub sine + filtered saw, plucky."""
    n=int(dur*SR); t=np.arange(n)/SR
    if slide_to is not None and slide_to>0:
        # linear pitch slide
        f = np.linspace(freq, slide_to, n)
        phase = 2*np.pi*np.cumsum(f)/SR
        sub = np.sin(phase)
        saw2 = signal.sawtooth(2*np.pi*2*phase)
    else:
        sub = np.sin(2*np.pi*freq*t)
        saw2 = signal.sawtooth(2*np.pi*2*freq*t)
    e = env_adsr(n, a=0.004, d=0.12, s=0.6, r=0.18)
    # filter env
    cut = cutoff*(0.4+0.6*np.exp(-t*12))
    # approximate time-varying lowpass by segment (cheap)
    out=np.zeros(n); step=max(n//8,1)
    for i in range(0,n,step):
        j=min(i+step,n)
        c = float(np.mean(cut[i:j])); c=min(max(c,120),5000)
        b,a=signal.butter(2, c/(SR/2),'low')
        out[i:j]=signal.lfilter(b,a,saw2[i:j])
    out = sub*0.7 + out*0.5
    return fade_edges(out*e*(amp*0.9))

# ---- formant vocal (lead voice) -------------------------------------------
VOWELS = {
 'a':(800,1150,2900,  90, 90,120),   # F1 F2 F3 BW1 BW2 BW3
 'e':(420,2000,2900,  60,100,120),
 'i':(300,2300,3000,  55,100,120),
 'o':(500, 900,2400,  70, 90,120),
 'u':(330, 870,2240,  60,110,120),
 'ae':(700,1800,2600, 90,100,120),
}
def vocal(freq, dur, amp=1.0, vowel='a', vib=0.04, vr=5.4, breath=0.22):
    """formant-synth voice: glottal saw source -> 3 parallel formant resonators."""
    n=int(dur*SR); t=np.arange(n)/SR
    f0 = np.maximum(freq*(1+ (0.0 if vib==0 else vib)*np.sin(2*np.pi*vr*t + 0.4)), 60.0)
    phase = 2*np.pi*np.cumsum(f0)/SR
    # glottal-ish source: saw with rolloff, lowpassed to remove harsh top
    kmax = max(3, min(40, int(5000.0/np.mean(f0))))
    src=np.zeros(n)
    for k in range(1,kmax+1):
        src += np.sin(k*phase)/k
    src *= (2/np.pi)
    b,a=signal.butter(2, 3000/(SR/2),'low')
    src=signal.lfilter(b,a,src)
    F1,F2,F3,BW1,BW2,BW3 = VOWELS[vowel]
    gains=(1.0,0.55,0.30)
    sig=np.zeros(n)
    for F,BW,g in ((F1,BW1,gains[0]),(F2,BW2,gains[1]),(F3,BW3,gains[2])):
        w0=2*np.pi*F/SR; alpha=np.sin(w0)*np.sinh(np.log(2)/2*BW/F*w0)
        b=[g*alpha,0,-g*alpha]
        a=[1+alpha,-2*np.cos(w0),1-alpha]
        sig += signal.lfilter(b,a,src)
    # breath
    if breath>0:
        nb = 0.03*breath*signal.lfilter(*signal.butter(2,3000/(SR/2),'low'), np.random.randn(n))
        sig += nb*np.exp(-t*3)*(t<0.6)
    e=env_adsr(n, a=0.02, d=0.08, s=0.92, r=0.12)
    return fade_edges(sig*e*(amp*0.95))

# ---- drums (modal/noise) ---------------------------------------------------
def d_kick(amp=1.0, tune=0.0):
    n=int(0.28*SR); t=np.arange(n)/SR
    f=140*np.exp(-t*30)+45
    ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)
    click=0.5*np.exp(-t*200)*np.random.randn(n)*np.random.rand(n)
    e=np.exp(-t*9)
    return fade_edges((body*e+click*0.4)*(amp/2.0), 48)

def d_snare(amp=1.0):
    n=int(0.2*SR); t=np.arange(n)/SR
    tone=0.35*np.sin(2*np.pi*180*t)*np.exp(-t*22)
    nz=np.random.randn(n)
    b,a=signal.butter(2,[1500/(SR/2),7500/(SR/2)],'band')
    nz=signal.lfilter(b,a,nz)*np.exp(-t*13)
    e=np.exp(-t*13)
    snap=0.2*np.exp(-t*60)*np.random.randn(n)
    return fade_edges((tone+nz+snap)*e*(amp), 48)

def d_hat(amp=1.0, open_=False):
    n=int((0.12 if not open_ else 0.30)*SR)
    t=np.arange(n)/SR
    nz=np.random.randn(n)
    b,a=signal.butter(2, 8000/(SR/2),'high')
    nz=signal.lfilter(b,a,nz)
    e=np.exp(-t*(34 if not open_ else 11))
    return fade_edges(nz*e*amp*(0.35), 32)

def d_tom(amp=1.0,f0=130):
    n=int(0.3*SR); t=np.arange(n)/SR
    f=f0*np.exp(-t*14)
    ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t*9)
    nz=0.15*np.random.randn(n)*np.exp(-t*22)
    return fade_edges((body+nz)*amp*0.7, 32)

def d_crash(amp=1.0):
    n=int(1.6*SR); t=np.arange(n)/SR
    nz=np.random.randn(n)
    b,a=signal.butter(2, 5000/(SR/2),'high')
    nz=signal.lfilter(b,a,nz)
    # modal shimmer
    sh=np.zeros(n)
    for f,pp in ((7400,0.4),(9100,0.3),(11300,0.2)):
        sh += pp*np.sin(2*np.pi*f*t)
    e=np.exp(-t*2.4)
    return fade_edges((nz*0.5+sh*0.3)*e*amp*0.4, 64, 2048)

def d_ride(amp=1.0):
    n=int(0.5*SR); t=np.arange(n)/SR
    sh=np.zeros(n)
    for f,pp in ((5200,0.5),(6600,0.4),(8400,0.3),(10100,0.2)):
        sh += pp*np.sin(2*np.pi*f*t)
    nz=0.2*signal.lfilter(*signal.butter(2,6000/(SR/2),'high'),np.random.randn(n))
    e=np.exp(-t*7)
    return fade_edges((sh*0.5+nz)*e*amp*0.4, 32)

def fx_riser(dur=2.0, amp=0.5):
    n=int(dur*SR); t=np.arange(n)/SR
    nz=np.random.randn(n)
    bp=[200/(SR/2),12000/(SR/2)]
    sig=signal.lfilter(*signal.butter(2,bp,'bandpass'),nz)
    envelope=(t/dur)**2
    sig*=envelope
    return fade_edges(sig*amp, 256, 512)

def fx_sweep_down(dur=1.2, amp=0.4):
    n=int(dur*SR); t=np.arange(n)/SR
    nz=np.random.randn(n)
    cut=np.linspace(9000,300,n)
    out=np.zeros(n); step=max(n//12,1)
    for i in range(0,n,step):
        j=min(i+step,n); c=float(np.mean(cut[i:j])); c=max(c,200)
        b,a=signal.butter(2,c/(SR/2),'low')
        out[i:j]=signal.lfilter(b,a,nz[i:j])
    out*=(1-t/dur)
    return fade_edges(out*amp,256,512)

# ----------------------------------------------------------------------------
# 4. TRACKS  (mono stems)  +  a place() helper
# ----------------------------------------------------------------------------
TRACKS = {}
def newtrack(name):
    TRACKS[name]=np.zeros(NS,dtype=np.float64)
    return TRACKS[name]

def place(track_name, buf, start_beat, gain=1.0):
    if buf is None or len(buf)==0: return
    s=clk(start_beat)
    if s>=NS: return
    L=len(buf)
    # allow small negative (pre-roll) just clip
    if s<0:
        buf=buf[-s:]; s=0; L=len(buf)
    e=min(s+L,NS)
    TRACKS[track_name][s:e]+=buf[:e-s]*gain

# synth-dispatch: given a voice name render a single note
def render_voice(voice, freq, dur, amp, vowel='a', **kw):
    if voice=='pluck':  return ks_pluck(freq,dur,amp,bright=1.0)
    if voice=='pluckW': return ks_pluck(freq,dur,amp,bright=0.4)
    if voice=='ep':     return fm_ep(freq,dur,amp, ratio=kw.get('ratio',1.0), mod_i=kw.get('mod_i',2.2))
    if voice=='organ':  return organ(freq,dur,amp, leslie=kw.get('leslie',0.10), lp=kw.get('lp',3500))
    if voice=='bell':   return bell(freq,dur,amp)
    if voice=='calliope':return calliope(freq,dur,amp)
    if voice=='pad':    return pad(freq,dur,amp, lp=kw.get('lp',2400))
    if voice=='bowed':  return bowed(freq,dur,amp)
    if voice=='bass':   return synth_bass(freq,dur,amp, cutoff=kw.get('cutoff',600), slide_to=kw.get('slide',None))
    if voice=='vocal':  return vocal(freq,dur,amp, vowel=vowel, vib=kw.get('vib',0.04))
    raise ValueError(voice)

# ----------------------------------------------------------------------------
# 5. HARMONY / ARRANGEMENT HELPERS  (place chords, bass, arps, drums, melody)
# ----------------------------------------------------------------------------
def bar_inside(section, bar):  # section=(start,end)
    return section[0] <= bar <= section[1]

def schedule_chord_voice(track, voice, bar, dur_beats=4, amp=0.6, octave_shift=0, **kw):
    """play the chord's color voicing sustained for dur_beats."""
    ch=chord_of(bar)
    for m in VOIC[ch]:
        place(track, render_voice(voice, mtof(m+octave_shift), dur_beats*SPB, amp, **kw), ab(bar,1), gain=1.0)

def schedule_bass(track, bar, dur_beats=4, amp=0.9, pattern='root', slide=False):
    ch=chord_of(bar); b=BASS[ch]; f=mtof(b)
    if pattern=='root':
        place(track, synth_bass(f, dur_beats*SPB, amp, cutoff=520), ab(bar,1))
    elif pattern=='walk':
        # roots with a quarter feel + small ghost
        for i in range(4):
            f=mtof(b)
            place(track, synth_bass(f, 0.85*SPB, amp, cutoff=(600 if i==0 else 480)), ab(bar,1+i))
    elif pattern=='walkup':
        # root then approach next root
        place(track, synth_bass(f, 2*SPB, amp, cutoff=560), ab(bar,1))
        # approach
        nxt=chord_of(bar+1); b2=BASS[nxt]
        place(track, synth_bass(mtof(b2-1), 2*SPB, amp*0.85, cutoff=560), ab(bar,3))

def schedule_arpeggio(track, voice, bar, amp=0.5, pattern='up', dur=0.5, octave=0):
    ch=chord_of(bar); notes=VOIC[ch]
    if pattern=='up': seq=notes
    elif pattern=='updown': seq=notes+notes[-2::-1]
    elif pattern=='skip': seq=notes[::2]+notes[1::2]
    else: seq=notes
    seq=[n+octave*12 for n in seq]
    # 8th-note arp across the bar: 8 steps
    steps=[]
    while len(steps)<8: steps+=seq
    for i in range(8):
        place(track, render_voice(voice, mtof(steps[i]), dur*SPB, amp*0.9), ab(bar,1+i*0.5))

# ---- DRUM PATTERNS ---------------------------------------------------------
def drums_bar(track_k,track_s,track_h,track_c, bar, style='groove', density=1.0, fill=False, amp=1.0):
    """place a drum bar.  bars index for crash decisions."""
    def p(t,buf,g=1.0): place(t,buf,ab(bar,1)); 
    # groove: kick on 1 & (3 with ghost), snare on 2 & 4, hats 8ths with swing
    if style=='groove':
        # kicks
        place('dr_kick', d_kick(amp*1.0), ab(bar,1))
        place('dr_kick', d_kick(amp*0.85), ab(bar,1+2.0))      # beat3
        place('dr_kick', d_kick(amp*0.6),  ab(bar,1+0.75+4)) if False else None
        # extra syncopated kick on "+" of 4 sometimes
        if bar%2==0:
            place('dr_kick', d_kick(amp*0.7), ab(bar,1+3.5))
        # snares backbeat
        place('dr_snare', d_snare(amp*0.9), ab(bar,1+1.0))
        place('dr_snare', d_snare(amp*0.9), ab(bar,1+3.0))
        # hats 8ths with swing
        for i in range(8):
            sw = 0.5 if i%2==0 else 0.5+0.06   # slight swing on offbeat
            place('dr_hat', d_hat(amp*(0.7 if i%2 else 0.9)), ab(bar,1+i*sw))
        # ride touch every 4 bars
        if bar%4==3 and not fill:
            place('dr_ride', d_ride(amp*0.5), ab(bar,1+2))
    if style=='light':
        place('dr_hat', d_hat(amp*0.6), ab(bar,1))
        place('dr_hat', d_hat(amp*0.5), ab(bar,1+1))
        place('dr_hat', d_hat(amp*0.6), ab(bar,1+2))
        place('dr_hat', d_hat(amp*0.5), ab(bar,1+3))
        place('dr_kick', d_kick(amp*0.6), ab(bar,1))
    if style=='sparse_intro':
        if bar%2==1:
            place('dr_hat', d_hat(amp*0.4,True), ab(bar,1+1))
            place('dr_kick', d_kick(amp*0.5), ab(bar,1))
    if fill:
        # 1-beat snare buildup to the crash
        for i in range(6):
            g=0.5+0.1*i
            place('dr_snare', d_snare(amp*g*0.7), ab(bar,1+1+ i*0.33))
        place('dr_tom', d_tom(amp*1.0,90), ab(bar,1+3.0))
        place('dr_crash', d_crash(amp*1.0), ab(bar+1,1))   # crash on NEXT bar
    if bar%8==1 and not fill and style=='groove':
        if not (bar<=8):   # no crash on intro
            place('dr_crash', d_crash(amp*0.7), ab(bar,1))

# ----------------------------------------------------------------------------
# 6. MELODIC CONTENT
# ----------------------------------------------------------------------------
# The carnival motif (intro & outro lead) -- 4-bar phrase, played by bowed/calliope
MOTIF = [
    # (bar_offset_within_phrase, beat, dur, midi)
    (0,1,1.0,69),(0,2,1.0,72),(0,3,1.0,76),(0,4,1.0,74),
    (1,1,0.5,76),(1,1.5,0.5,74),(1,2,1.0,72),(1,3,1.0,69),(1,4,1.0,68),
    (2,1,2.0,76),(2,3,0.5,68),(2,3.5,0.5,65),(2,4,1.0,64),
    (3,1,2.0,69),(3,3,1.0,72),(3,4,1.0,71),
]

# CHORUS HOOK melody + lyric (over CH 8-bar progression)
HOOK = [
 # bar,beat,dur,midi,syllable,vowel
 (0,1,1.0,69,"I",'a'),(0,2,0.5,71,"will",'i'),(0,2.5,1.0,72,"ride",'a'),(0,3.5,0.5,69,"the",'e'),
 (1,1,1.0,74,"fer",'e'),(1,2,0.5,76,"ris",'i'),(1,2.5,1.5,74,"wheel",'e'),
 (2,1,1.0,71,"I",'a'),(2,2,0.5,72,"will",'i'),(2,2.5,1.0,74,"ride",'a'),(2,3.5,0.5,71,"it",'e'),
 (3,1,0.5,72,"till",'i'),(3,1.5,1.0,74,"it",'e'),(3,2.5,1.5,76,"stops",'a'),
 (4,1,1.0,76,"far",'a'),(4,2,1.0,74,"a",'a'),(4,3,0.5,72,"bove",'e'),(4,3.5,0.5,74,"the",'e'),
 (5,1,1.0,76,"lan",'a'),(5,2,1.0,77,"tern",'e'),(5,3,2.0,74,"light",'a'),
 (6,1,1.0,72,"where",'e'),(6,2,1.0,71,"the",'e'),(6,3,1.0,69,"last",'a'),(6,4,1.0,74,"spark",'a'),
 (7,1,3.0,69,"drops",'a'),
]
HOOK_TITLE = ("THE LAST FERRIS WHEEL  (inspired by The Cardigans - Carnival)\n"
 "lyric:\n"
 "[verse1-2] now the fairground's folding up / the painted ponies sleep / lights string down / "
 "into puddles at my feet / you were standing on the deck / of a wheel that won't come down / "
 "i called your name across the smoke / music drowned the sound ... "
 "[pre] and the wheel keeps turning turning / though the crowd is going home / "
 "all this gold is only paper / all this fire is only foam\n"
 "[chorus] I will ride the ferris wheel / I will ride it till it stops / "
 "far above the lantern light / where the last spark drops\n")

# Verse melody generator (coherent walking line bound to chord tones)
def nearest_chord_tone(prev, chord_pcs, lo=62, hi=72):
    cand=[]
    for c in range(lo,hi+1):
        if (c%12) in chord_pcs: cand.append(c)
    if not cand: cand=[lo]
    best=min(cand, key=lambda c:(abs(c-prev), abs(c-prev)*0+ (c-prev<0)))
    return best
def gen_verse_melody(start_bar,nbars,seed_off=0, lo=62, hi=72):
    rng=np.random.RandomState(123+seed_off)
    notes=[]
    prev=rng.randint(lo+2,hi-2)
    # rhythmic template per bar: a mix of quarters / eighths
    templates=[
        [(0,1.0),(1,1.0),(2,1.0),(3,1.0)],
        [(0,0.5),(0.5,0.5),(1,1.0),(2,0.5),(2.5,0.5),(3,1.0)],
        [(0,1.5),(1.5,0.5),(2,1.0),(3,1.0)],
        [(0,1.0),(1,0.5),(1.5,0.5),(2,1.5),(3.5,0.5)],
    ]
    for bar_i in range(nbars):
        bar=start_bar+bar_i
        ch=chord_of(bar); pcs={m%12 for m in VOIC[ch]}
        tmpl=templates[rng.randint(len(templates))]
        for off,dur in tmpl:
            beat=1+off
            strong = (off in (0,2))
            if strong:
                note=nearest_chord_tone(prev,pcs,lo,hi)
            else:
                # passing tone: step toward next chord tone via scale, small random
                step = rng.choice([-2,-1,1,2])
                note=prev+step
                if note<lo: note=lo
                if note>hi: note=hi
                if rng.rand()<0.4: note=nearest_chord_tone(note,pcs,lo,hi)
            notes.append((bar,beat,dur,note))
            prev=note
    return notes

VERSES = gen_verse_melody(9,16,0) + gen_verse_melody(45,16,1)

# ----------------------------------------------------------------------------
# 7. ASSEMBLY  -- build every stem track
# ----------------------------------------------------------------------------
for name in ['pad','organ','keys','pluck','bass','lead','calliope','bells',
             'vocal','backing','dr_kick','dr_snare','dr_hat','dr_tom',
             'dr_crash','dr_ride','fx']:
    newtrack(name)

# ---- INTRO (1-8) ----
for b in range(1,9):
    schedule_chord_voice('pad','pad',b,amp=0.18, lp=1800)
    schedule_chord_voice('organ','organ',b,amp=0.10, leslie=0.12)
    schedule_bass('bass',b,amp=0.5,pattern='root')
    drums_bar(None,None,None,None, b, style='sparse_intro', amp=0.6)
# motif on bowed (violin) each 4 bars of intro, low
for phrase,b0 in ((1,1),(2,5)):
    for bo,beat,dur,midi in MOTIF:
        place('lead', render_voice('bowed',mtof(midi),dur*SPB,amp=0.32), ab(b0,1)+ (bo*4)+ (beat-1))

# ---- VERSE 1 (9-24) ----
# vocals only bars 1-8 and 13-16 of the verse run (relative). Here verses span 9-24 (16 bars).
# sing bars 9-16 (first half phrase) ; bars 17-24 = pluck instrumental answer.
# sing verse 1: first half (bars 9-16); leave 17-24 as pluck instrumental answer
for (bar,beat,dur,midi) in [n for n in VERSES if 9<=n[0]<=16]:
    place('vocal', render_voice('vocal',mtof(midi),dur*SPB,1.1,'a' if bar%4<2 else 'e'), ab(bar,beat))
for b in range(9,25):
    schedule_chord_voice('keys','ep',b,amp=0.16)
    schedule_chord_voice('pad','pad',b,amp=0.10,lp=2200)
    schedule_bass('bass',b,amp=0.7,pattern='walk')
    if b%2==0:
        schedule_arpeggio('pluck','pluck',b,amp=0.18,pattern='updown',dur=0.45)
    drums_bar(None,None,None,None, b, style='groove', amp=0.9, fill=(b%8==0))

# ---- PRE 1 (25-28) ----
for b in range(25,29):
    schedule_chord_voice('keys','ep',b,amp=0.18)
    schedule_chord_voice('pad','pad',b,amp=0.16,lp=2600)
    schedule_chord_voice('organ','organ',b,amp=0.14,leslie=0.14)
    schedule_bass('bass',b,amp=0.8,pattern='walk')
    drums_bar(None,None,None,None, b, style='groove', amp=0.97)
place('fx', fx_riser(2.0,amp=0.45), ab(27,3))
drums_bar(None,None,None,None, 28, style='groove', amp=1.0, fill=True)   # fill -> crash on 29

# ---- CHORUS 1 (29-44) ----
for b in range(29,45):
    schedule_chord_voice('pad','pad',b,amp=0.11,lp=2600)
    schedule_chord_voice('organ','organ',b,amp=0.10,leslie=0.12)
    schedule_chord_voice('keys','ep',b,amp=0.08)
    schedule_bass('bass',b,amp=0.85,pattern='walk')
    if b%2==0: schedule_arpeggio('pluck','pluck',b,amp=0.10,pattern='skip',dur=0.5,octave=1)
    drums_bar(None,None,None,None, b, style='groove', amp=1.0, fill=(b%8==0))
# hook vocal (sing 8 bars starting at 29) + repeat at 37 with harmony
def sing_hook(start_bar, with_backing=True):
    for (bo,beat,dur,midi,syl,vowel) in HOOK:
        place('vocal', render_voice('vocal',mtof(midi),dur*SPB,2.8,vowel), ab(start_bar,1+bo*4)+(beat-1))
        # octave double thickens melody presence
        place('backing', render_voice('vocal',mtof(midi-12),dur*SPB,0.6,'o'), ab(start_bar,1+bo*4)+(beat-1))
        if with_backing:
            place('backing', render_voice('vocal',mtof(midi+4),dur*SPB,0.95,'o'), ab(start_bar,1+bo*4)+(beat-1))
            if bo%2==0:
                place('backing', render_voice('vocal',mtof(midi+7),dur*SPB*min(1,dur),0.55,'o'),
                      ab(start_bar,1+bo*4)+(beat-1))
    # calliope counter on turnaround (bars 4-5 of the phrase) for sparkle
    for phrase,bb0 in ((0,start_bar+4),(1,start_bar)):
        pass
# chorus1: first 8 bars (29-36) plain hook, second 8 (37-44) with backing
sing_hook(29)
sing_hook(37, with_backing=True)
# calliope sparkle counter over chorus
for phrase in (29,37):
    for (bo,beat,dur,midi) in MOTIF:
        place('calliope', render_voice('calliope',mtof(midi+12),dur*SPB,0.07), ab(phrase,1)+bo*4+(beat-1))

# ---- VERSE 2 (45-60) ----
for (bar,beat,dur,midi) in [n for n in VERSES if 45<=n[0]<=52]:
    place('vocal', render_voice('vocal',mtof(midi),dur*SPB,1.3,'a' if bar%4<2 else 'e'), ab(bar,beat))
for b in range(45,61):
    schedule_chord_voice('keys','ep',b,amp=0.16)
    schedule_chord_voice('pad','pad',b,amp=0.12,lp=2200)
    schedule_bass('bass',b,amp=0.75,pattern='walk')
    if b%2==0: schedule_arpeggio('pluck','pluck',b,amp=0.20,pattern='updown',dur=0.45)
    # countermelody bowed in verse2
    drums_bar(None,None,None,None, b, style='groove', amp=0.95, fill=(b%8==0))
# bowed countermelody small motif over verse2 bars 53-56
for (bo,beat,dur,midi) in MOTIF[:4]:
    place('lead', render_voice('bowed',mtof(midi-5),dur*SPB,0.16), ab(53,1)+bo*4+(beat-1))

# ---- PRE 2 (61-64) ----
for b in range(61,65):
    schedule_chord_voice('keys','ep',b,amp=0.18)
    schedule_chord_voice('pad','pad',b,amp=0.18,lp=2800)
    schedule_chord_voice('organ','organ',b,amp=0.16,leslie=0.14)
    schedule_bass('bass',b,amp=0.85,pattern='walk')
    drums_bar(None,None,None,None, b, style='groove', amp=1.0)
place('fx', fx_riser(2.0,amp=0.5), ab(63,3))
drums_bar(None,None,None,None, 64, style='groove', amp=1.0, fill=True)

# ---- CHORUS 2 (65-80) ----
for b in range(65,81):
    schedule_chord_voice('pad','pad',b,amp=0.12,lp=2800)
    schedule_chord_voice('organ','organ',b,amp=0.10,leslie=0.12)
    schedule_chord_voice('keys','ep',b,amp=0.08)
    schedule_bass('bass',b,amp=0.9,pattern='walk')
    if b%2==0: schedule_arpeggio('pluck','pluck',b,amp=0.10,pattern='skip',dur=0.5,octave=1)
    drums_bar(None,None,None,None, b, style='groove', amp=1.05, fill=(b%8==0))
sing_hook(65)
sing_hook(73, with_backing=True)
for phrase in (65,73):
    for (bo,beat,dur,midi) in MOTIF:
        place('calliope', render_voice('calliope',mtof(midi+12),dur*SPB,0.07), ab(phrase,1)+bo*4+(beat-1))

# ---- OUTRO (81-96) instrumental ----
for b in range(81,97):
    schedule_chord_voice('pad','pad',b,amp=max(0.06,0.20*(1-(b-81)/16)),lp=1900)
    schedule_chord_voice('organ','organ',b,amp=0.10,leslie=0.10)
    schedule_bass('bass',b,amp=max(0.0,0.55*(1-(b-81)/16)),pattern='root')
    if b<=92:
        drums_bar(None,None,None,None, b, style='light', amp=0.5*(1-(b-86)/10) if b>86 else 0.5)
# bowed violin motif over outro first 8
for (bo,beat,dur,midi) in MOTIF:
    place('lead', render_voice('bowed',mtof(midi),dur*SPB,0.34), ab(85,1)+0 + (bo*4)+(beat-1))
# calliope motif over outro second 8, octave up shimmer
for (bo,beat,dur,midi) in MOTIF:
    place('calliope', render_voice('calliope',mtof(midi+12),dur*SPB,0.18), ab(89,1)+bo*4+(beat-1))
# bell rings on downbeats of outro
for b in (81,83,85,89,92,95,96):
    ch=chord_of(b)
    for m in VOIC[ch][1:3]:
        place('bells', render_voice('bell',mtof(m+12),(2.0)*SPB,0.18), ab(b,1))
# final Amadd9 shimmer + slow crash
for m in VOIC['Am_final']:
    place('pad', render_voice('pad',mtof(m),3.5*SPB,0.16,lp=2600), ab(95,1))
    place('bells', render_voice('bell',mtof(m+12),3.0*SPB,0.10), ab(95,1))
place('dr_crash', d_crash(0.8), ab(95,1))
place('fx', fx_sweep_down(2.5,0.25), ab(94,1))

print("== stems placed ==", flush=True)

# ----------------------------------------------------------------------------
# 8. MIXDOWN  (mono stems -> stereo bus with pan + reverb + chorus + master)
# ----------------------------------------------------------------------------
def pan_law(p):   # p in [-1,1]
    return (np.cos((p+1)*np.pi/4), np.sin((p+1)*np.pi/4))

# stem routing: (track, gain_db, pan, reverb_send)
ROUTING = [
 ('bass',     -2.0,  0.0, 0.04),
 ('dr_kick',  -4.0,  0.0, 0.05),
 ('dr_snare', -7.0,  0.0, 0.16),
 ('dr_hat',   -12.0, 0.15,0.10),
 ('dr_tom',   -9.0, -0.2, 0.16),
 ('dr_crash', -10.0,0.3, 0.30),
 ('dr_ride',  -14.0,0.25,0.22),
 ('keys',     -7.0, -0.18,0.16),
 ('organ',    -8.0, -0.30,0.20),
 ('pad',      -10.0,0.0, 0.34),
 ('pluck',    -10.0,0.22,0.18),
 ('lead',     -6.0, 0.08,0.28),
 ('calliope', -9.0, -0.15,0.30),
 ('bells',    -10.0,0.18,0.34),
 ('vocal',    12.0,  0.0, 0.28),
 ('backing',   3.0,  0.0, 0.30),
 ('fx',       -8.0,  0.0, 0.50),
]

# ---- stereo reverb impulse (two channels) ---------------------------------
def build_ir(dur=1.5, decay=3.2):
    n=int(dur*SR)
    ir = np.random.randn(n)
    # diffuse: multiple short delays + smearing
    for d in (7,13,23,37,53):
        ir[d:] += 0.6*np.random.rand()*ir[:-d]
    ir *= np.exp(-np.arange(n)/SR*decay)
    # lowpass to soften
    b,a=signal.butter(1, 3000/(SR/2),'low')
    ir=signal.lfilter(b,a,ir)
    ir/= np.max(np.abs(ir)+1e-9)
    return ir
IR_L = build_ir(1.6, 3.4)
IR_R = build_ir(1.6, 3.6)
def reverb_stereo(mono):
    if np.max(np.abs(mono))<1e-9: return np.zeros((2,len(IR_L)))
    wl=signal.fftconvolve(mono, IR_L)[:len(mono)]
    wr=signal.fftconvolve(mono, IR_R)[:len(mono)]
    return np.stack([wl,wr])

def chorus(x, depth=0.0009, rate=0.7, mix=0.18):
    n=len(x); t=np.arange(n)/SR
    delay=depth*SR*(1+0.5*np.sin(2*np.pi*rate*t+0.3))
    # fractional delay via linear interp
    dd=np.clip(delay,0, n-2)
    i0=dd.astype(int); f=dd-i0
    out=np.zeros(n)
    valid=i0 < n-1
    out[valid]=x[i0[valid]]*(1-f[valid])+x[i0[valid]+1]*f[valid]
    return x*(1-mix)+out*mix

def stereo_width(In):  # simple mid/side trick
    mid=0.5*(In[0]+In[1]); side=0.5*(In[0]-In[1])
    return np.stack([mid+1.2*side, mid-1.2*side])

def master_chain(L,R, scale=None, target=0.89):
    X=np.stack([L,R])
    # soft high shelf
    b,a=signal.butter(1, 8000/(SR/2),'high')
    high=signal.lfilter(b,a, X)
    X=X+0.6*high
    # low shelf warmth
    b,a=signal.butter(1, 120/(SR/2),'low')
    low=signal.lfilter(b,a, X)
    X=X+0.35*low
    # gentle saturation
    X=np.tanh(X*1.3)
    if scale is None:
        peak=np.max(np.abs(X))
        scale = target/peak if peak>0 else target
    return X*scale, scale

def mixdown(include_vocals=True, scale=None):
    L=np.zeros(NS); R=np.zeros(NS); wetL=np.zeros(NS); wetR=np.zeros(NS)
    for name,gdb,pan,rsend in ROUTING:
        if not include_vocals and name in ('vocal','backing'): continue
        g=db(gdb)
        ch=np.clip(TRACKS[name], -2.0, 2.0)
        pl,pr=pan_law(pan)
        L+=ch*pl*g
        R+=ch*pr*g
        if rsend>0:
            w=reverb_stereo(ch*rsend)
            wetL+=w[0]; wetR+=w[1]
    # eq the wet a touch + chorus on wet for size
    wetL=chorus(wetL,0.001,0.6,0.30)
    wetR=chorus(wetR,0.001,0.55,0.30)
    L=L+wetL; R=R+wetR
    L=chorus(L,0.0008,0.6,0.10)
    R=chorus(R,0.0008,0.7,0.10)
    X=stereo_width(np.stack([L,R]))
    X, sc = master_chain(X[0],X[1], scale=scale)
    return X, sc

print("== rendering full mix ==", flush=True)
FULL, sc = mixdown(True)
print("== rendering instrumental ==", flush=True)
INST, _ = mixdown(False, scale=sc)

# ----------------------------------------------------------------------------
# 9. WRITE WAV + ENCODE MP3
# ----------------------------------------------------------------------------
def write_wav(path, X):
    X=np.clip(X,-1.0,1.0)
    i16=(X*32767).astype(np.int16)
    # interleave L/R  (NOT sequential!)
    inter=np.empty(i16.shape[1]*2, dtype=np.int16)
    inter[0::2]=i16[0]; inter[1::2]=i16[1]
    with wave.open(path,'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(inter.tobytes())

def to_mp3(wav_path, mp3_path):
    cmd=['ffmpeg','-y','-loglevel','error','-i',wav_path,
         '-codec:a','libmp3lame','-b:a','192k', mp3_path]
    subprocess.run(cmd, check=True)

OUT_DIR=os.path.dirname(os.path.abspath(__file__))
full_wav=os.path.join(OUT_DIR,'the_last_ferris_wheel.wav')
inst_wav=os.path.join(OUT_DIR,'the_last_ferris_wheel_instrumental.wav')
write_wav(full_wav, FULL)
write_wav(inst_wav, INST)
print("== encoding mp3 ==", flush=True)
to_mp3(full_wav, os.path.join(OUT_DIR,'the_last_ferris_wheel.mp3'))
to_mp3(inst_wav, os.path.join(OUT_DIR,'the_last_ferris_wheel_instrumental.mp3'))

# print lyric + info
print("\n"+ "="*70)
print(HOOK_TITLE)
print("="*70)
print("DONE -> ", OUT_DIR)
print("  full:          the_last_ferris_wheel.mp3")
print("  instrumental:  the_last_ferris_wheel_instrumental.mp3")
print("  source:        the_last_ferris_wheel.py")