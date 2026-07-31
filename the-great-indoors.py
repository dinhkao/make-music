"""THE GREAT INDOORS - ONE-FILE version (self-contained).
Run:  python3 the-great-indoors.py   ->  THE-GREAT-INDOORS-v2.wav
Everything inline: tempo map + instruments (KS/Wurli/organ/bass/horn/
vocal formants), modal-synthesis drum kit, humanized performer with
5-mic bleed model, drum arrangement, full arrangement, mix.
Needs only: numpy + scipy.
"""
import struct
import numpy as np
from scipy import signal as sg
from scipy.special import jv

SR = 44100
rng = np.random.default_rng(430)

# ===================== ENGINE: TEMPO + NOTES + INSTRUMENTS =====================

# ---------- tempo map: 118 nen, day len 134 o outro, sup xuong 92 o tag ----------
TEMPO=[(0,312,118,119)]   # <- chi +1 BPM tren toan bai, khong ritardando
_gb=np.arange(0,314,0.004)
def _bpm(b):
    for s,e,b0,b1 in TEMPO:
        if s<=b<e: return b0+(b1-b0)*(b-s)/(e-s)
    return TEMPO[-1][3]
_ct=np.concatenate([[0],np.cumsum(np.array([60.0/_bpm(b) for b in _gb])*0.004)[:-1]])
def T(b): return float(np.interp(b,_gb,_ct))
def SPB(b): return 60.0/_bpm(b)
TOTAL=T(312)+5

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

# ---------- KARPLUS-STRONG: day dan that ----------
_KS={}
def ks(m, dur, damp=0.9955, bright=0.55, seed=0):
    key=(m,round(dur,2),round(bright,2),seed)
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

# ---------- WURLITZER (2-op FM, hoi lech tone) ----------
def wurli(b_,t0,m,dur,g=0.13,det=0.0):
    L=int(dur*SR)+int(0.4*SR); t=np.arange(L)/SR
    f=hz(m)*2**(det/1200)
    idx=2.1*np.exp(-t*5.5)+0.35
    x=np.sin(2*np.pi*f*t+idx*np.sin(2*np.pi*f*2*t))
    x+=np.sin(2*np.pi*f*t*1.001)*0.4
    x*=np.exp(-t*2.4)*np.minimum(1,t*260)
    x*= (1+0.10*np.sin(2*np.pi*5.4*t))            # tremolo
    bq,aq=sg.butter(2,4200/(SR/2),'low'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,np.tanh(x*1.3),g)

# ---------- COMBO ORGAN (drawbar) ----------
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
    L=int(min(dur,1.1)*SR)+int(0.18*SR); t=np.arange(L)/SR
    f=hz(m); ff=f*(2**(-gl/12*np.exp(-t*26)))
    ph=2*np.pi*np.cumsum(ff)/SR
    x=sum(np.sin(ph*k)/k for k in range(1,11))*0.5+np.sin(ph)*0.75+np.sin(ph/2)*0.30
    bq,aq=sg.butter(2,760/(SR/2),'low'); x=sg.lfilter(bq,aq,x)
    x*=np.exp(-t*2.6)*np.minimum(1,t*480)
    put(b_,t0,np.tanh(x*1.35),g)

