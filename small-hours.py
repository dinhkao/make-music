# =============================================================================
#  "DIAL TONE"  -- PinkPantheress-style pop-DnB / 2-step, drums played
#                  in the Nick Villa (Magdalena Bay) vocabulary.
#
#  Chay:  python3 small-hours.py
#  Xuat:  small-hours.wav  +  small-hours-inst.wav
#  Chi dung numpy + scipy (nhu moi engine cua du an). Khong file mau ngoai.
#
#  ------------------------------------------------------------------
#  BAN THIET KE (chep ai, chep cai gi)
#  ------------------------------------------------------------------
#  HOA AM   : chep KHUNG cua "Mosquito" (PinkPantheress, Heaven Knows).
#             Hooktheory: i7 - iv7 - bVII7 - v - VImaj7 - iv7 - VImaj7 - V7
#             Doi tu Si thu -> FA thu. Giu nguyen dac diem quan trong nhat:
#             hop am DOI SOM, roi vao phach "and of 4" (3.5 + 4.5 phach),
#             va chi mot lan duy nhat dung V TRUONG (C7, hoa thanh thu)
#             o cuoi vong 8 o nhip. Khong phai vong 4 hop am pop.
#  PRE      : chep "Stars" (Fancy That) -- hai hop am i11 <-> iv11.
#  BRIDGE   : chep "Noises" -- hop am troi tren mot not tram giu nguyen.
#  CAU TRUC : theo dung loi cua co -- CHI MOT DOAN VERSE
#             ("I don't do second verses - that's ridiculous"), tong < 2:30.
#  BASS     : hai lop, theo dung tai lieu 2-step:
#             (1) sub = not goc, chi danh dung cho kick (buoc 1 va 11)
#             (2) mid = MOT RIFF CO DINH 2 o nhip, LAP nguyen xi ben duoi
#                 hop am dang doi -> KHONG bam theo goc hop am.
#                 (Giong cach "Illegal" lap bassline sample Underworld.)
#  TRONG    : tu vung Nick Villa (tu chinh video anh day "Death & Romance")
#             - hi-hat 16 luon chay, la "moc gio" cua anh
#             - kick dao phach
#             - ghost note tren snare RUNG VOI KICK (khong phai rai deu)
#             - fill vao o phach "2-and" (buoc 7)
#             - chuyen sang ride + bell de nang doan
#             - tom la concert tom (mot mat, kho, ngan, co cao do)
#             - clap stack la MOT LOP RIENG chong len backbeat
#             - moi doan mot nguyen mau trong khac nhau (Matt/Mica lap trinh
#               truoc, khong phai drummer ngau hung)
#             Khung kick/snare van la 2-step (1, 11 / 5, 13) de hop
#             PinkPantheress; Villa la cach CHOI de len tren khung do.
# =============================================================================
import struct
import numpy as np
from scipy import signal as sg
from scipy.special import jv

SR = 44100
rng = np.random.default_rng(2208)

# ============================ 1. LOI ============================
TEMPO = [(0, 356, 163, 163)]
_gb = None; _ct = None; TOTAL = None

def _bpm(b):
    for s, e, b0, b1 in TEMPO:
        if s <= b < e: return b0 + (b1 - b0) * (b - s) / (e - s)
    return TEMPO[-1][3]

def configure(bpm0=163, bpm1=163, end=356):
    global TEMPO, _gb, _ct, TOTAL
    TEMPO = [(0, end, bpm0, bpm1)]
    _gb = np.arange(0, end + 2, 0.004)
    _ct = np.concatenate([[0], np.cumsum(np.array([60.0 / _bpm(b) for b in _gb]) * 0.004)[:-1]])
    TOTAL = T(end) + 4
    return TOTAL

def T(b):   return float(np.interp(b, _gb, _ct))
def SPB(b): return 60.0 / _bpm(b)

def nn(s):
    base = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    n = base[s[0]]; i = 1
    while i < len(s) and s[i] in '#b':
        n += 1 if s[i] == '#' else -1; i += 1
    return 12 * (int(s[i:]) + 1) + n

def hz(m):  return 440.0 * 2 ** ((m - 69) / 12)
def buf():  return np.zeros(int(TOTAL * SR) + SR)

def put(b, t0, x, g=1.0):
    i = int(t0 * SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(b) - i)
    if n > 0: b[i:i+n] += x[:n] * g

def env(L, a, d, s, r):
    e = np.ones(L); ai = min(int(a * SR), L)
    if ai > 0: e[:ai] = np.linspace(0, 1, ai)
    di = int(d * SR)
    if ai + di < L:
        e[ai:ai+di] = np.linspace(1, s, di); e[ai+di:] = s
    else:
        e[ai:] = np.linspace(1, s, max(L - ai, 1))
    ri = min(int(r * SR), L)
    if ri > 0: e[L-ri:] *= np.linspace(1, 0, ri) ** 1.3
    return e

def _hp(x, f, o=2):
    b, a = sg.butter(o, min(f, SR/2-100)/(SR/2), 'high'); return sg.lfilter(b, a, x)
def _lp(x, f, o=2):
    b, a = sg.butter(o, min(f, SR/2-100)/(SR/2), 'low');  return sg.lfilter(b, a, x)
def _bp(x, lo, hi, o=2):
    hi = min(hi, SR/2-100); lo = max(lo, 20)
    b, a = sg.butter(o, [lo/(SR/2), hi/(SR/2)], 'band'); return sg.lfilter(b, a, x)
def _ramp(x, ms=0.8):
    n = min(int(ms/1000*SR), len(x))
    if n > 1: x = x.copy(); x[:n] *= np.linspace(0, 1, n)
    return x
def _fadeout(x, ms=20.0):
    n = min(int(ms/1000*SR), len(x))
    if n > 1: x = x.copy(); x[-n:] *= np.linspace(1, 0, n)
    return x

# ============================ 2. BO TRONG ============================
IDEAL = [1.0000,1.5934,2.1356,2.2952,2.6528,2.9172,3.1551,3.4998,3.5983,3.6470]
JMN   = [2.405,3.832,5.136,5.520,6.380,7.016,7.588,8.417,8.654,8.771]
MORD  = [0,1,2,0,3,1,4,2,0,5]
AIRLOADED = [1.00,1.50,1.98,2.44,2.89,3.36]

def modal(f0, taus, gains, L, rg, glide=0.05, tg=0.02, detune_cents=0, ratios=IDEAL):
    t = np.arange(L)/SR
    g = 1 + glide*np.exp(-t/tg)
    ph = 2*np.pi*np.cumsum(g)/SR
    det = 2**(detune_cents/1200)
    out = np.zeros(L)
    for r, tau, gn in zip(ratios, taus, gains):
        f = f0*r*det
        if f > SR/2.2: continue
        out += gn*np.exp(-t/tau)*np.sin(ph*f + rg.uniform(0, 2*np.pi))
    return out

def bessel_gains(r_rel, rg, n=10, jitter=0.08):
    r = np.clip(r_rel + rg.normal(0, jitter), 0.0, 0.92)
    g = [abs(jv(MORD[i], JMN[i]*r)) * 10**(rg.normal(0, 0.35)) for i in range(n)]
    g = np.array(g); return g/(g.max()+1e-9)

# Ride bell: not goc D6 (quang nam cua SOL truong) + ty le bat dieu hoa
# cua bell that (1.00, 1.42, 1.72, 2.14, 2.87, 3.48, 4.24...).
BELL_F = 1174.66
BELL_PART = [(1.000,1.00,1.15),(1.420,0.52,0.75),(1.719,0.34,0.55),
             (2.141,0.22,0.42),(2.869,0.13,0.30),(3.483,0.09,0.24),(4.236,0.06,0.18)]

