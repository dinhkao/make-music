"""THE GREAT INDOORS - drum arrangement (Performer/Kit engine).
Run: python3 great-indoors-drums.py -> drums_new.npy (mono drum bus)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gi_engine import T, SPB, TOTAL, rng
from kit import Kit
from perform import Performer, mix_kit

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
np.save('drums_new.npy', DRUMS.astype(np.float32))
print("saved drums_new.npy", DRUMS.shape)