# ---------- HORNS (kem hoi phe, rat indie) ----------
def horn(b_,t0,m,dur,g=0.10,det=0.0,rough=1.0):
    L=int(dur*SR)+int(0.25*SR); t=np.arange(L)/SR
    f=hz(m)*2**(det/1200)
    vf=1+0.006*np.sin(2*np.pi*4.8*t)*np.minimum(1,t*2.2)
    drift=1+0.0035*np.sin(2*np.pi*0.7*t+m)          # hoi phe tone
    ph=2*np.pi*np.cumsum(f*vf*drift)/SR
    x=sum(np.sin(ph*k)/(k**1.12) for k in range(1,20))
    x=np.tanh(x*(1.1+0.9*rough))
    for fc,gg,bw in [(1150,1.0,300),(2200,0.55,420)]:
        bq,aq=sg.butter(2,[(fc-bw)/(SR/2),(fc+bw)/(SR/2)],'band'); x+=sg.lfilter(bq,aq,x)*gg*0.7
    bq,aq=sg.butter(2,[230/(SR/2),5200/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(b_,t0,x*env(L,0.055,0.18,0.85,0.22),g)

# ---------- VOCAL FORMANT (dung lai tu bai truoc) ----------
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

# ---------- DRUMS ----------
def kick(b_,t0,g=0.9,room=0.25):
    L=int(0.45*SR); t=np.arange(L)/SR
    f=54*np.exp(-t*24)+43
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8.0)
    x+=rng.standard_normal(L)*np.exp(-t*230)*0.24
    put(b_,t0,np.tanh(x*1.6),g)
def snare(b_,t0,g=0.5,rim=False,ghost=False):
    L=int(0.34*SR); t=np.arange(L)/SR
    n=rng.standard_normal(L)
    bq,aq=sg.butter(2,[780/(SR/2),8200/(SR/2)],'band'); ns=sg.lfilter(bq,aq,n)
    tone=(np.sin(2*np.pi*186*t)+np.sin(2*np.pi*312*t)*0.7)*0.42
    x=(ns*0.95+tone)*np.exp(-t*(26 if ghost else 15))
    if rim:
        bq,aq=sg.butter(2,[1500/(SR/2),4000/(SR/2)],'band')
        x=sg.lfilter(bq,aq,n)*np.exp(-t*60)*1.4
    put(b_,t0,np.tanh(x*1.25),g*(0.30 if ghost else 1.0))
def hat(b_,t0,g=0.13,op=False):
    L=int((0.22 if op else 0.05)*SR); t=np.arange(L)/SR
    n=rng.standard_normal(L); bq,aq=sg.butter(3,8600/(SR/2),'high'); n=sg.lfilter(bq,aq,n)
    put(b_,t0,n*np.exp(-t*(13 if op else 70)),g)
def ride(b_,t0,g=0.10):
    L=int(0.7*SR); t=np.arange(L)/SR
    n=rng.standard_normal(L); x=np.zeros(L)
    for fr in (3100,4300,5700,7200):
        bq,aq=sg.iirpeak(fr/(SR/2),42); x+=sg.lfilter(bq,aq,n)
    put(b_,t0,x*np.exp(-t*5.5)*0.45,g)
def tamb(b_,t0,g=0.09):
    L=int(0.24*SR); t=np.arange(L)/SR
    n=rng.standard_normal(L); x=np.zeros(L)
    for fr in (5200,6800,8600,10400):
        bq,aq=sg.iirpeak(fr/(SR/2),60); x+=sg.lfilter(bq,aq,n)
    put(b_,t0,x*np.exp(-t*17)*0.5,g)
def clap(b_,t0,g=0.16,n=7):
    r2=np.random.default_rng(int(t0*7919)%9999)
    for i in range(n):
        j=r2.normal(0,0.014)+ (0.006*i if i<3 else 0)
        L=int(0.2*SR); t=np.arange(L)/SR
        x=r2.standard_normal(L)
        bq,aq=sg.butter(2,[1100/(SR/2),4200/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
        put(b_,t0+j,x*np.exp(-t*(38 if i<3 else 16)),g/np.sqrt(n))
def noise_sw(b_,t0,dur,g=0.09,up=True,lo=300,hi=9000):
    L=int(dur*SR); t=np.linspace(0,1,L)
    n=rng.standard_normal(L)
    bq,aq=sg.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); n=sg.lfilter(bq,aq,n)
    put(b_,t0,n*((t**2) if up else ((1-t)**2)),g)


# ===================== ENGINE: DRUM KIT (MODAL SYNTH) =====================
"""
Engine trong moi: modal synthesis + mo hinh nhan hoa dua tren so lieu do duoc.
Nguon: Hofmann/Fuhrmann (microtiming), Rasanen et al. (PLOS, hi-hat),
Gillick et al. (Groove MIDI Dataset), SoS drum synthesis series, Penn State membrane modes.
"""

# ---- bang ti le mode mang tron ly tuong (Bessel zeros / j01) ----
IDEAL=[1.0000,1.5934,2.1356,2.2952,2.6528,2.9172,3.1551,3.4998,3.5983,3.6470]
JMN  =[2.405,3.832,5.136,5.520,6.380,7.016,7.588,8.417,8.654,8.771]
MORD =[0,1,2,0,3,1,4,2,0,5]
# ---- mang co tai khong khi (tom/timpani): gan chuoi hai am ----
AIRLOADED=[1.00,1.50,1.98,2.44,2.89,3.36]

def _hp(x,f,o=2): b,a=sg.butter(o,min(f,SR/2-100)/(SR/2),'high'); return sg.lfilter(b,a,x)
def _lp(x,f,o=2): b,a=sg.butter(o,min(f,SR/2-100)/(SR/2),'low');  return sg.lfilter(b,a,x)
def _bp(x,lo,hi,o=2):
    hi=min(hi,SR/2-100); lo=max(lo,20)
    b,a=sg.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return sg.lfilter(b,a,x)

def modal(f0,taus,gains,L,rng,glide=0.05,tg=0.02,detune_cents=0,ratios=IDEAL):
    """Tong modal dang dong. PHA NGAU NHIEN moi cu danh -> giet comb filter."""
    t=np.arange(L)/SR
    g=1+glide*np.exp(-t/tg)                       # cao do luot xuong (cang mang phi tuyen)
    ph=2*np.pi*np.cumsum(g)/SR
    det=2**(detune_cents/1200)
    out=np.zeros(L)
    for r,tau,gn in zip(ratios,taus,gains):
        f=f0*r*det
        if f>SR/2.2: continue
        out+=gn*np.exp(-t/tau)*np.sin(ph*f+rng.uniform(0,2*np.pi))
    return out

def bessel_gains(r_rel,rng,n=10,jitter=0.08):
    """Vi tri danh -> do loi tung mode. Danh giua = chi mode m=0 (day),
       danh ria = nhieu mode bac cao (sang, mong)."""
    r=np.clip(r_rel+rng.normal(0,jitter),0.0,0.92)
    g=[]
    for i in range(n):
        v=abs(jv(MORD[i], JMN[i]*r))
        g.append(v*10**(rng.normal(0,0.35)))       # +-3..7 dB moi mode
    g=np.array(g); return g/ (g.max()+1e-9)

# =========================================================
class Kit:
    def __init__(self, seed=7):
        self.rng=np.random.default_rng(seed)
        self._cache={}

    # ---------- KICK ----------
    def kick(self, vel=1.0, tune=48.0, click=1.0, mode='acoustic'):
        R=self.rng; L=int(0.55*SR); t=np.arange(L)/SR
        det=2**(R.normal(0,28)/1200)
        if mode=='acoustic':
            # SoS: chuoi rieng le f_k = 43k+7 (lech hai am -> khong phai sine)
            body=np.zeros(L)
            for k in range(1,7):
                f=(tune*k*0.9+7)*det
                tau=0.26/ (k**0.72)
                body+=(1.0/k**0.9)*np.exp(-t/tau)*np.sin(2*np.pi*f*t+R.uniform(0,2*np.pi))
            gl=1+0.09*np.exp(-t/0.025)             # vat ly: +9%, tau 25ms
            body*= gl
        else:                                       # 'elec' — kick lap trinh kieu MagBay
            f=tune*det*(1+2.6*np.exp(-t/0.030))
            body=np.sin(2*np.pi*np.cumsum(f)/SR+R.uniform(0,2*np.pi))*np.exp(-t/0.16)
            body+=np.sin(2*np.pi*np.cumsum(f*0.5)/SR)*np.exp(-t/0.22)*0.5
        # dai 250Hz-1kHz: FM (khong the lam bang cong hai am)
        fm=np.sin(2*np.pi*185*det*t+ (2.2*np.exp(-t/0.04))*np.sin(2*np.pi*259*t))
        body+=fm*np.exp(-t/0.045)*0.24
        # beater click: LPF quet 8k -> 300 Hz trong 6 ms
        n=R.standard_normal(L)*np.exp(-t/0.0045)
        cl=_lp(_hp(n,220),4200)*click*0.5*vel
        x=body*vel + cl
        x=_hp(x,32,4)                               # cong thung
        return np.tanh(x*1.5)

    # ---------- SNARE ----------
    def snare(self, vel=1.0, tune=205.0, art='center'):
        R=self.rng; L=int(0.42*SR); t=np.arange(L)/SR
        r_rel={'center':0.12,'edge':0.62,'ghost':0.34,'rim':0.20,'cross':0.80}[art]
        g=bessel_gains(r_rel,R)
        taus=np.array([0.045,0.20,0.17,0.055,0.14,0.11,0.09,0.08,0.05,0.07])
        taus=taus*(1+R.normal(0,0.10,10))
        if art=='rim': taus*=0.7
        det=R.normal(0,30)
        mem=modal(tune,taus,g,L,R,glide=0.06,tg=0.02,detune_cents=det)
        # mat cong huong: bo mode thu 2 lech -> phach
        mem+=modal(tune*1.42,taus*0.8,g*0.55,L,R,glide=0.05,tg=0.018,
                   detune_cents=det+R.normal(0,18))*0.6
        # ---- day snare: NGUONG PHI TUYEN (day khong rung duoi mot muc) ----
        envm=np.abs(sg.lfilter(*sg.butter(2,120/(SR/2),'low'), np.abs(mem)))
        envm/= (envm.max()+1e-9)
        thr={'ghost':0.42,'center':0.14,'edge':0.20,'rim':0.06,'cross':0.85}[art]
        wire_env=np.clip(envm-thr,0,None)/(1-thr)
        n=R.standard_normal(L)
        wire=_bp(n,1100,9500,3)
        # rung day = chuoi va cham roi rac, khong phai noise muot
        buzz=(R.random(L)<0.055).astype(float)
        buzz=sg.lfilter([1],[1,-0.90],buzz)
        wire=wire*(0.55+0.85*buzz/ (buzz.max()+1e-9))
        d=int(R.uniform(0.0005,0.003)*SR)           # tre 0.5-3 ms qua thung
        wire=np.concatenate([np.zeros(d),wire])[:L]
        wire*=wire_env*np.exp(-t/R.uniform(0.11,0.24))
        # ---- transient dui ----
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
        return np.tanh(x*1.25)

    def flam(self, vel=1.0, tune=205.0, art='center'):
        R=self.rng
        gap=int(R.uniform(0.012,0.032)*SR)
        a=self.snare(vel*R.uniform(0.30,0.48),tune*1.01,'ghost')
        b=self.snare(vel,tune,art)
        out=np.zeros(max(len(a),len(b))+gap)
        out[:len(a)]+=a; out[gap:gap+len(b)]+=b
        return out

    # ---------- TOM ----------
    def tom(self, vel=1.0, tune=120.0, art='center'):
        R=self.rng; L=int(0.7*SR); t=np.arange(L)/SR
        g=bessel_gains(0.20 if art=='center' else 0.6,R,n=6)
        taus=np.array([0.30,0.42,0.34,0.26,0.20,0.16])*(1+R.normal(0,0.12,6))
        x=modal(tune,taus,g,L,R,glide=0.08,tg=0.03,detune_cents=R.normal(0,35),
                ratios=AIRLOADED)
        x+=modal(tune*1.06,taus*0.85,g*0.5,L,R,glide=0.07,tg=0.028,
                 ratios=AIRLOADED)*0.5              # mat cong huong -> phach
        stick=_bp(R.standard_normal(L),1800,5500,2)*np.exp(-t/0.004)
        return np.tanh((x+stick*0.5)*vel*1.2)

    # ---------- CYMBAL / HI-HAT: modal bank thua, di chuyen nang luong len cao ----
    def _cym(self, L, nmodes, fmin, fmax, tau_lo, tau_hi, seed, migrate=0.10):
        R=np.random.default_rng(seed); t=np.arange(L)/SR
        f=np.sort(R.uniform(fmin,fmax,nmodes)**1.0)
        f=f*(1+R.normal(0,0.02,nmodes))
        tau=tau_hi*(f/fmin)**(-0.62)*(1+R.normal(0,0.18,nmodes))
        tau=np.clip(tau,tau_lo,tau_hi)
        ph=R.uniform(0,2*np.pi,nmodes)
        amp=(f/fmin)**(-0.42)*(1+R.normal(0,0.35,nmodes))
        # nang luong di len cao dan: mode cao vao muon (mo phong phi tuyen)
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
        """openness 0..1. Hai cymbal gan giong nhau -> phach (khong the lam bang sample)."""
        R=self.rng
        v=int(R.integers(0,7)) if variant is None else variant
        o=float(np.clip(openness,0,1))
        key=('hat',round(o,2),art,v)
        if key not in self._cache:
            L=int((0.06+0.75*o)*SR)
            tau_hi=0.045+0.62*o
            a=self._cym(L,260,320,15500,0.012,tau_hi,seed=9000+v*13+int(o*100),migrate=0.05*o)
            b=self._cym(L,260,320,15500,0.012,tau_hi,seed=9500+v*13+int(o*100),migrate=0.05*o)
            delta=0.004+0.016*o                     # hai cymbal lech nhau -> phach
            bb=np.interp(np.clip(np.arange(L)*(1+delta),0,L-1),np.arange(L),b)
            x=a+bb*(0.55+0.45*o)
            if o<0.15:                              # sizzle: hai cymbal cham nhau
                buzz=(np.random.default_rng(7+v).random(L)<0.09).astype(float)
                x=x*(1+0.5*buzz)
            self._cache[key]=(x/ (np.abs(x).max()+1e-9)).astype(np.float32)
        x=self._cache[key].astype(np.float64).copy()
        L=len(x); t=np.arange(L)/SR
        if art=='edge':  x=_bp(x,380,11000,2)*1.6   # go, thap hon, to hon
        elif art=='tip': x=_bp(x,900,15000,2)
        elif art=='foot':x=_bp(x,200,4200,2)*1.2    # dam chan: thap hon han
        # bien doi cao do nho moi cu danh (chong "sung may")
        sh=2**(R.normal(0,0.018))
        idx=np.clip(np.arange(L)*sh,0,L-1); i0=idx.astype(int); fr=idx-i0
        x=x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr
        return x*vel*np.exp(-t/(0.05+0.85*o))

    def choke(self, x, at_samples):
        """Bop hi-hat mo bang cu dong tiep theo — bat buoc trong disco."""
        y=x.copy()
        if at_samples<len(y):
            n=min(int(0.006*SR),len(y)-at_samples)
            y[at_samples:at_samples+n]*=np.linspace(1,0,n)
            y[at_samples+n:]=0
        return y

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
        return (x[i0]*(1-fr)+x[np.minimum(i0+1,L-1)]*fr)*vel
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
        return (x+ping*(0.45 if not bell else 0.8))*vel

    def clap(self, vel=1.0):
        """Nhieu nguoi vo tay: 3-6 xung cach nhau ~11 ms, ngau nhien +-3 ms."""
        R=self.rng; L=int(0.45*SR); t=np.arange(L)/SR
        out=np.zeros(L); n=int(R.integers(3,7))
        for i in range(n):
            d=int(max(0,R.normal(i*0.011,0.003))*SR)
            b=_bp(R.standard_normal(L),1050,4400,2)*np.exp(-t/0.006)
            out[d:]+=b[:L-d]*R.uniform(0.6,1.0)
        tail=_bp(R.standard_normal(L),900,3600,2)*np.exp(-t/0.055)*0.55
        return (out+tail)*vel
    def tamb(self, vel=1.0):
        R=self.rng; L=int(0.3*SR); t=np.arange(L)/SR
        x=np.zeros(L)
        for fr in (4700,6100,7900,9800,12200):
            b,a=sg.iirpeak(fr/(SR/2),R.uniform(45,75)); x+=sg.lfilter(b,a,R.standard_normal(L))
        jingle=(R.random(L)<0.14).astype(float)
        return x*np.exp(-t/R.uniform(0.028,0.055))*(0.6+0.7*jingle)*vel*0.45
    def shaker(self, vel=1.0):
        R=self.rng; L=int(0.16*SR); t=np.arange(L)/SR
        n=_bp(R.standard_normal(L),4200,13000,2)
        return n*np.exp(-t/R.uniform(0.016,0.030))*vel*0.5



# ===================== ENGINE: PERFORMER + MIX_KIT =====================
"""
Lop bieu dien: nhan hoa theo so lieu do duoc, + mo hinh micro/bleed.
Nguyen tac chinh (nguoc voi cach lam thong thuong):
  - TIMING: ~50% la mau lech CO DINH lap moi o nhip (systematic), ~50% la nhieu Gauss.
  - VELOCITY: mau accent gan nhu TAT DINH (r=0.92 giua cac o nhip), chi +-4% nhieu.
  - Jitter ONSET tuyet doi, khong jitter khoang cach -> tu sinh anticorrelation lag-1.
  - Not tren phach danh TRE (+2..6ms), not le 16 danh SOM (-2..6ms)  [Groove MIDI Dataset]
"""

SIGMA={'kick':0.0055,'snare':0.0026,'hat':0.0031,'tom':0.0035,'cym':0.0040,'perc':0.0045}
# 8ths mot tay: downbeat manh, upbeat la nay lai
ACC8 =[1.00,0.62,0.85,0.62,0.95,0.62,0.85,0.62]
ACC16=[1.00,0.45,0.70,0.45,0.85,0.45,0.68,0.45,0.95,0.45,0.70,0.45,0.85,0.48,0.68,0.52]

class Performer:
    def __init__(self, kit, Tfunc, SPBfunc, total_s, seed=11, style='indie'):
        self.k=kit; self.T=Tfunc; self.SPB=SPBfunc
        self.rng=np.random.default_rng(seed)
        N=int(total_s*SR)+SR
        self.bus={n:np.zeros(N) for n in ['kick','snare','hat','tom','cym','perc']}
        self.style=style
        # --- mau lech CO DINH, rut MOT LAN, lap lai suot bai ---
        R=np.random.default_rng(seed+1)
        self.sysoff={}
        for inst in SIGMA:
            for p in range(16):
                self.sysoff[(inst,p)]=R.normal(0,0.0034)
        # laid-back: indie = trong hoi tut lai
        self.laid={'kick':0.0,'snare':0.012 if style=='indie' else 0.004,
                   'hat':-0.002,'tom':0.006,'cym':0.0,'perc':0.003}
        self.openhats=[]
        self.hum=1.0          # he so nhan hoa: 0 = may moc tuyet doi, >1 = long leo

    def _t(self, beat, inst, pos16):
        p=int(round(pos16))%16
        metric = 0.004 if p%4==0 else -0.0032          # tren phach tre / le 16 som
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

    # ---------------- cac cu danh ----------------
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
        if o>0.25 and choke_beat is not None:        # BOP hat mo bang cu tiep theo (disco)
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

    def apply_chokes(self):
        h=self.bus['hat']
        for start,cut in self.openhats:
            if cut>start and cut<len(h):
                n=min(int(0.005*SR),len(h)-cut)
                # chi bop phan duoi cua chinh cu do (xap xi: fade vung sau diem cut)
                seg=slice(cut,cut+n); h[seg]*=np.linspace(1,0.25,n)

    # ---------------- FILL (thay cho riser) ----------------
    def fill(self, beat_start, beats=2.0, kind='tom', intensity=1.0, next_crash_beat=None):
        """Fill thay the hoan toan cho noise riser."""
        R=self.rng
        if kind=='tom':
            toms=[168,140,112,92]
            n=int(beats*4)
            for i in range(n):
                p=beat_start+i*0.25
                v=(0.55+0.45*i/max(n-1,1))*intensity
                self.TM(p,(i%16),v,tune=toms[min(int(i/max(n/4,1)),3)])
                if i%4==0: self.K(p,(i%16),0.6*intensity)
        elif kind=='snare':
            n=int(beats*4)
            for i in range(n):
                p=beat_start+i*0.25
                v=(0.45+0.55*i/max(n-1,1))*intensity
                art='ghost' if (i%4 in (1,2) and i<n-4) else 'center'
                self.S(p,(i%16),v,art=art)
        elif kind=='roll':                            # cuon 32 dan len
            n=int(beats*8)
            for i in range(n):
                p=beat_start+i*0.125
                self.S(p,int(i/2)%16,(0.30+0.70*i/max(n-1,1))*intensity,
                       art='ghost' if i<n*0.5 else 'center')
        elif kind=='negative':                        # "fill am": bo het, chi con kick
            self.K(beat_start,0,0.9*intensity)
            self.S(beat_start+beats-0.25,12,0.8*intensity,art='rim')
        elif kind=='stutter':                         # kieu Villa: nhom 3 lech phach
            n=int(beats*4)
            for i in range(n):
                p=beat_start+i*0.25
                if i%3==0: self.K(p,i%16,0.85*intensity)
                else:      self.S(p,i%16,(0.4+0.5*(i/n))*intensity,
                                  art='ghost' if i%3==1 else 'center')
        if next_crash_beat is not None:
            self.CR(next_crash_beat,0,0.85*intensity)
            self.K(next_crash_beat,0,1.0*intensity)   # crash LUON di kem kick

# ================= MO HINH MICRO + BLEED =================
def delay(x,ms):
    d=int(ms/1000*SR); return np.concatenate([np.zeros(d),x])[:len(x)]

def mix_kit(bus, room_amount=0.22, oh_amount=0.85, lofi=0.0, lpf=9000):
    """Dung 5 micro ao. Bleed la thu lam bo trong nghe nhu MOT vat the."""
    K,S,H,TMb,CY,PC=(bus['kick'],bus['snare'],bus['hat'],bus['tom'],bus['cym'],bus['perc'])
    # --- close mics + bleed (muc va do tre theo hinh hoc that) ---
    kick_m  = K + _lp(delay(S,0.6),800)*0.11 + _lp(delay(TMb,0.8),700)*0.09
    snare_m = S + _lp(delay(K,0.5),650)*0.15 + _hp(delay(H,0.3),1500)*0.17 + delay(TMb,0.7)*0.12
    hat_m   = _hp(H,400) + _hp(delay(S,0.4),900)*0.20
    tom_m   = TMb + _lp(delay(K,0.6),600)*0.10 + delay(S,0.5)*0.14
    # --- overhead (1.3 m -> 3.8 ms), nghe TOAN BO bo trong ---
    ohsrc = _lp(K,900)*0.42 + S*0.85 + H*0.95 + TMb*0.75 + CY*1.0 + PC*0.6
    OH    = _hp(delay(ohsrc,3.8),120)
    # --- room mono (3 m -> 8.7 ms) + phan xa som ---
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


# ===================== RENDER FX (REVERB/CHORUS/WAV) =====================
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

def write_wav(path, data):
    d = np.clip(data, -1, 1)
    pcm = (d*32767).astype('<i2')
    n = pcm.size*2
    with open(path,'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,2,SR,SR*4,4,16)+b'data'+struct.pack('<I',n))
        f.write(pcm.tobytes())

# ===================== DRUM ARRANGEMENT =====================
"""THE GREAT INDOORS - drum arrangement (Performer/Kit engine).
Run: python3 great-indoors-drums.py -> drums_new.npy (mono drum bus)
"""

K=Kit(seed=430); P=Performer(K,T,SPB,TOTAL,seed=77,style='indie')
def arcv(i,n):  # duong dong trong 4/8 o nhip: dinh o o 1, hoi lun giua, nhac len o cuoi
    return [1.0,0.94,0.96,1.02][i%4]*(1.0+0.03*(i>=n-1))

# ---------------- INTRO 0-16 : dem gay + fill nho (khong riser) ----------------
for k in range(4): P.S(12+k,(k*4)%16,0.40+0.05*k,art='cross')
P.fill(15.0,1.0,'snare',0.55,next_crash_beat=16)

# ---------------- VERSE 1  16-48 : indie kho, cross-stick, khong ghost ----------------
for i in range(8):
    b=16+i*4; a=arcv(i,8); last=(i==7)
    P.K(b+0,0,0.95,a); P.K(b+2.5,10,0.62,a)
    if i%2==1: P.K(b+3.75,15,0.45,a)
    P.S(b+1,4,0.80,'cross',a); P.S(b+3,12,0.84,'cross',a)
    for s in range(8):
        p=b+s*0.5
        if i%4==3 and s>=6: continue                 # FILL AM: bo hat 1 phach cuoi
        P.H(p,s*2,0.72,o=0.0,art='tip' if s%2==0 else 'edge',arc=a)
    P.H(b+1,4,0.30,o=0.0,art='foot',arc=a)           # dam chan tren 2 va 4
    P.H(b+3,12,0.30,o=0.0,art='foot',arc=a)
    if i==3: P.fill(b+3.5,0.5,'snare',0.5)
    if last: P.fill(b+3.0,1.0,'tom',0.75,next_crash_beat=48)

# ---------------- REFRAIN 1  48-80 : snare that + tambourine giu nhip (Motown) ----------------
for i in range(8):
    b=48+i*4; a=arcv(i,8)
    P.K(b+0,0,1.0,a); P.K(b+2.5,10,0.70,a)
    if i%2==1: P.K(b+1.75,7,0.48,a)
    P.S(b+1,4,1.0,'center',a); P.S(b+3,12,1.0,'rim' if i%4==3 else 'center',a)
    if i%2==1: P.S(b+2.75,11,0.9,'ghost',a)
    for s in range(8):
        p=b+s*0.5; op=(s==5 and i%2==1)
        P.H(p,s*2,0.85 if s%2==0 else 0.58,o=0.5 if op else 0.0,
            art='tip' if s%2==0 else 'edge',arc=a,choke_beat=(b+3.0) if op else None)
    for s in range(8): P.TB(b+s*0.5,s*2,0.55,a)
    if i==3: P.fill(b+3.5,0.5,'snare',0.6)
    if i==7: P.fill(b+3.0,1.0,'tom',0.85,next_crash_beat=80)

# ---------------- VERSE 2  80-112 : ride thay hat, ghost xuat hien, kick day hon ----------------
for i in range(8):
    b=80+i*4; a=arcv(i,8)
    P.K(b+0,0,0.98,a); P.K(b+2.5,10,0.68,a); P.K(b+3.5,14,0.44,a)
    P.S(b+1,4,0.94,'center',a); P.S(b+3,12,0.96,'center',a)
    for gp in (1.75,2.75,3.25):
        P.S(b+gp,int(gp*4)%16,0.85,'ghost',a)
    for s in range(8): P.RD(b+s*0.5,s*2,0.72 if s%2==0 else 0.50,bell=(s==0 and i%4==0),arc=a)
    if i==3: P.fill(b+3.5,0.5,'stutter',0.6)
    if i==7: P.fill(b+3.0,1.0,'stutter',0.9,next_crash_beat=112)

# ---------------- REFRAIN 2  112-144 : backbeat GHEP snare+clap+tamb (0/+4/+9ms) ----------------
for i in range(8):
    b=112+i*4; a=arcv(i,8)
    P.K(b+0,0,1.0,a); P.K(b+2.5,10,0.72,a); P.K(b+1.75,7,0.5,a)
    for bp_ in (1,3):
        P.S(b+bp_,bp_*4,1.0,'center',a)
        P.CL(b+bp_+0.004/SPB(b),bp_*4,0.85,a)
        P.TB(b+bp_+0.009/SPB(b),bp_*4,0.8,a)
    if i%2==1: P.S(b+2.75,11,0.9,'ghost',a)
    for s in range(16):
        p=b+s*0.25; op=(s in (6,14) and i%2==1)
        P.H(p,s,0.90 if s%4==0 else (0.62 if s%2==0 else 0.42),
            o=0.55 if op else 0.0,art='tip' if s%4==0 else 'edge',arc=a,
            choke_beat=(b+(s+2)*0.25) if op else None)
    for s in range(8): P.TB(b+s*0.5,s*2,0.45,a)
    if i==3: P.fill(b+3.5,0.5,'snare',0.7)
    if i==7: P.fill(b+2.5,1.5,'tom',1.0,next_crash_beat=144)

# ---------------- BRIDGE 144-176 : chi tom san, khong hat -> "ca ban cung danh accent" ----
for i in range(8):
    b=144+i*4; a=arcv(i,8)
    for off,tn,v in [(0,168,0.9),(0.75,140,0.6),(1.5,168,0.75),(2,112,0.85),
                     (2.75,140,0.6),(3.5,92,0.7)]:
        P.TM(b+off,int(off*4)%16,v,tune=tn,arc=a)
    P.K(b+0,0,0.9,a); P.K(b+2,8,0.75,a)
    P.S(b+2,8,0.85,'rim',a)
    if i%2==1: P.S(b+3.5,14,0.6,'ghost',a)
    if i==7: P.fill(b+3.0,1.0,'tom',1.0,next_crash_beat=176)

# ---------------- RAMP 176-192 : XAY BANG TRONG, khong dung noise riser ----------------
for i in range(4):
    b=176+i*4; a=1.0+0.06*i
    for j in range(4): P.K(b+j,j*4,0.9+0.02*i,a)
    P.S(b+1,4,0.95,'center',a); P.S(b+3,12,1.0,'center',a)
    div=[8,8,16,32][i]                                # 8 -> 8 -> 16 -> 32: tang mat do
    for s in range(div):
        p=b+s*(4.0/div)
        P.H(p,int(s*16/div)%16,(0.55+0.05*i) if s%(div//4)==0 else (0.36+0.05*i),
            o=0.0,art='tip' if s%(div//4)==0 else 'edge',arc=a)
    for s in range(8): P.TB(b+s*0.5,s*2,0.5+0.08*i,a)
    if i==3:
        P.fill(b+2.0,2.0,'roll',1.0)                  # cuon snare 32 thay cho riser

# ---------------- CUT 192-200 : im lang that + fill stutter kieu Villa ----------------
P.S(192,0,0.55,'cross')
P.H(193,4,0.22,o=0.0,art='foot')
P.H(195,12,0.22,o=0.0,art='foot')
P.fill(197.0,3.0,'stutter',0.95,next_crash_beat=200)

# ---------------- OUTRO 1  200-232 : disco 4/4 + HAT MO BI BOP (chu ky MagBay) ----------
def outro_bar(b,a,level=1.0,tamb16=False,ride=False,claps=True,elec=True):
    for j in range(4):
        P.K(b+j,j*4,(1.0 if j%2==0 else 0.82)*level,a,mode='elec' if elec else 'acoustic')
    P.S(b+1,4,0.98*level,'center',a); P.S(b+3,12,1.0*level,'center',a)
    if claps:
        P.CL(b+1+0.004/SPB(b),4,0.85*level,a); P.CL(b+3+0.004/SPB(b),12,0.9*level,a)
    for s in range(8):
        p=b+s*0.5
        if s%2==1:                                     # hat MO tren tat ca phach le...
            P.H(p,s*2,0.72*level,o=0.62,art='edge',arc=a,choke_beat=b+(s+1)*0.5)
        else:                                          # ...bi BOP boi cu dong ke tiep
            P.H(p,s*2,0.88*level,o=0.0,art='tip',arc=a)
    if tamb16:
        for s in range(16): P.TB(b+s*0.25,s,0.42*level,a)
    else:
        for s in range(8): P.TB(b+s*0.5,s*2,0.5*level,a)
    if ride:
        for s in range(8): P.RD(b+s*0.5,s*2,0.45*level,bell=(s==0),arc=a)

for i in range(8):
    b=200+i*4; a=arcv(i,8)
    outro_bar(b,a,1.0,tamb16=False,ride=False)
    if i==0: P.CR(b,0,0.9); P.K(b,0,1.0,mode='elec')
    if i==3: P.fill(b+3.5,0.5,'snare',0.7)
    if i==7: P.fill(b+3.0,1.0,'tom',1.0,next_crash_beat=232)

# ---------------- OUTRO 2  232-264 : + ride, tambourine 16, crash moi 4 o ----------------
for i in range(8):
    b=232+i*4; a=arcv(i,8)
    outro_bar(b,a,1.06,tamb16=True,ride=True)
    if i%4==0: P.CR(b,0,0.8);
    if i%2==1: P.S(b+2.75,11,0.9,'ghost',a); P.S(b+3.75,15,0.85,'ghost',a)
    if i==3: P.fill(b+3.5,0.5,'stutter',0.8)
    if i==7: P.fill(b+2.5,1.5,'tom',1.0,next_crash_beat=264)

# ---------------- OUTRO 3  264-296 : max, crash moi 2 o, fill lech kieu Villa ----------
for i in range(8):
    b=264+i*4; a=arcv(i,8)
    outro_bar(b,a,1.12,tamb16=True,ride=True)
    for j in (0.5,1.5,2.5,3.5): P.K(b+j,int(j*4)%16,0.55,a,mode='elec')
    if i%2==0: P.CR(b,0,0.85,size=1.15);
    P.S(b+1.75,7,0.9,'ghost',a); P.S(b+3.25,13,0.9,'ghost',a)
    if i==3: P.fill(b+3.25,0.75,'stutter',1.0)
    if i==5: P.fill(b+3.5,0.5,'tom',0.9)
    if i==7: P.fill(b+2.0,2.0,'tom',1.1)
P.CR(296,0,0.7,size=1.3)

# ---------------- TAG 296-312 : khong trong, chi mot cross-stick cuoi ----------------
P.S(310,8,0.30,'cross')

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.26,oh_amount=0.90,lofi=0.0,lpf=9500)
print("drums:",round(float(np.abs(DRUMS).max()),2),"peak /",round(float(np.sqrt((DRUMS**2).mean())),4),"rms")


# ===================== ARRANGEMENT (MUSIC) =====================
"""THE GREAT INDOORS - full arrangement + mix.
Run: python3 great-indoors-drums.py first (makes drums_new.npy),
then: python3 great-indoors.py -> THE-GREAT-INDOORS-v2.wav
"""
def _noop(*a,**k): pass
def drums(*a,**k): pass
CH={'Amaj7':['A2','C#4','E4','G#4'],'C#7':['C#3','F3','G#3','B3'],
    'Dmaj7':['D3','F#3','A3','C#4'],'D#dim7':['D#3','F#3','A3','C4'],
    'A/E':['E2','A3','C#4','E4'],'F#7':['F#2','A#3','C#4','E4'],
    'Bm7':['B2','D3','F#3','A3'],'E7sus4':['E2','A3','B3','D4'],
    'A/C#':['C#3','E3','A3','C#4'],'E7':['E2','G#3','B3','D4'],
    'G#':['G#2','C4','D#4','G#4'],'C':['C3','E3','G3','C4'],
    'B7':['B2','D#3','F#3','A3'],'A7':['A2','C#4','E4','G4'],
    'D':['D3','F#3','A3','D4'],'G':['G2','B3','D4','G4'],
    'Gmaj7':['G2','B3','D4','F#4'],'Bm':['B2','D3','F#3','B3'],
    'Bm/A':['A2','D3','F#3','B3'],'A':['A2','C#4','E4','A4']}
def C(n): return [nn(x) for x in CH[n]]
VERSE_P =['Amaj7','C#7','Dmaj7','D#dim7','A/E','F#7','Bm7','E7sus4']
REFR_P  =['Dmaj7','A/C#','Bm7','E7sus4','Dmaj7','A/C#','Bm7','E7']
BRIDGE_P=['G#','Amaj7','G#','Amaj7','C','Dmaj7','C','Dmaj7']
RAMP_P  =['F#7','B7','E7','A7']
OUTRO_P =['D','Dmaj7','G','Gmaj7','Bm','Bm/A','G','A']
gt=buf(); gt2=buf(); sol=buf(); kb=buf(); org=buf(); bs=buf()
dr=buf(); vx=buf(); hn=buf(); fx=buf()
def bed(b_,t0,dur,g,up,lo,hi):
    L=int(dur*SR); t=np.linspace(0,1,L); n=rng.standard_normal(L)
    bq,aq=sg.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); n=sg.lfilter(bq,aq,n)
    put(b_,t0,n*((t**2) if up else ((1-t)**2)),g)

MV=[(0,1,'B3','o'),(1,1,'C#4','o'),(2,1,'B3','u'),
    (4,1.5,'A3','o'),(5.5,.5,'B3','o'),(6,1,'G#3','u'),
    (8,1.5,'E4','a'),(9.5,1,'C#4','o'),(10.5,1,'D4','o'),
    (12,2,'A3','u'),
    (16,1,'B3','o'),(17,1,'C#4','o'),(18,1.5,'E4','a'),
    (20,1,'C#4','o'),(21,1.5,'B3','u'),(22.5,1,'A#3','o'),
    (24,1,'D4','a'),(25,1,'F#4','a'),(26,1,'D4','o'),
    (28,1,'B3','o'),(29,2,'A3','u')]
MR=[(0,2,'F#4','a'),(2,2,'E4','o'),(4,2,'E4','o'),(6,2,'C#4','o'),
    (8,1,'D4','a'),(9,1,'F#4','a'),(10,2,'A4','a'),(12,1.5,'A4','a'),(13.5,2,'E4','o'),
    (16,2,'F#4','a'),(18,2,'E4','o'),(20,2,'E4','o'),(22,2,'C#4','o'),
    (24,1,'D4','a'),(25,1,'F#4','a'),(26,2,'B4','a'),(28,1.5,'B4','a'),(29.5,2.5,'A4','o')]
# BRIDGE: giu NGUYEN mot not trong khi hoa am truot nua cung ben duoi
MB=[(0,1,'G#4','e'),(1,1,'G#4','e'),(2,2,'G#4','e'),
    (4,2,'G#4','e'),(6,2,'G#4','o'),
    (8,1,'G#4','e'),(9,1,'G#4','e'),(10,2,'G#4','o'),
    (12,3,'G#4','u'),
    (16,1,'E4','e'),(17,1,'E4','e'),(18,2,'E4','e'),
    (20,2,'E4','e'),(22,2,'E4','o'),
    (24,1,'E4','e'),(25,1,'E4','e'),(26,2,'E4','o'),
    (28,1,'F#4','a'),(29,1,'G#4','a'),(30,2,'A4','a')]
MO=[(0,1,'A4','a'),(1,1,'A4','a'),(2,1,'B4','a'),(3,1,'A4','a'),
    (4,2,'F#4','o'),
    (8,1,'B4','a'),(9,1,'B4','a'),(10,1,'D5','a'),(11,1,'B4','a'),
    (12,2,'G4','o'),
    (16,1,'D5','a'),(17,1,'D5','a'),(18,1,'E5','a'),(19,1,'D5','a'),
    (20,2,'B4','o'),
    (24,1,'F#5','a'),(25,1,'E5','a'),(26,1,'D5','a'),(28,3,'A4','o')]

def mel(b_,b0,M,fn,shift=0):
    for off,d,nm,v in M:
        fn(b_, T(b0+off), nn(nm)+shift, T(b0+off+d)-T(b0+off), v)

# ================= PART BUILDERS =================
def play_chords(b0,prog,barlen=4,strum=True,g=0.085,seed=0,second=False,arp=None):
    for i,cn in enumerate(prog):
        bb=b0+i*barlen; ns=C(cn)
        tops=[m for m in ns if m>=nn('C3')]
        if arp:                                   # arpeggio jangly
            k=0; p=0.0
            while p<barlen-1e-6:
                jangle(gt,T(bb+p),tops[k%len(tops)]+(12 if k%5==4 else 0),
                       T(bb+p+1.2)-T(bb+p),g,seed=(seed+k)%7)
                p+=arp; k+=1
        if strum:
            for off,acc in [(0,1.0),(1.5,.6),(2,.85),(3.5,.55)]:
                if off<barlen:
                    for j,m in enumerate(tops):
                        jangle(gt,T(bb+off)+j*0.011,m,T(bb+off+1.0)-T(bb+off),g*acc,seed=(seed+i+j)%7)
        if second:
            for off in (1,3):
                for m in tops[:3]:
                    crunch(gt2,T(bb+off),m,T(bb+off+0.5)-T(bb+off),0.055,drive=7)

def play_bass(b0,prog,barlen=4,g=0.30,style='root'):
    for i,cn in enumerate(prog):
        bb=b0+i*barlen; r=min(C(cn))
        if style=='root':
            bassn(bs,T(bb),r,T(bb+2)-T(bb),g,gl=2)
            bassn(bs,T(bb+2.5),r+7,T(bb+3.5)-T(bb+2.5),g*.85)
        elif style=='walk':
            for k,(off,iv) in enumerate([(0,0),(1,7),(2,12),(3,7)]):
                bassn(bs,T(bb+off),r+iv,T(bb+off+0.9)-T(bb+off),g,gl=(2 if k==0 else 0))
        elif style=='eighths':
            p=0.0
            while p<barlen-1e-6:
                iv=0 if int(p*2)%4 in(0,3) else (12 if int(p*2)%4==1 else 7)
                bassn(bs,T(bb+p),r+iv,SPB(bb)*0.45,g); p+=0.5

def play_wurli(b0,prog,barlen=4,g=0.12,sparse=False):
    for i,cn in enumerate(prog):
        bb=b0+i*barlen
        for j,m in enumerate(C(cn)):
            if sparse and j==0: continue
            wurli(kb,T(bb)+j*0.02,m,T(bb+barlen*0.9)-T(bb),g,det=(-6+4*j))
def play_organ(b0,prog,barlen=4,g=0.055):
    for i,cn in enumerate(prog):
        bb=b0+i*barlen
        organ(org,T(bb),[m for m in C(cn) if m>=nn('B2')],T(bb+barlen*0.95)-T(bb),g)

def drums(*a,**k): pass
# ================= ARRANGEMENT =================
bed(fx,0,T(312),0.010,True,60,1400)          # room tone
bed(fx,0,T(312),0.006,False,3000,15000)      # tape hiss

# --- INTRO 0-16 : lounge, chi Wurli ---
play_wurli(0,VERSE_P[:4],4,0.14)
wurli(kb,T(1.6),nn('E4'),T(3)-T(1.6),0.06,det=14)
for k in range(4): _noop(dr,T(12+k),0.22,rim=True)          # dem gay 1-2-3-4
_noop(fx,T(14),T(16)-T(14),0.05,up=True)

# --- VERSE 1 16-48 ---
play_chords(16,VERSE_P,4,strum=False,g=0.075,arp=0.5,seed=1)
play_bass(16,VERSE_P,4,0.27,'root')
play_wurli(16,VERSE_P,4,0.055,sparse=True)

mel(vx,16,MV,lambda b,t,m,d,v: sing(b,t,m,d,v,0.17,breath=0.30,seed=3))

# --- REFRAIN 1 48-80 ---
play_chords(48,REFR_P,4,strum=True,g=0.085,seed=2)
play_bass(48,REFR_P,4,0.30,'walk')
play_wurli(48,REFR_P,4,0.06,sparse=True)

mel(vx,48,MR,lambda b,t,m,d,v: sing(b,t,m,d,v,0.19,breath=0.22,seed=5))
mel(vx,48,MR,lambda b,t,m,d,v: sing(b,t,m-12,d,v,0.055,breath=0.3,seed=9))

# --- VERSE 2 80-112 ---
play_chords(80,VERSE_P,4,strum=False,g=0.075,arp=0.5,seed=3,second=True)
play_bass(80,VERSE_P,4,0.28,'walk')
play_organ(80,VERSE_P,4,0.045)

mel(vx,80,MV,lambda b,t,m,d,v: sing(b,t,m,d,v,0.17,breath=0.26,seed=4))

# --- REFRAIN 2 112-144 ---
play_chords(112,REFR_P,4,strum=True,g=0.095,seed=4,second=True)
play_bass(112,REFR_P,4,0.31,'eighths')
play_organ(112,REFR_P,4,0.055)

mel(vx,112,MR,lambda b,t,m,d,v: sing(b,t,m,d,v,0.19,breath=0.2,seed=6))
mel(vx,112,MR,lambda b,t,m,d,v: gang(vx,t,m,d,v,0.10,n=4,spread=14))

# --- BRIDGE 144-176 : truot nua cung, giu nguyen mot not ---
play_chords(144,BRIDGE_P,4,strum=True,g=0.075,seed=5)
play_bass(144,BRIDGE_P,4,0.30,'root')
play_organ(144,BRIDGE_P,4,0.07)

mel(vx,144,MB,lambda b,t,m,d,v: sing(b,t,m,d,v,0.20,breath=0.24,seed=7))
mel(vx,144,MB,lambda b,t,m,d,v: sing(b,t,m-12,d,v,0.07,breath=0.34,seed=11))

# --- RAMP 176-192 : chuoi at phu vong quang 5 ---
play_chords(176,RAMP_P,4,strum=True,g=0.10,seed=6,second=True)
play_bass(176,RAMP_P,4,0.32,'eighths')
play_organ(176,RAMP_P,4,0.08)

for i,(cn,mno) in enumerate(zip(RAMP_P,['A#4','D#5','G#4','C#5'])):
    gang(vx,T(176+i*4),nn(mno),T(176+i*4+3)-T(176+i*4),'a',0.09+0.02*i,n=4)
_noop(fx,T(184),T(192)-T(184),0.22,up=True)

# --- CUT 192-200 : gan nhu im lang ---
_noop(dr,T(192),0.5,rim=True)
wurli(kb,T(192),nn('A3'),T(196)-T(192),0.10,det=-8)
wurli(kb,T(192.05),nn('C#4'),T(196)-T(192),0.08,det=6)
sing(vx,T(193),nn('A4'),T(196)-T(193),'u',0.16,breath=0.4,seed=2)
_noop(fx,T(196),T(200)-T(196),0.16,up=True)
for k in range(8): _noop(dr,T(196+k*0.5),0.03+0.02*k)

# --- OUTRO 1  200-232 : mot giong ---
play_chords(200,OUTRO_P,4,strum=True,g=0.10,seed=7,arp=1.0)
play_bass(200,OUTRO_P,4,0.32,'eighths')
play_organ(200,OUTRO_P,4,0.07)

mel(vx,200,MO,lambda b,t,m,d,v: sing(b,t,m,d,v,0.20,breath=0.2,seed=8))

# --- OUTRO 2  232-264 : gang vocal + ken ---
play_chords(232,OUTRO_P,4,strum=True,g=0.11,seed=8,second=True,arp=1.0)
play_bass(232,OUTRO_P,4,0.33,'eighths')
play_organ(232,OUTRO_P,4,0.085)

mel(vx,232,MO,lambda b,t,m,d,v: gang(vx,t,m,d,v,0.15,n=6,spread=18))
mel(vx,232,MO,lambda b,t,m,d,v: sing(b,t,m,d,v,0.13,breath=0.18,seed=12))
HORN=[(0,2,'D4'),(2,2,'F#4'),(4,2,'A4'),(6,2,'F#4'),
      (8,2,'B3'),(10,2,'D4'),(12,4,'G4'),
      (16,2,'F#4'),(18,2,'B4'),(20,4,'A4'),
      (24,2,'D4'),(26,2,'E4'),(28,4,'F#4')]
for off,d,m in HORN:
    horn(hn,T(232+off),nn(m),T(232+off+d)-T(232+off),0.085,det=+7,rough=0.9)
    horn(hn,T(232+off)+0.012,nn(m)-12,T(232+off+d)-T(232+off),0.075,det=-9,rough=1.1)

# --- OUTRO 3  264-296 : max + solo guitar ---
play_chords(264,OUTRO_P,4,strum=True,g=0.115,seed=9,second=True,arp=0.5)
play_bass(264,OUTRO_P,4,0.34,'eighths')
play_organ(264,OUTRO_P,4,0.09)

mel(vx,264,MO,lambda b,t,m,d,v: gang(vx,t,m,d,v,0.16,n=7,spread=20))
mel(vx,264,MO,lambda b,t,m,d,v: gang(vx,t,m+12,d,v,0.085,n=3,spread=22))   # D5-D6
for off,d,m in HORN:
    horn(hn,T(264+off),nn(m)+ (12 if d<=2 else 0),T(264+off+d)-T(264+off),0.095,det=+8,rough=1.0)
    horn(hn,T(264+off)+0.014,nn(m)-12,T(264+off+d)-T(264+off),0.085,det=-10,rough=1.1)
SOLO=[(0,.75,'D5',0),(0.75,.75,'F#5',0),(1.5,1,'A5',0),(2.5,1.5,'G5',-1),
      (4,.5,'F#5',0),(4.5,.5,'E5',0),(5,2,'D5',2),
      (8,.75,'B4',0),(8.75,.75,'D5',0),(9.5,1.5,'G5',0),(11,1,'F#5',0),
      (12,.5,'E5',0),(12.5,.5,'D5',0),(13,3,'B4',1),
      (16,1,'D5',0),(17,1,'E5',0),(18,1,'F#5',0),(19,1,'A5',0),
      (20,4,'B5',-2),
      (24,.5,'A5',0),(24.5,.5,'G5',0),(25,.5,'F#5',0),(25.5,.5,'E5',0),
      (26,1,'D5',0),(27,5,'A5',2)]
for off,d,m,bd in SOLO:
    leadgtr(sol,T(264+off),nn(m),T(264+off+d)-T(264+off),0.115,bend=bd,seed=int(off)%5)

# --- TAG 296-312 : quay ve Wurli co doc, dung o Amaj7 (V trong Re truong => khong giai quyet) ---
for j,m in enumerate(C('Amaj7')):
    wurli(kb,T(296)+j*0.03,m,T(303)-T(296),0.13,det=(-7+5*j))
wurli(kb,T(300),nn('B4'),T(303)-T(300),0.05,det=11)
for j,m in enumerate(C('Amaj7')):
    wurli(kb,T(304)+j*0.03,m,T(312)-T(304),0.11,det=(-9+6*j))
sing(vx,T(305),nn('E4'),T(310)-T(305),'u',0.11,breath=0.45,seed=1)
_noop(fx,T(296),T(312)-T(296),0.014,up=False,lo=60,hi=2000)
print("arranged")


DRUMS=np.asarray(DRUMS)
if len(DRUMS)<len(dr): DRUMS=np.concatenate([DRUMS,np.zeros(len(dr)-len(DRUMS))])
dr[:]=DRUMS[:len(dr)]
print("arranged (trong moi, khong riser)")

# ================= MIX =================
def comp(x,thr,ratio,atk,rel):
    e=np.abs(x); aA=np.exp(-1/(atk*SR)); aR=np.exp(-1/(rel*SR))
    e=np.maximum(sg.lfilter([1-aR],[1,-aR],e),sg.lfilter([1-aA],[1,-aA],e))
    g=np.ones_like(e); o=e>thr; g[o]=(thr+(e[o]-thr)/ratio)/np.maximum(e[o],1e-9)
    bg,ag=sg.butter(2,70/(SR/2),'low'); return x*np.clip(sg.lfilter(bg,ag,g),0.06,1.0)
def hp(x,f,o=2): b,a=sg.butter(o,f/(SR/2),'high'); return sg.lfilter(b,a,x)
def lp(x,f,o=2): b,a=sg.butter(o,f/(SR/2),'low');  return sg.lfilter(b,a,x)
def bp(x,lo,hi,o=2): b,a=sg.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return sg.lfilter(b,a,x)

V=hp(vx,150); V=comp(V,0.045,4.0,0.005,0.13); V=comp(V,0.085,3.2,0.001,0.05)
V=V+bp(V,1900,4300)*1.15+hp(V,7200)*0.55
V=hp(V,300); V=np.tanh(V*1.1)*2.95

G1=comp(bp(gt,180,7000),0.05,3.5,0.006,0.10)*2.2
G2=comp(bp(gt2,280,4200),0.05,4.0,0.004,0.09)*2.1
SOLOB=comp(bp(sol,380,4600),0.05,4.0,0.003,0.10)*2.6
KB=comp(lp(hp(kb,120),5200),0.06,3.0,0.008,0.12)*1.25
ORG=comp(bp(org,200,6000),0.05,3.0,0.01,0.15)*1.20
HN=comp(bp(hn,230,5600),0.05,3.2,0.02,0.14)*1.7

ve=lp(np.abs(V),13); ve/=(np.percentile(ve,99.5)+1e-9)
duckV=np.clip(1-0.34*np.clip(ve,0,1),0.6,1.0)
def carve(x,amt=0.45): return (x-bp(x,1500,4000)*amt*(1-duckV)/0.34)*duckV
G1=carve(G1); KB=carve(KB); ORG=carve(ORG,0.60); HN=carve(HN,0.55); SOLOB=carve(SOLOB,0.50)

BS=hp(comp(bs,0.10,3.0,0.01,0.12),50)*0.82
# --- trong moi: chuan hoa roi nen bus (Fridmann: nen song song bang thiet bi xau) ---
D0=dr/(np.abs(dr).max()+1e-9)*0.95
DR=comp(D0,0.16,3.0,0.004,0.10)*0.72
crush=hp(np.tanh(D0*4.2),175)*0.24

WL=G1*0.55+np.roll(G2,int(0.008*SR))*0.5+KB*0.5+ORG*0.5+SOLOB*0.45+HN*0.5+fx*1.0
WR=np.roll(G1,int(0.013*SR))*0.5+G2*0.55+KB*0.5+ORG*0.5+SOLOB*0.55+HN*0.5+fx*0.9
CEN=V*1.0+BS*1.0+DR*1.0+crush*1.0
L,R=reverb(WL,WR,1.5,0.20)
M=(L+R)*0.5; S=hp((L-R)*0.5,230)*2.1
L,R=M+S,M-S
L=L+CEN; R=R+CEN
st=np.stack([L,R]); st=np.tanh(st*0.80); st=hp(st,26)
st/=np.abs(st).max(); st*=0.94
f=int(0.02*SR); st[:,:f]*=np.linspace(0,1,f)
fo=int(2.5*SR); st[:,-fo:]*=np.linspace(1,0,fo)**0.8
write_wav('THE-GREAT-INDOORS-v2.wav', st.T.astype(np.float32))
def rms_(x): return float(np.sqrt((np.asarray(x)**2).mean()+1e-18))
REST=(G1+G2+KB+ORG+SOLOB+HN+fx)+BS+DR+crush
lb=bp(V,300,4000); rb=bp(REST,300,4000)
print(f"\nDONE {st.shape[1]/SR:.1f}s  peak {np.abs(st).max():.2f} rms {rms_(st):.4f}")
MAP=[('INTRO',0,16),('VERSE1',16,48),('REFRAIN1',48,80),('VERSE2',80,112),('REFRAIN2',112,144),
     ('BRIDGE',144,176),('RAMP',176,192),('CUT',192,200),('OUTRO1',200,232),
     ('OUTRO2',232,264),('OUTRO3',264,296),('TAG',296,312)]
mono=st.mean(0)
print("doan            giong/con-lai   nang luong")
for nm,b0,b1 in MAP:
    sl=slice(int(T(b0)*SR),int(T(b1)*SR))
    r=20*np.log10(rms_(lb[sl])/max(rms_(rb[sl]),1e-12))
    print(f"  {nm:9s} {int(T(b0)//60)}:{T(b0)%60:04.1f} {r:+6.1f} dB   rms {rms_(mono[sl]):.4f} {'█'*int(rms_(mono[sl])*90)}")
