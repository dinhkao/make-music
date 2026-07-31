"""
Lop bieu dien: nhan hoa theo so lieu do duoc, + mo hinh micro/bleed.
Nguyen tac chinh (nguoc voi cach lam thong thuong):
  - TIMING: ~50% la mau lech CO DINH lap moi o nhip (systematic), ~50% la nhieu Gauss.
  - VELOCITY: mau accent gan nhu TAT DINH (r=0.92 giua cac o nhip), chi +-4% nhieu.
  - Jitter ONSET tuyet doi, khong jitter khoang cach -> tu sinh anticorrelation lag-1.
  - Not tren phach danh TRE (+2..6ms), not le 16 danh SOM (-2..6ms)  [Groove MIDI Dataset]
"""
import numpy as np
from scipy import signal as sg
from kit import Kit, SR, _hp, _lp, _bp

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
print("performer ok")