class Kit:
    def __init__(self, seed=7):
        self.rng = np.random.default_rng(seed); self._cache = {}

    def kick(self, vel=1.0, tune=46.0, click=1.0, mode='acoustic'):
        R = self.rng; L = int(0.55*SR); t = np.arange(L)/SR
        det = 2**(R.normal(0, 28)/1200)
        if mode == 'acoustic':
            body = np.zeros(L)
            for k in range(1, 7):
                f = (tune*k*0.9 + 7)*det; tau = 0.26/(k**0.72)
                body += (1.0/k**0.9)*np.exp(-t/tau)*np.sin(2*np.pi*f*t + R.uniform(0, 2*np.pi))
            body *= 1 + 0.09*np.exp(-t/0.025)
        else:
            f = tune*det*(1 + 2.6*np.exp(-t/0.030))
            body = np.sin(2*np.pi*np.cumsum(f)/SR + R.uniform(0, 2*np.pi))*np.exp(-t/0.16)
            body += np.sin(2*np.pi*np.cumsum(f*0.5)/SR)*np.exp(-t/0.22)*0.5
        fm = np.sin(2*np.pi*185*det*t + (2.2*np.exp(-t/0.04))*np.sin(2*np.pi*259*t))
        body += fm*np.exp(-t/0.045)*0.24
        n = R.standard_normal(L)*np.exp(-t/0.0045)
        cl = _lp(_hp(n, 220), 4200)*click*0.5*vel
        return _ramp(np.tanh(_hp(body*vel + cl, 32, 4)*1.5))

    def snare(self, vel=1.0, tune=212.0, art='center'):
        R = self.rng; L = int(0.42*SR); t = np.arange(L)/SR
        r_rel = {'center':0.12,'edge':0.62,'ghost':0.34,'rim':0.20,'cross':0.80}[art]
        g = bessel_gains(r_rel, R)
        taus = np.array([0.045,0.20,0.17,0.055,0.14,0.11,0.09,0.08,0.05,0.07])*(1+R.normal(0,0.10,10))
        if art == 'rim': taus *= 0.7
        det = R.normal(0, 30)
        mem = modal(tune, taus, g, L, R, glide=0.06, tg=0.02, detune_cents=det)
        mem += modal(tune*1.42, taus*0.8, g*0.55, L, R, glide=0.05, tg=0.018,
                     detune_cents=det+R.normal(0,18))*0.6
        envm = np.abs(sg.lfilter(*sg.butter(2, 120/(SR/2), 'low'), np.abs(mem)))
        envm /= (envm.max()+1e-9)
        thr = {'ghost':0.42,'center':0.14,'edge':0.20,'rim':0.06,'cross':0.85}[art]
        wire_env = np.clip(envm-thr, 0, None)/(1-thr)
        n = R.standard_normal(L); wire = _bp(n, 1100, 9500, 3)
        buzz = (R.random(L) < 0.055).astype(float); buzz = sg.lfilter([1], [1,-0.90], buzz)
        wire = wire*(0.55 + 0.85*buzz/(buzz.max()+1e-9))
        d = int(R.uniform(0.0005, 0.003)*SR); wire = np.concatenate([np.zeros(d), wire])[:L]
        wire *= wire_env*np.exp(-t/R.uniform(0.11, 0.24))
        stick = _bp(R.standard_normal(L), 2200, 7000, 2)*np.exp(-t/0.0035)
        if art == 'rim':
            shell = _bp(R.standard_normal(L), 420, 900, 2)*np.exp(-t/0.035)*1.1
            x = (mem*0.55 + wire*1.5 + stick*1.5 + shell)*vel*2.2
        elif art == 'cross':
            wood = _bp(R.standard_normal(L), 1300, 3400, 2)*np.exp(-t/0.006)*2.2
            x = (mem*0.16 + wood + wire*0.10)*vel*1.5
        elif art == 'ghost':
            x = (mem*0.85 + wire*0.55 + stick*0.35)*vel*0.22
        else:
            x = (mem*0.75 + wire*1.0 + stick*0.8)*vel
        return _ramp(np.tanh(x*1.25))

    def ctom(self, vel=1.0, tune=180.0):
        """CONCERT TOM -- mot mat, khong co mat duoi -> kho, ngan, co cao do ro.
        Day dung la bo tom Nick Villa noi trong phong van: 'They're not rotos.
        They're concert toms.' Vi vay tau (decay) rat ngan so voi tom thuong."""
        R = self.rng; L = int(0.34*SR); t = np.arange(L)/SR
        g = bessel_gains(0.16, R, n=6)
        taus = np.array([0.115,0.085,0.060,0.045,0.034,0.026])*(1+R.normal(0,0.10,6))
        x = modal(tune, taus, g, L, R, glide=0.10, tg=0.022,
                  detune_cents=R.normal(0,25), ratios=AIRLOADED)
        stick = _bp(R.standard_normal(L), 1900, 6000, 2)*np.exp(-t/0.0032)*0.8
        shell = _bp(R.standard_normal(L), 300, 800, 2)*np.exp(-t/0.012)*0.35
        return _ramp(np.tanh((x + stick + shell)*vel*1.3))

    def _cym(self, L, nmodes, fmin, fmax, tau_lo, tau_hi, seed, migrate=0.10):
        R = np.random.default_rng(seed); t = np.arange(L)/SR
        f = np.sort(R.uniform(fmin, fmax, nmodes)); f = f*(1+R.normal(0, 0.02, nmodes))
        tau = np.clip(tau_hi*(f/fmin)**(-0.62)*(1+R.normal(0,0.18,nmodes)), tau_lo, tau_hi)
        ph = R.uniform(0, 2*np.pi, nmodes)
        amp = (f/fmin)**(-0.42)*(1+R.normal(0, 0.35, nmodes))
        atk = migrate*(f-fmin)/(fmax-fmin) + 0.0008
        out = np.zeros(L)
        for i in range(0, nmodes, 200):
            ff = f[i:i+200][:,None]; tt = tau[i:i+200][:,None]; aa = amp[i:i+200][:,None]
            pp = ph[i:i+200][:,None]; kk = atk[i:i+200][:,None]
            out += (aa*np.exp(-t/tt)*(1-np.exp(-t/kk))*np.sin(2*np.pi*ff*t+pp)).sum(0)
        return out/(np.abs(out).max()+1e-9)

    def hat(self, vel=1.0, openness=0.0, art='tip', variant=None):
        R = self.rng; v = int(R.integers(0, 7)) if variant is None else variant
        o = float(np.clip(openness, 0, 1)); key = ('hat', round(o,2), art, v)
        if key not in self._cache:
            L = int((0.06+0.75*o)*SR); tau_hi = 0.045+0.62*o
            a = self._cym(L, 260, 320, 15500, 0.012, tau_hi, seed=9000+v*13+int(o*100), migrate=0.05*o)
            b = self._cym(L, 260, 320, 15500, 0.012, tau_hi, seed=9500+v*13+int(o*100), migrate=0.05*o)
            delta = 0.004+0.016*o
            bb = np.interp(np.clip(np.arange(L)*(1+delta), 0, L-1), np.arange(L), b)
            x = a + bb*(0.55+0.45*o)
            if o < 0.15:
                bz = (np.random.default_rng(7+v).random(L) < 0.09).astype(float); x = x*(1+0.5*bz)
            self._cache[key] = (x/(np.abs(x).max()+1e-9)).astype(np.float32)
        x = self._cache[key].astype(np.float64).copy(); L = len(x); t = np.arange(L)/SR
        if art == 'edge': x = _bp(x, 380, 11000, 2)*1.6
        elif art == 'tip': x = _bp(x, 900, 15000, 2)
        elif art == 'foot': x = _bp(x, 200, 4200, 2)*1.2
        sh = 2**(R.normal(0, 0.018)); idx = np.clip(np.arange(L)*sh, 0, L-1)
        i0 = idx.astype(int); fr = idx-i0
        x = x[i0]*(1-fr) + x[np.minimum(i0+1, L-1)]*fr
        return _ramp(x*vel*np.exp(-t/(0.05+0.85*o)))

    def _bell(self, L, seed):
        """Ride BELL co cao do ro: cac thanh phan BAN DINH (ty le bat dieu hoa
        cua bell that) tren not goc D6 -- quang nam cua SOL truong, "ding" vao
        dung cung bai. Truoc day la 60 mode ngau nhien 520-7000 Hz: nghe ra
        kim loai lech cung, khong co not nao."""
        R = np.random.default_rng(seed)
        t = np.arange(L)/SR
        out = np.zeros(L)
        for ratio, g, tau in BELL_PART:
            f = BELL_F*ratio*2**(R.normal(0, 5)/1200)
            if f > SR/2.2: continue
            out += g*(1+R.normal(0, 0.10))*np.exp(-t/tau)*np.sin(2*np.pi*f*t + R.uniform(0, 2*np.pi))
        wash = self._cym(L, 36, 950, 5600, 0.06, 0.28, seed+77, migrate=0.05)
        y = out + wash*0.35
        return y/(np.abs(y).max()+1e-9)

    def ride(self, vel=1.0, bell=False, variant=None):
        R = self.rng; v = int(R.integers(0, 5)) if variant is None else variant
        key = ('ride', bell, v)
        if key not in self._cache:
            L = int(0.95*SR)
            x = self._bell(L, 4400+v*11) if bell else \
                self._cym(L, 420, 330, 14000, 0.06, 0.72, seed=4000+v*11, migrate=0.10)
            self._cache[key] = x.astype(np.float32)
        x = self._cache[key].astype(np.float64)
        ping = _bp(R.standard_normal(len(x)), 2500, 7000, 2)*np.exp(-np.arange(len(x))/SR/0.006)
        # chuan hoa x+ping nhu cac tieng trong bo trong -> vel danh dung muc lon
        y = x + ping*(0.45 if not bell else 0.5)
        return _ramp((y/(np.abs(y).max()+1e-9))*vel)

    def crash(self, vel=1.0, size=1.0, variant=None):
        R = self.rng; v = int(R.integers(0, 4)) if variant is None else variant
        key = ('crash', round(size,2), v)
        if key not in self._cache:
            self._cache[key] = self._cym(int(1.5*size*SR), 700, 260, 15800, 0.10,
                                         1.35*size, seed=3000+v*17, migrate=0.22).astype(np.float32)
        x = self._cache[key].astype(np.float64); L = len(x)
        sh = 2**(R.normal(0, 0.02)); idx = np.clip(np.arange(L)*sh, 0, L-1)
        i0 = idx.astype(int); fr = idx-i0
        return _ramp((x[i0]*(1-fr) + x[np.minimum(i0+1, L-1)]*fr)*vel)

    def clapstack(self, vel=1.0):
        """CLAP STACK -- Reverie Versa Stack: 3 la cymbal thep bat vao nhau + lac.
        Villa: 'you're always on that'. Day la MOT LOP RIENG, khong phai snare."""
        R = self.rng; L = int(0.40*SR); t = np.arange(L)/SR
        out = np.zeros(L); n = int(R.integers(3, 6))
        for i in range(n):
            d = int(max(0, R.normal(i*0.0085, 0.0022))*SR)
            b = _bp(R.standard_normal(L), 1200, 5200, 2)*np.exp(-t/0.005)
            out[d:] += b[:L-d]*R.uniform(0.65, 1.0)
        metal = np.zeros(L)
        for fr_ in (3100, 4700, 6400, 8900, 11800):
            bq, aq = sg.iirpeak(fr_/(SR/2), R.uniform(28, 55))
            metal += sg.lfilter(bq, aq, R.standard_normal(L))
        metal *= np.exp(-t/0.038)
        tail = _bp(R.standard_normal(L), 900, 3600, 2)*np.exp(-t/0.045)*0.45
        return _ramp((out + metal*0.5 + tail)*vel*0.9)

    def shaker(self, vel=1.0):
        R = self.rng; L = int(0.16*SR); t = np.arange(L)/SR
        return _ramp(_bp(R.standard_normal(L), 4200, 13000, 2)*np.exp(-t/R.uniform(0.016,0.030))*vel*0.5)

    def tamb(self, vel=1.0):
        R = self.rng; L = int(0.3*SR); t = np.arange(L)/SR; x = np.zeros(L)
        for fr in (4700, 6100, 7900, 9800, 12200):
            b, a = sg.iirpeak(fr/(SR/2), R.uniform(45, 75)); x += sg.lfilter(b, a, R.standard_normal(L))
        j = (R.random(L) < 0.14).astype(float)
        return _ramp(x*np.exp(-t/R.uniform(0.028,0.055))*(0.6+0.7*j)*vel*0.45)

