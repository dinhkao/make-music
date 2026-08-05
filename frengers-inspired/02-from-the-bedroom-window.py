import struct
import sys
import os
import numpy as np
from scipy import signal as sg
from scipy.special import jv

SR = 44100
rng = np.random.default_rng(430)

# ===================== TEMPO (configurable) =====================
TEMPO=[(0,326,126,127)]
_gb=None; _ct=None; TOTAL=None

def _bpm(b):
    for s,e,b0,b1 in TEMPO:
        if s<=b<e: return b0+(b1-b0)*(b-s)/(e-s)
    return TEMPO[-1][3]

def configure(bpm0=126,bpm1=127,end=326):
    global TEMPO,_gb,_ct,TOTAL
    TEMPO=[(0,end,bpm0,bpm1)]
    _gb=np.arange(0,end+2,0.004)
    _ct=np.concatenate([[0],np.cumsum(np.array([60.0/_bpm(b) for b in _gb])*0.004)[:-1]])
    TOTAL=T(end)+5
    return TOTAL

def T(b): return float(np.interp(b,_gb,_ct))
def SPB(b): return 60.0/_bpm(b)

def nn(s):
    base={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    n=base[s[0]];i=1
    while i<len(s) and s[i] in '#b': n+=1 if s[i]=='#' else -1;i+=1
    return 12*(int(s[i:])+1)+n

def hz(m): return 440.0*2**((m-69)/12)
def buf(): return np.zeros(int(TOTAL*SR)+SR)

def put(b,t0,x,g=1.0):
    i=int(t0*SR)
    if i<0: x=x[-i:]; i=0
    n=min(len(x),len(b)-i)
    if n>0: b[i:i+n]+=x[:n]*g

def env(L,a,d,s,r):
    e=np.ones(L); ai=min(int(a*SR),L); e[:ai]=np.linspace(0,1,ai)
    di=int(d*SR)
    if ai+di<L: e[ai:ai+di]=np.linspace(1,s,di); e[ai+di:]=s
    else: e[ai:]=np.linspace(1,s,max(L-ai,1))
    ri=min(int(r*SR),L); e[L-ri:]*=np.linspace(1,0,ri)**1.3
    return e

# ---------- KARPLUS-STRONG ----------
_KS={}
def ks(m, dur, damp=0.9955, bright=0.55, seed=0):
    key=(m,round(dur,2),round(bright,2),round(damp,4),seed)
    if key in _KS: return _KS[key]
    f=hz(m); N=max(int(round(SR/f)),2); L=int(dur*SR)+int(0.15*SR)
    r2=np.random.default_rng(1000+m*7+seed)
    burst=r2.standard_normal(N)
    b,a=sg.butter(2,min(900+7000*bright,SR/2-200)/(SR/2),'low'); burst=sg.lfilter(b,a,burst)
    burst*=np.linspace(1,0.2,N)
    exc=np.zeros(L); exc[:N]=burst
    A=np.zeros(N+2); A[0]=1.0; A[N]=-damp/2; A[N+1]=-damp/2
    y=sg.lfilter([1.0],A,exc)
    y*=np.exp(-np.arange(L)/SR*0.55)
    y/= (np.abs(y).max()+1e-9)
    fo=min(int(0.020*SR),L)
    y[-fo:]*=np.linspace(1,0,fo)
    ri=min(int(0.0008*SR),L); y[:ri]*=np.linspace(0,1,ri)
    _KS[key]=y.astype(np.float32)
    return _KS[key]

def jangle(b_, t0, m, dur, g=0.10, seed=0):
    x=ks(m,dur,0.9962,0.72,seed).astype(np.float64)
    bq,aq=sg.butter(2,[180/(SR/2),8800/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x,g)

def crunch(b_, t0, m, dur, g=0.09, drive=6.0, seed=0):
    x=ks(m,dur,0.9950,0.55,seed).astype(np.float64)
    x=np.tanh(x*drive)
    bq,aq=sg.butter(2,[300/(SR/2),6800/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x*env(len(x),0.002,0.05,0.85,0.12),g)

def leadgtr(b_, t0, m, dur, g=0.13, bend=0.0, seed=0):
    x=ks(m,dur,0.9975,0.65,seed).astype(np.float64)
    x=np.tanh(x*9.0)
    L=len(x)
    if bend:
        t=np.arange(L)/SR
        d=(2**((bend*np.minimum(1,t*6))/12)-1)
        idx=np.clip(np.cumsum(1+d),0,L-1); i0=idx.astype(int); fr=idx-i0
        x=x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr
    bq,aq=sg.butter(2,[380/(SR/2),7800/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x*env(L,0.004,0.1,0.9,0.15),g)

# ---------- WURLITZER (2-op FM) ----------
def wurli(b_,t0,m,dur,g=0.13,det=0.0):
    L=int(dur*SR)+int(0.4*SR); t=np.arange(L)/SR
    f=hz(m)*2**(det/1200)
    idx=2.1*np.exp(-t*5.5)+0.35
    x=np.sin(2*np.pi*f*t+idx*np.sin(2*np.pi*f*2*t))
    x+=np.sin(2*np.pi*f*t*1.001)*0.4
    x*=np.exp(-t*2.4)*np.minimum(1,t*260)
    x*= (1+0.10*np.sin(2*np.pi*5.4*t))
    bq,aq=sg.butter(2,4200/(SR/2),'low'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,np.tanh(x*1.3),g)

# ---------- COMBO ORGAN ----------
def organ(b_,t0,notes,dur,g=0.07):
    L=int(dur*SR)+int(0.1*SR); t=np.arange(L)/SR
    e=env(L,0.012,0.05,0.95,0.06)
    for m in notes:
        f=hz(m); x=np.zeros(L)
        for k,amp in [(1,1.0),(2,.55),(3,.30),(4,.35),(6,.16),(8,.12)]:
            x+=np.sin(2*np.pi*f*k*t*(1+0.0006*k))*amp
        x*= (1+0.05*np.sin(2*np.pi*6.6*t+f))
        put(b_,t0,x*e*0.18,g)

# ---------- BASS ----------
def bassn(b_,t0,m,dur,g=0.30,gl=0):
    L=int(min(dur,1.4)*SR)+int(0.18*SR); t=np.arange(L)/SR
    f=hz(m); ff=f*(2**(-gl/12*np.exp(-t*26)))
    ph=2*np.pi*np.cumsum(ff)/SR
    x=sum(np.sin(ph*k)/k for k in range(1,11))*0.5+np.sin(ph)*0.75+np.sin(ph/2)*0.30
    bq,aq=sg.butter(2,1600/(SR/2),'low'); x=sg.lfilter(bq,aq,x)
    pres=_bp(x,1400,3200,2)*0.35
    x=x+pres
    x*=np.exp(-t*2.6)*np.minimum(1,t*480)
    put(b_,t0,np.tanh(x*1.35),g)

# ---------- HORNS ----------
def horn(b_,t0,m,dur,g=0.10,det=0.0,rough=1.0):
    L=int(dur*SR)+int(0.25*SR); t=np.arange(L)/SR
    f=hz(m)*2**(det/1200)
    vf=1+0.006*np.sin(2*np.pi*4.8*t)*np.minimum(1,t*2.2)
    drift=1+0.0035*np.sin(2*np.pi*0.7*t+m)
    ph=2*np.pi*np.cumsum(f*vf*drift)/SR
    x=sum(np.sin(ph*k)/(k**1.12) for k in range(1,20))
    x=np.tanh(x*(1.1+0.9*rough))
    for fc,gg,bw in [(1150,1.0,300),(2200,0.55,420)]:
        bq,aq=sg.butter(2,[(fc-bw)/(SR/2),(fc+bw)/(SR/2)],'band'); x+=sg.lfilter(bq,aq,x)*gg*0.7
    bq,aq=sg.butter(2,[230/(SR/2),5200/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x*env(L,0.055,0.18,0.85,0.22),g)

# ---------- VOCAL FORMANT ----------
VOW={'a':[(800,.10,90),(1150,.06,110),(2900,.03,160)],
     'e':[(430,.10,70),(1700,.07,110),(2700,.03,150)],
     'i':[(300,.10,60),(2150,.08,110),(3000,.03,160)],
     'o':[(450,.10,70),(820,.06,100),(2830,.02,150)],
     'u':[(330,.10,60),(700,.05,100),(2530,.02,150)]}
def voice(f0,L,vow='a',breath=0.22,vib=5.2,vibd=0.005,seed=0):
    t=np.arange(L)/SR
    r2=np.random.default_rng(500+seed)
    vf=1+vibd*np.sin(2*np.pi*vib*t+seed)*np.minimum(1,t*2.5)
    ph=2*np.pi*np.cumsum(f0*vf)/SR
    K=int(min(46,(SR/2.2)//max(f0,1)))
    src=sum(np.sin(ph*k)/(k**1.05) for k in range(1,K+1))*0.5
    n=r2.standard_normal(L); bq,aq=sg.butter(2,[1200/(SR/2),6500/(SR/2)],'band')
    src=src+sg.lfilter(bq,aq,n)*breath
    out=np.zeros(L)
    for fc,gg,bw in VOW[vow]:
        bq,aq=sg.butter(2,[max(fc-bw,40)/(SR/2),min(fc+bw,SR/2-100)/(SR/2)],'band')
        out+=sg.lfilter(bq,aq,src)*gg*14
    return out

def sing(b_,t0,m,dur,vow='a',g=0.16,breath=0.24,seed=0,det=0.0):
    L=int(dur*SR)+int(0.35*SR)
    x=voice(hz(m)*2**(det/1200),L,vow,breath,seed=seed)
    put(b_,t0,x*env(L,0.07,0.25,0.78,0.3),g)

def gang(b_,t0,m,dur,vow='a',g=0.14,n=6,spread=17,jit=0.022):
    r2=np.random.default_rng(int(t0*1000)%9999)
    for i in range(n):
        d=r2.normal(0,spread); j=r2.normal(0,jit)
        mm=m+(12 if i>=n-2 else 0)
        sing(b_,t0+j,mm,dur,vow,g/np.sqrt(n)*1.5,breath=0.30,seed=i*13+int(m),det=d)

# ---------- noise bed ----------
def noise_sw(b_,t0,dur,g=0.09,up=True,lo=300,hi=9000):
    L=int(dur*SR); t=np.linspace(0,1,L)
    n=rng.standard_normal(L)
    bq,aq=sg.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); n=sg.lfilter(bq,aq,n)
    put(b_,t0,n*((t**2) if up else ((1-t)**2)),g)

# ===================== DRUM KIT (MODAL SYNTH) =====================
IDEAL=[1.0000,1.5934,2.1356,2.2952,2.6528,2.9172,3.1551,3.4998,3.5983,3.6470]
JMN  =[2.405,3.832,5.136,5.520,6.380,7.016,7.588,8.417,8.654,8.771]
MORD =[0,1,2,0,3,1,4,2,0,5]
AIRLOADED=[1.00,1.50,1.98,2.44,2.89,3.36]

def _hp(x,f,o=2): b,a=sg.butter(o,min(f,SR/2-100)/(SR/2),'high'); return sg.lfilter(b,a,x)
def _lp(x,f,o=2): b,a=sg.butter(o,min(f,SR/2-100)/(SR/2),'low');  return sg.lfilter(b,a,x)
def _bp(x,lo,hi,o=2):
    hi=min(hi,SR/2-100); lo=max(lo,20)
    b,a=sg.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return sg.lfilter(b,a,x)

def modal(f0,taus,gains,L,rng,glide=0.05,tg=0.02,detune_cents=0,ratios=IDEAL):
    t=np.arange(L)/SR
    g=1+glide*np.exp(-t/tg)
    ph=2*np.pi*np.cumsum(g)/SR
    det=2**(detune_cents/1200)
    out=np.zeros(L)
    for r,tau,gn in zip(ratios,taus,gains):
        f=f0*r*det
        if f>SR/2.2: continue
        out+=gn*np.exp(-t/tau)*np.sin(ph*f+rng.uniform(0,2*np.pi))
    return out

def bessel_gains(r_rel,rng,n=10,jitter=0.08):
    r=np.clip(r_rel+rng.normal(0,jitter),0.0,0.92)
    g=[]
    for i in range(n):
        v=abs(jv(MORD[i], JMN[i]*r))
        g.append(v*10**(rng.normal(0,0.35)))
    g=np.array(g); return g/ (g.max()+1e-9)

def _ramp(x, ms=0.7):
    n=min(int(ms/1000*SR),len(x)); x[:n]*=np.linspace(0,1,n); return x

class Kit:
    def __init__(self, seed=7):
        self.rng=np.random.default_rng(seed)
        self._cache={}
    def kick(self, vel=1.0, tune=48.0, click=1.0, mode='acoustic'):
        R=self.rng; L=int(0.55*SR); t=np.arange(L)/SR
        det=2**(R.normal(0,28)/1200)
        if mode=='acoustic':
            body=np.zeros(L)
            for k in range(1,7):
                f=(tune*k*0.9+7)*det
                tau=0.26/ (k**0.72)
                body+=(1.0/k**0.9)*np.exp(-t/tau)*np.sin(2*np.pi*f*t+R.uniform(0,2*np.pi))
            gl=1+0.09*np.exp(-t/0.025)
            body*= gl
        else:
            f=tune*det*(1+2.6*np.exp(-t/0.030))
            body=np.sin(2*np.pi*np.cumsum(f)/SR+R.uniform(0,2*np.pi))*np.exp(-t/0.16)
            body+=np.sin(2*np.pi*np.cumsum(f*0.5)/SR)*np.exp(-t/0.22)*0.5
        fm=np.sin(2*np.pi*185*det*t+ (2.2*np.exp(-t/0.04))*np.sin(2*np.pi*259*t))
        body+=fm*np.exp(-t/0.045)*0.24
        n=R.standard_normal(L)*np.exp(-t/0.0045)
        cl=_lp(_hp(n,220),4200)*click*0.5*vel
        x=body*vel + cl
        x=_hp(x,32,4)
        return _ramp(np.tanh(x*1.5))
    def snare(self, vel=1.0, tune=205.0, art='center'):
        R=self.rng; L=int(0.42*SR); t=np.arange(L)/SR
        r_rel={'center':0.12,'edge':0.62,'ghost':0.34,'rim':0.20,'cross':0.80}[art]
        g=bessel_gains(r_rel,R)
        taus=np.array([0.045,0.20,0.17,0.055,0.14,0.11,0.09,0.08,0.05,0.07])
        taus=taus*(1+R.normal(0,0.10,10))
        if art=='rim': taus*=0.7
        det=R.normal(0,30)
        mem=modal(tune,taus,g,L,R,glide=0.06,tg=0.02,detune_cents=det)
        mem+=modal(tune*1.42,taus*0.8,g*0.55,L,R,glide=0.05,tg=0.018,
                   detune_cents=det+R.normal(0,18))*0.6
        envm=np.abs(sg.lfilter(*sg.butter(2,120/(SR/2),'low'), np.abs(mem)))
        envm/= (envm.max()+1e-9)
        thr={'ghost':0.42,'center':0.14,'edge':0.20,'rim':0.06,'cross':0.85}[art]
        wire_env=np.clip(envm-thr,0,None)/(1-thr)
        n=R.standard_normal(L)
        wire=_bp(n,1100,9500,3)
        buzz=(R.random(L)<0.055).astype(float)
        buzz=sg.lfilter([1],[1,-0.90],buzz)
        wire=wire*(0.55+0.85*buzz/ (buzz.max()+1e-9))
        d=int(R.uniform(0.0005,0.003)*SR)
        wire=np.concatenate([np.zeros(d),wire])[:L]
        wire*=wire_env*np.exp(-t/R.uniform(0.11,0.24))
        stick=_bp(R.standard_normal(L),2200,7000,2)*np.exp(-t/0.0035)
        if art=='rim':
            shell=_bp(R.standard_normal(L),420,900,2)*np.exp(-t/0.035)*1.1
            x=mem*0.55+wire*1.5+stick*1.5+shell
            x*=vel*2.2
        elif art=='cross':
            wood=_bp(R.standard_normal(L),1300,3400,2)*np.exp(-t/0.006)*2.2
            x=(mem*0.16+wood+wire*0.10)*vel*1.5
        elif art=='ghost':
            x=(mem*0.85+wire*0.55+stick*0.35)*vel*0.22
        else:
            x=(mem*0.75+wire*1.0+stick*0.8)*vel
        return _ramp(np.tanh(x*1.25))
    def flam(self, vel=1.0, tune=205.0, art='center'):
        R=self.rng
        gap=int(R.uniform(0.012,0.032)*SR)
        a=self.snare(vel*R.uniform(0.30,0.48),tune*1.01,'ghost')
        b=self.snare(vel,tune,art)
        out=np.zeros(max(len(a),len(b))+gap)
        out[:len(a)]+=a; out[gap:gap+len(b)]+=b
        return out
    def tom(self, vel=1.0, tune=120.0, art='center'):
        R=self.rng; L=int(0.7*SR); t=np.arange(L)/SR
        g=bessel_gains(0.20 if art=='center' else 0.6,R,n=6)
        taus=np.array([0.30,0.42,0.34,0.26,0.20,0.16])*(1+R.normal(0,0.12,6))
        x=modal(tune,taus,g,L,R,glide=0.08,tg=0.03,detune_cents=R.normal(0,35),
                ratios=AIRLOADED)
        x+=modal(tune*1.06,taus*0.85,g*0.5,L,R,glide=0.07,tg=0.028,
                 ratios=AIRLOADED)*0.5
        stick=_bp(R.standard_normal(L),1800,5500,2)*np.exp(-t/0.004)
        return _ramp(np.tanh((x+stick*0.5)*vel*1.2))
    def _cym(self, L, nmodes, fmin, fmax, tau_lo, tau_hi, seed, migrate=0.10):
        R=np.random.default_rng(seed); t=np.arange(L)/SR
        f=np.sort(R.uniform(fmin,fmax,nmodes)**1.0)
        f=f*(1+R.normal(0,0.02,nmodes))
        tau=tau_hi*(f/fmin)**(-0.62)*(1+R.normal(0,0.18,nmodes))
        tau=np.clip(tau,tau_lo,tau_hi)
        ph=R.uniform(0,2*np.pi,nmodes)
        amp=(f/fmin)**(-0.42)*(1+R.normal(0,0.35,nmodes))
        atk=migrate*(f-fmin)/(fmax-fmin)+0.0008
        out=np.zeros(L)
        CH=200
        for i in range(0,nmodes,CH):
            ff=f[i:i+CH][:,None]; tt=tau[i:i+CH][:,None]
            aa=amp[i:i+CH][:,None]; pp=ph[i:i+CH][:,None]; kk=atk[i:i+CH][:,None]
            seg=aa*np.exp(-t/tt)*(1-np.exp(-t/kk))*np.sin(2*np.pi*ff*t+pp)
            out+=seg.sum(0)
        return out/ (np.abs(out).max()+1e-9)
    def hat(self, vel=1.0, openness=0.0, art='tip', variant=None):
        R=self.rng
        v=int(R.integers(0,7)) if variant is None else variant
        o=float(np.clip(openness,0,1))
        key=('hat',round(o,2),art,v)
        if key not in self._cache:
            L=int((0.06+0.75*o)*SR)
            tau_hi=0.045+0.62*o
            a=self._cym(L,260,320,15500,0.012,tau_hi,seed=9000+v*13+int(o*100),migrate=0.05*o)
            b=self._cym(L,260,320,15500,0.012,tau_hi,seed=9500+v*13+int(o*100),migrate=0.05*o)
            delta=0.004+0.016*o
            bb=np.interp(np.clip(np.arange(L)*(1+delta),0,L-1),np.arange(L),b)
            x=a+bb*(0.55+0.45*o)
            if o<0.15:
                buzz=(np.random.default_rng(7+v).random(L)<0.09).astype(float)
                x=x*(1+0.5*buzz)
            self._cache[key]=(x/ (np.abs(x).max()+1e-9)).astype(np.float32)
        x=self._cache[key].astype(np.float64).copy()
        L=len(x); t=np.arange(L)/SR
        if art=='edge':  x=_bp(x,380,11000,2)*1.6
        elif art=='tip': x=_bp(x,900,15000,2)
        elif art=='foot':x=_bp(x,200,4200,2)*1.2
        sh=2**(R.normal(0,0.018))
        idx=np.clip(np.arange(L)*sh,0,L-1); i0=idx.astype(int); fr=idx-i0
        x=x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr
        return _ramp(x*vel*np.exp(-t/(0.05+0.85*o)))
    def crash(self, vel=1.0, size=1.0, variant=None):
        R=self.rng
        v=int(R.integers(0,4)) if variant is None else variant
        key=('crash',round(size,2),v)
        if key not in self._cache:
            L=int(1.5*size*SR)
            x=self._cym(L,700,260,15800,0.10,1.35*size,seed=3000+v*17,migrate=0.22)
            self._cache[key]=x.astype(np.float32)
        x=self._cache[key].astype(np.float64)
        sh=2**(R.normal(0,0.02)); L=len(x)
        idx=np.clip(np.arange(L)*sh,0,L-1); i0=idx.astype(int); fr=idx-i0
        return _ramp((x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr)*vel)
    def ride(self, vel=1.0, bell=False, variant=None):
        R=self.rng
        v=int(R.integers(0,5)) if variant is None else variant
        key=('ride',bell,v)
        if key not in self._cache:
            L=int(0.95*SR)
            if bell: x=self._cym(L,60,520,7000,0.20,0.85,seed=4400+v*11,migrate=0.02)
            else:    x=self._cym(L,420,330,14000,0.06,0.72,seed=4000+v*11,migrate=0.10)
            self._cache[key]=x.astype(np.float32)
        x=self._cache[key].astype(np.float64)
        ping=_bp(self.rng.standard_normal(len(x)),2500,7000,2)*np.exp(-np.arange(len(x))/SR/0.006)
        return _ramp((x+ping*(0.45 if not bell else 0.8))*vel)
    def clap(self, vel=1.0):
        R=self.rng; L=int(0.45*SR); t=np.arange(L)/SR
        out=np.zeros(L); n=int(R.integers(3,7))
        for i in range(n):
            d=int(max(0,R.normal(i*0.011,0.003))*SR)
            b=_bp(R.standard_normal(L),1050,4400,2)*np.exp(-t/0.006)
            out[d:]+=b[:L-d]*R.uniform(0.6,1.0)
        tail=_bp(R.standard_normal(L),900,3600,2)*np.exp(-t/0.055)*0.55
        return _ramp((out+tail)*vel)
    def tamb(self, vel=1.0):
        R=self.rng; L=int(0.3*SR); t=np.arange(L)/SR
        x=np.zeros(L)
        for fr in (4700,6100,7900,9800,12200):
            b,a=sg.iirpeak(fr/(SR/2),R.uniform(45,75)); x+=sg.lfilter(b,a,R.standard_normal(L))
        jingle=(R.random(L)<0.14).astype(float)
        return _ramp(x*np.exp(-t/R.uniform(0.028,0.055))*(0.6+0.7*jingle)*vel*0.45)
    def shaker(self, vel=1.0):
        R=self.rng; L=int(0.16*SR); t=np.arange(L)/SR
        n=_bp(R.standard_normal(L),4200,13000,2)
        return _ramp(n*np.exp(-t/R.uniform(0.016,0.030))*vel*0.5)
    def conga(self, vel=1.0, tune=210.0, art='open'):
        R=self.rng; L=int(0.45*SR); t=np.arange(L)/SR
        g=bessel_gains(0.15 if art=='open' else 0.55,R,n=6)
        taus=np.array([0.20,0.14,0.10,0.08,0.06,0.05])*(1+R.normal(0,0.12,6))
        if art=='slap': taus*=0.35
        x=modal(tune,taus,g,L,R,glide=0.10,tg=0.02,detune_cents=R.normal(0,25),ratios=AIRLOADED)
        skin=_bp(R.standard_normal(L),900,5200,2)*np.exp(-t/(0.010 if art=='slap' else 0.004))
        return _ramp(np.tanh((x+skin*(1.6 if art=='slap' else 0.7))*vel*1.3))
    def wood(self, vel=1.0, tune=850.0):
        R=self.rng; L=int(0.14*SR); t=np.arange(L)/SR
        x=np.sin(2*np.pi*tune*t)*np.exp(-t/0.012)+np.sin(2*np.pi*tune*2.7*t)*np.exp(-t/0.006)*0.5
        x+=_bp(R.standard_normal(L),1500,6000,2)*np.exp(-t/0.002)*0.8
        return _ramp(np.tanh(x*vel*1.4))

# ===================== PERFORMER + MIX_KIT =====================
SIGMA={'kick':0.0055,'snare':0.0026,'hat':0.0031,'tom':0.0035,'cym':0.0040,'perc':0.0045}
ACC8 =[1.00,0.62,0.85,0.62,0.95,0.62,0.85,0.62]
ACC16=[1.00,0.45,0.70,0.45,0.85,0.45,0.68,0.45,0.95,0.45,0.70,0.45,0.85,0.48,0.68,0.52]

class Performer:
    def __init__(self, kit, Tfunc, SPBfunc, total_s, seed=11, style='indie'):
        self.k=kit; self.T=Tfunc; self.SPB=SPBfunc
        self.rng=np.random.default_rng(seed)
        N=int(total_s*SR)+SR
        self.bus={n:np.zeros(N) for n in ['kick','snare','hat','tom','cym','perc']}
        self.style=style
        R=np.random.default_rng(seed+1)
        self.sysoff={}
        for inst in SIGMA:
            for p in range(16):
                self.sysoff[(inst,p)]=R.normal(0,0.0034)
        self.laid={'kick':0.0,'snare':0.012 if style=='indie' else 0.004,
                   'hat':-0.002,'tom':0.006,'cym':0.0,'perc':0.003}
        self.openhats=[]
        self.hum=1.0
    def _t(self, beat, inst, pos16):
        p=int(round(pos16))%16
        metric = 0.004 if p%4==0 else -0.0032
        h=self.hum
        j=self.rng.normal(0,SIGMA[inst]*h)
        return self.T(beat)+self.sysoff[(inst,p)]*h+j+metric*h+self.laid[inst]*h
    def _add(self,name,t0,x,g=1.0):
        b=self.bus[name]; i=int(t0*SR)
        if i<0: x=x[-i:]; i=0
        n=min(len(x),len(b)-i)
        if n>0: b[i:i+n]+=x[:n]*g
        return i
    def _v(self,base,pos16,grid=16,arc=1.0):
        acc=(ACC16[int(pos16)%16] if grid==16 else ACC8[int(pos16/2)%8])
        return base*acc*arc*(1+self.rng.normal(0,0.042*self.hum))
    def K(self,beat,pos16,v=1.0,arc=1.0,mode='acoustic',tune=48.0):
        vv=self._v(v,pos16,arc=arc)
        self._add('kick',self._t(beat,'kick',pos16),self.k.kick(vv,tune,mode=mode))
    def S(self,beat,pos16,v=1.0,art='center',arc=1.0,tune=205.0):
        vv=self._v(v,pos16,arc=arc)
        x=self.k.flam(vv,tune,art) if art=='flam' else self.k.snare(vv,tune,art)
        self._add('snare',self._t(beat,'snare',pos16),x)
    def H(self,beat,pos16,v=1.0,o=0.0,art='tip',arc=1.0,choke_beat=None):
        vv=self._v(v,pos16,grid=16,arc=arc)
        x=self.k.hat(vv,o,art)
        i=self._add('hat',self._t(beat,'hat',pos16),x)
        if o>0.25 and choke_beat is not None:
            self.openhats.append((i,int(self.T(choke_beat)*SR)))
    def TM(self,beat,pos16,v=1.0,tune=120.0,arc=1.0):
        self._add('tom',self._t(beat,'tom',pos16),self.k.tom(self._v(v,pos16,arc=arc),tune))
    def CR(self,beat,pos16,v=1.0,size=1.0):
        self._add('cym',self._t(beat,'cym',pos16),self.k.crash(v*(1+self.rng.normal(0,.04)),size))
    def RD(self,beat,pos16,v=1.0,bell=False,arc=1.0):
        self._add('cym',self._t(beat,'cym',pos16),self.k.ride(self._v(v,pos16,arc=arc),bell))
    def CL(self,beat,pos16,v=1.0,arc=1.0):
        self._add('perc',self._t(beat,'perc',pos16),self.k.clap(self._v(v,pos16,arc=arc)))
    def TB(self,beat,pos16,v=1.0,arc=1.0):
        self._add('perc',self._t(beat,'perc',pos16),self.k.tamb(self._v(v,pos16,arc=arc)))
    def SH(self,beat,pos16,v=1.0,arc=1.0):
        self._add('perc',self._t(beat,'perc',pos16),self.k.shaker(self._v(v,pos16,arc=arc)))
    def CG(self,beat,pos16,v=1.0,tune=210.0,art='open',arc=1.0):
        self._add('perc',self._t(beat,'perc',pos16),self.k.conga(self._v(v,pos16,arc=arc),tune,art))
    def WD(self,beat,pos16,v=1.0,tune=850.0,arc=1.0):
        self._add('perc',self._t(beat,'perc',pos16),self.k.wood(self._v(v,pos16,arc=arc),tune))
    def apply_chokes(self):
        h=self.bus['hat']
        for start,cut in self.openhats:
            if cut>start and cut<len(h):
                n=min(int(0.005*SR),len(h)-cut)
                h[cut:cut+n]*=np.linspace(1,0.25,n)
    def fill(self, beat_start, beats=2.0, kind='tom', intensity=1.0, next_crash_beat=None):
        R=self.rng
        if kind=='tom':
            toms=[168,140,112,92]
            n=max(int(beats*4),1)
            for i in range(n):
                p=beat_start+i*0.25
                v=(0.55+0.45*i/max(n-1,1))*intensity
                self.TM(p,(i%16),v,tune=toms[min(int(i/max(n/4,1)),3)])
                if i%4==0: self.K(p,(i%16),0.6*intensity)
        elif kind=='snare':
            n=max(int(beats*4),1)
            for i in range(n):
                p=beat_start+i*0.25
                v=(0.45+0.55*i/max(n-1,1))*intensity
                art='ghost' if (i%4 in (1,2) and i<n-4) else 'center'
                self.S(p,(i%16),v,art=art)
        elif kind=='roll':
            n=max(int(beats*8),1)
            for i in range(n):
                p=beat_start+i*0.125
                self.S(p,int(i/2)%16,(0.30+0.70*i/max(n-1,1))*intensity,
                       art='ghost' if i<n*0.5 else 'center')
        elif kind=='negative':
            self.K(beat_start,0,0.9*intensity)
            self.S(beat_start+beats-0.25,12,0.8*intensity,art='rim')
        elif kind=='stutter':
            n=max(int(beats*4),1)
            for i in range(n):
                p=beat_start+i*0.25
                if i%3==0: self.K(p,i%16,0.85*intensity)
                else:      self.S(p,i%16,(0.4+0.5*(i/n))*intensity,
                                  art='ghost' if i%3==1 else 'center')
        elif kind=='trib':
            n=max(int(beats*3),1)
            for i in range(n):
                p=beat_start+i*(beats/n)
                if i%3==0: self.K(p,int(i*16/max(n,1))%16,0.9*intensity)
                else: self.TM(p,int(i*16/max(n,1))%16,0.6*intensity,tune=[150,120,96][i%3])
        elif kind=='burst32':
            n=max(int(beats*8),1)
            for i in range(n):
                p=beat_start+i*0.125
                if i%5==0: self.K(p,int(p*4)%16,0.9*intensity)
                elif i%5 in (1,2): self.S(p,int(p*4)%16,(0.35+0.5*i/n)*intensity,'ghost')
                else: self.TM(p,int(p*4)%16,(0.4+0.4*i/n)*intensity,tune=[150,112][i%2])
        if next_crash_beat is not None:
            self.CR(next_crash_beat,0,0.85*intensity)
            self.K(next_crash_beat,0,1.0*intensity)

def delay(x,ms):
    d=int(ms/1000*SR); return np.concatenate([np.zeros(d),x])[:len(x)]

def mix_kit(bus, room_amount=0.22, oh_amount=1.0, lofi=0.0, lpf=15500):
    K,S,H,TMb,CY,PC=(bus['kick'],bus['snare'],bus['hat'],bus['tom'],bus['cym'],bus['perc'])
    kick_m  = K + _lp(delay(S,0.6),800)*0.11 + _lp(delay(TMb,0.8),700)*0.09
    snare_m = S + _lp(delay(K,0.5),650)*0.15 + _hp(delay(H,0.3),1500)*0.17 + delay(TMb,0.7)*0.12
    hat_m   = _hp(H,400) + _hp(delay(S,0.4),900)*0.20
    tom_m   = TMb + _lp(delay(K,0.6),600)*0.10 + delay(S,0.5)*0.14
    ohsrc = _lp(K,900)*0.42 + S*0.85 + H*0.95 + TMb*0.75 + CY*1.0 + PC*0.6
    OH    = _hp(delay(ohsrc,3.8),120)
    rsrc  = _lp(K,1200)*0.6 + S + H*0.7 + TMb + CY*0.9 + PC*0.7
    RM    = delay(rsrc,8.7)
    for d,g in [(17,0.5),(23,0.38),(31,0.3),(41,0.22),(53,0.16)]:
        RM=RM+delay(rsrc,8.7+d)*g
    RM=_bp(np.tanh(RM*1.5),180,7000,2)
    dry = kick_m*1.0 + snare_m*0.95 + hat_m*0.85 + tom_m*0.8 + CY*0.5 + PC*0.85
    out = dry + OH*oh_amount + RM*room_amount
    if lofi>0:
        step=2**(1+int(6*(1-lofi)))
        out=(1-lofi)*out+lofi*np.round(out*step)/step
    return _lp(out,lpf,3)

# ===================== RENDER FX =====================
_IR = {}
def _ir(decay=1.6):
    if decay in _IR: return _IR[decay]
    n = int(decay*SR)
    r = np.random.default_rng(7)
    e = np.exp(-np.arange(n)/(decay*SR/4.2))
    irL = r.standard_normal(n)*e; irR = r.standard_normal(n)*e
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

def echo(x, ms, fb=0.35, n=6, g=0.5):
    out=np.zeros_like(x); a=g
    for i in range(1,n+1):
        out+=delay(x,ms*i)*a; a*=fb
    return out

def write_wav24(path, data):
    d=np.clip(np.asarray(data,dtype=np.float64),-1,1)
    q=np.ascontiguousarray((d*8388607.0).astype('<i4').ravel())
    pcm=q.view(np.uint8).reshape(-1,4)[:,:3].tobytes()
    n=len(pcm)
    with open(path,'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '+
                struct.pack('<IHHIIHH',16,1,2,SR,SR*6,6,24)+b'data'+struct.pack('<I',n))
        f.write(pcm)

def write_wav(path, data):
    d = np.clip(data, -1, 1)
    pcm = (d*32767).astype('<i2')
    n = pcm.size*2
    with open(path,'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,2,SR,SR*4,4,16)+b'data'+struct.pack('<I',n))
        f.write(pcm.tobytes())

# ================================================================= NHAC CU MO RONG
def _fade(x, ms_in=1.0, ms_out=12.0):
    a=min(int(ms_in/1000*SR),len(x)); b=min(int(ms_out/1000*SR),len(x))
    if a>1: x[:a]*=np.linspace(0,1,a)
    if b>1: x[-b:]*=np.linspace(1,0,b)
    return x

def bowed(b_,t0,m,dur,g=0.09,rough=0.5,det=0.0,atk=0.16,seed=0):
    L=int(dur*SR)+int(0.12*SR); t=np.arange(L)/SR
    R=np.random.default_rng(700+seed+int(m))
    f=hz(m)*2**(det/1200)
    drift=1+0.0022*np.sin(2*np.pi*0.33*t+seed)+0.0016*np.sin(2*np.pi*0.11*t)
    vib=1+0.0035*np.sin(2*np.pi*4.6*t)*np.clip((t-atk)*2.0,0,1)
    ph=2*np.pi*np.cumsum(f*drift*vib)/SR
    x=np.zeros(L)
    for k in range(1,26):
        x+=np.sin(ph*k+R.uniform(0,6.28))/(k**(1.0+0.35*(1-rough)))
    scr=_bp(R.standard_normal(L),1800,7000,2)*0.06*rough
    scr*= (1+0.9*np.sin(2*np.pi*0.9*t))
    x=x*0.35+scr
    for fc,gg,bw in [(430,0.9,120),(980,0.55,220),(2400,0.35,500)]:
        x+=_bp(x,fc-bw,fc+bw,2)*gg*0.5
    e=np.clip(t/atk,0,1)**1.4
    ro=min(int(0.09*SR),L); e[-ro:]*=np.linspace(1,0,ro)**1.2
    put(b_,t0,_fade(np.tanh(x*1.2)*e),g)

def tackpiano(b_,t0,m,dur,g=0.11,tack=0.7,seed=0):
    L=int(min(dur,3.2)*SR)+int(0.5*SR); t=np.arange(L)/SR
    R=np.random.default_rng(800+seed+int(m))
    f=hz(m); x=np.zeros(L)
    B=0.00042
    for k in range(1,17):
        fk=f*k*np.sqrt(1+B*k*k)
        if fk>SR/2.2: break
        tau=(2.2/(1+0.42*k))*(1+R.normal(0,0.07))
        x+=np.exp(-t/tau)*np.sin(2*np.pi*fk*t+R.uniform(0,6.28))/(k**1.15)
    ham=_bp(R.standard_normal(L),900,6500,2)*np.exp(-t/0.0035)
    tk=_bp(R.standard_normal(L),2600,11000,2)*np.exp(-t/0.0016)*tack*2.2
    x=x*0.5+ham*0.6+tk
    put(b_,t0,_fade(np.tanh(x*1.25)),g)

def clav(b_,t0,m,dur,g=0.10,seed=0):
    x=ks(m,min(dur,0.9),0.9905,0.85,seed).astype(np.float64)
    x=np.tanh(x*3.4)
    x=_bp(x,420,5200,2)
    L=len(x); t=np.arange(L)/SR
    x*=np.exp(-t*(3.2+2.4/max(dur,0.08)))
    put(b_,t0,_fade(x),g)

def slidegtr(b_,t0,m0,m1,dur,g=0.11,seed=0,drive=4.0):
    L=int(dur*SR)+int(0.25*SR); t=np.arange(L)/SR
    R=np.random.default_rng(900+seed)
    tr=np.clip((t-0.05)/max(dur*0.45,0.05),0,1)**0.85
    f=hz(m0)*2**((m1-m0)*tr/12)
    ph=2*np.pi*np.cumsum(f)/SR
    x=sum(np.sin(ph*k+R.uniform(0,6.28))/(k**1.25) for k in range(1,14))
    x=np.tanh(x*drive)
    x+=_bp(R.standard_normal(L),2500,8000,2)*np.exp(-t/0.02)*0.25
    x=_bp(x,260,5000,2)
    e=np.minimum(1,t*90)*np.exp(-t*1.5)
    put(b_,t0,_fade(x*e),g)

def marimba(b_,t0,m,dur,g=0.10,metal=False,seed=0):
    L=int(min(dur,2.4)*SR)+int(0.3*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1100+seed+int(m)); f=hz(m)
    rat=[1.0,3.93,9.6,16.5] if not metal else [1.0,4.0,10.7,18.4]
    tau=[0.42,0.16,0.08,0.05] if not metal else [1.6,0.9,0.5,0.3]
    x=np.zeros(L)
    for r,ta,a in zip(rat,tau,[1.0,0.42,0.18,0.09]):
        if f*r>SR/2.2: continue
        x+=a*np.exp(-t/(ta*(1+R.normal(0,0.08))))*np.sin(2*np.pi*f*r*t+R.uniform(0,6.28))
    mal=_bp(R.standard_normal(L),700,4200,2)*np.exp(-t/0.0022)*0.5
    if metal: x*= (1+0.22*np.sin(2*np.pi*5.5*t))
    put(b_,t0,_fade(np.tanh((x+mal)*1.1)),g)

def mellotron(b_,t0,m,dur,g=0.09,kind='flute',seed=0):
    L=int(min(dur,8.0)*SR)+int(0.25*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1200+seed+int(m))
    wow=1+0.0042*np.sin(2*np.pi*0.55*t+R.uniform(0,6))+0.0018*np.sin(2*np.pi*6.3*t)
    f=hz(m)*wow
    ph=2*np.pi*np.cumsum(f)/SR
    if kind=='flute':
        x=np.sin(ph)+0.22*np.sin(ph*2)+0.07*np.sin(ph*3)
        x+=_bp(R.standard_normal(L),1500,7000,2)*0.30
    elif kind=='choir':
        x=sum(np.sin(ph*k+R.uniform(0,6))/(k**1.2) for k in range(1,14))*0.4
        for fc,gg,bw in [(600,1.0,150),(1100,0.6,220),(2600,0.3,500)]:
            x+=_bp(x,fc-bw,fc+bw,2)*gg*0.7
        x+=_bp(R.standard_normal(L),900,5000,2)*0.10
    else:
        x=sg.lfilter([1],[1,-0.2],np.sign(np.sin(ph))*0.3+np.sin(ph)*0.7)
        x=_lp(x,3800,2)
    hiss=R.standard_normal(L)*0.012
    x=_lp(x,9500,2)+hiss
    e=np.minimum(1,t*14)
    ro=min(int(0.10*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(x*e),g)

def nylon(b_,t0,m,dur,g=0.11,seed=0):
    x=ks(m,min(dur,2.6),0.9938,0.30,seed).astype(np.float64)
    x=_bp(x,150,3200,2)
    put(b_,t0,_fade(x),g)

def chime12(b_,t0,m,dur,g=0.09,seed=0):
    x=ks(m,min(dur,3.0),0.9970,0.80,seed).astype(np.float64)
    y=ks(m+12,min(dur,3.0),0.9964,0.86,seed+3).astype(np.float64)*0.55
    n=min(len(x),len(y)); x=x[:n]+np.roll(y[:n],int(0.006*SR))
    x=_bp(x,300,9000,2)
    put(b_,t0,_fade(x),g)

def fuzzbass(b_,t0,m,dur,g=0.20,gl=0,seed=0):
    L=int(min(dur,2.0)*SR)+int(0.15*SR); t=np.arange(L)/SR
    f=hz(m)*(2**(-gl/12*np.exp(-t*22)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sign(np.sin(ph))*0.6+np.sin(ph)*0.9+np.sin(ph*2)*0.25
    x=np.tanh(x*7.0)
    x=_bp(x,55,2600,2)
    x*=np.minimum(1,t*300)*np.exp(-t*1.1)
    put(b_,t0,_fade(x),g)

def subbass(b_,t0,m,dur,g=0.26,gl=0):
    L=int(min(dur,3.0)*SR)+int(0.12*SR); t=np.arange(L)/SR
    f=hz(m)*(2**(-gl/12*np.exp(-t*20)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)+0.12*np.sin(ph*2)
    x*=np.minimum(1,t*160)*np.exp(-t*0.9)
    put(b_,t0,_fade(x,2.0,25.0),g)

def fingerbass(b_,t0,m,dur,g=0.28,gl=0,dead=False,seed=0):
    L=int(min(dur,1.6)*SR)+int(0.16*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1300+seed+int(m))
    f=hz(m)*(2**(-gl/12*np.exp(-t*24)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=sum(np.sin(ph*k+R.uniform(0,6))/(k**1.45) for k in range(1,9))
    x+=_bp(R.standard_normal(L),700,3000,2)*np.exp(-t/0.004)*0.5
    x=_lp(x,900 if not dead else 380,2)
    x*=np.minimum(1,t*420)*np.exp(-t*(2.4 if not dead else 12.0))
    put(b_,t0,_fade(np.tanh(x*1.3)),g)

def bone(b_,t0,m,dur,g=0.10,det=0.0,growl=0.4,seed=0):
    L=int(dur*SR)+int(0.2*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1400+seed+int(m))
    f=hz(m)*2**(det/1200)
    vf=1+0.005*np.sin(2*np.pi*5.1*t)*np.minimum(1,t*3)
    ph=2*np.pi*np.cumsum(f*vf)/SR
    x=sum(np.sin(ph*k)/(k**0.92) for k in range(1,22))
    x=np.tanh(x*(1.4+2.2*growl))
    for fc,gg,bw in [(520,1.0,180),(1200,0.7,320),(2100,0.35,420)]:
        x+=_bp(x,fc-bw,fc+bw,2)*gg*0.6
    x=_bp(x,90,4600,2)
    x+=_bp(R.standard_normal(L),400,2500,2)*np.exp(-t/0.03)*0.18
    put(b_,t0,_fade(x*env(L,0.035,0.14,0.86,0.18)),g)

def leslie(x, rate=6.4, depth=0.35, seed=0):
    n=len(x); t=np.arange(n)/SR
    lfo=np.sin(2*np.pi*rate*t)
    d=(4.5+3.0*lfo)/1000*SR
    idx=np.clip(np.arange(n)-d,0,n-1); i0=idx.astype(int); fr=idx-i0
    y=x[i0]*(1-fr)+x[np.minimum(i0+1,n-1)]*fr
    am=1+depth*lfo
    return y*am

def gospelorgan(b_,t0,notes,dur,g=0.08,drive=1.6):
    L=int(min(dur,10.0)*SR)+int(0.12*SR); t=np.arange(L)/SR
    out=np.zeros(L)
    for m in notes:
        f=hz(m)
        for k,amp in [(0.5,.45),(1,1.0),(1.5,.30),(2,.62),(3,.34),(4,.40),(5,.20),(6,.18),(8,.14)]:
            ff=f*k
            if ff>SR/2.2: continue
            out+=np.sin(2*np.pi*ff*t*(1+0.0004*k))*amp
    out=np.tanh(out*drive*0.22)
    e=np.minimum(1,t*130); ro=min(int(0.035*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(out*e),g)

def saw_drone(b_,t0,m,dur,g=0.06,det=0.0,seed=0):
    L=int(dur*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1500+seed)
    f=hz(m)*2**(det/1200)*(1+0.0016*np.sin(2*np.pi*0.19*t+R.uniform(0,6)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)+0.10*np.sin(ph*3)+0.04*np.sin(ph*5)
    x*= (1+0.10*np.sin(2*np.pi*5.9*t))
    e=np.minimum(1,t*3.0); ro=min(int(0.5*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(x*e),g)

def tapewarp(x, depth=0.0035, rate=0.42, seed=1):
    n=len(x); t=np.arange(n)/SR
    R=np.random.default_rng(seed)
    w=depth*np.sin(2*np.pi*rate*t+R.uniform(0,6))+depth*0.4*np.sin(2*np.pi*rate*3.7*t)
    idx=np.clip(np.cumsum(1+w),0,n-1); i0=idx.astype(int); fr=idx-i0
    return x[i0]*(1-fr)+x[np.minimum(i0+1,n-1)]*fr

# ================================================================= GIONG HAT CO PHU AM
CONS={
 'd' :('plos',0.013,260,2800,1.00), 't':('plos',0.015,1600,7500,1.05),
 'k' :('plos',0.017,800,4200,0.95), 'b':('plos',0.013,110,900,0.95),
 'p' :('plos',0.015,280,1900,0.80), 'g':('plos',0.017,180,1500,0.90),
 's' :('fric',0.070,4200,11500,0.55),'sh':('fric',0.082,2100,7200,0.62),
 'f' :('fric',0.058,1400,7800,0.34), 'h':('fric',0.052,420,3600,0.30),
 'th':('fric',0.055,2900,9500,0.28), 'v':('fric',0.052,900,4200,0.30),
 'z' :('fric',0.058,3200,9200,0.42),
 'm' :('nas', 0.058,260,0,1.0),      'n':('nas',0.052,330,0,1.0),
 'ng':('nas', 0.060,290,0,0.9),
 'l' :('liq', 0.046,380,0,1.0),      'r':('liq',0.052,1250,0,1.0),
 'w' :('liq', 0.056,300,0,1.0),      'y':('liq',0.048,2150,0,1.0),
 'ch':('affr',0.072,2000,7400,0.85), 'j':('affr',0.066,1150,5200,0.72),
 '  ':('none',0.0,0,0,0.0), '':('none',0.0,0,0,0.0),
}
def _consonant(cname, f0, g, seed):
    typ,cd,lo,hi,amp=CONS.get(cname,CONS[''])
    if typ=='none': return np.zeros(1),0.0
    L=max(int(cd*SR),8); t=np.arange(L)/SR
    R=np.random.default_rng(2000+seed+len(cname))
    if typ=='plos':
        x=_bp(R.standard_normal(L),lo,hi,2)*np.exp(-t/(cd*0.28))
        if cname in ('b','d','g'):
            x+=np.sin(2*np.pi*f0*0.9*t)*np.exp(-t/(cd*0.5))*0.35
        x*=amp*1.5
    elif typ=='fric':
        e=np.minimum(1,t/(cd*0.25))*np.exp(-np.maximum(0,t-cd*0.5)/(cd*0.5))
        x=_bp(R.standard_normal(L),lo,hi,3)*e*amp*1.15
        if cname in ('v','z'): x+=np.sin(2*np.pi*f0*t)*e*0.30
    elif typ=='affr':
        h=max(int(L*0.32),4)
        x=np.zeros(L)
        x[:h]=_bp(R.standard_normal(h),1500,6000,2)*np.exp(-np.arange(h)/SR/0.003)
        x[h:]=_bp(R.standard_normal(L-h),lo,hi,3)*np.exp(-np.arange(L-h)/SR/(cd*0.55))
        x*=amp*1.4
    elif typ=='nas':
        ph=2*np.pi*f0*t
        x=sum(np.sin(ph*k)/(k**1.9) for k in range(1,7))
        x=_bp(x,max(lo-140,60),lo+260,2)*3.0
        x*=np.minimum(1,t/0.006)*amp
    else:
        ph=2*np.pi*f0*t
        x=sum(np.sin(ph*k)/(k**1.25) for k in range(1,14))
        x=_bp(x,max(lo-220,60),lo+420,2)*2.4
        x*=np.minimum(1,t/0.008)*amp
        x+=_bp(R.standard_normal(L),600,2800,2)*0.05
    return x*g, cd

def say(b_, t0, m, dur, vow='a', cons='', g=0.16, style='croon', breath=0.24,
        seed=0, det=0.0, drift=0.0):
    f0=hz(m)*2**(det/1200)
    vib  ={'croon':5.2,'deadpan':4.4,'shout':6.1,'whisper':4.0,'falsetto':5.8}[style]
    vibd ={'croon':0.0055,'deadpan':0.0015,'shout':0.009,'whisper':0.002,'falsetto':0.011}[style]
    br   =breath*{'croon':1.0,'deadpan':1.25,'shout':0.8,'whisper':3.2,'falsetto':1.4}[style]
    L=int(max(dur,0.06)*SR)+int(0.20*SR)
    t=np.arange(L)/SR
    cx,cd=_consonant(cons,f0,1.0,seed)
    slide=1.0
    if drift: slide=2**((drift*np.clip((t-dur*0.55)/max(dur*0.45,0.05),0,1))/12)
    R=np.random.default_rng(2500+seed)
    vf=(1+vibd*np.sin(2*np.pi*vib*t+seed)*np.minimum(1,t*2.6))*slide
    vf*= (1+0.0018*np.sin(2*np.pi*0.7*t+seed*0.3))
    ph=2*np.pi*np.cumsum(f0*vf)/SR
    K=int(min(46,(SR/2.2)//max(f0,1)))
    tilt={'croon':1.05,'deadpan':1.18,'shout':0.80,'whisper':1.6,'falsetto':1.45}[style]
    src=sum(np.sin(ph*k)/(k**tilt) for k in range(1,K+1))*0.5
    nz=R.standard_normal(L); src=src+_bp(nz,1200,6500,2)*br
    out=np.zeros(L)
    for fc,gg,bw in VOW[vow]:
        out+=_bp(src,max(fc-bw,40),min(fc+bw,SR/2-100),2)*gg*14
    if style=='shout':
        out=np.tanh(out*2.2)*0.9+_bp(nz,2000,6000,2)*0.20
    elif style=='whisper':
        out=out*0.35+_bp(nz,700,7000,2)*0.55
    a={'croon':0.035,'deadpan':0.018,'shout':0.012,'whisper':0.03,'falsetto':0.045}[style]
    e=env(L,a,0.14,{'croon':0.80,'deadpan':0.72,'shout':0.86,'whisper':0.7,'falsetto':0.8}[style],
          min(0.16,dur*0.55+0.05))
    out*=e
    if len(cx)>4:
        pre=t0-cd*0.82
        put(b_,pre,cx,g*1.0)
    put(b_,t0,out,g)

def line(b_, b0, cells, g=0.17, style='croon', oct8=0.0, det=0.0, breath=0.24,
         seedbase=0, jit=0.010, drag=0.006, Tf=None):
    Tf=Tf or T
    R=np.random.default_rng(3000+seedbase)
    for i,c in enumerate(cells):
        off,d,name,vow=c[0],c[1],c[2],c[3]
        cons=c[4] if len(c)>4 else ''
        drift=c[5] if len(c)>5 else 0.0
        t0=Tf(b0+off)+drag+float(R.normal(0,jit))
        dur=Tf(b0+off+d)-Tf(b0+off)
        m=nn(name) if isinstance(name,str) else name
        say(b_,t0,m,dur,vow,cons,g*float(max(0.4,1+R.normal(0,0.09))),style,breath,
            seed=seedbase+i*7,det=det+float(R.normal(0,7)),drift=drift)
        if oct8>0:
            say(b_,t0+float(R.normal(0,0.008)),m+12,dur,vow,cons,g*oct8,
                'falsetto' if style!='shout' else 'shout',breath*1.2,
                seed=seedbase+i*7+511,det=det+float(R.normal(0,11)))

def chant(b_, b0, cells, g=0.11, n=5, spread=18, style='shout', Tf=None, seedbase=0):
    Tf=Tf or T
    R=np.random.default_rng(4000+seedbase)
    for k in range(n):
        for i,c in enumerate(cells):
            off,d,name,vow=c[0],c[1],c[2],c[3]
            cons=c[4] if len(c)>4 else ''
            t0=Tf(b0+off)+float(R.normal(0,0.020))
            dur=(Tf(b0+off+d)-Tf(b0+off))*float(1+R.normal(0,0.05))
            m=(nn(name) if isinstance(name,str) else name)+(12 if k>=n-1 else 0)
            say(b_,t0,m,dur,vow,cons,g/np.sqrt(n)*1.6,style,0.30,
                seed=seedbase+k*97+i*7,det=float(R.normal(0,spread)))

def shriek(b_,t0,m,dur,g=0.14,seed=0):
    L=int(dur*SR)+int(0.2*SR); t=np.arange(L)/SR
    R=np.random.default_rng(5000+seed)
    f=hz(m)*(1+0.06*np.exp(-t*4))*(1+0.02*np.sin(2*np.pi*7.5*t))
    ph=2*np.pi*np.cumsum(f)/SR
    x=sum(np.sin(ph*k)/(k**0.72) for k in range(1,26))
    x=np.tanh(x*4.0)
    x+=_bp(R.standard_normal(L),1800,9000,2)*0.35
    for fc,gg,bw in [(950,1.0,220),(2400,0.8,500),(3400,0.5,600)]:
        x+=_bp(x,fc-bw,fc+bw,2)*gg*0.6
    e=np.minimum(1,t*45)*np.exp(-t*1.4)
    put(b_,t0,_fade(_bp(x,300,9000,2)*e),g)

# ================================================================= MIX HELPERS
def comp(x,thr,ratio,atk,rel):
    e=np.abs(x); aA=np.exp(-1/(atk*SR)); aR=np.exp(-1/(rel*SR))
    e=np.maximum(sg.lfilter([1-aR],[1,-aR],e),sg.lfilter([1-aA],[1,-aA],e))
    g=np.ones_like(e); o=e>thr; g[o]=(thr+(e[o]-thr)/ratio)/np.maximum(e[o],1e-9)
    bg,ag=sg.butter(2,70/(SR/2),'low'); return x*np.clip(sg.lfilter(bg,ag,g),0.06,1.0)
def comp_gain(x,thr,ratio,atk,rel):
    e=np.abs(x); aA=np.exp(-1/(atk*SR)); aR=np.exp(-1/(rel*SR))
    e=np.maximum(sg.lfilter([1-aR],[1,-aR],e),sg.lfilter([1-aA],[1,-aA],e))
    g=np.ones_like(e); o=e>thr; g[o]=(thr+(e[o]-thr)/ratio)/np.maximum(e[o],1e-9)
    bg,ag=sg.butter(2,70/(SR/2),'low'); return np.clip(sg.lfilter(bg,ag,g),0.06,1.0)
def hp(x,f,o=2): b,a=sg.butter(o,f/(SR/2),'high'); return sg.lfilter(b,a,x)
def lp(x,f,o=2): b,a=sg.butter(o,min(f,SR/2-100)/(SR/2),'low');  return sg.lfilter(b,a,x)
def bp(x,lo,hi,o=2):
    hi=min(hi,SR/2-100); b,a=sg.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return sg.lfilter(b,a,x)
def rms_(x): return float(np.sqrt((np.asarray(x)**2).mean()+1e-18))

def voxchain(vx):
    V=hp(vx,150); V=comp(V,0.045,4.0,0.005,0.13); V=comp(V,0.085,3.2,0.001,0.05)
    V=V+bp(V,1900,4300)*1.15+hp(V,7200)*0.85
    V=hp(V,300); V=np.tanh(V*1.1)*2.9
    return V

def master(L,R,vocals=True,rms_target=0.175,boost=1.0):
    st=np.stack([L,R])*boost
    r=rms_(st)
    if r>1e-9: st=st*(rms_target/r)
    st=np.tanh(st*0.95); st=hp(st,26)
    st/= (np.abs(st).max()+1e-9); st*=0.94
    st=st+bp(st,1900,5200,2)*0.20
    st=st+hp(st,8500,2)*0.75+hp(st,12000,2)*0.45
    st=np.tanh(st*1.05)
    st/= (np.abs(st).max()+1e-9); st*=0.92
    f=int(0.02*SR); st[:,:f]*=np.linspace(0,1,f)
    fo=int(2.2*SR); st[:,-fo:]*=np.linspace(1,0,fo)**0.8
    return st

def widen(L,R,amt=2.4,fc=320):
    M=(L+R)*0.5; S=hp((L-R)*0.5,fc)*amt
    return M+S, M-S

def report(st, V, REST, MAP, Tf=None):
    Tf=Tf or T
    lb=bp(V,300,4000); rb=bp(REST,300,4000); mono=st.mean(0)
    print("  doan          thoi diem  giong/nhac  nang luong")
    es=[]
    for row in MAP:
        nmv,b0,b1 = row[0],row[1],row[2]
        sl=slice(int(Tf(b0)*SR),min(int(Tf(b1)*SR),st.shape[1]))
        rr=20*np.log10(max(rms_(lb[sl]),1e-12)/max(rms_(rb[sl]),1e-12))
        e=rms_(mono[sl]); es.append(e)
        print(f"    {nmv:12s} {int(Tf(b0)//60)}:{Tf(b0)%60:04.1f} {rr:+6.1f}dB  {e:.4f} {'#'*int(e*90)}")
    print(f"    -> dai dong: {max(es)/max(min(es),1e-9):.2f}x   peak {np.abs(st).max():.3f}  rms {rms_(st):.4f}")

def deliver(st, name, vocals):
    p=f"{name}.wav" if vocals else f"{name}-instrumental.wav"
    write_wav(p, st.T.astype(np.float32))
    print(f"  -> {p}  {st.shape[1]/SR:.1f}s")
    return p

# ================================================================= MIXDOWN CHUNG
def _fit(x,n):
    x=np.asarray(x,dtype=np.float64)
    if len(x)<n: return np.concatenate([x,np.zeros(n-len(x))])
    return x[:n]

def _autobal(V, REST, MAP, n, Tf=None, default_target=2.5):
    Tf=Tf or T
    lb=bp(V,300,4000); rb=bp(REST,300,4000)
    step=max(int(0.05*SR),1)
    idx=np.arange(0,n,step); gc=np.ones(len(idx))
    for row in MAP:
        nm,b0,b1 = row[0],row[1],row[2]
        tgt = row[3] if len(row)>3 else default_target
        s=int(Tf(b0)*SR); e=min(int(Tf(b1)*SR),n)
        if e<=s: continue
        rv=rms_(lb[s:e]); rr=rms_(rb[s:e])
        if rv<2e-5: continue
        cur=20*np.log10(rv/max(rr,1e-12))
        adj=float(np.clip(10**((tgt-cur)/20.0),0.45,3.2))
        gc[(idx>=s)&(idx<e)]=adj
    k=np.hanning(45); k/=k.sum()
    gc=np.convolve(np.pad(gc,22,mode='edge'),k,mode='valid')
    if len(gc)!=len(idx): gc=np.resize(gc,len(idx))
    return np.interp(np.arange(n), idx, gc)

def mixdown(name, vx, stems, drums, bass, MAP, vocals=True,
            wet=0.22, decay=1.6, wide=2.3, drum_gain=0.62, bass_gain=0.88,
            crush_amt=0.22, rms_target=0.185, vox_gain=1.0, boost_inst=1.10,
            duck=0.32, Tf=None, tape=0.0, report_on=True):
    Tf=Tf or T
    n=len(vx)
    D0=_fit(drums,n); D0=D0/(np.abs(D0).max()+1e-9)*0.95
    DR=comp(D0,0.16,3.0,0.004,0.10)*drum_gain
    CRUSH=hp(np.tanh(D0*4.2),175)*crush_amt
    BS=hp(comp(_fit(bass,n),0.10,3.0,0.01,0.12),50)*bass_gain
    if vocals:
        V=voxchain(vx)*vox_gain
        ve=lp(np.abs(V),13); ve/= (np.percentile(ve,99.5)+1e-9)
        duckV=np.clip(1-duck*np.clip(ve,0,1),1-duck-0.06,1.0)
    else:
        V=np.zeros(n); duckV=np.ones(n)
    def carve(x,amt):
        if amt<=0 or not vocals: return x*duckV
        return (x-bp(x,1500,4000)*amt*(1-duckV)/duck)*duckV
    WL=np.zeros(n); WR=np.zeros(n)
    for st_ in stems:
        b_,pan,g_,cv = st_[0],st_[1],st_[2],st_[3]
        haas = st_[4] if len(st_)>4 else 0.0
        x=carve(_fit(b_,n),cv)*g_
        a=(pan+1)*0.25*np.pi
        gl,gr=np.cos(a),np.sin(a)
        if haas:
            d=int(abs(haas)/1000*SR)
            if haas>0: WL+=x*gl; WR+=np.roll(x,d)*gr
            else:      WL+=np.roll(x,d)*gl; WR+=x*gr
        else:
            WL+=x*gl; WR+=x*gr
    if tape>0:
        WL=tapewarp(WL,tape,0.37,3); WR=tapewarp(WR,tape,0.41,9)
    if vocals:
        REST=np.zeros(n)
        for st_ in stems: REST+=_fit(st_[0],n)*st_[2]
        REST=REST+BS+DR+CRUSH
        gv=_autobal(V,REST,MAP,n,Tf)
        V=V*gv
    L,R=reverb(WL,WR,decay,wet)
    L,R=widen(L,R,wide)
    CEN=V+BS+DR+CRUSH
    _side=hp(CEN,1200,2)*0.75
    L=L+CEN+_side; R=R+CEN-_side
    st=master(L,R,vocals,rms_target,1.0 if vocals else boost_inst)
    rail=int((np.abs(st)>0.985).sum())
    print(f"\n[{name}{'' if vocals else ' / instrumental'}]  peak {np.abs(st).max():.3f} rms {rms_(st):.4f} rail {rail}")
    if report_on and vocals:
        REST2=np.zeros(n)
        for st_ in stems: REST2+=_fit(st_[0],n)*st_[2]
        report(st,V,REST2+BS+DR+CRUSH,MAP,Tf)
    return st

def run(name, build, MAP):
    a=sys.argv[1] if len(sys.argv)>1 else 'both'
    if a in ('both','--vocals'):
        deliver(build(True), name, True)
    if a in ('both','--no-vocals'):
        deliver(build(False), name, False)
    print("DONE", name)

# ================================================================= HUMANIZE (dot 2)
_HR=np.random.default_rng(97)
def hseed(n):
    global _HR; _HR=np.random.default_rng(n)
def ht(b,j=0.009,lag=0.005,swing=0.0):
    sw=swing*SPB(b)*0.5 if (int(round(b*2))%2==1) else 0.0
    return T(b)+lag+sw+float(_HR.normal(0,j))
def hg(g,s=0.10): return g*float(max(0.25,1+_HR.normal(0,s)))
def hd(d,s=0.07): return float(max(0.04,d*(1+_HR.normal(0,s))))
def hoff(ms=0.0,sd=6.0): return (ms+float(_HR.normal(0,sd)))/1000.0

def fzbass(b_,t0,m,dur,g=0.24,gl=0,seed=0,bite=1.0):
    L=int(min(dur,2.0)*SR)+int(0.15*SR); t=np.arange(L)/SR
    R=np.random.default_rng(3300+seed+int(m)%97)
    f=hz(m)*(2**(-gl/12*np.exp(-t*22)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.tanh((np.sin(ph)+0.34)*5.2)-np.tanh(0.34*5.2)
    x=x+0.42*np.sin(2*ph)+0.16*np.sin(3*ph)
    x=_lp(x,155,6)
    e=np.minimum(1,t*320)*np.exp(-t*(1.5+1.9/max(dur,0.08)))
    gr=_bp(R.standard_normal(L),650,3800,2)*np.exp(-t*42)*0.62*bite
    put(b_,t0,_fade(np.tanh((x*e+gr*e)*1.35)),g)

def hbone(b_,t0,m,dur,g=0.10,det=0.0,growl=0.55,seed=0):
    L=int(dur*SR)+int(0.16*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1400+seed+int(m))
    f=hz(m)*2**(det/1200)
    vf=1+0.004*np.sin(2*np.pi*5.4*t)*np.minimum(1,t*6)
    ph=2*np.pi*np.cumsum(f*vf)/SR
    x=sum(np.sin(ph*k)/(k**0.92) for k in range(1,22))
    x=np.tanh(x*(1.5+2.6*growl))
    for fc,gg,bw in [(520,1.0,180),(1200,0.75,320),(2100,0.42,420)]:
        x+=_bp(x,fc-bw,fc+bw,2)*gg*0.6
    x=_bp(x,90,5400,2)
    x+=_bp(R.standard_normal(L),420,3200,2)*np.exp(-t/0.013)*0.34
    put(b_,t0,_fade(x*env(L,0.008,0.05,0.52,min(0.10,dur*0.6+0.03))),g)

# ================================================================= NHAC CU MOI - MEW FLavored (Frengers-inspired album)
# Strings ensemble: 3 saw detuned, slow attack, lowpass, vibrato chung
def strings(b_,t0,notes,dur,g=0.07,atk=0.45,seed=0,det=9.0):
    L=int(dur*SR)+int(0.4*SR); t=np.arange(L)/SR
    R=np.random.default_rng(6000+seed)
    out=np.zeros(L)
    for m in notes:
        f=hz(m)
        ph=2*np.pi*np.cumsum(f*(1+0.0018*np.sin(2*np.pi*0.3*t+seed)))/SR
        x=np.zeros(L)
        for d2 in (-det,0,det):
            phd=2*np.pi*np.cumsum(f*(1+d2/1200))/SR
            x+=np.sin(phd)+0.28*np.sin(2*phd)+0.09*np.sin(3*phd)
        x*= (1+0.035*np.sin(2*np.pi*5.1*t+R.uniform(0,6)))
        out+=x/3.0
    out=_lp(out,4800,2)
    e=np.clip(t/atk,0,1)**1.6
    ro=min(int(0.35*SR),L); e[-ro:]*=np.linspace(1,0,ro)**1.4
    put(b_,t0,_fade(out*e),g)

# Glockenspiel: partials 1, 2.76, 5.4, 8.93, decay dai, sang
def glock(b_,t0,m,dur,g=0.09,seed=0):
    L=int(min(dur,3.5)*SR)+int(0.3*SR); t=np.arange(L)/SR
    R=np.random.default_rng(6100+seed+int(m)); f=hz(m)
    rat=[1.0,2.76,5.40,8.93]; tau=[2.2,0.9,0.42,0.22]; amp=[1.0,0.50,0.22,0.10]
    x=np.zeros(L)
    for r,ta,a in zip(rat,tau,amp):
        if f*r>SR/2.2: continue
        x+=a*np.exp(-t/(ta*(1+R.normal(0,0.06))))*np.sin(2*np.pi*f*r*t+R.uniform(0,6.28))
    hit=_bp(R.standard_normal(L),1800,9000,2)*np.exp(-t/0.0018)*0.5
    x=np.tanh((x+hit)*1.15)
    put(b_,t0,_fade(x),g)

# Glassarp: 12-string airy pluck, 2 day capo detune + octave shimmer - Mew intro dyads
def glassarp(b_,t0,m,dur,g=0.10,seed=0,shimmer=0.5):
    L=int(min(dur,4.0)*SR)+int(0.4*SR); t=np.arange(L)/SR
    R=np.random.default_rng(6200+seed+int(m))
    x=ks(m,min(dur,3.4),0.9972,0.78,seed).astype(np.float64)
    y=ks(m+12,min(dur,3.4),0.9965,0.85,seed+5).astype(np.float64)*0.6*shimmer
    n=min(len(x),len(y)); x=x[:n]+np.roll(y[:n],int(R.uniform(0.004,0.014)*SR))
    x=_bp(x,900,9200,2)
    tt=np.arange(len(x))/SR
    x*= (1+0.10*np.sin(2*np.pi*0.8*tt+seed))
    put(b_,t0,_fade(x),g)

# E-bow: guitar sustain khong transient gây, attack cham, hoi chorus - Comforting Sounds outro
def ebow(b_,t0,m,dur,g=0.10,seed=0,atk=0.5):
    L=int(dur*SR)+int(0.3*SR); t=np.arange(L)/SR
    R=np.random.default_rng(6300+seed+int(m))
    f=hz(m)
    drift=1+0.0035*np.sin(2*np.pi*0.23*t+seed)+0.0015*np.sin(2*np.pi*5.9*t)
    ph=2*np.pi*np.cumsum(f*drift)/SR
    x=np.sin(ph)+0.10*np.sin(2*ph)
    x+=_bp(R.standard_normal(L),2200,7800,2)*0.16
    x=_lp(x,6400,2)
    e=np.clip(t/atk,0,1)**1.3
    ro=min(int(0.12*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(np.tanh(x*1.4)*e),g)

# Airlead: lead guitar sạch, chorus nhẹ, Bo Madsen style
def airlead(b_,t0,m,dur,g=0.12,seed=0,bend=0.0):
    x=ks(m,dur,0.9978,0.62,seed).astype(np.float64)
    L=len(x)
    if bend:
        tt=np.arange(L)/SR
        d=(2**((bend*np.minimum(1,tt*7))/12)-1)
        idx=np.clip(np.cumsum(1+d),0,L-1); i0=idx.astype(int); fr=idx-i0
        x=x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr
    x=_bp(x,400,8000,2)
    tt=np.arange(L)/SR
    mod=1+0.012*np.sin(2*np.pi*5.2*tt+seed)
    idx=np.clip(np.cumsum(mod),0,L-1); i0=idx.astype(int); fr=idx-i0
    x=x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr
    put(b_,t0,x*env(L,0.006,0.09,0.85,0.2),g)

# ================================================================= HELPERS CHUNG - dan hop am kieu Bo Madsen (Mew)
def arp8(fn,b_,b0,ch,dur,g,seedbase,dt=0.006):
    seq=[ch[0],ch[2],ch[1],ch[2]]
    for s in range(8):
        fn(b_,ht(b0+s*0.25,j=0.006),seq[s%4],dur,hg(g),seed=seedbase*10+s)
def strum8(fn,b_,b0,ch,dur,g,seedbase,dt=0.006):
    for s in range(8):
        for k,m in enumerate(ch):
            fn(b_,ht(b0+s*0.25,j=0.005)+k*dt,m,dur,hg(g/len(ch)),seed=seedbase*10+s+k)
def chchord(fn,b_,t0,ch,dur,g,seedbase=0,dt=0.006):
    for k,m in enumerate(ch):
        fn(b_,ht(t0,j=0.005)+k*dt,m,dur,hg(g/len(ch)),seed=seedbase*10+k)
def chord0(fn,b_,t0,ch,dur,g,dt=0.006,**kw):
    # cho organ/mellotron/strings (khong nhan seed, nhan notes list)
    for k,m in enumerate(ch):
        fn(b_,ht(t0,j=0.005)+k*dt,m,dur,hg(g/len(ch)),**kw)
def vline(b_,b0,cells,g=0.12,style='falsetto',breath=0.3,seedbase=0,oct8=0.0):
    return line(b_,b0,cells,g=g,style=style,breath=breath,seedbase=seedbase,oct8=oct8)
def stchord(b_,t0,ch,dur,g,atk=0.5,seed=0):
    strings(b_,ht(t0,j=0.005),ch,dur,g,atk=atk,seed=seed)
def arpchord(fn,b_,t0,ch,dur,g,seedbase,dt=0.006):
    # arpeggio 8ths: root-5th-3rd-5th (ben doi dien voi chord)
    seq=[ch[0],ch[2],ch[1],ch[2]]
    for s in range(8):
        fn(b_,ht(t0+s*0.25,j=0.006),seq[s%4],dur,hg(g),seed=seedbase*10+s)
# ============================================================ BAI 2: FROM THE BEDROOM WINDOW
# Model: Mew - "156" (Frengers 2003) - E major, 130 BPM
#   vong C#m-A-E-B (vi-IV-I-V) - bat dau bang vi nen "home" bi tri hoan
#   bass 8ths octave-jump (C#2-C#3, A2-A3, E2-E3, B2-B3) - do tu stem that
#   verse: giong thap, drums offbeat pulse; chorus: backbeat, kick 8ths drive
BAR=4.0
NAME="02-from-the-bedroom-window"
SECS=[('IN',4),('V1',8),('V2',8),('CH',8),('IN2',4),('V3',8),('CH2',8),('BR',8),('CH3',8),('OUT',40)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(130,130,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('C#3'),nn('E4'),nn('G#4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('B2'),nn('D#4'),nn('F#4')]]
def vch(i): return VCH[i%4]
def broot(i): return VCH[i%4][0]

def bass8(b,b0,root,g=0.26):
    for s in range(8):  # 8ths octave-jump nhu 156
        m=root+(12 if s%2==0 else 0)
        bassn(bs,T(b0+s*0.25),m,SPB(b)*0.85,hg(g))

K=Kit(seed=1212); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.72
def villa(b,lvl=0.8,arc=1.0,mode='drive'):
    a=arc
    if mode=='drive':   # verse: hat 8ths + kick offbeat, snare ghost
        for s in range(16):
            P.H(b+s*0.25,s,0.72*lvl if s%2==1 else 0.5*lvl,o=0.0,art='tip',arc=a)
        P.K(b+0.5,2,0.8*lvl,a); P.K(b+2.5,10,0.8*lvl,a); P.K(b+3.0,12,0.5*lvl,a)
        P.S(b+1,4,0.5*lvl,'ghost',a); P.S(b+3,12,0.6*lvl,'ghost',a)
    else:               # chorus: kick 8ths song song bass, backbeat that
        for s in range(16):
            P.H(b+s*0.25,s,0.75*lvl if s%4==0 else 0.5*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
            if s%2==0: P.K(b+s*0.25,s,0.75*lvl,a)
        P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+2.5,10,0.28*lvl,'ghost',a)
        P.RD(b,0,0.45*lvl,bell=True,arc=a)
        if int(b*130/60)%4==3:
            P.TM(b+2.75,11,0.65*lvl,130); P.TM(b+3.25,13,0.75*lvl,104); P.TM(b+3.75,15,0.85*lvl,86)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: bass 8ths C#m + jangle + giong vang ----
for i in range(4):
    b=bar_at('IN',i)
    bass8(b,b,vch(i)[0],0.16)
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.055),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.055),i+50)
    villa(b,hg(0.35),arc=0.6,mode='drive')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.085),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.085),i+50)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.035),atk=0.8,seed=i+20)
    villa(b,hg(0.45),arc=0.8,mode='drive')
    if i%4==0:
        line(vx,b,[(0,.75,'C#4','a','f'),(.75,.5,'B3','o',''),(1.25,1.0,'A3','a',''),(2.5,.75,'B3','e',''),(3.25,.75,'C#4','a','')],
             g=0.145,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.09),i+50)
    glassarp(st,T(b+0.5),vch(i)[2]+12,SPB(b)*1.4,hg(0.05),seed=i)
    glock(st,T(b+1),vch(i)[2]+12,SPB(b)*1.2,hg(0.05),seed=i+3)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.04),atk=0.7,seed=i+40)
    villa(b,hg(0.5),arc=0.85,mode='drive')
    line(vx,b,[(0,.5,'C#4','o',''),(.5,.75,'E4','a','n'),(1.25,.5,'B3','e',''),(2.0,.75,'A3','a',''),(2.75,1.25,'C#4','i','')],
         g=0.15,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH: kick 8ths ----
for i in range(8):
    b=bar_at('CH',i)
    bass8(b,b,vch(i)[0],0.3)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.10),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.10),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'B4','i',''),(2.5,1.5,'A4','a','')],
             g=0.13,style='falsetto',breath=0.32,seedbase=200+i)
# ---- IN2 ----
for i in range(4):
    b=bar_at('IN2',i)
    bass8(b,b,vch(i)[0],0.12)
    glassarp(gtR,T(b+1),vch(i)[2]+12,SPB(b)*1.5,hg(0.04),seed=i)
    villa(b,hg(0.3),arc=0.5,mode='drive')
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.09),i+50)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.042),atk=0.6,seed=i+80)
    villa(b,hg(0.52),arc=0.88,mode='drive')
    line(vx,b,[(0,.5,'C#4','a',''),(.5,.75,'E4','e',''),(1.25,.5,'G#4','o',''),(2.0,.75,'B3','a',''),(2.75,1.25,'C#4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i)
    bass8(b,b,vch(i)[0],0.32)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.11),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.11),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    villa(b,hg(0.82),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'B4','a',''),(2.5,1.5,'A4','a','')],
         g=0.135,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: A-E-F#m-D (di len) ----
BRC=[[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('F#2'),nn('A3'),nn('C#4')],[nn('D3'),nn('F#4'),nn('A4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    bass8(b,b,c[0],0.26)
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.6,hg(0.045))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.6,hg(0.045))
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    villa(b,hg(0.7),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'A4','o',''),(1.0,1.0,'B4','a',''),(2.0,2.0,'C#5','e','v')],
             g=0.125,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i)
    bass8(b,b,vch(i)[0],0.34)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.12),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.12),i+50)
    strings(st,T(b),vch(i)+[x+12 for x in vch(i)[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    glock(st,T(b+2),vch(i)[2]+12,SPB(b)*1.2,hg(0.055),seed=i+7)
    villa(b,hg(0.9),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'C#5','i',''),(2.5,1.5,'B4','a','')],
         g=0.14,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: false-stop 2 bar dau roi build to fade ----
for i in range(40):
    b=bar_at('OUT',i)
    f=0.45+0.018*i if i<28 else 0.95
    if i<2: f=0.30
    bass8(b,b,vch(i)[0],0.24*f)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.10*f),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.10*f),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.05*f),atk=0.4,seed=i+160)
    villa(b,hg(0.85*f),arc=0.7+0.3*min(f,1.0),mode='chorus')
    if i%4==0 and i>=2:
        line(vx,b,[(0,.5,'A4','a','f'),(.5,.5,'A4','a',''),(1.0,.5,'G#4','o',''),(1.5,.5,'F#4','e',''),(2.0,.5,'A4','a',''),(2.5,1.5,'G#4','o','')],
             g=0.12,style='falsetto',breath=0.3,seedbase=700+i//4)
    if i%8==7:
        P.fill(b+3.0,1.0,'snare',0.7)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
