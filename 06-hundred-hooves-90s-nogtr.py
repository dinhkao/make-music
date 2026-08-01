"""06-hundred-hooves-90s-nogtr - mot file duy nhat, chi can numpy + scipy.
   python3 06-hundred-hooves-90s-nogtr.py             -> ca hai ban wav (co giong + instrumental)
   python3 06-hundred-hooves-90s-nogtr.py --vocals    -> chi ban co giong
   python3 06-hundred-hooves-90s-nogtr.py --no-vocals -> chi ban instrumental
"""
# ================================================================= ENGINE (inlined)
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
    y[-fo:]*=np.linspace(1,0,fo)          # loi #14: fade cuoi, khong click
    ri=min(int(0.0008*SR),L); y[:ri]*=np.linspace(0,1,ri)
    _KS[key]=y.astype(np.float32)
    return _KS[key]
def jangle(b_, t0, m, dur, g=0.10, seed=0):
    x=ks(m,dur,0.9962,0.72,seed).astype(np.float64)
    bq,aq=sg.butter(2,[220/(SR/2),6200/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x,g)
def crunch(b_, t0, m, dur, g=0.09, drive=6.0, seed=0):
    x=ks(m,dur,0.9950,0.55,seed).astype(np.float64)
    x=np.tanh(x*drive)
    bq,aq=sg.butter(2,[300/(SR/2),3800/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
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
    bq,aq=sg.butter(2,[380/(SR/2),4200/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
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
    bq,aq=sg.butter(2,760/(SR/2),'low'); x=sg.lfilter(bq,aq,x)
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
        elif kind=='trib':                       # 3 tren luoi 4, kieu math-rock
            n=max(int(beats*3),1)
            for i in range(n):
                p=beat_start+i*(beats/n)
                if i%3==0: self.K(p,int(i*16/max(n,1))%16,0.9*intensity)
                else: self.TM(p,int(i*16/max(n,1))%16,0.6*intensity,tune=[150,120,96][i%3])
        if next_crash_beat is not None:
            self.CR(next_crash_beat,0,0.85*intensity)
            self.K(next_crash_beat,0,1.0*intensity)
def delay(x,ms):
    d=int(ms/1000*SR); return np.concatenate([np.zeros(d),x])[:len(x)]
def mix_kit(bus, room_amount=0.22, oh_amount=0.85, lofi=0.0, lpf=9000):
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
    dry = kick_m*1.0 + snare_m*0.95 + hat_m*0.55 + tom_m*0.8 + CY*0.5 + PC*0.85
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
configure()

# ================================================================= NHAC CU MO RONG (bang mau Geese)
def _fade(x, ms_in=1.0, ms_out=12.0):
    a=min(int(ms_in/1000*SR),len(x)); b=min(int(ms_out/1000*SR),len(x))
    if a>1: x[:a]*=np.linspace(0,1,a)
    if b>1: x[-b:]*=np.linspace(1,0,b)
    return x
# --- dan day keo (viola / violin drone kieu Venus in Furs) ---
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
# --- dan piano tack / upright (day co dinh ghim) ---
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
# --- clavinet (funk, ngan, sac) ---
def clav(b_,t0,m,dur,g=0.10,seed=0):
    x=ks(m,min(dur,0.9),0.9905,0.85,seed).astype(np.float64)
    x=np.tanh(x*3.4)
    x=_bp(x,420,5200,2)
    L=len(x); t=np.arange(L)/SR
    x*=np.exp(-t*(3.2+2.4/max(dur,0.08)))
    put(b_,t0,_fade(x),g)
# --- guitar slide / bottleneck ---
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
# --- marimba / vibes go ---
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
# --- mellotron / sao bang tu (wow-flutter) ---
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
    else:  # strings
        x=sg.lfilter([1],[1,-0.2],np.sign(np.sin(ph))*0.3+np.sin(ph)*0.7)
        x=_lp(x,3800,2)
    hiss=R.standard_normal(L)*0.012
    x=_lp(x,6800,2)+hiss
    e=np.minimum(1,t*14)
    ro=min(int(0.10*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(x*e),g)
# --- guitar nylon (fingerpick) ---
def nylon(b_,t0,m,dur,g=0.11,seed=0):
    x=ks(m,min(dur,2.6),0.9938,0.30,seed).astype(np.float64)
    x=_bp(x,150,3200,2)
    put(b_,t0,_fade(x),g)
# --- guitar 12 day chimey ---
def chime12(b_,t0,m,dur,g=0.09,seed=0):
    x=ks(m,min(dur,3.0),0.9970,0.80,seed).astype(np.float64)
    y=ks(m+12,min(dur,3.0),0.9964,0.86,seed+3).astype(np.float64)*0.55
    n=min(len(x),len(y)); x=x[:n]+np.roll(y[:n],int(0.006*SR))
    x=_bp(x,300,9000,2)
    put(b_,t0,_fade(x),g)
# --- bass fuzz ---
def fuzzbass(b_,t0,m,dur,g=0.20,gl=0,seed=0):
    L=int(min(dur,2.0)*SR)+int(0.15*SR); t=np.arange(L)/SR
    f=hz(m)*(2**(-gl/12*np.exp(-t*22)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sign(np.sin(ph))*0.6+np.sin(ph)*0.9+np.sin(ph*2)*0.25
    x=np.tanh(x*7.0)
    x=_bp(x,55,2600,2)
    x*=np.minimum(1,t*300)*np.exp(-t*1.1)
    put(b_,t0,_fade(x),g)
# --- bass sub thuan ---
def subbass(b_,t0,m,dur,g=0.26,gl=0):
    L=int(min(dur,3.0)*SR)+int(0.12*SR); t=np.arange(L)/SR
    f=hz(m)*(2**(-gl/12*np.exp(-t*20)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)+0.12*np.sin(ph*2)
    x*=np.minimum(1,t*160)*np.exp(-t*0.9)
    put(b_,t0,_fade(x,2.0,25.0),g)
# --- bass flatwound ngon tay (ban le, co tieng day) ---
def fingerbass(b_,t0,m,dur,g=0.28,gl=0,dead=False,seed=0):
    L=int(min(dur,1.6)*SR)+int(0.16*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1300+seed+int(m))
    f=hz(m)*(2**(-gl/12*np.exp(-t*24)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=sum(np.sin(ph*k+R.uniform(0,6))/(k**1.45) for k in range(1,9))
    x+=_bp(R.standard_normal(L),700,3000,2)*np.exp(-t/0.004)*0.5   # tieng ngon tay
    x=_lp(x,900 if not dead else 380,2)
    x*=np.minimum(1,t*420)*np.exp(-t*(2.4 if not dead else 12.0))
    put(b_,t0,_fade(np.tanh(x*1.3)),g)
# --- ken trombone (dam, co growl) ---
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
# --- organ gospel qua Leslie ---
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
# --- dan cua / theremin (drone lo lung) ---
def saw_drone(b_,t0,m,dur,g=0.06,det=0.0,seed=0):
    L=int(dur*SR); t=np.arange(L)/SR
    R=np.random.default_rng(1500+seed)
    f=hz(m)*2**(det/1200)*(1+0.0016*np.sin(2*np.pi*0.19*t+R.uniform(0,6)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)+0.10*np.sin(ph*3)+0.04*np.sin(ph*5)
    x*= (1+0.10*np.sin(2*np.pi*5.9*t))
    e=np.minimum(1,t*3.0); ro=min(int(0.5*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(b_,t0,_fade(x*e),g)
# --- bang tu chay nguoc (khong phai riser: mot lop tinh) ---
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
        if cname in ('b','d','g'):   # co tieng thanh quan
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
    else:  # liq
        ph=2*np.pi*f0*t
        x=sum(np.sin(ph*k)/(k**1.25) for k in range(1,14))
        x=_bp(x,max(lo-220,60),lo+420,2)*2.4
        x*=np.minimum(1,t/0.008)*amp
        x+=_bp(R.standard_normal(L),600,2800,2)*0.05
    return x*g, cd
def say(b_, t0, m, dur, vow='a', cons='', g=0.16, style='croon', breath=0.24,
        seed=0, det=0.0, drift=0.0):
    """Mot am tiet: phu am dan vao + nguyen am co cao do.
       style: croon | deadpan | shout | whisper | falsetto"""
    f0=hz(m)*2**(det/1200)
    vib  ={'croon':5.2,'deadpan':4.4,'shout':6.1,'whisper':4.0,'falsetto':5.8}[style]
    vibd ={'croon':0.0055,'deadpan':0.0015,'shout':0.009,'whisper':0.002,'falsetto':0.011}[style]
    br   =breath*{'croon':1.0,'deadpan':1.25,'shout':0.8,'whisper':3.2,'falsetto':1.4}[style]
    L=int(max(dur,0.06)*SR)+int(0.20*SR)
    t=np.arange(L)/SR
    # phu am
    cx,cd=_consonant(cons,f0,1.0,seed)
    # nguyen am
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
    # bao hinh: tan cong nhanh (co phu am -> nhu noi), buong nhanh
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
    """cells = [(phach, dodai_phach, 'C4', nguyen_am, phu_am)]  hoac 4 phan tu."""
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
    """Nhieu nguoi cung hat mot cau - dung cho chorus."""
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
    V=V+bp(V,1900,4300)*1.15+hp(V,7200)*0.55
    V=hp(V,300); V=np.tanh(V*1.1)*2.9
    return V

def master(L,R,vocals=True,rms_target=0.175,boost=1.0):
    st=np.stack([L,R])*boost
    r=rms_(st)
    if r>1e-9: st=st*(rms_target/r)          # gain staging THEO RMS truoc tanh (loi #13)
    st=np.tanh(st*0.95); st=hp(st,26)
    st/= (np.abs(st).max()+1e-9); st*=0.94
    f=int(0.02*SR); st[:,:f]*=np.linspace(0,1,f)
    fo=int(2.2*SR); st[:,-fo:]*=np.linspace(1,0,fo)**0.8
    return st

def widen(L,R,amt=1.6,fc=240):
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
            wet=0.22, decay=1.6, wide=1.5, drum_gain=0.72, bass_gain=0.85,
            crush_amt=0.22, rms_target=0.175, vox_gain=1.0, boost_inst=1.10,
            duck=0.32, Tf=None, tape=0.0, report_on=True):
    """stems = [(buffer, pan(-1..1), gain, carve_amt, haas_ms), ...]"""
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
    L=L+CEN; R=R+CEN
    st=master(L,R,vocals,rms_target,1.0 if vocals else boost_inst)
    rail=int((np.abs(st)>0.985).sum())
    print(f"\n[{name}{'' if vocals else ' / instrumental'}]  peak {np.abs(st).max():.3f} rms {rms_(st):.4f} rail {rail}")
    if report_on and vocals:
        REST2=np.zeros(n)
        for st_ in stems: REST2+=_fit(st_[0],n)*st_[2]
        report(st,V,REST2+BS+DR+CRUSH,MAP,Tf)
    return st

def run(name, build, MAP):
    """build(vocals) -> st ; CLI: mac dinh render ca hai ban."""
    a=sys.argv[1] if len(sys.argv)>1 else 'both'
    if a in ('both','--vocals'):
        deliver(build(True), name, True)
    if a in ('both','--no-vocals'):
        deliver(build(False), name, False)
    print("DONE", name)


# ================================================================= XUAT STEM
def stemdown(name, vx, stems, drums, bass, MAP, stem_names=None,
             kitbus=None, kitmix=None, outdir="stems",
             wet=0.22, decay=1.6, wide=1.5, drum_gain=0.72, bass_gain=0.85,
             crush_amt=0.22, rms_target=0.175, vox_gain=1.0, duck=0.32,
             Tf=None, tape=0.0):
    """Moi nguon mot file stereo. Cong tat ca lai = ban master (bo qua tanh bao hoa).
       kitbus = Performer.bus  -> tach rieng kick/snare/hat/tom/cym/perc."""
    Tf=Tf or T; n=len(vx)
    os.makedirs(outdir,exist_ok=True)
    kitmix=kitmix or {}
    D0=_fit(drums,n); dn=0.95/(np.abs(D0).max()+1e-9); D0=D0*dn
    gdr=comp_gain(D0,0.16,3.0,0.004,0.10)
    DR=D0*gdr*drum_gain
    CRUSH=hp(np.tanh(D0*4.2),175)*crush_amt
    B0=_fit(bass,n); BS=hp(B0*comp_gain(B0,0.10,3.0,0.01,0.12),50)*bass_gain
    V=voxchain(vx)*vox_gain
    ve=lp(np.abs(V),13); ve/=(np.percentile(ve,99.5)+1e-9)
    duckV=np.clip(1-duck*np.clip(ve,0,1),1-duck-0.06,1.0)
    def carve(x,amt):
        if amt<=0: return x*duckV
        return (x-bp(x,1500,4000)*amt*(1-duckV)/duck)*duckV
    REST=np.zeros(n)
    for st_ in stems: REST+=_fit(st_[0],n)*st_[2]
    V=V*_autobal(V,REST+BS+DR+CRUSH,MAP,n,Tf)
    def widepair(x,pan,haas):
        a=(pan+1)*0.25*np.pi; gl,gr=np.cos(a),np.sin(a)
        if haas:
            d=int(abs(haas)/1000*SR)
            if haas>0: L,R=x*gl,np.roll(x,d)*gr
            else:      L,R=np.roll(x,d)*gl,x*gr
        else: L,R=x*gl,x*gr
        if tape>0: L=tapewarp(L,tape,0.37,3); R=tapewarp(R,tape,0.41,9)
        L,R=reverb(L,R,decay,wet)
        return widen(L,R,wide)
    out=[]
    for i,st_ in enumerate(stems):
        b_,pan,g_,cv = st_[0],st_[1],st_[2],st_[3]
        haas = st_[4] if len(st_)>4 else 0.0
        nm = stem_names[i] if stem_names else "STEM%02d"%i
        if nm is None: continue
        L,R=widepair(carve(_fit(b_,n),cv)*g_,pan,haas)
        out.append((nm,L.astype(np.float32),R.astype(np.float32)))
    for nm,x in [("VOCALS",V),("BASS",BS)]:
        out.append((nm,x.astype(np.float32),x.astype(np.float32)))
    if kitbus is not None:
        for nm,key in [("KICK","kick"),("SNARE","snare"),("HATS","hat"),
                       ("TOMS","tom"),("CYMBALS","cym"),("PERC","perc")]:
            solo={k2:(kitbus[k2] if k2==key else np.zeros(len(kitbus[k2]))) for k2 in kitbus}
            d=_fit(mix_kit(solo,**kitmix),n)*dn*gdr*drum_gain
            out.append((nm,d.astype(np.float32),d.astype(np.float32)))
        out.append(("DRUM-CRUSH",CRUSH.astype(np.float32),CRUSH.astype(np.float32)))
    else:
        out.append(("DRUMS",DR.astype(np.float32),DR.astype(np.float32)))
        out.append(("DRUM-CRUSH",CRUSH.astype(np.float32),CRUSH.astype(np.float32)))
    sL=np.zeros(n); sR=np.zeros(n)
    for _,L,R in out: sL+=L; sR+=R
    st=np.stack([sL,sR]); k=rms_target/max(rms_(st),1e-12)
    probe=hp(np.tanh(st*k*0.95),26)
    K_=k*(0.94/(np.abs(probe).max()+1e-9))
    fi=int(0.02*SR); fo=int(2.2*SR)
    win=np.ones(n); win[:fi]=np.linspace(0,1,fi); win[-fo:]=np.linspace(1,0,fo)**0.8
    pk=max(float(np.abs(np.stack([L,R]).astype(np.float64)*K_).max()) for _,L,R in out)
    pk=max(pk,float(np.abs(np.stack([sL,sR])*K_).max()))
    hr=min(1.0,0.89/max(pk,1e-9))
    print(f"\n  He so du dau chung: x{hr:.4f}  ({20*np.log10(hr):+.2f} dB)")
    print("  STEM                 peak    rms")
    for i,(nm,L,R) in enumerate(out):
        a=np.stack([L.astype(np.float64),R.astype(np.float64)])*K_*hr*win
        p=f"{outdir}/{name}-{i+1:02d}-{nm}.wav"
        write_wav24(p,a.T)
        print(f"  {nm:18s} {np.abs(a).max():6.3f} {rms_(a):7.4f}   {p}")
    a=np.stack([sL,sR])*K_*hr*win
    write_wav24(f"{outdir}/{name}-00-TONG-KIEM-TRA.wav",a.T)
    print(f"  {'(tong kiem tra)':18s} {np.abs(a).max():6.3f} {rms_(a):7.4f}")
    print(f"  -> {len(out)} stem (24-bit) trong {outdir}/ ; keo master len {-20*np.log10(hr):+.2f} dB de ve muc ban mix")

# ================================================================= BAI 06 (BAN 1'30 - KHONG GUITAR)
# HUNDRED HOOVES  -  funk hanh quan, mot not bass duy nhat
# KHONG GUITAR, KHONG CLAVINET, KHONG MARIMBA, KHONG ORGAN.
# Chi con NAM thu: trong - fuzz bass - trombone - kim loai - giong. Kèn ganh cau hook.
# Y tuong mot cau: mot not bass duy nhat trong 90 giay, va bo trong doi cach danh
# sau lan - moi lan mot buoc, khong lan nao quay lai - cho toi khi no thanh double-time.
NAME="06-hundred-hooves-90s-nogtr"
BAR=4.0
SECS=[('INTRO',8),('A1',6),('A2',8),('A3',6),('STOP',3),
      ('A4',6),('A5',8),('A6',8),('TAG',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(152,153,END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,"bars",int(END/BAR),"->",round(TOTAL,1),"s")

bhk=buf(); brs=buf(); mtl=buf(); vx=buf(); bs=buf(); fx=buf()

CH={'Em9':['E2','G3','B3','D4','F#4'],
    'Cmaj7':['C3','E3','G3','B3'],
    'D69':['D3','F#3','A3','B3','E4']}
def C_(k): return [nn(x) for x in CH[k]]
def top(k,lo):
    ns=[m for m in C_(k) if m>=nn(lo)]
    return ns if ns else [m+12 for m in C_(k)[1:]]
LOOP8=['Em9']*6+['Cmaj7','D69']
def kof(i): return LOOP8[i%8]


# --------- FUZZ BASS KHONG SINH BAC 3 ---------
# Loi cu: tanh(square) -> hai am le 1,3,5,7,9 = E,B,G#,D,F# -> chinh la mot hop am E7
#         (hai am 5 = G# manh hon ca hai am 4 = E). Bai o E dorian nen no doi nhau.
# Cach chua: than bass cat o 155 Hz (chi con E1,E2,B2,E3 - khong co bac 3),
#            do "ran" lay tu NHIEU loc dai (khong co cao do) chu khong tu hai am cao.
def fzbass(b_,t0,m,dur,g=0.24,gl=0,seed=0,bite=1.0):
    L=int(min(dur,2.0)*SR)+int(0.15*SR); t=np.arange(L)/SR
    R=np.random.default_rng(3300+seed+int(m)%97)
    f=hz(m)*(2**(-gl/12*np.exp(-t*22)))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.tanh((np.sin(ph)+0.34)*5.2)-np.tanh(0.34*5.2)      # meo khong doi xung
    x=x+0.42*np.sin(2*ph)+0.16*np.sin(3*ph)
    x=_lp(x,155,6)                                          # cat tu hai am 4 tro len
    e=np.minimum(1,t*320)*np.exp(-t*(1.5+1.9/max(dur,0.08)))
    gr=_bp(R.standard_normal(L),650,3800,2)*np.exp(-t*42)*0.62*bite
    put(b_,t0,_fade(np.tanh((x*e+gr*e)*1.35)),g)

# --------- BASS: mot not E, khong nghi ---------
def bass_bar(b0,g=0.25,octjump=False,k='Em9',dens=16):
    r=nn('E1')
    for s in range(0,16,16//dens):
        p=s*0.25; iv=0
        if octjump and s in (6,7,14,15): iv=12
        if k=='Cmaj7' and s>=8: iv+=-4
        if k=='D69'   and s>=8: iv+=-2
        fzbass(bs,T(b0+p),r+iv,SPB(b0)*0.22,g*(1.0 if s%4==0 else (0.62 if s%2==0 else 0.48)),seed=s)
    subbass(bs,T(b0),r-12,SPB(b0)*3.7,g*0.5)

# --------- TROMBONE STACCATO (tan cong 8ms - de thoi duoc not ngan) ---------
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
    x+=_bp(R.standard_normal(L),420,3200,2)*np.exp(-t/0.013)*0.34      # tieng luoi + hoi
    put(b_,t0,_fade(x*env(L,0.008,0.05,0.52,min(0.10,dur*0.6+0.03))),g)

# --------- KEN GANH CAU HOOK (thay guitar) ---------
# hook = goi 3 lan: (B B A) (B B G) (E5 D5 B) roi doi (A)
HOOKR=[(0.0,7,1.00),(0.25,7,0.70),(0.5,5,0.95),
       (1.0,7,1.00),(1.25,7,0.70),(1.5,3,0.95),
       (2.0,12,1.05),(2.25,10,0.75),(2.5,7,0.95),
       (3.0,5,1.00),(3.5,3,0.60)]
def hook_bone(b0,g=0.105,seed=0,oct_=0,dbl8=False,growl=0.6):
    r=nn('E3')
    for off,iv,acc in HOOKR:
        hbone(bhk,T(b0+off),r+iv+oct_,SPB(b0)*0.21,g*acc,det=-6,growl=growl,seed=(seed+int(off*4))%6)
        if dbl8:
            hbone(bhk,T(b0+off)+0.008,r+iv+oct_+12,SPB(b0)*0.19,g*acc*0.60,
                  det=+7,growl=growl*0.8,seed=(seed+int(off*4)+3)%6)

# --------- KEN NEN (thay guitar gat): goc + quang 5, o phach le ---------
def bone_chug(b0,k,g=0.075,seed=0):
    r=min(C_(k))
    for off,acc in [(0.75,1.0),(1.25,0.62),(2.5,0.95),(3.25,0.68)]:
        for j,m in enumerate([r,r+7]):
            hbone(brs,T(b0+off)+j*0.007,m,SPB(b0)*0.24,g*acc,det=-10+18*j,
                  growl=0.85,seed=(seed+j)%6)

# --------- KEN DAM (dong thanh goc + quang 8) ---------
def brass_bar(b0,k,g=0.090,hi=False):
    r=min(C_(k))+12
    ns=[r,r+12] if not hi else [r+12,r+24]
    for off,d,acc in [(0.0,0.45,1.0),(1.75,0.35,0.75),(2.5,0.55,0.95)]:
        for j,m in enumerate(ns):
            bone(brs,T(b0+off)+j*0.010,m,SPB(b0)*d,g*acc,det=-8+16*j,growl=0.7,seed=j)

# ================= TRONG =================
K=Kit(seed=606); P=Performer(K,T,SPB,TOTAL,seed=113,style='indie')

# --------- LOP KIM LOAI + CHUONG AGOGO ---------
_METAL={}
def _metalbed(v=0):
    if v not in _METAL:
        _METAL[v]=K._cym(int(3.2*SR),320,620,13500,0.30,2.8,seed=7700+v*29,migrate=0.38)
    return _METAL[v]
def metalair(b0,dur,g=0.045,seed=0,bright=1.0,rate=0.70):
    x=_metalbed(seed%4)
    L=min(int(dur*SR),len(x)); x=x[:L].copy(); t=np.arange(L)/SR
    lfo=1+0.60*np.sin(2*np.pi*rate*t+seed)+0.32*np.sin(2*np.pi*rate*2.7*t+seed*0.4)
    x=x*np.clip(lfo,0.0,None)
    x=_bp(x,620*bright,13000,2)
    e=np.minimum(1,t*3.2); ro=min(int(0.30*SR),L); e[-ro:]*=np.linspace(1,0,ro)
    put(mtl,T(b0),_fade(x*e),g)
def agogo(vel=1.0,f=560.0,seed=0):
    L=int(0.30*SR); t=np.arange(L)/SR
    R=np.random.default_rng(6100+seed)
    x=np.sign(np.sin(2*np.pi*f*t))*0.62+np.sign(np.sin(2*np.pi*f*1.4986*t))*0.38
    x=_bp(x,f*0.85,min(f*8,15000),2)*np.exp(-t/0.052)
    x+=_bp(R.standard_normal(L),2200,8000,2)*np.exp(-t/0.0035)*0.55
    return _ramp(np.tanh(x*1.4)*vel*0.55)
def AG(beat,pos16,v=1.0,f=560.0,arc=1.0,seed=0):
    P._add('perc',P._t(beat,'perc',pos16),agogo(P._v(v,pos16,arc=arc),f,seed))

# --------- SAU CACH DANH, MOI CACH THEM MOT BUOC ---------
def kit1(b0,lvl,arc):                       # A1: don gian nhat - 4 kick, backbeat, hat 8
    for q in range(4): P.K(b0+q,q*4,(1.05 if q%2==0 else 0.85)*lvl,arc,tune=49)
    P.S(b0+1,4,1.0*lvl,'center',arc); P.S(b0+3,12,1.0*lvl,'center',arc)
    for s in range(8): P.H(b0+s*0.5,s*2,(0.74 if s%2==0 else 0.42)*lvl,o=0.0,
                           art='edge' if s%2==0 else 'tip',arc=arc)
def kit2(b0,lvl,arc):                       # A2: hat len 16, them ghost, lac tay

    for q in range(4): P.K(b0+q,q*4,(1.05 if q%2==0 else 0.85)*lvl,arc,tune=49)
    P.S(b0+1,4,1.0*lvl,'center',arc); P.S(b0+3,12,1.0*lvl,'center',arc)
    for gp in (1.75,3.5): P.S(b0+gp,int(gp*4)%16,0.42*lvl,'ghost',arc)
    for s in range(16): P.H(b0+s*0.25,s,(0.78 if s%4==0 else 0.42)*lvl,o=0.0,
                            art='edge' if s%4==0 else 'tip',arc=arc)
    for s in range(16): P.SH(b0+s*0.25,s,(0.34 if s%4==0 else 0.18)*lvl,arc)
def kit3(b0,lvl,arc,i=0):                   # A3: kick doi, ghost day, conga, hat mo cuoi o
    for q in range(4): P.K(b0+q,q*4,(1.05 if q%2==0 else 0.85)*lvl,arc,tune=49)
    for p in (0.75,2.75): P.K(b0+p,int(p*4)%16,0.62*lvl,arc,tune=49)
    P.S(b0+1,4,1.0*lvl,'center',arc); P.S(b0+3,12,1.0*lvl,'center',arc)
    for gp in (1.75,2.25,3.5,3.75): P.S(b0+gp,int(gp*4)%16,0.44*lvl,'ghost',arc)
    for s in range(16):
        op=(s==15)
        P.H(b0+s*0.25,s,(0.80 if s%4==0 else 0.44)*lvl,o=0.5 if op else 0.0,
            art='edge' if s%4==0 else 'tip',arc=arc,choke_beat=(b0+4.0) if op else None)
    for s in range(16): P.SH(b0+s*0.25,s,(0.36 if s%4==0 else 0.19)*lvl,arc)
    for p,tu,ar in [(0.25,235,'open'),(1.5,235,'open'),(2.75,175,'slap')]:
        P.CG(b0+p,int(p*4)%16,0.52*lvl,tune=tu,art=ar,arc=arc)
    P.CL(b0+1+0.005,4,0.80*lvl,arc); P.CL(b0+3+0.005,12,0.84*lvl,arc)
    if i%2==1:
        for p in (0.5,2.0): P.TM(b0+p,int(p*4)%16,0.58*lvl,tune=112 if p<1 else 92,arc=arc)
def kit4(b0,lvl,arc,i=0):                   # A4: them chuong agogo + ride xen ke + tom nhieu hon
    kit3(b0,lvl,arc,i)
    for p,f in [(0.0,830),(0.75,554),(1.5,830),(2.25,554),(2.75,830),(3.5,554)]:
        AG(b0+p,int(p*4)%16,(0.88 if f>700 else 0.64)*lvl,f,arc,seed=int(p*4))
    if i%2==0:
        for s in range(8): P.RD(b0+s*0.5,s*2,0.34*lvl,bell=(s==0),arc=arc)
    else:
        for p in (0.5,2.0,3.25): P.TM(b0+p,int(p*4)%16,0.60*lvl,
                                      tune=[112,92,76][int(p)%3],arc=arc)
def kit5(b0,lvl,arc,i=0):                   # A5: kick lech them, cuon 32 cuoi o, tambourine 16
    kit4(b0,lvl,arc,i)
    P.K(b0+1.5,6,0.60*lvl,arc,tune=49); P.K(b0+3.25,13,0.55*lvl,arc,tune=49)
    for s in range(16): P.TB(b0+s*0.25,s,(0.44 if s%4==0 else 0.22)*lvl,arc)
    if i%2==1:
        for j in range(8):
            P.S(b0+3.0+j*0.125,int((3.0+j*0.125)*4)%16,(0.34+0.06*j)*lvl,
                art='ghost' if j<5 else 'center',arc=arc)
def kit6(b0,lvl,arc,i=0):                   # A6: DOUBLE-TIME - kick not 8, snare cuon lien tuc, hat 32
    for s in range(8): P.K(b0+s*0.5,s*2,(1.10 if s%2==0 else 0.72)*lvl,arc,tune=49)
    P.S(b0+1,4,1.10*lvl,'center',arc); P.S(b0+3,12,1.10*lvl,'center',arc)
    for s in range(8):
        p=s*0.5
        if abs(p-1)<1e-6 or abs(p-3)<1e-6: continue
        P.S(b0+p,int(p*4)%16,0.46*lvl,'ghost',arc)
    for s in range(32):
        p=s*0.125
        P.H(b0+p,int(p*4)%16,(0.82 if s%8==0 else (0.46 if s%2==0 else 0.30))*lvl,o=0.0,
            art='edge' if s%8==0 else 'tip',arc=arc)
    for s in range(16): P.TB(b0+s*0.25,s,(0.48 if s%4==0 else 0.24)*lvl,arc)
    for p,f in [(0.0,830),(0.75,554),(1.5,830),(2.25,554),(2.75,830),(3.5,554)]:
        AG(b0+p,int(p*4)%16,(0.92 if f>700 else 0.68)*lvl,f,arc,seed=int(p*4))
    P.CL(b0+1+0.005,4,0.88*lvl,arc); P.CL(b0+3+0.005,12,0.92*lvl,arc)
    for p in (0.5,2.5): P.TM(b0+p,int(p*4)%16,0.55*lvl,tune=112 if p<1 else 88,arc=arc)

# --------- INTRO: thang bac cham ---------
for i in range(8):
    b=bar_at('INTRO',i); a=[1.0,0.97,1.0,1.02][i%4]
    if i<1:
        for p in (0.5,2.5): P.WD(b+p,int(p*4)%16,0.42,tune=1150)
    else:
        for p in (0.5,1.0,1.75,2.5,3.0,3.75):
            P.WD(b+p,int(p*4)%16,0.45 if p in (0.5,2.5) else 0.30,tune=1150 if p in (0.5,2.5) else 820)
    if i>=2:
        for q in range(4): P.K(b+q,q*4,0.60+0.06*(i-2),a,tune=49)
    if 4<=i<6: P.S(b+1,4,0.54,'cross',a); P.S(b+3,12,0.57,'cross',a)
    if i>=6:   P.S(b+1,4,0.78,'center',a); P.S(b+3,12,0.80,'center',a)
    if i>=5:
        for s in range(8): P.H(b+s*0.5,s*2,0.42+0.04*(i-5),o=0.0,art='tip',arc=a)
    if i>=6:
        for s in range(8): P.SH(b+s*0.5,s*2,0.26+0.04*(i-6),a)
    if i==7:
        P.CL(b+1+0.005,4,0.64); P.CL(b+3+0.005,12,0.66)
        P.fill(b+3.0,1.0,'roll',0.90,next_crash_beat=S['A1'])

DR_OF={'A1':(kit1,1),'A2':(kit2,2),'A3':(kit3,3),'A4':(kit4,4),'A5':(kit5,5),'A6':(kit6,6)}
for sec,(fn,L) in DR_OF.items():
    nb=dict(SECS)[sec]
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.97,1.01,1.03][i%4]
        lv=0.90+0.038*L
        if fn is kit1 or fn is kit2: fn(b,lv,a)
        else: fn(b,lv,a,i)
        # crash CHI o o dau moi cach danh moi; A1 va A4 da co crash tu fill dan vao
        if i==0 and sec not in ('A1','A4'): P.CR(b,0,0.60+0.028*L,size=0.95)
        if i==nb-1: P.fill(b+3.0,1.0,'stutter',0.9+0.05*L)
# STOP-TIME
for i in range(3):
    b=bar_at('STOP',i)
    if i<2:
        P.K(b,0,1.15); P.S(b,0,1.0,'center')
        if i==0: P.CR(b,0,0.72,size=1.05)
        P.K(b+2.5,10,1.05); P.S(b+2.5,10,0.95,'center')
        for p in (0.0,2.5): P.CG(b+p,int(p*4)%16,0.7,tune=150,art='slap')
        P.CL(b+1,4,0.7); P.CL(b+3,12,0.72)
    else:
        kit4(b,1.16,1.0,1)
        P.fill(b+2.0,2.0,'roll',1.15,next_crash_beat=S['A4'])
# TAG: day len roi tat, ket bang mot cu dam
for i in range(4):
    b=bar_at('TAG',i)
    if i<2:
        kit6(b,1.22-0.10*i,1.0,i)
    elif i==2:
        for s in range(8): P.K(b+s*0.5,s*2,0.98,tune=49)
        P.S(b+1,4,1.0,'center'); P.S(b+3,12,1.05,'center')
        P.fill(b+3.0,1.0,'roll',1.3)
    else:
        P.K(b,0,1.25); P.CR(b,0,0.85,size=1.35); P.S(b,0,1.08,'center')
        P.CG(b,0,0.85,tune=150,art='slap'); AG(b,0,1.0,830,seed=1); AG(b,0,0.85,554,seed=2)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.20,oh_amount=0.86,lofi=0.0,lpf=10500)

# ================= SAP XEP =================
noise_sw(fx,0,T(END),0.009,True,80,1500)
for i in range(8):
    b=bar_at('INTRO',i); k=kof(i)
    if i>=5: hook_bone(b,0.040+0.024*(i-5),seed=i,growl=0.45)   # cau hook he lo
    if i>=6: bass_bar(b,0.15+0.050*(i-6),k=k,dens=8)
LAY={'A1':1,'A2':2,'A3':3,'A4':4,'A5':5,'A6':6}
for sec,L in LAY.items():
    nb=dict(SECS)[sec]
    for i in range(nb):
        b=bar_at(sec,i); k=kof(i)
        hook_bone(b,0.108,seed=i,dbl8=(L>=5),oct_=(12 if L>=6 and i%4==3 else 0),growl=0.45+0.06*L)
        bass_bar(b,0.25,octjump=(L>=4),k=k,dens=(8 if L<=1 else 16))
        if L>=2: bone_chug(b,k,0.075,seed=i)
        if L>=3: brass_bar(b,k,0.085,hi=(L>=6))
        if L>=4: metalair(b,T(b+BAR*1.05)-T(b),0.052+0.006*L,seed=i,bright=0.9+0.08*L)
        if L>=6: metalair(b+2.0,T(b+BAR*1.1)-T(b+2.0),0.044,seed=i+2,bright=1.6,rate=1.2)
for i in range(3):
    b=bar_at('STOP',i); k=kof(i)
    if i<2:
        for off in (0.0,2.5):
            r=min(C_(k))+12
            for j,m in enumerate([r,r+12]):
                bone(brs,T(b+off)+j*0.010,m,SPB(b)*0.42,0.115,det=-8+16*j,growl=0.8,seed=j)
                hbone(bhk,T(b+off)+j*0.006,m+12,SPB(b)*0.26,0.100,det=-6,growl=0.8,seed=j%6)
            fzbass(bs,T(b+off),nn('E1'),SPB(b)*0.40,0.36,bite=1.3)
        metalair(b,T(b+BAR*0.98)-T(b),0.038,seed=i,bright=1.5,rate=1.5)
    else:
        hook_bone(b,0.112,seed=i,dbl8=True,growl=0.8); bass_bar(b,0.26,octjump=True,k=k)
        bone_chug(b,k,0.080,seed=i); brass_bar(b,k,0.095)
        metalair(b,T(b+BAR*1.1)-T(b),0.066,seed=9,bright=1.3)
for i in range(4):
    b=bar_at('TAG',i); k=kof(i)
    if i<3:
        f=[1.0,0.9,0.78][i]
        hook_bone(b,0.108*f,seed=i,dbl8=True,growl=0.8); bass_bar(b,0.25*f,octjump=(i<2),k=k)
        bone_chug(b,k,0.075*f,seed=i); brass_bar(b,k,0.090*f,hi=(i<2))
        metalair(b,T(b+BAR*1.05)-T(b),0.062*f,seed=i+5,bright=1.2)
    else:
        r=nn('E3')
        for j,m in enumerate([r,r+12,r+24]):
            bone(brs,T(b)+j*0.012,m,SPB(b)*2.2,0.112,det=-8+12*j,growl=0.6,seed=j)
        hbone(bhk,T(b),r+19,SPB(b)*1.8,0.095,det=-6,growl=0.7,seed=1)
        fzbass(bs,T(b),nn('E1'),SPB(b)*1.6,0.36,bite=1.2)
        metalair(b,SPB(b)*3.0,0.092,seed=3,bright=1.1,rate=0.5)

# ================= GIONG HAT =================
HOOK=[(0,.25,'B4','a','h'),(.25,.25,'B4','o','n'),(.5,.5,'A4','a','d'),
      (1,.25,'B4','a','h'),(1.25,.25,'B4','o','n'),(1.5,.5,'G4','a','d'),
      (2,.25,'E5','a','k'),(2.25,.25,'D5','o','m'),(2.5,.5,'B4','a','l'),
      (3,1.0,'A4','a','w')]
ANS =[(0,.25,'B4','a','h'),(.25,.25,'B4','o','n'),(.5,.5,'A4','a','d'),
      (1,.25,'B4','a','h'),(1.25,.25,'B4','o','n'),(1.5,.5,'G4','a','d'),
      (2,.25,'E5','a','k'),(2.25,.25,'D5','o','m'),(2.5,.5,'A4','a','l'),
      (3,1.0,'E4','a','y')]
STOPC=[(1.0,.25,'B4','a','h'),(1.25,.25,'B4','o','n'),(1.5,.5,'A4','a','d'),
       (3.0,.25,'E5','a','k'),(3.25,.25,'D5','o','m'),(3.5,.5,'B4','a','w')]
for sec,L in LAY.items():
    if L<=1: continue                       # A1: guitar noi cau hook mot luot, chua co giong
    nb=dict(SECS)[sec]
    for i in range(nb):
        b=bar_at(sec,i)
        cells=ANS if i%4==3 else HOOK
        st='deadpan' if L<=2 else ('croon' if L<=4 else 'shout')
        line(vx,b,cells,g=0.205+0.006*L,style=st,oct8=0.06*L,breath=0.26,seedbase=L*100+i*29)
        if L>=3: chant(vx,b,cells,g=0.030+0.024*(L-2),n=min(6,L+1),spread=10+2*L,
                       style='shout' if L>=5 else 'croon',seedbase=L*300+i)
for i in range(3):
    b=bar_at('STOP',i)
    if i<2:
        chant(vx,b,STOPC,g=0.21+0.02*i,n=6,spread=20,style='shout',seedbase=2000+i*29)
        line(vx,b,STOPC,g=0.16,style='shout',oct8=0.35,breath=0.20,seedbase=2100+i*29)
    else:
        line(vx,b,HOOK,g=0.21,style='shout',oct8=0.45,breath=0.18,seedbase=2200)
        chant(vx,b,HOOK,g=0.15,n=6,spread=20,style='shout',seedbase=2300)
        shriek(vx,T(b+3.0),nn('B5'),0.55,0.10)
for i in range(4):
    b=bar_at('TAG',i)
    if i<3:
        cells=ANS if i==2 else HOOK
        line(vx,b,cells,g=0.20,style='shout',oct8=0.44,breath=0.18,seedbase=2500+i*29)
        chant(vx,b,cells,g=0.15,n=6,spread=20,style='shout',seedbase=2600+i)
    else:
        chant(vx,b,[(0,1.5,'B4','a','h')],g=0.16,n=6,spread=20,style='shout',seedbase=2700)

# ================= MIX =================
STEMS=[(bhk,-0.34,0.66,0.48,0.0),(brs,0.34,0.60,0.50,6.0),
       (mtl,0.0,0.46,0.62,0.0),(fx,0.0,1.0,0.0,0.0)]
STEM_NAMES=["BRASS-HOOK","BRASS-RHYTHM","METAL",None]
MAPT=[(n,a,b_,(4.5 if n=='STOP' else 3.0)) for n,a,b_ in MAP]
KITMIX=dict(room_amount=0.20,oh_amount=0.86,lofi=0.0,lpf=10500)
MIXARGS=dict(wet=0.15,decay=1.15,wide=1.30,drum_gain=0.82,bass_gain=0.86,
             crush_amt=0.22,rms_target=0.180)
if (sys.argv[1] if len(sys.argv)>1 else "")=="--stems":
    stemdown(NAME,vx,STEMS,DRUMS,bs,MAPT,stem_names=STEM_NAMES,
             kitbus=P.bus,kitmix=KITMIX,outdir="stems-90s-nogtr",**MIXARGS)
else:
    run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,**MIXARGS), MAPT)