# ============================ 3. NGUOI CHOI ============================
SIGMA = {'kick':0.0048,'snare':0.0024,'hat':0.0026,'tom':0.0030,'cym':0.0034,'perc':0.0038}
ACC16 = [1.00,0.45,0.70,0.45,0.85,0.45,0.68,0.45,0.95,0.45,0.70,0.45,0.85,0.48,0.68,0.52]

class Performer:
    """Villa tu noi anh giu hi-hat 16 'to be consistent with my time' -> tay phai
    RAT deu, sai so nho. Nhung kick dao phach va ghost note thi nguoi.
    swing: chi ap len hat/shaker/perc (dung theo tai lieu garage), khong len kick."""
    def __init__(self, kit, total_s, seed=11, swing=0.55):
        self.k = kit
        self.rng = np.random.default_rng(seed)
        N = int(total_s*SR) + SR
        self.bus = {n: np.zeros(N) for n in ['kick','snare','hat','tom','cym','perc']}
        R = np.random.default_rng(seed+1)
        self.sysoff = {}
        for inst in SIGMA:
            for p in range(16): self.sysoff[(inst, p)] = R.normal(0, 0.0030)
        self.laid = {'kick':0.0,'snare':0.004,'hat':-0.001,'tom':0.004,'cym':0.0,'perc':0.002}
        self.swing = swing
        self.openhats = []

    def _t(self, beat, inst, pos16):
        p = int(round(pos16)) % 16
        metric = 0.0032 if p % 4 == 0 else -0.0026
        sw = 0.0
        if inst in ('hat','perc','cym') and p % 2 == 1:
            sw = (self.swing - 0.5)*(SPB(beat)/2.0)
        return (T(beat) + self.sysoff[(inst,p)] + self.rng.normal(0, SIGMA[inst])
                + metric + self.laid[inst] + sw)

    def _add(self, name, t0, x, g=1.0):
        b = self.bus[name]; i = int(t0*SR)
        if i < 0: x = x[-i:]; i = 0
        n = min(len(x), len(b)-i)
        if n > 0: b[i:i+n] += x[:n]*g
        return i

    def _v(self, base, pos16, arc=1.0):
        return base*ACC16[int(pos16) % 16]*arc*(1 + self.rng.normal(0, 0.040))

    def K(self, beat, p, v=1.0, arc=1.0, tune=46.0):
        self._add('kick', self._t(beat,'kick',p), self.k.kick(self._v(v,p,arc), tune))
    def S(self, beat, p, v=1.0, art='center', arc=1.0, tune=212.0):
        self._add('snare', self._t(beat,'snare',p), self.k.snare(self._v(v,p,arc), tune, art))
    def H(self, beat, p, v=1.0, o=0.0, art='tip', arc=1.0, choke_beat=None):
        i = self._add('hat', self._t(beat,'hat',p), self.k.hat(self._v(v,p,arc), o, art))
        if o > 0.25 and choke_beat is not None:
            self.openhats.append((i, int(T(choke_beat)*SR)))
    def TM(self, beat, p, v=1.0, tune=180.0, arc=1.0):
        self._add('tom', self._t(beat,'tom',p), self.k.ctom(self._v(v,p,arc), tune))
    def RD(self, beat, p, v=1.0, bell=False, arc=1.0):
        self._add('cym', self._t(beat,'cym',p), self.k.ride(self._v(v,p,arc), bell))
    def CR(self, beat, p, v=1.0, size=1.0):
        self._add('cym', self._t(beat,'cym',p), self.k.crash(v*(1+self.rng.normal(0,.04)), size))
    def CS(self, beat, p, v=1.0, arc=1.0):
        self._add('perc', self._t(beat,'perc',p), self.k.clapstack(self._v(v,p,arc)))
    def SH(self, beat, p, v=1.0, arc=1.0):
        self._add('perc', self._t(beat,'perc',p), self.k.shaker(self._v(v,p,arc)))
    def TB(self, beat, p, v=1.0, arc=1.0):
        self._add('perc', self._t(beat,'perc',p), self.k.tamb(self._v(v,p,arc)))
    def apply_chokes(self):
        h = self.bus['hat']
        for start, cut in self.openhats:
            if start < cut < len(h):
                n = min(int(0.005*SR), len(h)-cut); h[cut:cut+n] *= np.linspace(1, 0.25, n)

def delay(x, ms):
    d = int(ms/1000*SR); return np.concatenate([np.zeros(d), x])[:len(x)]

def mix_kit(bus, room_amount=0.20, oh_amount=0.80, lpf=11000):
    K,S,H,TMb,CY,PC = (bus['kick'],bus['snare'],bus['hat'],bus['tom'],bus['cym'],bus['perc'])
    kick_m  = K + _lp(delay(S,0.6),800)*0.11 + _lp(delay(TMb,0.8),700)*0.09
    snare_m = S + _lp(delay(K,0.5),650)*0.15 + _hp(delay(H,0.3),1500)*0.17 + delay(TMb,0.7)*0.12
    hat_m   = _hp(H,400) + _hp(delay(S,0.4),900)*0.20
    tom_m   = TMb + _lp(delay(K,0.6),600)*0.10 + delay(S,0.5)*0.14
    ohsrc = _lp(K,900)*0.42 + S*0.85 + H*0.95 + TMb*0.75 + CY*1.0 + PC*0.6
    OH    = _hp(delay(ohsrc,3.8),120)
    rsrc  = _lp(K,1200)*0.6 + S + H*0.7 + TMb + CY*0.9 + PC*0.7
    RM    = delay(rsrc,8.7)
    for d,g in [(17,0.5),(23,0.38),(31,0.3),(41,0.22),(53,0.16)]:
        RM = RM + delay(rsrc, 8.7+d)*g
    RM = _bp(np.tanh(RM*1.5), 180, 7000, 2)
    dry = kick_m*1.0 + snare_m*0.92 + hat_m*0.50 + tom_m*0.80 + CY*0.48 + PC*0.80
    return _lp(dry + OH*oh_amount + RM*room_amount, lpf, 3)

# ============================ 4. FX ============================
_IR = {}
def _ir(decay=1.6):
    if decay in _IR: return _IR[decay]
    n = int(decay*SR); r = np.random.default_rng(7)
    e = np.exp(-np.arange(n)/(decay*SR/4.2))
    irL = r.standard_normal(n)*e; irR = r.standard_normal(n)*e
    b, a = sg.butter(2, 3600/(SR/2), 'low')
    irL = sg.lfilter(b,a,irL); irR = sg.lfilter(b,a,irR)
    irR = 0.90*irR + 0.10*irL
    irL[:int(0.035*SR)] = 0; irR[:int(0.035*SR)] = 0
    irL /= np.abs(irL).sum()/8; irR /= np.abs(irR).sum()/8
    _IR[decay] = (irL, irR); return _IR[decay]

def reverb(l, r, decay=1.6, wet=0.28):
    irL, irR = _ir(decay)
    wl = sg.fftconvolve(l, irL)[:len(l)]; wr = sg.fftconvolve(r, irR)[:len(r)]
    return l*(1-wet)+wl*wet, r*(1-wet)+wr*wet

def comp(x, thr=0.10, ratio=3.0, atk=0.005, rel=0.10, mu=1.0):
    e = np.abs(x)
    env_ = _lp(e, 1.0/max(rel,1e-3)/6.283, 1)
    env_ = np.maximum(env_, _lp(e, 1.0/max(atk,1e-4)/6.283, 1)*0.35)
    g = np.ones_like(x); over = env_ > thr
    g[over] = (thr + (env_[over]-thr)/ratio)/(env_[over]+1e-9)
    return x*g*mu

def write_wav(path, data):
    d = np.clip(data, -1, 1); pcm = (d*32767).astype('<i2'); n = pcm.size*2
    with open(path, 'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '
                + struct.pack('<IHHIIHH',16,1,2,SR,SR*4,4,16)+b'data'+struct.pack('<I',n))
        f.write(pcm.tobytes())

# ============================ 5. HOA AM ============================
PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
QUAL = {
 '':[0,4,7],'M':[0,4,7],'maj':[0,4,7],'m':[0,3,7],'min':[0,3,7],
 '5':[0,7],'sus2':[0,2,7],'sus4':[0,5,7],'dim':[0,3,6],'aug':[0,4,8],
 '6':[0,4,7,9],'m6':[0,3,7,9],
 '7':[0,4,7,10],'maj7':[0,4,7,11],'m7':[0,3,7,10],'mmaj7':[0,3,7,11],
 'dim7':[0,3,6,9],'m7b5':[0,3,6,10],
 '7sus4':[0,5,7,10],'7sus2':[0,2,7,10],
 'add9':[0,4,7,14],'madd9':[0,3,7,14],
 '9':[0,4,7,10,14],'maj9':[0,4,7,11,14],'m9':[0,3,7,10,14],
 '11':[0,4,7,10,14,17],'m11':[0,3,7,10,14,17],'13':[0,4,7,10,14,21],
 'm7sus2':[0,2,7,10],'msus2':[0,2,7],
}
def parse_ch(sym):
    s = sym.strip(); bass = None
    if '/' in s:
        s, bs = s.split('/', 1)
        b = PC[bs[0].upper()]; i = 1
        while i < len(bs) and bs[i] in '#b': b += 1 if bs[i]=='#' else -1; i += 1
        bass = b % 12
    r = PC[s[0].upper()]; i = 1
    while i < len(s) and s[i] in '#b': r += 1 if s[i]=='#' else -1; i += 1
    q = s[i:]
    if q not in QUAL: raise ValueError('unknown chord: %r' % sym)
    pcs = [(r+x) % 12 for x in QUAL[q]]
    return r % 12, pcs, (bass if bass is not None else r % 12)

