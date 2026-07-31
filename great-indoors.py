"""THE GREAT INDOORS - full arrangement + mix.
Run: python3 great-indoors-drums.py first (makes drums_new.npy),
then: python3 great-indoors.py -> THE-GREAT-INDOORS-v2.wav
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal as sg
from gi_engine import *
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


DRUMS=np.load('drums_new.npy').astype(np.float64)
if len(DRUMS)<len(dr): DRUMS=np.concatenate([DRUMS,np.zeros(len(dr)-len(DRUMS))])
dr[:]=DRUMS[:len(dr)]
print("arranged (trong moi, khong riser)")

# ================= MIX =================
from render import chorus as chfx, reverb, write_wav
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