def voicelead(pcs, prev, lo=52, hi=76):
    cands = []
    for pc in pcs:
        opts = [m for m in range(lo, hi+1) if m % 12 == pc]
        if not opts: opts = [lo + ((pc-lo) % 12)]
        cands.append(opts)
    if prev is None:
        out = []; cur = lo
        for opts in cands:
            o = [m for m in opts if m >= cur] or opts
            out.append(o[0]); cur = out[-1]+1
        return sorted(out)
    out = []; used = set()
    for opts in cands:
        best = min(opts, key=lambda m: (min(abs(m-p) for p in prev), m in used,
                                        abs(m-int(np.mean(prev)))))
        out.append(best); used.add(best)
    out = sorted(set(out))
    if len(out) < len(pcs):
        for pc in pcs:
            if not any(m % 12 == pc for m in out):
                o = [m for m in range(lo, hi+1) if m % 12 == pc]
                if o: out.append(min(o, key=lambda m: abs(m-int(np.mean(out)))))
        out = sorted(set(out))
    return out

class Prog:
    def __init__(self, items, lo=52, hi=76, bass_oct=2):
        self.items = items
        self.voicings = []; self.basses = []; self.syms = []; self.spans = []
        prev = None; b = 0.0
        for sym, dur in items:
            r, pcs, bs = parse_ch(sym)
            v = voicelead(pcs, prev, lo, hi); prev = v
            self.voicings.append(v); self.basses.append(12*(bass_oct+1)+bs)
            self.syms.append(sym); self.spans.append((b, b+dur)); b += dur
        self.length = b
    def idx_at(self, rel):
        rel = rel % self.length
        for i,(s,e) in enumerate(self.spans):
            if s <= rel < e: return i
        return len(self.spans)-1
    def at(self, rel):
        i = self.idx_at(rel); return self.voicings[i], self.basses[i], self.syms[i]
    def events(self, start=0.0, reps=1):
        out = []
        for r in range(reps):
            for i,(s,e) in enumerate(self.spans):
                out.append((start + r*self.length + s, e-s,
                            self.voicings[i], self.basses[i], self.syms[i]))
        return out

# ============================ 6. GIONG HAT ============================
VOWF = {
 'a' :[(800,1.00,90),(1150,0.60,110),(2900,0.30,160),(3900,0.12,220)],
 'e' :[(430,1.00,70),(1700,0.70,110),(2700,0.30,150),(3800,0.10,220)],
 'i' :[(300,1.00,60),(2150,0.80,110),(3000,0.30,160),(3900,0.12,220)],
 'o' :[(450,1.00,70),(820,0.60,100),(2830,0.20,150),(3700,0.08,220)],
 'u' :[(330,1.00,60),(700,0.50,100),(2530,0.20,150),(3600,0.07,220)],
 'y' :[(290,1.00,60),(1800,0.55,110),(2600,0.22,150),(3600,0.08,220)],
 'aa':[(700,1.00,95),(1250,0.65,115),(2600,0.28,165),(3800,0.10,220)],
}
CONS_PLOSIVE = {'p':(0,'lip'),'b':(1,'lip'),'t':(0,'tip'),'d':(1,'tip'),'k':(0,'back'),'g':(1,'back')}
CONS_FRIC = {'f':(0,900,5200),'v':(1,700,4200),'s':(0,4200,11000),'z':(1,3200,9000),
             'S':(0,2000,7000),'h':(0,600,4000),'T':(0,3000,8500)}
CONS_NASAL = {'m':320,'n':420,'N':520}
CONS_LIQ = {'l':(360,1200),'r':(320,1100)}
CONS_GLIDE = {'w':(300,700),'j':(300,2100)}
CONS_AFFR = {'C':(0,2200,7500),'J':(1,1800,6000)}

def _src(f0, L, vib=5.2, vibd=0.005, seed=0, breath=0.22, style='deadpan'):
    t = np.arange(L)/SR
    r2 = np.random.default_rng(500+int(seed))
    vd = vibd*(1.6 if style == 'croon' else (0.45 if style == 'deadpan' else 1.0))
    vf = 1 + vd*np.sin(2*np.pi*vib*t + seed)*np.minimum(1, t*2.5)
    drift = 1 + 0.0018*np.sin(2*np.pi*0.6*t + seed*0.7)
    ph = 2*np.pi*np.cumsum(f0*vf*drift)/SR
    K = int(min(48, (SR/2.2)//max(f0, 1)))
    tilt = 1.05 if style in ('shout','falsetto') else 1.24
    x = sum(np.sin(ph*k)/(k**tilt) for k in range(1, K+1))*0.5
    if style == 'falsetto':
        x = np.sin(ph)*0.85 + np.sin(ph*2)*0.14 + np.sin(ph*3)*0.05
    n = r2.standard_normal(L)
    return x + _bp(n, 1200, 6500, 2)*breath

def _formant(x, vow, shift=1.0, g=1.0):
    out = np.zeros(len(x))
    for fc, gg, bw in VOWF[vow]:
        fc = fc*shift
        lo = max(fc-bw, 40); hi = min(fc+bw, SR/2-100)
        if lo >= hi: continue
        out += _bp(x, lo, hi, 2)*gg*14
    return out*g

def _consonant(c, dur_s, f0, seed=0, style='deadpan'):
    R = np.random.default_rng(900+int(seed))
    if c in ('', None, ' '): return np.zeros(0), 0.0
    if c in CONS_PLOSIVE:
        voiced, place = CONS_PLOSIVE[c]
        sil = 0.018; bl = 0.011
        L = int((sil+bl)*SR); t = np.arange(L)/SR
        n = R.standard_normal(L)
        band = {'lip':(300,1800),'tip':(2400,7000),'back':(1200,3600)}[place]
        b = _bp(n, band[0], band[1], 2)*np.exp(-np.maximum(t-sil, 0)/0.0035)
        b[:int(sil*SR)] = 0
        if voiced: b = b*0.75 + np.sin(2*np.pi*f0*t)*np.exp(-t/0.05)*0.35
        return _ramp(b*1.5, 0.4), sil+bl
    if c in CONS_FRIC:
        voiced, lo, hi = CONS_FRIC[c]
        d = 0.050 if c in 'sSTz' else 0.040
        L = int(d*SR); t = np.arange(L)/SR
        x = _bp(R.standard_normal(L), lo, hi, 2)
        x *= np.minimum(1, t*90)*np.exp(-np.maximum(t-d*0.6, 0)/0.02)
        if voiced: x = x*0.7 + np.sin(2*np.pi*f0*t)*0.30
        return _ramp(x*1.1, 0.5), d
    if c in CONS_NASAL:
        fc = CONS_NASAL[c]; d = 0.050
        L = int(d*SR); t = np.arange(L)/SR
        s = _src(f0, L, seed=seed, breath=0.03, style=style)
        x = _bp(s, fc*0.6, fc*1.5, 2)*6.0*np.minimum(1, t*40)
        return _ramp(x, 0.5), d
    if c in CONS_LIQ:
        f1, f2 = CONS_LIQ[c]; d = 0.044
        L = int(d*SR); t = np.arange(L)/SR
        s = _src(f0, L, seed=seed, breath=0.05, style=style)
        x = (_bp(s, f1*0.7, f1*1.4, 2) + _bp(s, f2*0.75, f2*1.35, 2)*0.7)*7.0
        if c == 'r': x = x*(1 + 0.5*np.sin(2*np.pi*32*t))
        return _ramp(x*np.minimum(1, t*35), 0.5), d
    if c in CONS_GLIDE:
        f1, f2 = CONS_GLIDE[c]; d = 0.055
        L = int(d*SR); t = np.arange(L)/SR
        s = _src(f0, L, seed=seed, breath=0.04, style=style)
        sweep = np.linspace(0.75, 1.0, L)
        x = (_bp(s, f1*0.7, f1*1.5, 2) + _bp(s, f2*0.7, f2*1.5, 2)*0.6)*6.5*sweep
        return _ramp(x*np.minimum(1, t*25), 0.5), d
    if c in CONS_AFFR:
        voiced, lo, hi = CONS_AFFR[c]
        d = 0.065; L = int(d*SR); t = np.arange(L)/SR
        fr = _bp(R.standard_normal(L), lo, hi, 2)*np.minimum(1, np.maximum(t-0.018, 0)*120) \
             * np.exp(-np.maximum(t-0.030, 0)/0.018)
        x = fr
        if voiced: x = x*0.7 + np.sin(2*np.pi*f0*t)*np.exp(-t/0.05)*0.3
        return _ramp(x*1.3, 0.4), d
    return np.zeros(0), 0.0

def say(b_, t0, note, dur, vow='a', cons='', g=0.16, style='deadpan', seed=0,
        det=0.0, shift=1.0, breath=None):
    m = nn(note) if isinstance(note, str) else note
    f0 = hz(m)*2**(det/1200)
    br = {'deadpan':0.20,'croon':0.26,'shout':0.16,'whisper':0.95,'falsetto':0.30}[style]
    if breath is not None: br = breath
    L = int(dur*SR) + int(0.28*SR)
    if L <= 0: return
    src = _src(f0, L, seed=seed, breath=br, style=style)
    if style == 'whisper':
        src = _bp(np.random.default_rng(700+int(seed)).standard_normal(L), 400, 7000, 2)
    x = _formant(src, vow, shift=shift)
    a = {'deadpan':0.018,'croon':0.045,'shout':0.010,'whisper':0.030,'falsetto':0.035}[style]
    rl = min(0.16, dur*0.45 + 0.05)
    x *= env(L, a, 0.10, 0.80, rl)
    if style == 'shout': x = np.tanh(x*1.8)
    cx, cd = _consonant(cons, dur, f0, seed=seed, style=style)
    if len(cx): put(b_, t0-cd, cx, g*(0.85 if style != 'whisper' else 0.5))
    put(b_, t0, _ramp(x, 1.0), g)

# --- bo phien am gon: moi am tiet = [phu am][NGUYEN AM]  -------------------
#     nguyen am HOA:  A=a  E=e  I=i  O=o  U=u  Y=y  @=aa
#     phu am thuong:  p b t d k g f v s z h m n l r w j
#     ghep hai chu :  sh th ng ch dj   (-> S T N C J cua engine)
_VOW = {'A':'a','E':'e','I':'i','O':'o','U':'u','Y':'y','@':'aa'}
_DIG = {'sh':'S','th':'T','ng':'N','ch':'C','dj':'J'}
def _syl(s):
    v = _VOW[s[-1]]; c = s[:-1]
    if c in _DIG: c = _DIG[c]
    elif len(c) > 1: c = c[0]
    return v, c

def sing(b_, bar0, text, cells, g=0.16, style='deadpan', oct8=0.0, seed=0,
         det=0.0, shift=1.0):
    """text = chuoi am tiet cach nhau boi dau cach; cells = [(phach, dai, not)]"""
    syls = text.split()
    assert len(syls) == len(cells), 'lech am tiet: %d vs %d' % (len(syls), len(cells))
    for i, (sy, (bt, dur, note)) in enumerate(zip(syls, cells)):
        vow, cons = _syl(sy)
        t0 = T(bar0 + bt); t1 = T(bar0 + bt + dur)
        say(b_, t0, note, t1-t0, vow, cons, g=g, style=style, seed=seed+i*7,
            det=det, shift=shift)
        if oct8 > 0:
            m = (nn(note) if isinstance(note, str) else note) + 12
            say(b_, t0, m, t1-t0, vow, cons, g=g*oct8, style='falsetto',
                seed=seed+i*7+301, det=det+6, shift=shift*0.92)

def stack(b_, bar0, text, cells, g=0.12, n=3, spread=14, jit=0.012, seed=0, style='deadpan'):
    R = np.random.default_rng(int(bar0*97) % 99991 + seed)
    for k in range(n):
        d = R.normal(0, spread); j = R.normal(0, jit)
        for i, (sy, (bt, dur, note)) in enumerate(zip(text.split(), cells)):
            vow, cons = _syl(sy)
            t0 = T(bar0+bt) + j; t1 = T(bar0+bt+dur) + j
            m = nn(note) if isinstance(note, str) else note
            say(b_, t0, m, t1-t0, vow, cons, g=g/np.sqrt(n)*1.5, style=style,
                seed=seed+k*31+i*7, det=d, shift=1.0+R.normal(0, 0.025))

def vox_chain(V, vgain=2.9):
    x = _hp(V, 150, 2)
    x = comp(x, thr=0.045, ratio=4.0, atk=0.005, rel=0.130)
    x = comp(x, thr=0.085, ratio=3.2, atk=0.001, rel=0.050)
    x = x + _bp(x, 1900, 4300, 2)*1.15 + _hp(x, 7200, 2)*0.55
    x = _hp(x, 300, 2)
    return np.tanh(x*1.1)*vgain

# ============================ 7. NHAC CU ============================
def voxorgan(b_, t0, notes, dur, g=0.07, viby=1.0):
    """Vox Continental -- dan organ combo. Trong garage day la tieng 'stab'."""
    L = int(dur*SR) + int(0.10*SR); t = np.arange(L)/SR
    R = np.random.default_rng(int(t0*97) % 9999)
    e = env(L, 0.008, 0.04, 0.94, 0.05)
    for m in np.atleast_1d(notes):
        f = hz(m); x = np.zeros(L)
        for k, a in [(1,1.0),(2,.60),(3,.34),(4,.40),(5,.14),(6,.20),(8,.16)]:
            x += np.sin(2*np.pi*f*k*t*(1+0.0007*k) + R.uniform(0, 6))*a
        x *= (1 + 0.055*viby*np.sin(2*np.pi*6.9*t + f*0.001))
        put(b_, t0, np.tanh(x*0.55)*e*0.16, g)

def musicbox(b_, t0, m, dur, g=0.09):
    L = int(min(dur+1.4, 2.2)*SR); t = np.arange(L)/SR
    R = np.random.default_rng(int(m)*13 + int(t0*100) % 997)
    f = hz(m)*2; x = np.zeros(L)
    for r, a, tau in [(1,1.0,0.85),(2.76,0.42,0.42),(5.40,0.24,0.22),
                      (8.93,0.12,0.13),(13.4,0.06,0.08)]:
        ff = f*r*(1 + R.normal(0, 0.003))
        if ff > SR/2.2: continue
        x += a*np.exp(-t/tau)*np.sin(2*np.pi*ff*t + R.uniform(0, 6))
    click = _bp(R.standard_normal(L), 2200, 7000, 2)*np.exp(-t/0.0022)*0.5
    put(b_, t0, _ramp(np.tanh((x+click)*1.1)), g)

def dulcimer(b_, t0, m, dur, g=0.09, seed=0):
    L = int(min(dur+1.0, 1.9)*SR); t = np.arange(L)/SR
    R = np.random.default_rng(int(m)*11 + seed); x = np.zeros(L)
    for c in (-6, 6):
        f = hz(m)*2**(c/1200)
        for k, a, tau in [(1,1.0,0.75),(2,0.52,0.44),(3,0.34,0.30),(4,0.22,0.22),
                          (5,0.15,0.17),(6,0.10,0.13),(8,0.06,0.09)]:
            ff = f*k*(1 + 0.0009*k*k)
            if ff > SR/2.2: continue
            x += a*np.exp(-t/tau)*np.sin(2*np.pi*ff*t + R.uniform(0, 6))
    hit = _bp(R.standard_normal(L), 1800, 7000, 2)*np.exp(-t/0.0035)*0.6
    put(b_, t0, _ramp(np.tanh((x*0.5+hit)*1.1)), g)

def prepiano(b_, t0, m, dur, g=0.10, seed=0):
    L = int(min(dur+0.6, 1.6)*SR); t = np.arange(L)/SR
    R = np.random.default_rng(int(m)*29 + seed)
    f = hz(m); x = np.zeros(L)
    for r, a, tau in [(1,0.55,0.16),(2.03,0.30,0.10),(3.41,0.42,0.075),(4.77,0.35,0.055),
                      (6.9,0.26,0.038),(9.6,0.18,0.026),(13.7,0.10,0.018)]:
        ff = f*r*(1 + R.normal(0, 0.006))
        if ff > SR/2.2: continue
        x += a*np.exp(-t/tau)*np.sin(2*np.pi*ff*t + R.uniform(0, 6))
    buzz = _bp(R.standard_normal(L), 1400, 6000, 2)*np.exp(-t/0.030)*0.55
    thud = _lp(R.standard_normal(L), 300, 2)*np.exp(-t/0.022)*0.45
    put(b_, t0, _ramp(np.tanh((x+buzz+thud)*1.2)), g)

def choir(b_, t0, notes, dur, g=0.07, vow='e', n=3, spread=14):
    L = int(dur*SR) + int(0.3*SR)
    R = np.random.default_rng(int(t0*777) % 9999)
    e = env(L, 0.11, 0.20, 0.86, 0.28)
    for m in np.atleast_1d(notes):
        for i in range(n):
            d = R.normal(0, spread)
            s = _src(hz(m)*2**(d/1200), L, vib=5.6, vibd=0.010, seed=int(m)*3+i,
                     breath=0.16, style='croon')
            put(b_, t0 + abs(R.normal(0, 0.012)), _formant(s, vow, shift=1.06+R.normal(0,0.02))
                * e*0.010/np.sqrt(n), g)

def pad(b_, t0, notes, dur, g=0.05, cut=2600, det=6.0):
    L = int(dur*SR) + int(0.5*SR); t = np.arange(L)/SR
    e = env(L, 0.35, 0.3, 0.9, 0.6)
    for m in np.atleast_1d(notes):
        for c in (-det, det):
            f = hz(m)*2**(c/1200)
            x = _lp(sg.sawtooth(2*np.pi*f*t)*0.5, cut, 2)
            put(b_, t0, x*e*0.05, g)

def subbass(b_, t0, m, dur, g=0.34, gl=0.0, oct_down=0.0, hp=38.0, lp=760.0):
    """Sub. LUU Y: khong con quang tam duoi mac dinh -- no chi la tieng u o
    ~27 Hz, an het headroom ma tai khong nghe thay. Thay vao do la boi am 2 va 3
    de TAI DINH VI DUOC CAO DO tren loa nho. hp cat sach phan duoi 38 Hz."""
    L = int(min(dur, 2.6)*SR) + int(0.18*SR); t = np.arange(L)/SR
    ff = hz(m)*(2**(-gl/12*np.exp(-t*26)))
    ph = 2*np.pi*np.cumsum(ff)/SR
    x = np.sin(ph)*1.0 + np.sin(ph*2)*0.34 + np.sin(ph*3)*0.13
    if oct_down: x = x + np.sin(ph/2)*oct_down
    x = _lp(x, lp, 2)*env(L, 0.008, 0.10, 0.88, min(0.20, dur*0.4+0.05))
    x = _hp(x, hp, 2)
    put(b_, t0, np.tanh(x*0.75), g)

def seqpulse(b_, t0, m, dur, g=0.13, cut=1500, res=1.0, decay=0.09):
    """Bass giua co bo loc cong huong -- lop 'organ/mid bass' cua 2-step."""
    L = int(min(dur+0.25, 1.2)*SR); t = np.arange(L)/SR
    ph = 2*np.pi*hz(m)*t
    x = sg.sawtooth(ph)*0.6 + 0.4*sg.square(ph, 0.35)
    ce = cut*(1 + 2.4*np.exp(-t/decay))
    out = np.zeros(L); step = 512
    zi = np.zeros(2)
    for i in range(0, L, step):
        fc = float(np.clip(ce[min(i, L-1)], 90, SR/2-500))
        bq, aq = sg.butter(2, fc/(SR/2), 'low')
        seg, zi = sg.lfilter(bq, aq, x[i:i+step], zi=zi)
        out[i:i+len(seg)] += seg
    zi = np.zeros(2)
    for i in range(0, L, step):
        fc = float(np.clip(ce[min(i, L-1)], 90, SR/2-500))
        bq, aq = sg.iirpeak(min(fc, SR/2-600)/(SR/2), 2.6+5*res)
        seg, zi = sg.lfilter(bq, aq, out[i:i+step], zi=zi)
        out[i:i+len(seg)] += seg*0.40*res
    out *= env(L, 0.003, 0.06, 0.72, min(0.18, dur*0.5+0.03))
    put(b_, t0, np.tanh(out*0.7)*0.5, g)

# ============================ 8. TRON ============================
def _rms(x): return float(np.sqrt(np.mean(x*x)+1e-18))
def _seg(b0, b1): return slice(int(T(b0)*SR), int(T(b1)*SR))

def _autobal(V, REST, MAP, lo=300, hi=4000, step_s=0.050, smooth=45,
             gmin=0.10, gmax=4.5, passes=3):
    rb = _bp(REST, lo, hi, 2)
    N = len(V); hop = int(step_s*SR); nsteps = N//hop + 1
    total = np.ones(nsteps); cur_v = V.copy()
    for p in range(passes):
        vb = _bp(cur_v, lo, hi, 2); gain = np.ones(nsteps)
        for name, b0, b1, target in MAP:
            s = _seg(b0, b1); i0 = max(s.start//hop, 0); i1 = min(s.stop//hop, nsteps)
            if i1 <= i0: continue
            rv = _rms(vb[s]); rr = _rms(rb[s])
            if rv < 1e-7 or rr < 1e-7: continue
            cur = 20*np.log10(rv/rr)
            gain[i0:i1] = np.clip(10**((target-cur)/20.0), gmin, gmax)
        if smooth > 1:
            w = np.hanning(smooth); w /= w.sum()
            gain = np.convolve(np.pad(gain, (smooth, smooth), mode='edge'), w,
                               mode='same')[smooth:-smooth]
        total = np.clip(total*gain, gmin, gmax)
        cur_v = V*np.interp(np.arange(N), np.arange(nsteps)*hop, total)
    return cur_v, total

def mixdown(STEMS, VOXBUF, MAP, drum_bus=None, drum_gain=0.62, vgain=2.9,
            wide=1.15, rev_decay=1.5, rev_wet=0.19, air=0.48, pres=0.14,
            target_rms=0.175, peak=0.94, no_vocal=False, auto_wide=True):
    N = max([len(s[0]) for s in STEMS] + ([len(drum_bus)] if drum_bus is not None else [])
            + [len(VOXBUF)])
    def fit(x):
        y = np.zeros(N); y[:len(x)] += x[:N]; return y
    V = fit(VOXBUF)
    if no_vocal: V = np.zeros(N)
    Vp = vox_chain(V, vgain=1.0)
    REST = np.zeros(N)
    for bufx, pan, gn, carve, haas in STEMS: REST += fit(bufx)*gn
    if drum_bus is not None: REST += fit(drum_bus)*drum_gain
    Vb, genv = _autobal(Vp*vgain, REST, MAP)
    pk = float(np.percentile(np.abs(Vb), 99.85))
    if pk > 1e-9:
        lim = pk*1.35; Vb = np.tanh(Vb/lim)*lim
    ve = _lp(np.abs(Vb), 13, 2); ve /= (np.percentile(ve, 99.5)+1e-9)
    duckV = np.clip(1 - 0.34*np.clip(ve, 0, 1), 0.6, 1.0)
    L = np.zeros(N); R = np.zeros(N)
    for bufx, pan, gn, carve, haas in STEMS:
        x = fit(bufx)*gn
        if carve > 0:
            x = (x - _bp(x, 1500, 4000, 2)*carve*(1-duckV)/0.34)*duckV
        pl = np.sqrt((1-pan)/2); pr = np.sqrt((1+pan)/2)
        if haas:
            d = int(abs(haas)/1000*SR)
            xd = np.concatenate([np.zeros(d), x])[:N]
            if haas > 0: L += x*pl; R += xd*pr
            else:        L += xd*pl; R += x*pr
        else:
            L += x*pl; R += x*pr
    if drum_bus is not None:
        d = fit(drum_bus); d = d/(np.abs(d).max()+1e-9)
        d = comp(d, thr=0.16, ratio=3.0, atk=0.004, rel=0.100)*0.72
        par = _hp(np.tanh(d*4.2), 175, 2)*0.24
        d = (d+par)*drum_gain
        hi = _hp(d, 700, 2)
        dl = np.concatenate([np.zeros(int(0.0055*SR)), hi])[:N]
        dr = np.concatenate([np.zeros(int(0.0089*SR)), hi])[:N]
        L += d + dr*0.30 - dl*0.10; R += d + dl*0.30 - dr*0.10
    L += Vb*0.98; R += Vb*0.98
    L, R = reverb(L, R, decay=rev_decay, wet=rev_wet)
    M = (L+R)/2; S0 = (L-R)/2
    Sh = _hp(S0, 240, 2); Sl = _lp(S0, 240, 2)
    def _corr(w):
        S = Sh*w + Sl; return float(np.corrcoef(M+S, M-S)[0, 1])
    if auto_wide:
        best = wide; bd = 9e9
        for w in [1.0,1.15,1.3,1.5,1.7,1.95,2.2,2.5,2.8,3.2,3.6,4.1,4.6,5.2,6.0,7.0,
                  8.0,9.5,11.0,13.0,15.0,18.0,21.0,25.0]:
            c = _corr(w); dd = abs(c-0.945)
            if dd < bd: bd = dd; best = w
            if c < 0.925: break
        wide = best
    S = Sh*wide + Sl
    L, R = M+S, M-S
    L = L + _hp(L, 6800, 2)*air + _bp(L, 2000, 5000, 2)*pres
    R = R + _hp(R, 6800, 2)*air + _bp(R, 2000, 5000, 2)*pres
    cur = _rms((L+R)/2)
    if cur > 1e-9:
        k = target_rms/cur; L *= k; R *= k
    L = np.tanh(L*0.80); R = np.tanh(R*0.80)
    L = _hp(L, 26, 2); R = _hp(R, 26, 2)
    mx = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    L *= peak/mx; R *= peak/mx
    return np.stack([L, R], axis=1), (genv, Vb)

def railed(st, thr=0.75, flat=0.004, run_len=44, edge=0.35):
    cnt = 0
    for ch in (0, 1):
        x = st[:, ch]; d = np.abs(np.diff(x, prepend=x[0]))
        bad = (np.abs(x) > thr) & (d < flat)
        i = 0; n = len(bad)
        while i < n-run_len:
            if bad[i:i+run_len].all():
                j = i
                while j < n and bad[j]: j += 1
                lo = max(0, i-64); hi = min(n, j+64)
                if d[lo:hi].max() > edge: cnt += 1
                i = j
            else: i += 1
    return cnt

def report(st, VOXBUF, STEMS, MAP, drum_bus=None, drum_gain=0.62, name='', VB=None):
    N = st.shape[0]
    def fit(x):
        y = np.zeros(N); y[:len(x)] += x[:N]; return y
    V = fit(VB) if VB is not None else vox_chain(fit(VOXBUF), 1.0)
    REST = np.zeros(N)
    for b, pan, gn, c, h in STEMS: REST += fit(b)*gn
    if drum_bus is not None: REST += fit(drum_bus)*drum_gain
    lb = _bp(V, 300, 4000, 2); rb = _bp(REST, 300, 4000, 2)
    mono = (st[:, 0]+st[:, 1])/2
    rows = []; rms_list = []
    for nm, b0, b1, tg in MAP:
        s = _seg(b0, b1)
        rv = _rms(lb[s]); rr = _rms(rb[s])
        db = 20*np.log10((rv+1e-12)/(rr+1e-12)) if rr > 1e-9 else float('nan')
        r = _rms(mono[s]); rms_list.append(r)
        rows.append((nm, round(db, 2), round(r, 4)))
    dyn = max(rms_list)/(min(rms_list)+1e-9)
    corr = float(np.corrcoef(st[:, 0], st[:, 1])[0, 1])
    print('== %s ==' % name)
    print('  dai %d:%02d  peak %.3f  rms %.3f  railed %d  corrLR %.3f  dyn %.2fx' % (
        int(N/SR)//60, int(N/SR) % 60, np.abs(st).max(), _rms(mono), railed(st), corr, dyn))
    for nm, db, r in rows:
        print('   %-14s giong/nhac %+6.2f dB   rms %.4f' % (nm, db, r))
    return rows, dyn, corr


# =============================================================================
#  BO CONG CU CHUNG CHO CAC BAI  (trong kieu Nick Villa)
# =============================================================================
B = lambda bar: bar*4.0

#  16 buoc / o nhip, chi so 0..15.  G = ghost note tren snare.
#  Villa (video anh tu day "Death & Romance"):
#    - kick DAO PHACH
#    - "the ghost notes on the snare are sometimes coinciding with the kicks"
#    - "keep the hi-hat on 16th notes ... to be consistent with my time"
#    - fill vao o phach "two-and" (buoc 6)
#    - len doan thi chuyen sang RIDE va them BELL
PAT = {
 # -- khung 2-step / DnB: kick buoc 0 va 10, snare 4 va 12 -----------------
 'core'   : dict(K="x.........x.....", S="....x.......x...", G="x.........x....."),
 'syn'    : dict(K="x..x......x...x.", S="....x.......x...", G="...x......x...x."),
 'chorus' : dict(K="x..x......x...x.", S="....x.......x..x", G="...x......x...x."),
 'sparse' : dict(K="x...............", S="............x...", G="................"),
 'half'   : dict(K="x.....x.........", S="........x.......", G="......x........."),
 # -- Villa nguyen mau A: disco bon-tren-san (Image / Cry For Me) ----------
 'disco'  : dict(K="x...x...x...x...", S="....x.......x...", G="..x...x...x...x."),
 'disco2' : dict(K="x...x...x..xx...", S="....x.......x...", G="..x...x...x...x."),
 # -- Villa nguyen mau B: funk 16 dao phach, ghost bam theo kick ----------
 'funk16' : dict(K="x..x..x...x..x..", S="....x.......x...", G="...x..x...x..x.."),
 # -- Villa nguyen mau C: motorik / krautrock -----------------------------
 'motorik': dict(K="x.....x.x.....x.", S="....x.......x...", G="......x.x......."),
 # -- Villa nguyen mau E: breakbeat chopped -------------------------------
 'break'  : dict(K="x.....x...x.....", S="....x.......x..x", G="......x...x....."),
 # -- Amen-ish (Break It Off / jungle) ------------------------------------
 'amen'   : dict(K="x.........xx....", S="....x..g.g..x..g", G=".......x.x......"),
 'amen2'  : dict(K="..........xx....", S=".x..x..g.g....x.", G=".......x.x......"),
 # -- Jersey club: cu kick ba (Boy's a Liar) ------------------------------
 'jersey' : dict(K="x..x..x.....x...", S="....x.......x...", G="...x..x.....x..."),
 'jersey2': dict(K="x..x..x...x.x...", S="....x.......x..x", G="...x..x...x....."),
}

def bar_drums(P, bar, kind='core', hats='16', arc=1.0, clap=True, shk=True,
              openhat=None, ridebell=False, kv=1.0, sv=1.0, hv=0.42, ghost=0.30,
              tamb=None, snare_tune=212.0):
    b0 = B(bar); p = PAT[kind]
    for i in range(16):
        t = b0 + i*0.25
        if p['K'][i] == 'x': P.K(t, i, kv*arc*(1.0 if i == 0 else 0.92))
        if p['S'][i] == 'x': P.S(t, i, sv*arc, tune=snare_tune)
        elif p['S'][i] == 'g': P.S(t, i, 0.26*arc, art='ghost')
        if p['G'][i] == 'x' and p['S'][i] not in 'xg':
            P.S(t, i, ghost*arc, art='ghost')
        if hats == '16':
            P.H(t, i, hv*arc*(1.0 if i % 4 == 0 else 0.78), 0.0)
        elif hats == '8' and i % 2 == 0:
            P.H(t, i, (hv+0.04)*arc, 0.0)
        elif hats == 'ride' and i % 2 == 0:
            P.RD(t, i, hv*arc*(1.0 if i % 4 == 0 else 0.74), bell=(ridebell and i % 4 == 0))
        if openhat is not None and i == openhat:
            P.H(t, i, 0.55*arc, 0.55, choke_beat=b0+4.0)
        if shk: P.SH(t, i, 0.30*arc)
    if clap:
        for i in (4, 12): P.CS(b0 + i*0.25, i, 0.62*arc)
    if tamb:
        for i in tamb: P.TB(b0 + i*0.25, i, 0.32*arc)

def disco_openhat(P, bar, arc=1.0):
    """Villa nguyen mau disco: hat MO tren tung phach 'and' (buoc 2,6,10,14)."""
    for i in (2, 6, 10, 14):
        P.H(B(bar)+i*0.25, i, 0.46*arc, 0.42, choke_beat=B(bar)+(i+2)*0.25)

def villa_fill(P, bar, intensity=1.0, crash_next=True, start=6, tunes=None):
    """Fill vao buoc 6 = phach 'two-and'. Tom la CONCERT TOM (kho, ngan, co cao do)."""
    b0 = B(bar); tunes = tunes or [260, 205, 165, 128]
    steps = list(range(start, 16))
    for j, i in enumerate(steps):
        t = b0 + i*0.25
        v = (0.52 + 0.48*j/max(len(steps)-1, 1))*intensity
        if i < start+2:
            P.S(t, i, v*0.85, art='ghost' if i == start else 'center')
        else:
            P.TM(t, i, v, tune=tunes[min((i-start-2)//2, len(tunes)-1)])
        if i in (10, 14): P.K(t, i, 0.80*intensity)
    if crash_next:
        P.CR(B(bar+1), 0, 0.80*intensity, size=1.0)
        P.K(B(bar+1), 0, 1.0*intensity)

def hat_only(P, bar, v=0.28, shk=True, n=16):
    b0 = B(bar)
    for i in range(16):
        if n == 8 and i % 2: continue
        P.H(b0+i*0.25, i, v, 0.0)
        if shk: P.SH(b0+i*0.25, i, v*0.7)

def sect_finder(SECT):
    def prog_at(bar):
        for k, (a, b, p) in SECT.items():
            if a <= bar < b: return p, a
        return list(SECT.values())[-1][2], list(SECT.values())[-1][0]
    return prog_at

def play_riff(b_, bar, cell, g=0.125, cut=1500, res=1.0, inst=None):
    inst = inst or seqpulse
    for off, dur, note in cell:
        t0 = T(B(bar)+off)
        inst(b_, t0, nn(note) if isinstance(note, str) else note,
             T(B(bar)+off+dur)-t0, g=g, cut=cut, res=res)

def sub_line(b_, bar, prog, a0, steps=(0, 10), g=0.33, oct_off=-12, dur_beats=(1.35, 1.0)):
    for k, i in enumerate(steps):
        rel = (bar-a0)*4.0 + i*0.25
        _, bs, _ = prog.at(rel)
        subbass(b_, T(B(bar)+i*0.25), bs+oct_off,
                dur_beats[min(k, len(dur_beats)-1)]*SPB(B(bar)), g=g)

def render(NAME, build, MAP):
    for nv in (False, True):
        st, (V, STEMS, DRUM, Vb) = build(no_vocal=nv)
        fn = '%s%s.wav' % (NAME, '-inst' if nv else '')
        write_wav(fn, st)
        report(st, V, STEMS, MAP, drum_bus=DRUM, drum_gain=0.60,
               name=fn, VB=(None if nv else Vb))
        print('  -> %s' % fn)
# =============================================================================
#  "SMALL HOURS"
#  Chep khung cua "FEEL COMPLETE" (PinkPantheress, Heaven Knows).
#  Hooktheory: SI truong, 99 BPM.  MOI doan deu la cung mot o 2 nhip:
#  ii - V - iii - iii/5 - IV.  Doan giua them mot hop am giam vii*/VI lam
#  not chuyen.  Doi sang SOL truong.  Bai cham nhat trong bo -- 2:55.
#  Trong: nguyen mau MOTORIK cua Nick Villa (anh noi ro anh hoc Phil Selway:
#  "restraint, motorik pulse, texture-over-chops").
# =============================================================================
NAME = 'small-hours'
configure(99, 99, 292)

VERSE_P = Prog([('Am',2),('D',2),('Bm',1),('Bm/F#',1),('C/G',2)], lo=55, hi=79)
CHOR_P  = Prog([('Am7',2),('D',2),('Bm7',1),('Bm/F#',1),('C/G',2)], lo=55, hi=79)
PRE_P   = Prog([('Am7',4),('D',4),('Em7',4),('C',4)], lo=55, hi=79)
BRID_P  = Prog([('Cmaj7',4),('Cdim',2),('Bm7',2),('Am7',4),('D',4),
                ('Cmaj7',4),('Cdim',2),('Bm7',2),('Em7',4),('D',4)], lo=55, hi=79)

SECT = {'intro':(0,8,VERSE_P),'verse':(8,24,VERSE_P),'pre':(24,32,PRE_P),
        'chor1':(32,44,CHOR_P),'bridge':(44,52,BRID_P),
        'chor2':(52,64,CHOR_P),'outro':(64,72,VERSE_P)}
prog_at = sect_finder(SECT)

def build_drums(P):
    for bar in range(0,4): hat_only(P,bar,0.22+0.05*bar)
    for bar in range(4,8):
        bar_drums(P,bar,'sparse' if bar<6 else 'motorik','16',arc=0.70,clap=(bar>=6))
    villa_fill(P,7,0.68)
    for bar in range(8,24):
        if bar in (15,23): continue
        bar_drums(P,bar,'motorik' if bar%2==0 else 'core','16',arc=0.88,ghost=0.28,
                  openhat=14 if bar%4==3 else None)
    for bar in (15,23):
        bar_drums(P,bar,'motorik','16',arc=0.88); villa_fill(P,bar,0.80)
    for bar in range(24,30): bar_drums(P,bar,'funk16','16',arc=0.80,tamb=(2,6,10,14))
    bar_drums(P,30,'half','16',arc=0.70,clap=False)
    bar_drums(P,31,'half','16',arc=0.86,clap=False); villa_fill(P,31,1.0)
    for bar in range(32,44):
        if bar==43: continue
        bar_drums(P,bar,'motorik','ride',arc=1.0,ridebell=True,kv=1.04,hv=0.36,tamb=(2,6,10,14))
    bar_drums(P,43,'motorik','ride',arc=1.0,ridebell=True,hv=0.36); villa_fill(P,43,0.95)
    for bar in range(44,51):
        bar_drums(P,bar,'half','16',arc=0.46,clap=False,shk=False,kv=0.80,sv=0.68)
    bar_drums(P,51,'half','16',arc=0.60,clap=False,shk=False); villa_fill(P,51,1.0)
    for bar in range(52,64):
        if bar==63: continue
        bar_drums(P,bar,'motorik','ride',arc=1.04,ridebell=True,kv=1.08,hv=0.36,tamb=(2,6,10,14))
        if bar%4==0: P.CR(B(bar),0,0.40,size=0.8)
    bar_drums(P,63,'motorik','ride',arc=1.04,ridebell=True,hv=0.36); villa_fill(P,63,1.0,crash_next=False)
    for bar in range(64,70): bar_drums(P,bar,'core','16',arc=0.74-0.10*(bar-64),clap=(bar<68))
    for bar in range(70,72): hat_only(P,bar,0.18)
    P.apply_chokes()

RIFF  = [(0.00,0.42,'A1'),(0.75,0.22,'A2'),(1.50,0.42,'E2'),(2.25,0.22,'A1'),
         (3.00,0.40,'D2'),(3.50,0.45,'F#2'),
         (4.50,0.42,'B1'),(5.25,0.22,'B2'),(6.00,0.40,'G1'),(7.00,0.60,'D2')]
RIFF_B= [(0.00,0.42,'A1'),(0.75,0.22,'A2'),(1.50,0.42,'C2'),(2.25,0.22,'E2'),
         (2.75,0.30,'D2'),(3.50,0.45,'B1'),
         (4.50,0.42,'G1'),(5.25,0.22,'D2'),(6.00,0.40,'F#2'),(6.75,0.75,'A1')]

def build_sub(b_):
    for bar in range(4,70):
        prog,a0=prog_at(bar)
        if 44<=bar<52:
            if bar%2==0:
                _,bs,_=prog.at((bar-a0)*4.0)
                subbass(b_,T(B(bar)),bs-12,T(B(bar)+8)-T(B(bar)),g=0.30)
            continue
        sub_line(b_,bar,prog,a0,steps=(0,6,10),dur_beats=(0.9,0.7,1.0),g=0.34)

def build_mid(b_):
    for bar in range(8,70,2):
        if 44<=bar<52: continue
        cell,g=(RIFF_B,0.34) if (32<=bar<44 or 52<=bar<64) else (RIFF,0.30)
        if bar>=64: g=0.24
        play_riff(b_,bar,cell,g=g,cut=1500 if bar<32 else 1800,res=1.15)

def build_chords(pad_b,org_b,box_b):
    for name,(a,b,prog) in SECT.items():
        reps=int(round((b-a)*4.0/prog.length))
        for bt,dur,v,bs,sym in prog.events(B(a),reps):
            t0=T(bt);t1=T(bt+dur)
            gp={'intro':.030,'verse':.036,'pre':.046,'chor1':.052,
                'bridge':.050,'chor2':.054,'outro':.032}[name]
            pad(pad_b,t0,v,t1-t0,g=gp,cut=2200 if name in('verse','intro') else 3000)
            if name!='bridge':
                go={'intro':.052,'verse':.062,'pre':.055,'chor1':.080,
                    'chor2':.084,'outro':.040}[name]
                voxorgan(org_b,t0,v,min(0.45,dur*0.36)*SPB(bt),g=go)
                if dur>=2.0: voxorgan(org_b,T(bt+1.0),v,0.26*SPB(bt),g=go*0.58)
            else:
                choir(org_b,t0,v,t1-t0,g=0.078,vow='o',n=3)
            if name in ('intro','verse','chor1','chor2','outro'):
                gb=0.034 if name in('chor1','chor2') else 0.024
                # ha 1 quang tam (musicbox tu nhan doi tan so roi) va chi danh
                # tren not GOC cua the bam -> khong con phu am cao lac giong
                if dur>=2.0: musicbox(box_b,t0,v[0]-12,1.1,g=gb)
    for bt,dur,v,bs,sym in BRID_P.events(B(44),1):
        for j,m in enumerate(v): prepiano(box_b,T(bt+j*0.4),m,1.5,g=0.085,seed=j)
    for a in (32,52):
        for bt,dur,v,bs,sym in CHOR_P.events(B(a),6):
            if dur>=2.0: dulcimer(box_b,T(bt),v[0]-12,1.0,g=0.024)

Vs=[("I thU smO @ nU thI h@ pU",
     [(0.5,.5,'B4'),(1.0,.5,'B4'),(1.5,.5,'G4'),(2.0,.5,'B4'),(2.5,.5,'A4'),
      (3.0,.5,'G4'),(3.5,.5,'F#4'),(4.0,2.0,'E4')]),
    ("A mE U lI stU wU tA dU",
     [(8.5,.5,'A4'),(9.0,.5,'A4'),(9.5,.5,'B4'),(10.0,.5,'A4'),(10.5,.5,'G4'),
      (11.0,.5,'A4'),(11.5,.5,'F#4'),(12.0,2.0,'E4')]),
    ("thU r@ dI E tO I thU hO",
     [(16.5,.5,'D5'),(17.0,.5,'B4'),(17.5,.5,'A4'),(18.0,.5,'B4'),(18.5,.5,'A4'),
      (19.0,.5,'G4'),(19.5,.5,'F#4'),(20.0,2.0,'E4')]),
    ("@ nO bU dI kO tI n@",
     [(24.5,.5,'G4'),(25.0,.5,'B4'),(25.5,.5,'A4'),(26.0,.5,'G4'),(26.5,.5,'F#4'),
      (27.0,.5,'G4'),(27.5,2.0,'E4')])]
Vs2=[("jU kO I kwA E A kO I wE tI",
      [(0.5,.5,'B4'),(1.0,.5,'B4'),(1.5,.5,'A4'),(2.0,.5,'B4'),(2.5,.5,'D5'),
       (3.0,.5,'B4'),(3.5,.5,'A4'),(4.0,.5,'G4'),(4.5,.5,'A4'),(5.0,1.5,'G4')]),
     ("fO sU thI bI gO th@ U fO",
      [(8.5,.5,'A4'),(9.0,.5,'B4'),(9.5,.5,'A4'),(10.0,.5,'G4'),(10.5,.5,'F#4'),
       (11.0,.5,'G4'),(11.5,.5,'F#4'),(12.0,2.0,'E4')]),
     ("A wO tI I thU kI CU",
      [(16.5,.5,'D5'),(17.0,.5,'D5'),(17.5,.5,'B4'),(18.0,.5,'A4'),(18.5,.5,'B4'),
       (19.0,.5,'A4'),(19.5,2.0,'G4')]),
     ("@ A dO mA n@",
      [(24.5,.5,'G4'),(25.0,.5,'B4'),(25.5,.5,'A4'),(26.0,.5,'G4'),(26.5,2.5,'E4')])]
Pr=[("@ thU lA kU mU O slO",
     [(0.0,.5,'E4'),(0.5,.5,'G4'),(1.0,.5,'A4'),(1.5,.5,'B4'),(2.0,.5,'A4'),
      (2.5,.5,'G4'),(3.0,1.5,'F#4')]),
    ("@ thU lA kU mU O slO",
     [(8.0,.5,'G4'),(8.5,.5,'B4'),(9.0,.5,'D5'),(9.5,.5,'E5'),(10.0,.5,'D5'),
      (10.5,.5,'B4'),(11.0,1.5,'A4')]),
    ("A dO wO I tU",
     [(16.0,.5,'D5'),(16.5,.5,'B4'),(17.0,.5,'A4'),(17.5,.5,'G4'),(18.0,2.0,'F#4')]),
    ("bU I O wE dU",
     [(24.0,.5,'E5'),(24.5,.5,'D5'),(25.0,.5,'B4'),(25.5,.5,'A4'),(26.0,2.5,'B4')])]
Ch=[("I thU smO @ smO @",
     [(0.5,.5,'G4'),(1.0,.5,'A4'),(1.5,1.0,'B4'),(3.0,.5,'A4'),(3.5,.5,'G4'),
      (4.0,2.0,'E4')]),
    ("A @ thU O lI wU U wE",
     [(8.5,.5,'G4'),(9.0,.5,'A4'),(9.5,.5,'B4'),(10.0,.5,'D5'),(10.5,.5,'B4'),
      (11.0,.5,'A4'),(11.5,.5,'G4'),(12.0,2.5,'F#4')]),
    ("A tE jU E vrI thI A thI",
     [(16.5,.5,'D5'),(17.0,.5,'D5'),(17.5,.5,'B4'),(18.0,.5,'D5'),(18.5,.5,'B4'),
      (19.0,.5,'A4'),(19.5,.5,'G4'),(20.0,2.0,'F#4')]),
    ("I fU wO hI tU hI mI sE",
     [(24.5,.5,'B4'),(25.0,.5,'A4'),(25.5,.5,'G4'),(26.0,.5,'B4'),(26.5,.5,'A4'),
      (27.0,.5,'G4'),(27.5,.5,'F#4'),(28.0,3.0,'E4')])]
Br=[("kU b@ I kU b@ I",
     [(0.5,.5,'G4'),(1.0,.5,'A4'),(2.0,1.0,'B4'),(4.0,.5,'A4'),(4.5,.5,'G4'),
      (6.0,1.5,'E4')]),
    ("A lE thU dO O pU",
     [(16.0,.5,'D5'),(16.5,.5,'D5'),(17.0,.5,'B4'),(17.5,1.0,'A4'),(19.0,.5,'G4'),
      (19.5,2.0,'F#4')])]

def build_vox(V):
    for t,c in Vs:  sing(V,B(8),t,c,g=0.175,oct8=0.14,seed=41)
    for t,c in Vs2: sing(V,B(16),t,c,g=0.175,oct8=0.16,seed=73)
    for t,c in Pr:  sing(V,B(24),t,c,g=0.175,oct8=0.24,seed=109)
    for t,c in Ch:
        sing(V,B(32),t,c,g=0.185,oct8=0.32,seed=139); stack(V,B(32),t,c,g=0.072,n=3,seed=139)
    for t,c in Br:
        sing(V,B(44),t,c,g=0.155,style='croon',seed=193)
        sing(V,B(44),t,c,g=0.055,style='whisper',seed=167)
    for t,c in Ch:
        sing(V,B(52),t,c,g=0.19,oct8=0.38,seed=239); stack(V,B(52),t,c,g=0.092,n=4,seed=239)
    sing(V,B(64),Ch[0][0],Ch[0][1],g=0.155,oct8=0.26,seed=271)
    sing(V,B(68),Ch[0][0],Ch[0][1],g=0.10,style='whisper',seed=297)

MAP=[('intro',B(0),B(8),-3.0),('verse',B(8),B(24),1.5),('pre',B(24),B(32),1.8),
     ('chorus1',B(32),B(44),2.2),('bridge',B(44),B(52),3.0),
     ('chorus2',B(52),B(64),2.4),('outro',B(64),B(72),1.0)]

def build(no_vocal=False):
    P=Performer(Kit(seed=7),TOTAL,seed=11,swing=0.58)
    build_drums(P)
    DRUM=mix_kit(P.bus,room_amount=0.22,oh_amount=0.80,lpf=11500)
    SUB=buf();MID=buf();PADB=buf();ORG=buf();BOX=buf();V=buf()
    build_sub(SUB);build_mid(MID);build_chords(PADB,ORG,BOX);build_vox(V)
    STEMS=[(SUB,0.0,0.95,0.00,0.0),(MID,0.0,1.60,0.10,0.0),(PADB,0.0,1.08,0.30,7.0),
           (ORG,-0.22,1.18,0.34,0.0),(BOX,0.30,0.92,0.26,-5.0)]
    st,(genv,Vb)=mixdown(STEMS,V,MAP,drum_bus=DRUM,drum_gain=0.70,vgain=3.0,
                         rev_decay=1.7,rev_wet=0.205,target_rms=0.166,no_vocal=no_vocal)
    return st,(V,STEMS,DRUM,Vb)

if __name__=='__main__': render(NAME,build,MAP)
